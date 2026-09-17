import { getContext, setContext } from "svelte";

/**
 * Two languages, one build.
 *
 * Every page is rendered twice at build time — French at the root, English under
 * /en/ — so there is no runtime translation, no locale detection and no dictionary
 * shipped to the browser. A visitor downloads the language they asked for and nothing
 * of the other one.
 *
 * Because the pages are prerendered and never hydrated, the locale can travel through
 * Svelte's context rather than being threaded as a prop through every component: the
 * context is resolved once, during the render that produces the HTML.
 */

export const LOCALES = ["fr", "en"] as const;

export type Locale = (typeof LOCALES)[number];

/**
 * French is the default: it is what the site serves at the root, what `<html lang>`
 * says there, and what `hreflang="x-default"` points at. The audience is French, and
 * so is the freelance market this site exists to reach.
 */
export const DEFAULT_LOCALE: Locale = "fr";

/** A string in both languages, mirroring `Text` in backend/content.py. */
export interface Text {
  fr: string;
  en: string;
}

/** A span of time. `end: null` means it is still running. */
export interface Period {
  start: string;
  end: string | null;
}

const LOCALE_KEY = Symbol("locale");

/** Called once, by the root page component. */
export function setLocale(locale: Locale): void {
  setContext(LOCALE_KEY, locale);
}

/**
 * The locale of the page being rendered.
 *
 * Falls back to the default rather than throwing: a component rendered outside a page
 * should produce French text, not an exception during the build.
 */
export function useLocale(): Locale {
  return getContext<Locale | undefined>(LOCALE_KEY) ?? DEFAULT_LOCALE;
}

/** Pick one side of a `Text`. */
export function t(text: Text, locale: Locale): string {
  return text[locale];
}

/**
 * Interface strings — the chrome, not the content.
 *
 * Anything a visitor would call "the site's text" lives in backend/content.py, which
 * is the file to edit. What is left here is the vocabulary of the interface itself:
 * labels for assistive technology, and the words that glue rendered values together.
 */
export const messages = {
  skipToContent: { fr: "Aller au contenu", en: "Skip to content" },
  homepage: { fr: "Aller à l'accueil", en: "Go to homepage" },
  toggleTheme: { fr: "Changer de thème", en: "Toggle theme" },
  openMenu: { fr: "Ouvrir le menu", en: "Open menu" },
  closeMenu: { fr: "Fermer le menu", en: "Close menu" },
  menu: { fr: "Menu", en: "Menu" },
  language: { fr: "Langue", en: "Language" },
  languages: { fr: "Langues", en: "Languages" },
  readArticle: { fr: "Lire l'article", en: "Read the article" },
  present: { fr: "aujourd'hui", en: "present" },
  verify: { fr: "Vérifier", en: "Verify" },
  code: { fr: "Code", en: "Code" },
  // Connector for a date range. A dash would be the typographic convention, but the
  // copy of this site deliberately avoids dashes as separators.
  rangeConnector: { fr: "à", en: "to" },
  notFoundTitle: { fr: "Page introuvable", en: "Page not found" },
  notFoundBody: {
    fr: "Cette adresse ne correspond à rien sur ce site. Les quatre pages de l'en-tête en font le tour.",
    en: "That URL does not match anything on this site. The four pages in the header are the whole of it.",
  },
} as const satisfies Record<string, Text>;

/**
 * What each kind of timeline entry is called, and which icon draws it.
 *
 * Without this, a chess title and a master's degree render as the same tick in the
 * same list, and the reader has no way to tell a distinction from a qualification.
 */
export const achievementKinds = {
  experience: {
    icon: "briefcase",
    label: { fr: "Expérience", en: "Experience" },
  },
  education: {
    icon: "graduationCap",
    label: { fr: "Formation", en: "Education" },
  },
  certification: {
    icon: "badgeCheck",
    label: { fr: "Certification", en: "Certification" },
  },
  distinction: {
    icon: "award",
    label: { fr: "Distinction", en: "Award" },
  },
} as const;

