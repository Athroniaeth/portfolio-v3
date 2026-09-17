<script lang="ts">
  import {
    LOCALES,
    localeName,
    messages,
    switchLanguageLabel,
    t,
    type Locale,
  } from "../lib/i18n";
  import { pathFor } from "../lib/site";
  import Flag from "./Flag.svelte";
  import Icon from "./Icon.svelte";

  /**
   * The language menu: shows the language the site is in, opens the list to change it.
   *
   * A `<details>`, not a button and a script. The disclosure, the open state and the
   * keyboard handling are the browser's, so the control costs nothing in a bundle that
   * is about a kilobyte in total. A menu rather than a straight toggle because a third
   * language should be a line in backend/content.py and nothing else.
   *
   * Links inside it, not buttons: each language is a real URL with its own prerendered
   * document, so it has to be crawlable, openable in a new tab and usable with
   * JavaScript off. `data-lang-link` is how client.ts finds them to append the section
   * currently in the address bar, which is the one thing here that does need a script.
   */
  let { locale }: { locale: Locale } = $props();
</script>

<details class="relative">
  <summary
    class="text-muted-foreground hover:text-foreground hover:border-foreground/30 focus-visible:ring-ring inline-flex cursor-pointer list-none items-center gap-1.5 rounded-md border px-2 py-1 text-xs font-medium transition-colors focus-visible:ring-2 focus-visible:outline-none [&::-webkit-details-marker]:hidden"
  >
    <span class="sr-only">{t(messages.language, locale)}</span>
    <Flag {locale} class="h-3 w-4.5 rounded-xs" />
    <span>{localeName[locale]}</span>
    <Icon name="chevronDown" class="size-3" />
  </summary>

  <ul
    class="bg-background absolute right-0 z-10 mt-2 min-w-40 rounded-md border p-1 shadow-md"
  >
    {#each LOCALES as option (option)}
      <li>
        <a
          href={pathFor(option)}
          hreflang={option}
          lang={option}
          data-lang-link
          aria-label={switchLanguageLabel[option]}
          aria-current={option === locale ? "true" : undefined}
          class="hover:bg-accent hover:text-accent-foreground flex items-center gap-2 rounded-sm px-2 py-1.5 text-xs font-medium {option ===
          locale
            ? 'text-foreground'
            : 'text-muted-foreground'}"
        >
          <Flag locale={option} class="h-3 w-4.5 shrink-0 rounded-xs" />
          <span>{localeName[option]}</span>
          {#if option === locale}
            <Icon name="check" class="ml-auto size-3.5" />
          {/if}
        </a>
      </li>
    {/each}
  </ul>
</details>
