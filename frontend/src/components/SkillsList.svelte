<script lang="ts">
  import { useLocale } from "../lib/i18n";
  import { skillGroups } from "../lib/skills";

  /**
   * The skills section: a row per group, and no boxes at all.
   *
   * Chosen over a card grid because of where it sits. The projects above it are six
   * cards and the testimonials below are two more, so a third grid of frames made the
   * page read as nothing but boxes. Rows separated by hairlines give the eye somewhere
   * to rest, and the section is a list of short labels — it does not need a container
   * each.
   *
   * The middle dots are aria-hidden. A screen reader should announce the items, not
   * "Python middle dot FastAPI middle dot Litestar".
   */
  const locale = useLocale();
  const groups = skillGroups(locale);
</script>

<dl class="reveal divide-y">
  {#each groups as group (group.name)}
    <div class="grid gap-1 py-4 sm:grid-cols-[11rem_1fr] sm:gap-6">
      <dt
        class="text-muted-foreground pt-0.5 text-xs font-semibold tracking-wide uppercase"
      >
        {group.name}
      </dt>
      <dd class="flex flex-wrap items-baseline gap-x-2 gap-y-1 text-sm">
        {#each group.items as item, index (item)}
          {#if index > 0}
            <span class="text-muted-foreground/40" aria-hidden="true">·</span>
          {/if}
          <span>{item}</span>
        {/each}
      </dd>
    </div>
  {/each}
</dl>
