<script lang="ts">
  import { content } from "../lib/content";
  import { t, useLocale } from "../lib/i18n";
  import HeroSection from "../components/HeroSection.svelte";
  import Section from "../components/Section.svelte";
  import ProjectsList from "../components/ProjectsList.svelte";
  import SkillsList from "../components/SkillsList.svelte";
  import TimelineList from "../components/TimelineList.svelte";
  import TestimonialCard from "../components/TestimonialCard.svelte";
  import ContactList from "../components/ContactList.svelte";

  /**
   * The whole site, in one document.
   *
   * It used to be four pages sharing a header, a footer and a stylesheet, which the
   * browser re-parsed on every click. One document is both the simpler thing to read
   * and the cheaper one to serve: a visit is now a single request for everything, and
   * the header links scroll instead of navigating.
   *
   * Order is deliberate. Who, then the work, then what it is built with, then how it
   * got here, then what other people made of it, and the way to get in touch last —
   * which is the order a reader who does not already know the name goes looking.
   */
  const locale = useLocale();
</script>

<HeroSection />

<hr />
<Section id="about">
  <p
    class="text-muted-foreground max-w-4xl text-justify leading-7 hyphens-auto"
  >
    {t(content.profile.about, locale)}
  </p>
</Section>

<hr />
<Section id="projects">
  <ProjectsList />
</Section>

<hr />
<Section id="skills">
  <SkillsList />
</Section>

<hr />
<Section id="timeline">
  <TimelineList />
</Section>

{#if content.testimonials.length > 0}
  <hr />
  <Section id="testimonial">
    <div class="grid gap-6 lg:grid-cols-2">
      {#each content.testimonials as testimonial (testimonial.author)}
        <TestimonialCard {testimonial} />
      {/each}
    </div>
  </Section>
{/if}

<hr />
<Section id="contact">
  <ContactList />
</Section>
