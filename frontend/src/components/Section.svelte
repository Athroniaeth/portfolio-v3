<script lang="ts">
  import type { Snippet } from "svelte";
  import { content } from "../lib/content";
  import type { SectionId } from "../lib/site";
  import SectionIntro from "./SectionIntro.svelte";

  /**
   * One section of the page, and the anchor the header scrolls to.
   *
   * The id comes from the content struct rather than being typed here, so a section
   * and the nav entry that points at it cannot end up with different names.
   *
   * Clearing the sticky header is `scroll-padding-top` on the scroller, in app.css,
   * rather than a `scroll-mt` on each section here. Same result for an anchor click,
   * and it also covers the case a per-section margin never did: tabbing to a link
   * below the fold, which used to land focus underneath the header.
   *
   * The section *is* the container rather than wrapping one. Nothing here needs to
   * bleed to the edge of the viewport, so the outer element was a node per section
   * doing nothing but hold a class.
   */
  let { id, children }: { id: SectionId; children: Snippet } = $props();
</script>

<section {id} class="container space-y-12 py-20 md:space-y-16 md:py-32">
  <SectionIntro copy={content.sections[id]} />
  {@render children()}
</section>
