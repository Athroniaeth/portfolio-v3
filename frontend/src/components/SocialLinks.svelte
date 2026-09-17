<script lang="ts">
  import { content } from "../lib/content";
  import { useLocale, type Locale } from "../lib/i18n";
  import Icon from "./Icon.svelte";
  import type { IconName } from "../lib/icons";

  let { class: className = "" }: { class?: string } = $props();

  const locale: Locale = useLocale();
  const label = (platform: string) =>
    locale === "fr" ? `Mon profil ${platform}` : `My ${platform} profile`;
</script>

<ul class="flex items-center gap-8 {className}">
  {#each content.socials as social (social.platform)}
    <li>
      <a
        href={social.href}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={label(social.platform)}
        class="focus-visible:ring-ring inline-flex rounded-sm focus-visible:ring-2 focus-visible:outline-none"
      >
        <Icon
          name={social.icon as IconName}
          class="fill-muted-foreground hover:fill-primary size-5 md:size-6"
        />
      </a>
    </li>
  {/each}
</ul>
