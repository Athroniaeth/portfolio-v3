<script lang="ts">
  let { title, description }: { title: string; description: string } = $props();
</script>

<header class="max-w-2xl">
  <h1
    class="text-4xl leading-tight font-medium tracking-tight sm:text-5xl md:text-6xl md:text-balance"
  >
    {title}
  </h1>
  <p class="text-muted-foreground mt-6 leading-7 text-pretty">{description}</p>
</header>
