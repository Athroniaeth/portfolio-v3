/**
 * Every icon the site draws, as path data.
 *
 * Inlined rather than imported from lucide-react and simple-icons (the two packages
 * the Next.js site pulled in) for two reasons: an icon component library is a
 * runtime dependency for something that is ultimately a string, and these markers are
 * rendered into the HTML at build time, so nothing ships to the browser but the paths
 * below.
 *
 * `mode` picks how the sprite is drawn. Brand marks are solid shapes and fill;
 * interface icons come from lucide, which draws with a 2px round stroke on no fill.
 */
export type IconMode = "fill" | "stroke";

export interface IconSpec {
  viewBox: string;
  paths: string[];
  mode: IconMode;
  /** Set when the mark is not square, so the markup can keep its aspect ratio. */
  ratio?: number;
}

export const icons = {
  linkedin: {
    viewBox: "0 0 448 512",
    mode: "fill",
    paths: [
      "M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3zM135.4 416H69V202.2h66.5V416zm-33.2-243c-21.3 0-38.5-17.3-38.5-38.5S80.9 96 102.2 96c21.2 0 38.5 17.3 38.5 38.5 0 21.3-17.2 38.5-38.5 38.5zm282.1 243h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9V416z",
    ],
  },
  github: {
    viewBox: "0 0 496 512",
    mode: "fill",
    paths: [
      "M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3 .3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5 .3-6.2 2.3zm44.2-1.7c-2.9 .7-4.9 2.6-4.6 4.9 .3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3 .7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3 .3 2.9 2.3 3.9 1.6 1 3.6 .7 4.3-.7 .7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3 .7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3 .7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z",
    ],
  },
  // simple-icons ships the Malt wordmark and its knot in one 2 277-character path;
  // the site only ever shows the knot, which the original cropped to with a
  // viewBox of "0 9 7 7". Keeping that crop but dropping the wordmark's segments
  // renders identically for a third of the bytes, twice per page.
  malt: {
    viewBox: "0 9 7 7",
    mode: "fill",
    paths: [
      "M3.499 13.563l-.21.21.619.618c.304.304.79.598 1.244.144.339-.34.26-.695.073-.98-.06.004-1.726.008-1.726.008zm-.963-2.325.21-.21-.608-.607c-.304-.303-.765-.621-1.243-.143-.351.35-.273.692-.087.97Zm2.86.416c-.037.043-1.511 1.524-1.511 1.524h1.154c.43 0 .981-.101.981-.777 0-.496-.296-.683-.624-.747zm-3.244-.031H.981c-.43 0-.981.135-.981.778 0 .479.307.676.641.745.04-.046 1.511-1.523 1.511-1.523zm1.484 3.04-.618-.618-.608.607a2.613 2.613 0 0 1-.137.128c.07.333.266.639.745.639s.676-.307.745-.641c-.043-.037-.085-.073-.127-.115zM2.41 10.15l.608.607.618-.618a2.25 2.25 0 0 1 .128-.118c-.065-.327-.251-.623-.747-.623s-.682.297-.746.625c.046.04.092.08.14.127zm2.742.117c-.455-.454-.94-.16-1.244.144l-2.87 2.87c-.303.303-.621.765-.143 1.243.478.478.94.16 1.243-.143l2.87-2.87c.304-.304.598-.79.144-1.244Z",
    ],
  },
  sun: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: [
      "M12 2v2",
      "M12 20v2",
      "m4.93 4.93 1.41 1.41",
      "m17.66 17.66 1.41 1.41",
      "M2 12h2",
      "M20 12h2",
      "m6.34 17.66-1.41 1.41",
      "m19.07 4.93-1.41 1.41",
      "M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0z",
    ],
  },
  moon: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: [
      "M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401",
    ],
  },
  // lucide dropped `align-right` from its set; the three right-aligned rules it drew
  // are reproduced here rather than swapped for `menu`, which would have changed the
  // header's look.
  menu: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: ["M21 6H3", "M21 12H9", "M21 18H7"],
  },
  close: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: ["M18 6 6 18", "m6 6 12 12"],
  },
  mail: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: [
      // lucide draws the envelope as a <rect>; written as a path because Icon.svelte
      // only knows how to emit paths, the same way `briefcase` does.
      "M4,4 H20 A2,2 0 0 1 22,6 V18 A2,2 0 0 1 20,20 H4 A2,2 0 0 1 2,18 V6 A2,2 0 0 1 4,4 Z",
      "m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7",
    ],
  },
  chevronDown: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: ["m6 9 6 6 6-6"],
  },
  check: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: ["M20 6 9 17l-5-5"],
  },
  arrowUpRight: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: ["M7 7h10v10", "M7 17 17 7"],
  },
  star: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: [
      "M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z",
    ],
  },
  briefcase: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: [
      "M12 12h.01",
      "M16 6V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2",
      "M22 13a18.15 18.15 0 0 1-20 0",
      "M4,6 H20 A2,2 0 0 1 22,8 V18 A2,2 0 0 1 20,20 H4 A2,2 0 0 1 2,18 V8 A2,2 0 0 1 4,6 Z",
    ],
  },
  graduationCap: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: [
      "M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z",
      "M22 10v6",
      "M6 12.5V16a6 3 0 0 0 12 0v-3.5",
    ],
  },
  award: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: [
      "m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526",
      "M18 8a6 6 0 1 1-12 0 6 6 0 0 1 12 0z",
    ],
  },
  badgeCheck: {
    viewBox: "0 0 24 24",
    mode: "stroke",
    paths: [
      "M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z",
      "m16 9-5.5 5.5L8 12",
    ],
  },
} as const satisfies Record<string, IconSpec>;

export type IconName = keyof typeof icons;
