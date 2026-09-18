<script lang="ts">
  import type { Testimonial } from "../lib/content";
  import { formatDate, t, testimonialKinds, useLocale } from "../lib/i18n";
  import Icon from "./Icon.svelte";

  let { testimonial }: { testimonial: Testimonial } = $props();

  const locale = useLocale();
  const stars = $derived(
    Array.from({ length: testimonial.rating ?? 0 }, (_, index) => index),
  );

  // Name, role and company on one line, skipping whichever is absent. A freelance peer
  // has no employer, and joining with a fixed separator would leave a dangling comma.
  const byline = $derived(
    [testimonial.author, testimonial.role, testimonial.company]
      .filter(Boolean)
      .join(", "),
  );
</script>

<figure class="bg-muted/40 reveal flex flex-col rounded-2xl border p-6 md:p-8">
  <div class="flex flex-wrap items-center gap-x-3 gap-y-2">
    {#if testimonial.rating}
      <!-- Drawn as icons but announced as text: five identical glyphs tell a screen
           reader nothing. -->
      <div
        class="flex items-center gap-1"
        role="img"
        aria-label="{testimonial.rating}/5"
      >
        {#each stars as star (star)}
          <Icon name="star" class="fill-primary stroke-primary size-4" />
        {/each}
      </div>
    {/if}
    <span
      class="text-muted-foreground rounded-full border px-2 py-0.5 text-[0.625rem] tracking-wide uppercase"
    >
      {t(testimonialKinds[testimonial.kind], locale)}
    </span>
  </div>

  <blockquote class="mt-4 leading-7 text-pretty">
    {t(testimonial.quote, locale)}
  </blockquote>

  <figcaption class="text-muted-foreground mt-5 text-sm">
    <span class="text-foreground font-medium">{testimonial.author}</span
    >{byline.slice(testimonial.author.length)} ·
    {formatDate(testimonial.published, locale)} ·
    <!-- Linked only when the quote is actually readable at the other end. Malt shows
         that a recommendation exists but hides its text behind a login, so that one
         names its source without pretending to link to it. -->
    {#if testimonial.source_url}
      <a
        href={testimonial.source_url}
        target="_blank"
        rel="noopener noreferrer"
        class="hover:text-primary underline underline-offset-4"
      >
        {testimonial.source}
      </a>
    {:else}
      {testimonial.source}
    {/if}
  </figcaption>
</figure>
