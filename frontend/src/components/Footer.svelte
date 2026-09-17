<script lang="ts">
  import { content } from "../lib/content";
  import SocialLinks from "./SocialLinks.svelte";

  const year = new Date().getFullYear();
</script>

<footer class="border-t py-8">
  <div class="container flex flex-col justify-between gap-6 sm:flex-row">
    <p class="text-muted-foreground text-pretty">
      &copy; {year}
      {content.profile.name}
    </p>
    <SocialLinks />
  </div>
</footer>
