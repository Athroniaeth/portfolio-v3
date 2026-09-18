<script lang="ts">
  import { content } from "../lib/content";
  import { messages, t, useLocale } from "../lib/i18n";
  import Icon from "./Icon.svelte";
  import Picture from "./Picture.svelte";

  /** Kept for the day there are more projects than the section should show. */
  let { limit }: { limit?: number } = $props();

  const locale = useLocale();
  const projects = $derived(
    limit === undefined ? content.projects : content.projects.slice(0, limit),
  );
</script>

<div class="grid gap-4 sm:grid-cols-2 md:gap-6 lg:grid-cols-3">
  {#each projects as project (project.title)}
    <article
      class="group bg-card text-card-foreground reveal relative isolate h-60 min-w-60 overflow-hidden rounded-2xl border focus-within:ring"
    >
      <div class="flex flex-col gap-1 px-6 py-5">
        <h3
          class="overflow-hidden font-medium tracking-tight text-ellipsis whitespace-nowrap"
        >
          <a
            href={project.link}
            target="_blank"
            rel="noopener noreferrer"
            class="flex max-w-max items-center pr-2.5 after:absolute after:inset-0 after:z-10 after:content-[''] focus-visible:outline-none"
          >
            <!-- `after:absolute inset-0` stretches the link over the whole card, so
                 the hit area is the card and not the title alone. It used to be an
                 empty <span>, which is a node per card for something that draws
                 nothing. -->
            {project.title}
            <Icon
              name="arrowUpRight"
              class="size-4 origin-center -translate-x-0.5 opacity-0 transition-all duration-100 ease-out group-hover:translate-x-1 group-hover:opacity-100"
            />
          </a>
        </h3>

        <p
          class="text-muted-foreground line-clamp-2 text-sm/normal text-pretty"
        >
          {t(project.description, locale)}
        </p>

        <!-- The stack was already in the data and rendered nowhere. It is the first
             thing a prospect scans for, so it goes above the fold of the card. -->
        <ul class="mt-1.5 flex flex-wrap gap-1.5">
          {#each project.stack as item (item)}
            <li
              class="bg-muted text-muted-foreground rounded-full px-2 py-0.5 text-[0.6875rem] leading-4 font-medium"
            >
              {item}
            </li>
          {/each}
        </ul>

        <!-- Rendered only when the card's headline already points somewhere else, so
             the repository stays reachable without duplicating the same link twice. -->
        {#if project.repository && project.repository !== project.link}
          <a
            href={project.repository}
            target="_blank"
            rel="noopener noreferrer"
            class="text-primary relative z-20 mt-1.5 inline-flex max-w-max items-center gap-1 text-xs font-medium hover:underline"
          >
            {t(messages.code, locale)}
            <Icon name="arrowUpRight" class="size-3" />
          </a>
        {/if}

        {#if project.article}
          <!-- z-20 to sit above the card-wide link overlay, so this stays clickable
               on its own. -->
          <a
            href={t(project.article, locale)}
            target="_blank"
            rel="noopener noreferrer"
            class="text-primary relative z-20 mt-1.5 inline-flex max-w-max items-center gap-1 text-xs font-medium hover:underline"
          >
            {t(messages.readArticle, locale)}
            <Icon name="arrowUpRight" class="size-3" />
          </a>
        {/if}
      </div>

      <Picture
        src="projects/{project.image}"
        target="cards"
        alt={project.title}
        class="absolute top-44 -right-10 w-75 -rotate-6 rounded-2xl border object-cover transition-transform duration-100 ease-out group-hover:translate-x-0.5 group-hover:-translate-y-1 group-hover:-rotate-3"
      />
    </article>
  {/each}
</div>
