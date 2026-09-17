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
   * `x` descriptors rather than `w`: these boxes are a fixed number of CSS pixels at
   * every breakpoint, so the only question is the screen's pixel density. A `w` set
   * would oblige every <img> to carry a `sizes` attribute restating a width the CSS
   * already fixes, and would let a browser pick a file wider than the box.
   */
  function srcset(format: string): string {
    return spec.widths
      .map((w, i) => `/images/${src}-${w}.${format} ${i + 1}x`)
      .join(", ");
  }

  // The <img> fallback points at WebP, not the original PNG/JPEG: every browser that
  // can run this site has supported it for years, and a third copy of each image
  // would be weight in the repo and the image for traffic that does not exist.
  const fallback = $derived(`/images/${src}-${spec.widths[0]}.webp`);
</script>

<picture>
  {#each spec.formats as format (format)}
    {#if format !== "webp"}
      <source type="image/{format}" srcset={srcset(format)} />
    {/if}
  {/each}
  <source type="image/webp" srcset={srcset("webp")} />
  <!-- width/height are the intrinsic size, so the box is reserved before the bytes
       arrive and nothing below it jumps. -->
  <img
    src={fallback}
    {alt}
    width={spec.width}
    height={spec.height}
    class={className}
    loading={eager ? "eager" : "lazy"}
    fetchpriority={eager ? "high" : undefined}
    decoding="async"
  />
</picture>
