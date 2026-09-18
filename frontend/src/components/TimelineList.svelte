<script lang="ts">
  import { content } from "../lib/content";
  import {
    achievementKinds,
    formatDuration,
    formatRange,
    messages,
    t,
    useLocale,
    type AchievementKind,
  } from "../lib/i18n";
  import Icon from "./Icon.svelte";
  import type { IconName } from "../lib/icons";

  const locale = useLocale();
</script>

<ul class="space-y-10">
  {#each content.timeline as entry (entry.year)}
    <li class="reveal space-y-8">
      <!-- `w-fit` so the heading hugs the year the way the inner span used to,
           without being an element on its own. -->
      <h3
        class="border-primary/40 w-fit rounded-2xl border px-4 py-2 font-medium"
      >
        {entry.year}
      </h3>
      <ul class="space-y-6 pl-6">
        {#each entry.achievements as achievement (achievement.title.en)}
          {@const kind = achievementKinds[achievement.kind as AchievementKind]}
          <li class="flex items-start gap-x-2">
            <!-- The icon changes with the kind of entry. Drawing a job, a diploma and a
                 chess title with the same tick made two runner-up finishes read as
                 qualifications. -->
            <Icon
              name={kind.icon as IconName}
              class="stroke-primary h-[1lh] w-5 flex-none"
            />
            <div>
              <!-- The kind sits inside the heading rather than in a flex row beside
                   it. One element fewer per entry, and a screen reader reading the
                   outline hears "Data Scientist chez Scalian, expérience", which is
                   the distinction the chip exists to draw in the first place. -->
              <h4
                class="flex flex-wrap items-baseline gap-x-2 gap-y-1 font-medium tracking-tight"
              >
                {t(achievement.title, locale)}
                <span
                  class="text-muted-foreground rounded-full border px-2 py-0.5 text-[0.625rem] tracking-wide uppercase"
                >
                  {t(kind.label, locale)}
                </span>
              </h4>

              <!-- Dates and length are computed from the period in content.py rather
                   than written into the title, which is how the old site ended up
                   claiming a twenty-month job had lasted "1 year, 2 month". -->
              {#if achievement.period}
                <!-- The dot is a text node, not an aria-hidden element. Screen
                     readers do not announce punctuation at their default verbosity,
                     so the element bought nothing and cost one node per entry. -->
                <p class="text-muted-foreground mt-0.5 text-xs">
                  {formatRange(achievement.period, locale)} ·
                  {formatDuration(achievement.period, locale)}
                </p>
              {/if}

              <p class="text-muted-foreground mt-1 max-w-[85ch] text-sm/normal">
                {t(achievement.description, locale)}
              </p>

              {#if achievement.url}
                <a
                  href={achievement.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary mt-1 inline-flex items-center gap-1 text-xs font-medium hover:underline"
                >
                  {t(messages.verify, locale)}
                  <Icon name="arrowUpRight" class="size-3" />
                </a>
              {/if}
            </div>
          </li>
        {/each}
      </ul>
    </li>
  {/each}
</ul>
