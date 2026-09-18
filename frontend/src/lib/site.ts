import { content } from "./content";
import { t, DEFAULT_LOCALE, LOCALES, messages, type Locale } from "./i18n";
import { SITE_URL } from "./site-url";

/**
 * One document per language, and the sections inside it.
 *
 * The site used to be four pages. It is now a single page per locale: the header
 * links to `#about`, `#projects` and the rest, the browser scrolls there, and a
 * visitor downloads the whole portfolio once instead of re-fetching a shared header
 * and stylesheet on every click. There is correspondingly less to describe here —
 * two paths, two files, and the list of anchors the nav walks.
 *
 * The anchors are *not* translated. `#about` is the fragment in both languages so
 * that the language switch can carry the reader's position across: landing on
 * `/en/#projects` from `/#projects` only works while the two share a name.
 */

export { SITE_URL };

/** Used by <title> and the Open Graph card. */
export const siteName: Record<Locale, string> = {
  fr: `${content.profile.name} - ${content.profile.role.fr}`,
  en: `${content.profile.name} - ${content.profile.role.en}`,
};

export const OG_IMAGE = "/images/opengraph.jpg";

/**
 * A section of the page, which is also its anchor and a key into `content.sections`.
 *
 * This used to claim that adding a section in backend/content.py was a compile error
 * here until it was placed. It was not: `keyof` resolves against the hand-written
 * `Sections` interface in lib/content.ts, not against the JSON, so a section could be
 * added, exported, pass every test, and render nowhere. TypeScript cannot see the
 * difference, so the check moved to where it can be made — the prerenderer asserts
 * that every id below is an anchor in the finished document. See scripts/prerender.mjs.
 */
export type SectionId = keyof typeof content.sections;

/**
 * Every section the content declares, in the order Home.svelte renders them.
 *
 * Read from the exported JSON rather than written out, so the build has something to
 * check the document against.
 */
export const SECTION_IDS = Object.keys(content.sections) as SectionId[];

/**
 * What the header links to, in order.
 *
 * Testimonials are deliberately absent. They sit between the timeline and the
 * contact block, and a nav entry for them would promise a section a visitor is
 * already scrolling past.
 */
const NAV_SECTIONS: SectionId[] = [
  "about",
  "projects",
  "skills",
  "timeline",
  "contact",
];

export interface RouteDefinition {
  locale: Locale;
  /** URL path, always with a trailing slash. */
  path: string;
  /** File written under dist/ — `/en/` becomes `en/index.html`. */
  file: string;
  title: string;
  description: string;
}

/**
 * The prefix a locale lives under: nothing for the default, `/en` for the rest.
 *
 * Serving the default language at the root rather than at `/fr/` keeps the existing
 * URLs working and avoids a redirect on the only page of the site.
 */
export function localePrefix(locale: Locale): string {
  return locale === DEFAULT_LOCALE ? "" : `/${locale}`;
}

/** URL of the page in one language. */
export function pathFor(locale: Locale): string {
  return `${localePrefix(locale)}/`;
}

function routeFor(locale: Locale): RouteDefinition {
  const path = pathFor(locale);
  return {
    locale,
    path,
    // `/` is `index.html`; `/en/` is `en/index.html`.
    file: `${path.slice(1)}index.html`,
    title: siteName[locale],
    description: t(content.profile.summary, locale),
  };
}

/** Every document to prerender: one per locale. */
export const routes: RouteDefinition[] = LOCALES.map(routeFor);

/**
 * The header navigation for one locale.
 *
 * The label is the section's own heading, so the nav and the section it scrolls to
 * cannot end up calling the same thing by two names.
 */
export function navigation(
  locale: Locale,
): { id: SectionId; href: string; label: string }[] {
  return NAV_SECTIONS.map((id) => ({
    id,
    // Bare `#about` rather than `/#about`, so the browser scrolls instead of
    // re-requesting the document it is already showing.
    href: `#${id}`,
    label: t(content.sections[id].heading, locale),
  }));
}

/** Canonical URL plus every alternate, for the <link rel="alternate"> set. */
export function alternates(): { locale: Locale; href: string }[] {
  return LOCALES.map((locale) => ({
    locale,
    href: `${SITE_URL}${pathFor(locale)}`,
  }));
}

/** Title and description of the 404 document, which is not a section of the page. */
export function notFoundMeta(locale: Locale): {
  title: string;
  description: string;
} {
  return {
    title: `${messages.notFoundTitle[locale]} - ${siteName[locale]}`,
    description: messages.notFoundBody[locale],
  };
}
