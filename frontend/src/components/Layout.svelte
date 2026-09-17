<script lang="ts">
  import type { Snippet } from "svelte";
  import { messages, t, useLocale } from "../lib/i18n";
  import Header from "./Header.svelte";
  import Footer from "./Footer.svelte";

  let { children }: { children: Snippet } = $props();

  const locale = useLocale();
</script>

<a
  href="#main"
  class="bg-background focus:ring-ring sr-only focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-60 focus:rounded-md focus:px-4 focus:py-2 focus:ring-2"
>
  {t(messages.skipToContent, locale)}
</a>

<Header />
<main id="main">
  {@render children()}
</main>
<Footer />
