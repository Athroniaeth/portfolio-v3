/**
 * Re-encode the source images to the sizes the pages actually paint.
 *
 * The site this replaces served the originals: a 400x400 PNG avatar (197 KB) behind a
 * 36 px circle, and 1152x648 screenshots (203 KB) behind a 300x100 card. The waste was
 * not the codec, it was the pixels — the browser downloaded, decoded and then threw
 * away more than 90% of them.
 *
 * So each target here declares the box it is painted in, and the encoder crops to that
 * box rather than leaving the work to `object-fit`. Two widths per target cover 1x and
 * 2x screens, and `<picture>` offers AVIF first with WebP behind it. There is no
 * PNG/JPEG fallback: WebP has been supported everywhere that matters for years, and
 * carrying a third copy to serve a rounding error of traffic is its own kind of waste.
 *
 * Quality is set where artefacts stop being visible at these sizes rather than at the
 * codec defaults — see QUALITY. Run with `just images`; the output is committed, so
 * Dockerfile.web needs neither sharp nor its native binaries.
 */

import { copyFile, mkdir, readdir, rm, writeFile } from "node:fs/promises";
import { basename, extname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { statSync } from "node:fs";

import sharp from "sharp";

const ROOT = fileURLToPath(new URL("../..", import.meta.url));
const SOURCE_DIR = join(ROOT, "assets", "images");
const OUTPUT_DIR = join(ROOT, "frontend", "public", "images");
// The manifest is a build-time input, not an asset: writing it under public/ would
// ship a file to every visitor that only the prerenderer ever reads.
const MANIFEST = join(ROOT, "frontend", "src", "data", "images.json");
// Icons sit at the root of public/ rather than under images/, because a favicon is
// referenced by convention from paths this project does not control.
const ICONS_DIR = join(ROOT, "frontend", "public", "icons");

/**
 * AVIF at 55 and WebP at 80 are where a side-by-side stops showing a difference on
 * these crops. `effort` is maxed because this runs once on a laptop, not per request:
 * the extra seconds buy roughly 10% off every file, for every visitor, forever.
 */
const QUALITY = {
  avif: { quality: 55, effort: 9, chromaSubsampling: "4:2:0" },
  webp: { quality: 80, effort: 6 },
};

/**
 * Painted boxes, in CSS pixels, with the widths to emit for each.
 *
 * Both follow the root font size, which app.css sets to 110%. The boxes are sized in
 * `rem` like everything else, so leaving these behind would mean a 300 px file
 * stretched across a 330 px window — exactly the kind of waste this script exists to
 * remove, run backwards.
 *
 * `cards` matches the 3:1 window in ProjectsList, so the crop happens here instead of
 * in the browser. `avatar` is the 39.6 px header circle, rounded up to 40 so the 2x
 * file lands on a whole number.
 */
const TARGETS = {
  cards: { width: 330, height: 110, widths: [330, 660], position: "top" },
  avatar: { width: 40, height: 40, widths: [40, 80], position: "centre" },
};

/**
 * Favicon sizes. PNG, not AVIF or WebP: a favicon is read by browser chrome, feed
 * readers and OS launchers, and the one format all of them accept is PNG.
 *
 * The site this replaces served a single 256x256 ICO weighing 103 KB to draw a 16 px
 * square in a tab — more than this whole page now costs.
 */
const ICONS = [
  { size: 32, name: "favicon-32.png" },
  // Apple asks for 180x180 and composites its own rounded corners on top.
  { size: 180, name: "apple-touch-icon.png" },
];

/** Sources that are not part of a responsive set and get their own treatment. */
const SINGLES = {
  // Open Graph previews are fetched by crawlers, never by a visitor, and several of
  // them still refuse AVIF and WebP, so this one stays a JPEG. It is also copied
  // rather than re-encoded: the source is already 1200x630 at a sane quality, and
  // every setting tried came out larger (q82: 25.9 KB, q75: 23.3 KB, source: 23.6 KB)
  // while adding a second generation of JPEG loss for nothing.
  "opengraph.jpg": async (input, outDir) => {
    const out = join(outDir, "opengraph.jpg");
    const { width, height } = await sharp(input).metadata();
    if (width !== 1200 || height !== 630) {
      throw new Error(
        `opengraph.jpg must be 1200x630 to be copied verbatim, got ${width}x${height}`,
      );
    }
    await copyFile(input, out);
    return [{ file: out, bytes: statSync(out).size }];
  },
};

/**
 * Encode one source into every width and format of a target.
 *
 * @param {string} input Absolute path to the source image.
 * @param {string} outDir Absolute path to the directory to write into.
 * @param {{width: number, height: number, widths: number[], position: string}} target
 * @returns {Promise<{file: string, bytes: number}[]>} What was written.
 */
async function encodeResponsive(input, outDir, target) {
  const stem = basename(input, extname(input));
  const ratio = target.height / target.width;
  const written = [];

  for (const width of target.widths) {
    // `density` only affects vector input: rasterising an SVG at its default 72 dpi
    // and then upscaling would produce a blurry 2x file.
    const pipeline = sharp(input, {
      density: 72 * (width / target.width),
    }).resize(width, Math.round(width * ratio), {
      fit: "cover",
      position: target.position,
    });

    for (const [format, options] of Object.entries(QUALITY)) {
      const file = join(outDir, `${stem}-${width}.${format}`);
      const info = await pipeline.clone()[format](options).toFile(file);
      written.push({ file, bytes: info.size });
    }
  }

  return written;
}

/** Re-encode everything under assets/images into frontend/public/images. */
async function optimizeImages() {
  // Wipe rather than overwrite: a source removed from assets/ must not leave a
  // stale derivative behind to be deployed forever.
  await rm(OUTPUT_DIR, { recursive: true, force: true });
  await mkdir(join(OUTPUT_DIR, "projects"), { recursive: true });
  await rm(ICONS_DIR, { recursive: true, force: true });
  await mkdir(ICONS_DIR, { recursive: true });

  const report = [];

  const projectsIn = join(SOURCE_DIR, "projects");
  const projectsOut = join(OUTPUT_DIR, "projects");
  for (const name of (await readdir(projectsIn)).sort()) {
    const input = join(projectsIn, name);
    const written = await encodeResponsive(input, projectsOut, TARGETS.cards);
    report.push({ source: input, written });
  }

  for (const name of (await readdir(SOURCE_DIR)).sort()) {
    const input = join(SOURCE_DIR, name);
    if (statSync(input).isDirectory()) continue;

    if (SINGLES[name]) {
      report.push({
        source: input,
        written: await SINGLES[name](input, OUTPUT_DIR),
      });
      continue;
    }
    if (name.startsWith("avatar")) {
      const written = await encodeResponsive(input, OUTPUT_DIR, TARGETS.avatar);
      // The favicon is the same portrait, so it is cut from the same source rather
      // than from a second file that could drift away from it.
      for (const icon of ICONS) {
        const file = join(ICONS_DIR, icon.name);
        const info = await sharp(input)
          .resize(icon.size, icon.size, { fit: "cover" })
          .png({ compressionLevel: 9, palette: true })
          .toFile(file);
        written.push({ file, bytes: info.size });
      }
      report.push({ source: input, written });
    }
  }

  let before = 0;
  let after = 0;
  for (const { source, written } of report) {
    const sourceBytes = statSync(source).size;
    const outBytes = written.reduce((sum, w) => sum + w.bytes, 0);
    before += sourceBytes;
    after += outBytes;
    const kb = (n) => `${(n / 1024).toFixed(1)} KB`;
    console.log(
      `${basename(source).padEnd(30)} ${kb(sourceBytes).padStart(9)} -> ` +
        `${kb(outBytes).padStart(9)} in ${written.length} files`,
    );
  }
  console.log(
    `\ntotal ${(before / 1024).toFixed(0)} KB of sources -> ` +
      `${(after / 1024).toFixed(0)} KB of derivatives ` +
      `(a page paints one width in one format, not all of them)`,
  );

  // A manifest so the <picture> markup never has to guess which widths exist.
  await writeFile(
    MANIFEST,
    JSON.stringify(
      {
        cards: { ...TARGETS.cards, formats: Object.keys(QUALITY) },
        avatar: { ...TARGETS.avatar, formats: Object.keys(QUALITY) },
      },
      null,
      2,
    ) + "\n",
  );
}

await optimizeImages();
