import { content } from "./content";
import { messages, t, type Locale } from "./i18n";

/**
 * The skills section's data, flattened into one shape.
 *
 * `content.skills` and `content.languages` are separate structs in backend/content.py,
 * because a language carries a level and a tool does not, but on the screen they are
 * the same thing: a named group of short labels. Flattening here means the markup has
 * one list to walk instead of a special case at the end.
 */
export interface SkillGroupView {
  name: string;
  items: string[];
}

export function skillGroups(locale: Locale): SkillGroupView[] {
  return [
    ...content.skills.map((group) => ({
      name: t(group.name, locale),
      items: group.items.map((item) => t(item, locale)),
    })),
    {
      name: t(messages.languages, locale),
      items: content.languages.map((language) =>
        language.level
          ? `${t(language.name, locale)}, ${t(language.level, locale)}`
          : t(language.name, locale),
      ),
    },
  ];
}
