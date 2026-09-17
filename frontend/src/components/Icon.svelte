<script lang="ts">
  import { icons, type IconName } from "../lib/icons";

  interface Props {
    name: IconName;
    /** Tailwind classes; size comes from the caller since the same mark is drawn at
     *  several sizes. */
    class?: string;
    /** Set when the icon carries meaning on its own. Left undefined, the mark is
     *  hidden from assistive tech, which is right whenever a visible label sits
     *  next to it. */
    label?: string;
  }

  let { name, class: className = "", label }: Props = $props();

  const spec = $derived(icons[name]);
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox={spec.viewBox}
  class={className}
  role={label ? "img" : undefined}
  aria-label={label}
  aria-hidden={label ? undefined : "true"}
  fill={spec.mode === "fill" ? "currentColor" : "none"}
  stroke={spec.mode === "stroke" ? "currentColor" : undefined}
  stroke-width={spec.mode === "stroke" ? 2 : undefined}
  stroke-linecap={spec.mode === "stroke" ? "round" : undefined}
  stroke-linejoin={spec.mode === "stroke" ? "round" : undefined}
>
  {#each spec.paths as d (d)}
    <path {d} />
  {/each}
</svg>
