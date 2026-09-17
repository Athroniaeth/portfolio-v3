<script lang="ts">
  import { content } from "../lib/content";
  import { t, useLocale } from "../lib/i18n";
  import SocialLinks from "./SocialLinks.svelte";

  /**
   * The headline's measure is chosen, not rounded off.
   *
   * `26ch` broke it after "Engineer," and left "passionné de tech." alone on the
   * second line. Measured against the woff2 this site actually serves, at weight 500
   * and with the -0.025em of `tracking-tight`, the window that puts "Engineer," at the
   * head of the second line is 21ch to 23ch. 21 is the low edge on purpose: real
   * kerning is slightly tighter than the sum of the advance widths, which makes the
   * text narrower than computed and pushes the break the wrong way, so the error is
   * spent on the safe side.
   *
   * Below about 980px the container is narrower than this and decides the break
   * instead, which is as it should be.
   */

  /**
   * The summary is justified, and hyphenated because of it.
   *
   * Justification without hyphenation is what produces the rivers of white space that
   * give the setting a bad name, and `hyphens: auto` needs the language to know where
   * a word may break — which it has, since <html lang> is set per document. A wider
   * measure helps it too: the fewer words a line has to stretch, the further apart it
   * has to push them.
   */
  const locale = useLocale();
</script>

<section class="from-background to-muted/40 bg-gradient-to-br py-20 md:py-32">
  <div class="container">
    <h1
      class="max-w-[21ch] text-4xl leading-tight font-medium tracking-tight sm:text-5xl md:text-6xl"
    >
      {t(content.profile.headline, locale)}
    </h1>
    <p
      class="text-muted-foreground mt-6 max-w-[72ch] text-justify leading-7 hyphens-auto"
    >
      {t(content.profile.summary, locale)}
    </p>
    <SocialLinks class="mt-8" />
  </div>
</section>
