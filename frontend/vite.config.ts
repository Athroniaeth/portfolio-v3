import { defineConfig, type Plugin, type ViteDevServer } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import litestar from "litestar-vite-plugin";
import tailwindcss from "@tailwindcss/vite";

import { documentFor, stripHydrationMarkers } from "./scripts/document.mjs";

// Dev proxy target: the Litestar API started separately (`just dev-api`).
const API_TARGET = process.env.API_URL || "http://127.0.0.1:8000";

// Read by Node here, never inlined into the bundle (that would only happen with a
// VITE_ prefix). Mirrors what nginx injects in production, so the browser holds no
// secret in either environment.
const API_KEY = process.env.API_KEY ?? "";

// Where /op/ is proxied in development. In production nginx does this instead — see
// deploy/default.conf.template. Same path either way, so the analytics call is
// same-origin in both and the client code never branches on the environment.
const OPENPANEL_TARGET =
  process.env.OPENPANEL_API_URL || "https://opapi.athroniaeth.cloud";

/**
 * Serve the prerendered page in development.
 *
 * Production writes one static document per language (frontend/scripts/prerender.mjs);
 * without this, `vite dev` would have no HTML to serve at all, since the client entry
 * is a script and there is no index.html. Rendering through the same shell and the
 * same entry-server module is what keeps the two from drifting: a mistake in the
 * document template shows up on localhost, not on the domain.
 */
function prerenderDevServer(): Plugin {
  return {
    name: "portfolio:prerender-dev",
    apply: "serve",
    configureServer(server: ViteDevServer) {
      // Returned thunk, so this runs after Vite's own middlewares have had their
      // chance: static files under public/ must not be swallowed by the catch-all.
      return () => {
        server.middlewares.use(async (request, response, next) => {
          const url = (request.url ?? "/").split("?")[0];
          if (!request.headers.accept?.includes("text/html")) return next();

          try {
            const entry = await server.ssrLoadModule("/src/entry-server.ts");
            const {
              renderRoute,
              routes,
              siteName,
              alternates,
              notFoundMeta,
              DEFAULT_LOCALE,
              SITE_URL,
              OG_IMAGE,
            } = entry;

            // Accept /en as well as /en/, so a typed URL behaves the way it will once
            // nginx is doing the redirecting.
            const path = url.endsWith("/") ? url : `${url}/`;
            const match = routes.find(
              (candidate: { path: string }) => candidate.path === path,
            );
            // Anything else is a 404, and gets the 404 of its own language: /en/nope
            // is an English mistake.
            const locale =
              match?.locale ??
              (path.startsWith("/en/") ? "en" : DEFAULT_LOCALE);
            const route = match ?? { locale, path, ...notFoundMeta(locale) };

            const rendered = renderRoute(locale, !match);
            let html = documentFor(
              { ...route, alternates: match ? alternates() : [] },
              {
                body: stripHydrationMarkers(rendered.body),
                head: rendered.head,
              },
              // Unhashed in dev: Vite serves the entry from source and pulls the
              // stylesheet in through its import, so there is no manifest to read.
              { script: "/src/client.ts", styles: [] },
              { SITE_URL, siteName, OG_IMAGE },
            );
            // Injects the HMR client and rewrites asset URLs.
            html = await server.transformIndexHtml(url, html);

            response.statusCode = match ? 200 : 404;
            response.setHeader("Content-Type", "text/html; charset=utf-8");
            response.end(html);
          } catch (error) {
            server.ssrFixStacktrace(error as Error);
            next(error);
          }
        });
      };
    },
  };
}

export default defineConfig({
  // nginx serves the bundle at the root, not under Litestar's asset prefix, so use
  // the standard Vite base instead of the plugin's default.
  base: "/",
  // Assets copied verbatim: the optimised fonts and images, the vendored op1.js and
  // the favicon. The plugin disables this by default, which would silently drop them.
  publicDir: "public",
  build: {
    outDir: "dist",
    // The entry is a script, not an HTML file: the documents are written afterwards by
    // scripts/prerender.mjs, which needs the manifest to learn the hashed asset names.
    manifest: true,
    rolldownOptions: { input: "src/client.ts" },
    // One stylesheet for the whole site, which is now one page in two languages, so
    // there is nothing left to split it along.
    cssCodeSplit: false,
  },
  server: {
    host: "0.0.0.0",
    port: Number(process.env.VITE_PORT || "5173"),
    // Same single origin as production, where nginx plays this role: client code
    // never knows the API's URL, it calls /api relatively.
    proxy: {
      "/api": {
        target: API_TARGET,
        changeOrigin: true,
        headers: { "X-API-Key": API_KEY },
      },
      "/schema": { target: API_TARGET, changeOrigin: true },
      // The trailing slash matters: Vite matches proxy keys by prefix, so a bare
      // "/op" also swallows /op1.js and any other path that merely starts with those
      // three characters.
      "/op/": {
        target: OPENPANEL_TARGET,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/op/, ""),
      },
    },
  },
  plugins: [
    tailwindcss(),
    svelte(),
    prerenderDevServer(),
    // Kept for type generation only; it no longer serves the frontend.
    litestar({
      input: ["src/client.ts", "src/app.css"],
      types: "auto",
    }),
  ],
});
