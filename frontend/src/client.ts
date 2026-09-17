/**
 * The only JavaScript this site ships.
 *
 * Every page is prerendered to real HTML, so there is nothing to hydrate: no
 * framework runtime, no router, no client-side data fetching. What is left is the two
 * things HTML genuinely cannot do on its own — remembering a theme choice, and
 * counting a visit — plus one line so the language switch does not lose your place.
 * The mobile menu is not here because `popover` handles it natively, and the smooth
 * scroll to a section is `scroll-behavior` in the stylesheet.
 *
 * This file also owns the stylesheet import, which is what tells Tailwind to emit one.
 */

import "./app.css";
import { SITE_HOST } from "./lib/site-url";

const root = document.documentElement;

/**
 * Persist the theme the visitor picked.
 *
 * The class is already correct when this runs: the inline script in the prerendered
 * <head> (see scripts/prerender.mjs) applied it before first paint, which is what
 * avoids the flash of the wrong theme. All that is left is to flip it and write the
 * choice down.
 *
 * Writing to localStorage can throw when storage is disabled or the quota is full;
 * the toggle should still work for the rest of the page view when it does.
 */
document.getElementById("theme-toggle")?.addEventListener("click", () => {
  const dark = root.classList.toggle("dark");
  try {
    localStorage.setItem("theme", dark ? "dark" : "light");
  } catch {
    /* private mode, or storage disabled — the class change already took effect */
  }
});

/**
 * Close the mobile menu when a link in it is followed.
 *
 * `popovertarget` only works on buttons, and light dismiss only fires for a click
 * *outside* the popover, so neither covers a link inside one. It did not matter while
 * the menu held navigations, which replaced the whole document; now that they are
 * anchors on the same page, the panel would stay open over the section it just
 * scrolled to.
 */
const menu = document.getElementById("site-menu");
menu?.addEventListener("click", (event) => {
  if ((event.target as Element).closest("a")) menu.hidePopover();
});

/**
 * Keep the reader's position when they change language.
 *
 * The site is one document per language, so `/#projects` and `/en/#projects` are the
 * same place in two languages — but a link to `/en/` drops the fragment, and the
 * switch would always land at the top. The anchors are deliberately the same word in
 * both languages (see lib/site.ts), so copying the current one across is enough.
 *
 * Read at click time rather than at load: the fragment changes as the visitor uses
 * the nav, and an href fixed on load would point at wherever they first arrived.
 */
for (const link of document.querySelectorAll<HTMLAnchorElement>(
  "[data-lang-link]",
)) {
  link.addEventListener("click", () => {
    link.hash = location.hash;
  });
}

/**
 * OpenPanel, self-hosted and served first-party.
 *
 * `apiUrl` is a path, not a host. The SDK concatenates it (`${baseUrl}/track`), so a
 * relative value resolves against this origin and nginx proxies it on to the instance
 * — see the /op/ block in deploy/default.conf.template. Two things follow, both of
 * them the point: the browser opens no second connection, so a few hundred bytes of
 * telemetry stop costing a DNS lookup, a TCP handshake and a TLS negotiation; and the
 * Content-Security-Policy stays `'self'` throughout, with no third-party origin
 * allow-listed for scripts or for connections.
 *
 * `op1.js` is vendored under public/vendor/ rather than loaded from openpanel.dev for
 * the same reasons, plus one more: a third party cannot change the script running on
 * this domain without a commit here. It keeps its upstream name — this is not an
 * attempt to slip past a content blocker, and a visitor who blocks analytics should
 * keep blocking it.
 */
type OpenPanelStub = ((...args: unknown[]) => void) & { q: unknown[][] };

declare global {
  interface Window {
    op?: OpenPanelStub;
  }
}

// Public by design — it identifies the site to the analytics instance, the way a
// Plausible data-domain does, and every visitor's browser can read it. The project
// secret is the one that must never appear here: it signs server-side events, lives
// in the environment, and nothing in the frontend has any use for it.
const OPENPANEL_CLIENT_ID = "8226333d-2b9b-46fb-8311-fb2aea437bda";

/**
 * The documented op1.js queue shim, unminified.
 *
 * op1.js is deferred, so anything called before it parses has to be recorded. When it
 * runs it reads `op.q`, treats the first entry's second element as the init options,
 * and replays the rest as `op[name](...args)` — which is why the Proxy has to record
 * both call styles: `op("init", opts)` and `op.track("event")`.
 */
function createStub(): OpenPanelStub {
  const queue: unknown[][] = [];
  return new Proxy(
    ((...args: unknown[]) => {
      if (args.length) queue.push(args);
    }) as OpenPanelStub,
    {
      get: (_target, property) =>
        property === "q"
          ? queue
          : (...args: unknown[]) => queue.push([property, ...args]),
      has: (_target, property) => property === "q",
    },
  );
}

// Only on the real domain. The instance validates the Origin of every event against
// the project's allowed domains, so a call from localhost or a preview build is
// answered with 401 anyway — this just means not making it, which keeps the console
// clean in development and keeps local page loads out of the production figures.
if (location.hostname === SITE_HOST) {
  window.op = window.op ?? createStub();

  window.op("init", {
    clientId: OPENPANEL_CLIENT_ID,
    apiUrl: "/op",
    // One prerendered document per language, so the load event is the page view and
    // there is no router to hook into. Scrolling to a section is not a page view and
    // is not counted as one.
    trackScreenViews: true,
    // The site's whole purpose is the three outbound profile links; not counting them
    // would leave the only conversion it has unmeasured.
    trackOutgoingLinks: true,
    // Nothing uses data-track attributes, so the listener they need is dead weight.
    trackAttributes: false,
  });
}
