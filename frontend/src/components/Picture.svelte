<script lang="ts">
  import { images, type ImageTarget } from "../lib/content";

  interface Props {
    /** File stem under /images — the encoder emits one file per width and format. */
    src: string;
    alt: string;
    /** Which entry of the image manifest describes this picture's painted box. */
    target: keyof typeof images;
    /** Above the fold, so the browser must not defer it. */
    eager?: boolean;
    class?: string;
  }

  let {
    src,
    alt,
    target,
    eager = false,
    class: className = "",
  }: Props = $props();

  // $derived, not a plain const: reading a prop at initialisation captures its first
  // value only. Nothing re-renders these pages today — they are written to disk once —
  // but a component that silently ignores a changed prop is a trap for whoever reuses
  // it, and svelte-check is right to say so.
  const spec: ImageTarget = $derived(images[target]);

  /**
   * One <img>, no <picture>, and the format left to the server.
   *
   * The encoder still writes AVIF and WebP side by side, and a visitor still receives
   * whichever of the two their browser can decode — but the choosing now happens in
   * nginx, which reads the Accept header and hands over the AVIF for a URL that names
   * the WebP. See the /images/ block in deploy/default.conf.template.
   *
   * The markup this replaces was a <picture> with a <source> per format, three
   * elements for every image and twenty-one across the page, spent asking the browser
   * a question the server could answer on its own.
   *
   * `x` descriptors rather than `w`: these boxes are a fixed number of CSS pixels at
   * every breakpoint, so the only question left is the screen's pixel density. A `w`
   * set would oblige every <img> to carry a `sizes` attribute restating a width the
   * CSS already fixes, and would let a browser pick a file wider than the box.
   */
  const srcset = $derived(
    spec.widths.map((w, i) => `/images/${src}-${w}.webp ${i + 1}x`).join(", "),
  );
  const fallback = $derived(`/images/${src}-${spec.widths[0]}.webp`);
</script>

<!-- width/height are the intrinsic size, so the box is reserved before the bytes
     arrive and nothing below it jumps. -->
<img
  src={fallback}
  {srcset}
  {alt}
  width={spec.width}
  height={spec.height}
  class={className}
  loading={eager ? "eager" : "lazy"}
  fetchpriority={eager ? "high" : undefined}
  decoding="async"
/>
