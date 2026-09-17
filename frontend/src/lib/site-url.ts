/**
 * The production origin, on its own so that both the page templates and the client
 * bundle can read it.
 *
 * It lives here rather than in site.ts because site.ts imports content.json: pulling
 * that in from client.ts to read one string would put the whole content payload into
 * the browser bundle, which is exactly what prerendering exists to avoid.
 */
export const SITE_HOST = "pierrechaumont.fr";
export const SITE_URL = `https://${SITE_HOST}`;
