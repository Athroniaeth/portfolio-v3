import { content } from "./content";
import { t, type Locale } from "./i18n";
import type { IconName } from "./icons";

/**
 * The contact methods, resolved for display.
 *
 * `ContactMethod` in backend/content.py carries no icon, because a contact method is
 * an address and not a brand. The icon is looked up here instead, by matching the href
 * against `content.socials`, which does carry one — LinkedIn and Malt appear in both
 * lists at the same URL, so the two cannot disagree. Anything with a `mailto:` scheme
 * is an envelope.
 */
export interface ContactView {
  label: string;
  value: string;
  href: string;
  icon: IconName;
  /** True for the mailto: entry, which some layouts promote over the others. */
  primary: boolean;
  /** Off-site links open in a new tab; mailto: hands over to the mail client. */
  external: boolean;
}

export function contactMethods(locale: Locale): ContactView[] {
  return content.contact.map((method) => {
    const social = content.socials.find((item) => item.href === method.href);
    return {
      label: t(method.label, locale),
      value: method.value,
      href: method.href,
      icon: (method.href.startsWith("mailto:")
        ? "mail"
        : (social?.icon ?? "arrowUpRight")) as IconName,
      primary: method.href.startsWith("mailto:"),
      external: method.href.startsWith("http"),
    };
  });
}
