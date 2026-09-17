<script lang="ts">
  import type { Locale } from "../lib/i18n";

  /**
   * The two flags, drawn rather than imported.
   *
   * Flag emoji would have been one character, but Windows ships no flag glyphs and
   * renders them as the two-letter code instead — so the control would read "FR" on
   * one machine and show a flag on another. These are a handful of rects and strokes,
   * inlined into the HTML at build time.
   */
  let { locale, class: className = "" }: { locale: Locale; class?: string } =
    $props();

  // The language menu draws every flag, so the Union Jack now appears more than once
  // in a document and a hardcoded clip-path id would be duplicated. `$props.id()` is
  // unique per instance and stable across the render.
  const uid = $props.id();
</script>

{#if locale === "fr"}
  <svg viewBox="0 0 3 2" class={className} aria-hidden="true">
    <rect width="3" height="2" fill="#f5f5f5" />
    <rect width="1" height="2" fill="#002395" />
    <rect x="2" width="1" height="2" fill="#ed2939" />
  </svg>
{:else}
  <!-- The Union Jack's diagonals are red only on one side of each arm, which is what
       the clip path produces; without it the saltire comes out symmetrical and wrong. -->
  <svg viewBox="0 0 60 30" class={className} aria-hidden="true">
    <clipPath id="flag-saltire-{uid}">
      <path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z" />
    </clipPath>
    <rect width="60" height="30" fill="#012169" />
    <path d="M0,0 L60,30 M60,0 L0,30" stroke="#f5f5f5" stroke-width="6" />
    <path
      d="M0,0 L60,30 M60,0 L0,30"
      clip-path="url(#flag-saltire-{uid})"
      stroke="#c8102e"
      stroke-width="4"
    />
    <path d="M30,0 v30 M0,15 h60" stroke="#f5f5f5" stroke-width="10" />
    <path d="M30,0 v30 M0,15 h60" stroke="#c8102e" stroke-width="6" />
  </svg>
{/if}
