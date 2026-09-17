/**
 * Types for the shared page shell.
 *
 * document.mjs stays plain JavaScript because scripts/prerender.mjs is run by `node`
 * directly, with no transpile step in front of it. vite.config.ts is type-checked
 * though, and it imports the same module, so the contract is declared here rather than
 * letting it slip in as `any`.
 */

export interface RenderedPage {
  body: string;
  head: string;
}

export interface LocaleAlternate {
  locale: string;
  href: string;
}

export interface PageRoute {
  path: string;
  title: string;
  description: string;
  /** Goes into <html lang> and og:locale, so the shell needs it too. */
  locale: string;
  alternates?: LocaleAlternate[];
  /** hreflang="x-default", omitted on the 404 documents. */
  defaultHref?: string;
}

export interface PageAssets {
  /** URL of the client entry script. */
  script: string;
  /** URLs of the stylesheets to link, in order. */
  styles: string[];
}

export interface SiteMetadata {
  SITE_URL: string;
  /** Site name per locale, since the two languages title the page differently. */
  siteName: Record<string, string>;
  OG_IMAGE: string;
}

/** The inline <head> script, verbatim; its sha256 is what the CSP allow-lists. */
export const THEME_SCRIPT: string;

/** Remove the hydration markers svelte/server emits. */
export function stripHydrationMarkers(html: string): string;

/** Escape a string for use inside an HTML attribute value. */
export function escapeAttribute(value: string): string;

/** Assemble a complete HTML document for one route. */
export function documentFor(
  route: PageRoute,
  rendered: RenderedPage,
  assets: PageAssets,
  site: SiteMetadata,
): string;
