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
   * `scroll-mt-20` is not decoration: the header is sticky and 4rem tall, so without
   * it the browser would park the heading of every section underneath the header.
   * The extra rem is breathing room.
   */
  let { id, children }: { id: SectionId; children: Snippet } = $props();
</script>

<section {id} class="scroll-mt-20 py-20 md:py-32">
  <div class="container space-y-12 md:space-y-16">
    <SectionIntro copy={content.sections[id]} />
    {@render children()}
  </div>
</section>
