/**
 * The HTML shell every page is poured into.
 *
 * Shared between the production prerenderer (scripts/prerender.mjs) and the dev server
 * middleware (vite.config.ts) on purpose: a document template that exists twice is a
 * document template that drifts, and the difference would only surface in production.
 */

/**
 * Runs before first paint, so the page never flashes the wrong theme.
 *
 * It also sets `js`, which is what reveals the theme toggle: the control does nothing
 * without JavaScript and a dead button is worse than no button. Because this runs in
 * <head> before the body is parsed, revealing it costs no layout shift.
 *
 * Kept as one exact string because its sha256 goes into the Content-Security-Policy —
 * edit it and the hash changes, so `just build` rewrites deploy/csp-script-hash.conf
 * and CI's diff check catches a stale one.
 */
export const THEME_SCRIPT =
  `(()=>{var e=document.documentElement;e.classList.add("js");try{` +
  `var t=localStorage.getItem("theme");` +
  `if(t==="dark"||(t!=="light"&&matchMedia("(prefers-color-scheme:dark)").matches))` +
  `e.classList.add("dark")}catch(_){}})()`;

/**
 * Strip Svelte's hydration markers.
 *
 * `<!--[-->`, `<!--]-->`, `<!---->` and the indexed `<!--[0-->` / `<!--[-1-->` forms
 * that keyed {#each} blocks emit all exist so a client runtime can find the boundaries
 * of each block when it takes over. `<!--$s1-->` is the same idea for `$props.id()`,
 * which the flags use to keep their clip paths unique. Nothing takes over here — the
 * pages ship no framework runtime — so they are all bytes served to every visitor, on
 * every page, forever. The ids themselves are already written into the attributes that
 * reference them, so removing the marker changes nothing on the screen.
 *
 * The pattern is deliberately anchored on `[`, `]`, `$s` and the empty comment rather
 * than on "any comment": a comment someone writes in a .svelte file should survive.
 *
 * @param {string} html Markup from svelte/server.
 * @returns {string} The same markup without the markers.
 */
export function stripHydrationMarkers(html) {
  return html.replace(/<!--\[-?\d*-->|<!--\]-->|<!---->|<!--\$s\d+-->/g, "");
}

/**
 * Escape a string for use in an HTML attribute value.
 *
 * Page descriptions come from content.py and already contain apostrophes; one stray
 * quote would otherwise end the attribute and spill prose into the markup.
 *
 * @param {string} value
 * @returns {string}
 */
export function escapeAttribute(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/**
 * Assemble the full document for one route.
 *
 * @param {object} route Entry from the route table: path, title, description, locale
 *   and the alternates in the other languages.
 * @param {{body: string, head: string}} rendered Output of renderRoute.
 * @param {{script: string, styles: string[]}} assets Hashed client asset paths.
 * @param {{SITE_URL: string, siteName: Record<string,string>, OG_IMAGE: string}} site
 * @returns {string} A complete HTML document.
 */
export function documentFor(route, rendered, assets, site) {
  const canonical = `${site.SITE_URL}${route.path}`;
  const description = escapeAttribute(route.description);
  const title = escapeAttribute(route.title);
  const locale = route.locale;

  // The font is preloaded ahead of the stylesheet that references it: discovering it
  // only once the CSS has parsed would serialise two round trips that can overlap.
  // `crossorigin` is required even same-origin — fonts are always fetched in CORS
  // mode, and without it the preload is thrown away and fetched a second time.
  const styles = assets.styles
    .map((href) => `<link rel="stylesheet" href="${href}">`)
    .join("");

  // One <link rel="alternate"> per language, plus x-default pointing at French.
  // Without these a search engine treats the two versions as duplicates and picks
  // one, instead of serving each to the audience that reads it.
  const alternates = (route.alternates ?? [])
    .map(
      (alternate) =>
        `<link rel="alternate" hreflang="${alternate.locale}" href="${alternate.href}">`,
    )
    .join("\n");
  const defaultAlternate = route.defaultHref
    ? `\n<link rel="alternate" hreflang="x-default" href="${route.defaultHref}">`
    : "";

  return `<!doctype html>
<html lang="${locale}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title}</title>
<meta name="description" content="${description}">
<link rel="canonical" href="${canonical}">
${alternates}${defaultAlternate}
<link rel="icon" href="/icons/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="preload" href="/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
${styles}
<script>${THEME_SCRIPT}</script>
<meta property="og:type" content="website">
<meta property="og:locale" content="${locale === "fr" ? "fr_FR" : "en_GB"}">
<meta property="og:site_name" content="${escapeAttribute(site.siteName[locale])}">
<meta property="og:title" content="${title}">
<meta property="og:description" content="${description}">
<meta property="og:url" content="${canonical}">
<meta property="og:image" content="${site.SITE_URL}${site.OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
${rendered.head}
<script type="module" src="${assets.script}"></script>
<script src="/vendor/op1.js" defer></script>
</head>
<body>
${rendered.body}
</body>
</html>
`;
}
