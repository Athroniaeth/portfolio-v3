<script lang="ts">
  import type { SectionCopy } from "../lib/content";
  import { t, useLocale } from "../lib/i18n";

  let { copy }: { copy: SectionCopy } = $props();

  const locale = useLocale();
</script>

<div class="reveal">
  <h2 class="text-primary text-sm font-medium tracking-widest uppercase">
    {t(copy.heading, locale)}
  </h2>
  <p class="mt-3 text-2xl font-medium tracking-tight sm:text-4xl">
    {t(copy.subheading, locale)}
  </p>
  {#if t(copy.paragraph, locale)}
    <p class="text-muted-foreground mt-4 max-w-3xl leading-relaxed text-pretty">
      {t(copy.paragraph, locale)}
    </p>
  {/if}
</div>
