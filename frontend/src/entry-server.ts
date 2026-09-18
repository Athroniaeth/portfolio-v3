/**
 * Build-time entry point: turns a locale into HTML.
 *
 * Nothing here ever reaches a browser. Vite builds this module for the `ssr`
 * environment, scripts/prerender.mjs imports the result, and the HTML it returns is
 * written to disk. The client bundle is a separate build and shares none of it.
 */

import { render } from "svelte/server";

import Page from "./Page.svelte";
import { DEFAULT_LOCALE, LOCALES, type Locale } from "./lib/i18n";
import {
  alternates,
  navigation,
  notFoundMeta,
  routes,
  siteName,
  SECTION_IDS,
} from "./lib/site";

export {
  routes,
  siteName,
  alternates,
  notFoundMeta,
  navigation,
  SECTION_IDS,
  LOCALES,
  DEFAULT_LOCALE,
};
export { SITE_URL, OG_IMAGE, localePrefix } from "./lib/site";

export interface RenderedPage {
  /** Markup for <body>. */
  body: string;
  /** Anything the components pushed into <svelte:head>. */
  head: string;
}

/**
 * Render the page in one language.
 *
 * @param locale Language to render in.
 * @param notFound Render the 404 body instead of the portfolio.
 * @returns The markup to write into the page shell.
 */
export function renderRoute(locale: Locale, notFound = false): RenderedPage {
  const { body, head } = render(Page, { props: { locale, notFound } });
  return { body, head };
}
