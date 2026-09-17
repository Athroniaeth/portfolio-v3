import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

/**
 * The build whose output never reaches a browser.
 *
 * Vite compiles the Svelte components for the server here, so scripts/prerender.mjs
 * can import them and turn each route into HTML. It is a separate config rather than
 * an environment in vite.config.ts because the two builds share nothing useful: this
 * one wants no Tailwind (the client build emits the stylesheet), no manifest, no
 * public directory, and no dev server middleware.
 *
 * `.ssr/` sits outside dist/ on purpose — nginx serves dist/, and this bundle has no
 * business being downloadable.
 */
export default defineConfig({
  // Nothing here is served, so copying public/ into the output would duplicate the
  // fonts, images and vendored script for no reader.
  publicDir: false,
  build: {
    ssr: true,
    outDir: ".ssr",
    emptyOutDir: true,
    // Readable stack traces when a component throws during prerender, for a bundle
    // that is never shipped.
    minify: false,
    rolldownOptions: {
      input: "src/entry-server.ts",
      output: { entryFileNames: "entry.js" },
    },
  },
  plugins: [svelte()],
});
