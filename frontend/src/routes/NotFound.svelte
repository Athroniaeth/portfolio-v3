<script lang="ts">
  import { messages, t, useLocale } from "../lib/i18n";
  import PageIntro from "../components/PageIntro.svelte";

  const locale = useLocale();
</script>

<section class="py-10 md:py-20">
  <div class="container space-y-10">
    <PageIntro
      title={t(messages.notFoundTitle, locale)}
      description={t(messages.notFoundBody, locale)}
    />
  </div>
</section>
