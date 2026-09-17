/**
 * Pre-compress the text assets, once, at build time.
 *
 * nginx's `gzip on` re-compresses every response at level 1 for every request, on
 * every server it runs on, forever. `gzip_static on` instead serves a .gz sitting next
 * to the file — so the work happens here, at maximum level, and the bytes on the wire
 * shrink while the CPU cost per request drops to zero. Both halves of that are the
 * point: less energy in the datacentre, fewer bytes over the radio.
 *
 * Only text is worth it. AVIF, WebP, JPEG and woff2 are already compressed — woff2 is
 * brotli internally — and gzipping them again spends CPU to produce a larger file,
 * which is why COMPRESSIBLE is an allow-list rather than a deny-list.
 */

import { gzipSync, constants } from "node:zlib";
import { readFile, readdir, stat, writeFile } from "node:fs/promises";
import { extname, join } from "node:path";
import { fileURLToPath } from "node:url";

const DIST = fileURLToPath(new URL("../dist", import.meta.url));

const COMPRESSIBLE = new Set([
  ".html",
  ".css",
  ".js",
  ".json",
  ".svg",
  ".xml",
  ".txt",
  ".map",
]);

/**
 * gzip is not going to beat the framing overhead below roughly this size, and nginx
 * would still have to open a second file to find that out.
 */
const MIN_BYTES = 1024;

/**
 * Walk a directory tree.
 *
 * @param {string} dir
 * @returns {AsyncGenerator<string>} Absolute paths of every file below `dir`.
 */
async function* walk(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) yield* walk(full);
    else yield full;
  }
}

async function compress() {
  let raw = 0;
  let packed = 0;
  let count = 0;

  for await (const file of walk(DIST)) {
    if (!COMPRESSIBLE.has(extname(file))) continue;
    if ((await stat(file)).size < MIN_BYTES) continue;

    const source = await readFile(file);
    const gz = gzipSync(source, {
      level: constants.Z_BEST_COMPRESSION,
      // The largest window and memory level the format allows. Costs a few
      // milliseconds here and nothing at serve time.
      windowBits: 15,
      memLevel: 9,
    });

    // A .gz that came out bigger would be served in preference to the original by
    // gzip_static, so drop it rather than ship it.
    if (gz.length >= source.length) continue;

    await writeFile(`${file}.gz`, gz);
    raw += source.length;
    packed += gz.length;
    count += 1;
  }

  console.log(
    `  ${count} files  ${(raw / 1024).toFixed(0)} KB -> ` +
      `${(packed / 1024).toFixed(0)} KB gzipped (-${(100 * (1 - packed / raw)).toFixed(0)}%)`,
  );
}

await compress();
