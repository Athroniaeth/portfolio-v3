<script lang="ts">
  import { useLocale } from "../lib/i18n";
  import { contactMethods } from "../lib/contact";
  import Icon from "./Icon.svelte";

  /**
   * The contact block: one button per channel, each with its mark.
   *
   * This is the last section of the page and the only place it asks for anything, so
   * it is the one place that should look unmistakably clickable. The marks let the eye
   * pick a channel without reading the labels.
   *
   * The icon takes its colour from `currentColor` rather than a `fill-*` utility, so
   * the same markup works for the brand marks, which are filled, and the envelope,
   * which is stroked.
   */
  const locale = useLocale();
  const methods = contactMethods(locale);
</script>

<ul class="reveal flex flex-wrap gap-3">
  {#each methods as method (method.value)}
    <li>
      <a
        href={method.href}
        rel={method.external ? "noopener noreferrer" : undefined}
        target={method.external ? "_blank" : undefined}
        class="group bg-muted/40 hover:border-foreground/30 focus-visible:ring-ring inline-grid grid-cols-[auto_1fr] items-center gap-x-3 rounded-2xl border px-5 py-3 transition-colors focus-visible:ring-2 focus-visible:outline-none"
      >
        <!-- A grid rather than nested flex boxes: the mark spans both rows, so the
             label and the address need no wrapper element to be stacked. -->
        <Icon
          name={method.icon}
          class="text-muted-foreground group-hover:text-foreground row-span-2 size-5 shrink-0 transition-colors"
        />
        <span
          class="text-muted-foreground text-[0.625rem] tracking-wide uppercase"
        >
          {method.label}
        </span>
        <span class="text-sm font-medium break-all">{method.value}</span>
      </a>
    </li>
  {/each}
</ul>