export type AchievementKind = keyof typeof achievementKinds;

/**
 * The two kinds of thing someone else can say about you.
 *
 * A review is left at the end of a paid engagement and carries a rating; a
 * recommendation comes from someone who worked alongside, outside any mission. Calling
 * both "avis client" would overstate the second one.
 */
export const testimonialKinds = {
  review: { fr: "Avis de fin de mission", en: "End-of-engagement review" },
  recommendation: { fr: "Recommandation", en: "Recommendation" },
} as const;

export type TestimonialKind = keyof typeof testimonialKinds;

/**
 * The label on one entry of the language menu, in the language it leads to.
 *
 * The control itself shows the language the site is *currently* in, the way a
 * documentation site does, and opens a list to change it. Naming a toggle after its
 * current state is normally the classic ambiguity, but it stops being one as soon as
 * the control is a menu rather than a switch: the entries say where they go, and
 * there is room for a third language without renaming anything.
 */
export const switchLanguageLabel: Record<Locale, string> = {
  fr: "Afficher le site en français",
  en: "Switch to English",
};

/** Human name of each locale, in its own language. */
export const localeName: Record<Locale, string> = {
  fr: "Français",
  en: "English",
};

/**
 * Whole months between two dates, counting the start month.
 *
 * Day-of-month is ignored on purpose: content.py stores the 1st of the month because
 * that is the precision a CV actually has.
 */
function monthsBetween(from: Date, to: Date): number {
  return (
    (to.getFullYear() - from.getFullYear()) * 12 +
    (to.getMonth() - from.getMonth())
  );
}

const DURATION_UNITS: Record<
  Locale,
  { year: [string, string]; month: [string, string] }
> = {
  fr: { year: ["an", "ans"], month: ["mois", "mois"] },
  en: { year: ["year", "years"], month: ["month", "months"] },
};

/**
 * Render a period's length, e.g. "1 an 8 mois" or "1 year 8 months".
 *
 * This is why `Period` holds dates instead of a written-out duration: the previous
 * site said "1 year, 2 month" about a job that had been running for twenty months,
 * because the figure had been typed once and never revisited. Computed here, it is
 * correct as of the last deploy.
 *
 * @param period Start and optional end.
 * @param locale Language to render the units in.
 * @param now Reference point for an open period; injected so the build is testable.
 */
export function formatDuration(
  period: Period,
  locale: Locale,
  now = new Date(),
): string {
  const start = new Date(period.start);
  const end = period.end ? new Date(period.end) : now;
  const total = Math.max(monthsBetween(start, end), 0) + 1;
  const years = Math.floor(total / 12);
  const months = total % 12;
  const units = DURATION_UNITS[locale];

  const parts: string[] = [];
  if (years > 0) parts.push(`${years} ${units.year[years > 1 ? 1 : 0]}`);
  if (months > 0) parts.push(`${months} ${units.month[months > 1 ? 1 : 0]}`);
  // A period that rounds to nothing still has to say something.
  if (parts.length === 0) parts.push(`1 ${units.month[0]}`);
  return parts.join(" ");
}

/**
 * Render a period as a range, e.g. "janv. 2025 à aujourd'hui".
 *
 * @param period Start and optional end.
 * @param locale Language to format the month names in.
 */
export function formatRange(period: Period, locale: Locale): string {
  const format = new Intl.DateTimeFormat(locale, {
    month: "short",
    year: "numeric",
  });
  const start = format.format(new Date(period.start));
  const end = period.end
    ? format.format(new Date(period.end))
    : messages.present[locale];
  return `${start} ${messages.rangeConnector[locale]} ${end}`;
}

/** Render a date on its own, e.g. "21 nov. 2024". */
export function formatDate(value: string, locale: Locale): string {
  return new Intl.DateTimeFormat(locale, {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}
