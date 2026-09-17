<script lang="ts">
  import Layout from "./components/Layout.svelte";
  import Home from "./routes/Home.svelte";
  import NotFound from "./routes/NotFound.svelte";
  import { untrack } from "svelte";
  import { setLocale, type Locale } from "./lib/i18n";

  /**
   * The whole document body, in one language.
   *
   * There is no client-side router and, since the site became a single page, no route
   * table to switch on either: the prerenderer calls this once per locale and writes
   * the result to disk. `notFound` is the one branch left, because the 404 document is
   * a real file that nginx serves and it has to come out of the same shell.
   */
  let { locale, notFound = false }: { locale: Locale; notFound?: boolean } =
    $props();

  // Published once here so that every component below can read it without the locale
  // being threaded through a dozen component signatures.
  //
  // `untrack` is not a workaround: setContext has to run during initialisation, so
  // reading the prop's initial value is exactly what is wanted. Saying so explicitly
  // is what distinguishes it from the mistake the compiler warns about.
  setLocale(untrack(() => locale));
</script>

<Layout>
  {#if notFound}
    <NotFound />
  {:else}
    <Home />
  {/if}
</Layout>
