<script lang="ts">
  import { content } from "../lib/content";
  import { messages, t, useLocale } from "../lib/i18n";
  import { navigation, pathFor } from "../lib/site";
  import Icon from "./Icon.svelte";
  import LanguageSwitch from "./LanguageSwitch.svelte";
  import Picture from "./Picture.svelte";

  const locale = useLocale();
  const links = navigation(locale);

  /**
   * No active-link marking, and no `aria-current`.
   *
   * There is one page, so there is no current page to mark, and the only thing a
   * fragment tells us is where the visitor last *clicked* — not where they have
   * scrolled to since. Highlighting "Projets" while someone reads the contact block
   * would be worse than highlighting nothing.
   *
   * The nav hides below `md`: five French labels plus the language menu do not fit a
   * 640px header, and a nav that wraps onto a second line is worse than the menu
   * button that replaces it. At `md` itself it fits with about thirty pixels to
   * spare, which is what the tighter gap between the links buys.
   */
</script>

<header
  class="bg-background/95 supports-[backdrop-filter]:bg-background/80 sticky top-0 z-50 w-full border-b backdrop-blur"
>
  <div class="container flex h-16 items-center justify-between gap-4">
    <a
      href={pathFor(locale)}
      aria-label={t(messages.homepage, locale)}
      class="shrink-0"
    >
      <Picture
        src="avatar"
        target="avatar"
        alt={content.profile.name}
        eager
        class="size-9 rounded-full"
      />
    </a>

    <div class="flex items-center gap-3 md:gap-6">
      <nav class="hidden items-center gap-5 md:flex lg:gap-6">
        {#each links as link (link.id)}
          <a
            href={link.href}
            class="text-muted-foreground hover:text-primary text-sm font-medium transition-colors"
          >
            {link.label}
          </a>
        {/each}
      </nav>

      <LanguageSwitch {locale} />

      <!--
        Hidden until the inline head script adds `js` to <html>. The control does
        nothing without JavaScript, and showing a dead button is worse than showing
        none; the script runs before first paint, so this costs no layout shift.
      -->
      <button
        type="button"
        id="theme-toggle"
        class="hover:bg-accent hover:text-accent-foreground hidden size-9 items-center justify-center rounded-md [.js_&]:inline-flex"
        aria-label={t(messages.toggleTheme, locale)}
      >
        <Icon name="moon" class="size-4 dark:hidden" />
        <Icon name="sun" class="hidden size-4 dark:block" />
      </button>

      <!--
        A native popover: the browser supplies the top layer, light dismiss, Escape
        and focus handling that the Radix dialog on the old site shipped ~14 KB of
        JavaScript to reproduce. What it no longer gets for free is closing: the
        links used to be navigations, which replaced the document, and are now
        scrolls, which leave the panel sitting over the section it scrolled to. That
        is the three lines in client.ts.
      -->
      <button
        type="button"
        popovertarget="site-menu"
        class="md:hidden"
        aria-label={t(messages.openMenu, locale)}
      >
        <Icon name="menu" class="size-5" />
      </button>

      <div id="site-menu" popover="auto">
        <div class="flex h-16 items-center justify-end px-5">
          <button
            type="button"
            popovertarget="site-menu"
            popovertargetaction="hide"
            aria-label={t(messages.closeMenu, locale)}
          >
            <Icon name="close" class="size-5" />
          </button>
        </div>
        <nav class="px-6 py-14" aria-label={t(messages.menu, locale)}>
          <ul class="grid gap-3">
            {#each links as link (link.id)}
              <li>
                <a href={link.href} class="text-muted-foreground text-xl">
                  {link.label}
                </a>
              </li>
            {/each}
          </ul>
        </nav>
      </div>
    </div>
  </div>
</header>
