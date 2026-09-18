# pierrechaumont.fr

[![CI](https://github.com/Athroniaeth/template-litestar-svelte/actions/workflows/ci.yml/badge.svg)](https://github.com/Athroniaeth/template-litestar-svelte/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](.python-version)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Portfolio de Pierre Chaumont, porté depuis
[portfolio_v2](https://github.com/Athroniaeth/portfolio_v2) (Next.js 16 + React 19 +
shadcn/ui) sur le squelette Litestar + Svelte de ce dépôt. Même design, mêmes couleurs
— reconstruit en français et en anglais, pour peser 94 % de moins.

| | avant (Next.js) | après | écart |
|---|---:|---:|---:|
| poids de la page d'accueil | 1 334 Ko | **82 Ko** | −94 % |
| requêtes | 42 | **12** | −71 % |
| polices | 1 011 Ko | **25 Ko** | −98 % |
| JavaScript | 215 Ko | **4,3 Ko** | −98 % |
| First Contentful Paint | 276 ms | **128 ms** | −54 % |
| langues | 1 | **2** | |

Mesuré au même moment, dans le même navigateur, sur la même page, en faisant défiler
les deux jusqu'en bas pour déclencher le chargement différé. La page d'accueil porte
désormais *plus* de contenu qu'avant — six projets au lieu de cinq, leurs tags de
stack, un avis client — et pèse toujours seize fois moins. La méthode et le détail des
arbitrages sont dans [Éco-conception](#éco-conception).

Litestar 2.24, Svelte 5, Vite 8, Tailwind 4, nginx, pnpm, uv.

## Comment il est construit

Le site est **entièrement prégénéré**. Il n'y a pas de SPA, pas de routeur client, pas
d'hydratation : `frontend/scripts/prerender.mjs` rend chaque route en HTML au build et
écrit un fichier par page. Le navigateur reçoit du texte déjà mis en page, et les
~1 Ko de JavaScript qui restent ne servent qu'à deux choses que HTML ne sait pas faire
seul — retenir le thème choisi et compter une visite.

Le contenu vit en Python (`backend/content.py`), source de vérité unique, **dans les
deux langues**. `just content` le sérialise vers `frontend/src/data/content.json`, que
le prégénérateur incruste dans le HTML : le visiteur ne télécharge donc **aucune
donnée** en plus du balisage, et jamais le dictionnaire de la langue qu'il ne lit pas.
Les mêmes structures restent servies sur `/api/content`, ce qui les garde typées et
documentées dans `openapi.json` — même contrat versionné que le template d'origine.

En production, nginx sert les pages, proxifie `/api` vers Litestar et `/op` vers
l'instance OpenPanel : une seule origine côté navigateur, donc pas de CORS, pas d'URL
d'API dans le bundle, et aucune seconde poignée de main TLS pour la mesure d'audience.

## Structure

```
backend/               application Litestar — sert /api, rien d'autre
  __init__.py          chemins du projet
  app.py               handlers et configuration des plugins
  content.py           LE CONTENU DU SITE — textes FR/EN, projets, parcours
  export.py            sérialise content.py vers frontend/src/data/content.json
assets/                sources non optimisées, gardées pour pouvoir réencoder
  fonts/               InterVariable.woff2 d'origine (344 Ko)
  images/              captures et avatar en pleine résolution
scripts/
  optimize_fonts.py    sous-ensemble de la police (`just fonts`)
frontend/              projet Vite (racine Vite)
  src/components/      composants Svelte
  src/routes/          une page par route
  src/lib/             contenu typé, i18n, icônes inlinées, table des routes
  src/data/            content.json + images.json, générés et versionnés
  src/client.ts        le seul JavaScript envoyé au navigateur (~1 Ko)
  src/entry-server.ts  point d'entrée du rendu serveur, jamais servi
  scripts/document.mjs gabarit HTML partagé par le build et le dev server
  scripts/prerender.mjs écrit une page HTML par route
  scripts/compress.mjs  précompresse en gzip pour `gzip_static`
  scripts/optimize-images.mjs  réencode en AVIF + WebP (`just images`)
  public/              polices, images et op1.js optimisés, versionnés
  src/generated/       client TypeScript généré (non versionné)
  dist/                site de production (non versionné)
deploy/
  default.conf.template  nginx : pages + /api + /op sur une seule origine
  security-headers.conf  en-têtes de sécurité, CSP comprise
  csp-script-hash.conf   hash du script inline, généré par le prégénérateur
openapi.json           contrat d'API versionné, exporté depuis les handlers
Dockerfile.api         image de l'API (Python seul)
Dockerfile.web         image du site (build Vite + prégénération + nginx)
justfile               raccourcis des tâches courantes
```

## Installation

Il faut [uv](https://docs.astral.sh/uv/), [pnpm](https://pnpm.io/) et Node `^20.19`
ou `>=22.12`, contrainte de Vite 8. [`just`](https://github.com/casey/just) est
recommandé (`uv tool install rust-just`) mais facultatif.

```bash
cp .env.example .env
just install          # uv sync + litestar assets install
```

Sans `just`, la même chose à la main :

```bash
uv sync
uv run litestar assets install
```

Ne sautez pas la copie du `.env` : il définit `LITESTAR_APP`. Sans lui, la CLI
cherche l'application à la racine et ne la trouve pas, puisque le code est dans
`backend/`.

## Commandes

Les tâches courantes passent par `just` ; `just` seul liste les recettes.

| Commande | Effet |
|----------|-------|
| `just dev` | lance l'API (:8000) et le frontend (:5173) ensemble |
| `just dev-api` | l'API seule, en rechargement à chaud |
| `just dev-front` | le frontend seul, avec HMR |
| `just types` | exporte `openapi.json` et régénère le client TypeScript |
| `just content` | exporte `backend/content.py` vers `content.json` |
| `just fonts` | sous-ensemble la police aux glyphes de la page (1 008 Ko → 25 Ko) |
| `just images` | réencode les images en AVIF + WebP aux tailles peintes |
| `just assets` | les deux précédentes |
| `just preview` | build puis sert `frontend/dist` comme le fera nginx |
| `just lint` | ruff + pyrefly (Python), eslint + prettier + svelte-check (frontend) |
| `just format` | formate et corrige (ruff côté Python, prettier + eslint côté frontend) |
| `just test` | pytest avec couverture |
| `just build` | site de production : bundles, prégénération, gzip |
| `just check` | tout : contrats + lint + tests (ce que lance la CI) |

Chaque recette reprend les commandes `uv`/`pnpm` sous-jacentes ; rien n'oblige à
passer par `just`, mais c'est le point d'entrée unique, aligné sur les hooks
pre-commit et la CI.

## Démarrer

```bash
just dev
```

Deux process démarrent : l'API sur le port 8000 et le dev server Vite sur 5173.
**Le site se consulte sur http://127.0.0.1:5173** — Vite proxifie `/api` vers
l'API, exactement comme nginx le fera en production. Le code client appelle donc
`/api` en relatif et ignore où vit le backend, en dev comme en production.

L'API seule ne sert aucune page : `http://127.0.0.1:8000/` répond 404, par
construction. Un test le vérifie.

Si quelque chose cloche dans la configuration :

```bash
uv run litestar assets doctor
```

## Modifier le contenu

Tout le texte du site — titres, résumé, projets, parcours, coordonnées — vit dans
`backend/content.py`, en structures `msgspec`. C'est le seul endroit à éditer.

```bash
$EDITOR backend/content.py
just content          # réexporte frontend/src/data/content.json
just build            # régénère les pages
```

**Committez `content.json`.** Même logique que `openapi.json` : c'est lui que
`Dockerfile.web` lit, et l'image du site ne contient aucun interpréteur Python.
`just check` réexporte et échoue si le fichier a dérivé — une édition jamais exportée
déploierait silencieusement l'ancienne copie.

Trois invariants sont tenus par des tests plutôt que par la discipline : aucune
traduction vide, aucune période qui se termine avant de commencer, et une année de
parcours qui correspond toujours à l'année de *début* de ce qu'elle contient. Ce
dernier point est ce qui manquait au site précédent, où un poste était classé à son
année de début et un diplôme à son année de fin.

Pour ajouter un projet, déposez sa capture dans `assets/images/projects/`, référencez
son nom de fichier **sans extension** dans `content.py`, et lancez `just images`. Le
champ `image` est un radical, pas un chemin : l'encodeur produit plusieurs largeurs en
AVIF et en WebP, et le balisage `<picture>` reconstruit le `srcset`. Un test échoue si
un projet pointe vers un radical sans fichiers derrière.

Le site tient en une page. Les sections se déclarent dans le struct `Sections` de
`content.py` : le nom du champ devient l'ancre (`#projects`), et son `heading` devient
le libellé du lien dans l'en-tête. `frontend/src/lib/site.ts` décide lesquelles
apparaissent dans la navigation et dans quel ordre, `frontend/src/routes/Home.svelte`
les compose. Ajouter une section, c'est donc trois endroits : le contenu, la liste de
navigation, le rendu.

## Deux langues

Le site est en français par défaut et en anglais sous `/en/` :

| français | anglais |
|---|---|
| `/` | `/en/` |

Les ancres ne sont pas traduites : `#projects` désigne la même section dans les deux
langues. C'est ce qui permet au sélecteur de langue de conserver la position du
lecteur, et c'est une chose de moins à garder synchronisée. Les anciennes adresses
`/about`, `/projects` et `/contact` sont redirigées en 301 vers leur ancre, dans les
deux langues, parce qu'elles existent dans des résultats de recherche et des favoris.

**Rien n'est traduit à l'exécution.** Le document est rendu deux fois au build, donc
il n'y a ni détection de langue, ni dictionnaire embarqué, ni bascule côté client : un
visiteur télécharge la langue qu'il a demandée et jamais l'autre. Le sélecteur de
l'en-tête affiche la langue dans laquelle le site est affiché et ouvre la liste des
autres — un `<details>` et des liens, donc crawlable, ouvrable dans un nouvel onglet,
et fonctionnel sans JavaScript.

Le référencement suit : `<html lang>` par page, `<link rel="alternate" hreflang>` dans
les deux sens, `x-default` sur le français, et un `sitemap.xml` qui déclare les paires.
Le 404 existe aussi dans les deux langues, et nginx sert l'anglais sous `/en/`.

Côté code, la locale circule par le contexte Svelte (`setLocale` dans `Page.svelte`,
`useLocale()` partout ailleurs) plutôt qu'en prop à travers douze signatures. Comme
les pages ne sont jamais hydratées, le contexte est résolu une fois, pendant le rendu
qui produit le HTML.

Chaque chaîne visible est un `Text(fr=…, en=…)` dans `backend/content.py` : ajouter un
champ oblige à écrire les deux versions, et un test échoue si l'un des deux est vide.
Seules les chaînes d'interface (libellés d'accessibilité, « Lire l'article ») vivent
côté frontend, dans `src/lib/i18n.ts`.

### Les durées ne s'écrivent pas à la main

Une entrée de parcours porte un `Period(start=…, end=…)`, et le gabarit calcule
« 1 an 9 mois » au build. Le site précédent affichait « 1 year, 2 month » pour un poste
qui durait depuis vingt mois : le chiffre avait été tapé une fois, puis oublié. Un
`end=None` signifie « aujourd'hui », traduit selon la langue.

## Éco-conception

L'objectif de ce portage était de servir le même site en consommant beaucoup moins.
Voici où sont passés les 1 259 Ko économisés, par ordre de rendement.

### Les polices : 1 011 Ko → 25 Ko

C'était, de loin, le premier poste. Le site servait `InterVariable.woff2` (344 Ko),
son italique (379 Ko) et six fichiers IBM Plex Mono (285 Ko) — à chaque visite à froid,
sans aucun sous-ensemble : chaque visiteur téléchargeait aussi le cyrillique, le grec
et le vietnamien. Quatre coupes (`scripts/optimize_fonts.py`) :

- **latin seul** au lieu de latin + latin-ext : 158 Ko → 67 Ko.
- **axe optique figé** : 67 Ko → 44 Ko. L'axe `opsz` portait un second jeu de deltas
  `gvar` pour environ la moitié du fichier. Figé à sa valeur par défaut, les titres
  s'affichent comme de l'Inter 14 pt agrandi — ce que fait n'importe quel déploiement
  d'Inter statique. C'est le seul arbitrage de ce portage qui touche au rendu, et il
  se rouvre en une ligne (`PINNED_AXES`).
- **les seuls glyphes de la page** : 44 Ko → 25 Ko. Les quatre documents construits
  contiennent 110 caractères distincts ; le fichier ne porte que ceux-là. Ce choix
  avait d'abord été rejeté par crainte du carré blanc, et c'était une erreur de
  raisonnement : le script génère l'`unicode-range` **depuis le même jeu de
  caractères** que le sous-ensemble, donc un caractère que le fichier ne porte pas est
  aussi un caractère qu'il ne revendique pas, et le navigateur retombe sur la police
  système. Le pire cas est un mot dans une autre sans-serif, pas une rangée de carrés.
  Et `just check` construit puis échoue si les documents contiennent un caractère
  absent du fichier, donc ça se voit avant d'être publié.
- **italique et monospace supprimées** : rien n'est en italique sur le site, et la
  police mono ne servait qu'aux blocs de code du blog, non porté.

L'axe de graisse reste variable : un seul fichier sert les graisses 400, 500 et 600.

### Les images : ce n'est pas le codec, c'est le nombre de pixels

L'avatar était un PNG de 400 × 400 (197 Ko) affiché dans un cercle de 36 px. Les
captures de projets étaient servies en 1152 × 648, voire 2851 px pour le schéma SVG,
pour être peintes dans une vignette de 300 px. Le navigateur téléchargeait, décodait,
puis jetait plus de 90 % des pixels.

`frontend/scripts/optimize-images.mjs` déclare donc la boîte réellement peinte et
recadre à l'encodage plutôt que de laisser faire `object-fit` : deux largeurs par
cible (écrans 1× et 2×), en AVIF puis WebP via `<picture>`. Les cinq vignettes de la
page d'accueil pèsent 12 Ko au total en AVIF 300 px. L'avatar : 523 octets.

Pas de repli PNG/JPEG — WebP est supporté partout où ce site l'est — et le recadrage
se fait par le haut plutôt qu'au centre, ce qui donne une vignette nettement plus
lisible (au centre, l'échiquier de Bresse apparaissait vide).

### Le JavaScript : 215 Ko → 4,3 Ko

Le site n'a plus de runtime de framework parce qu'il n'a plus rien à hydrater. Ce qui
a disparu et par quoi c'est remplacé :

| avant | après |
|---|---|
| React + Next.js (hydratation, routeur) | rien : pages prégénérées, navigation native |
| Motion (~34 Ko) pour les apparitions au défilement | `animation-timeline: view()`, animations CSS pilotées par le défilement, sur le compositeur |
| Radix Dialog (~14 Ko) pour le menu mobile | l'attribut HTML natif `popover` — couche supérieure, fermeture au clic extérieur et à Échap, gestion du focus, gratuits |
| next-themes | ~200 octets inline, autorisés par hash CSP |
| lucide-react + simple-icons | tracés SVG inlinés dans le HTML au build |
| Lenis (défilement fluide) | `scroll-behavior: smooth` |

Les apparitions au défilement sont désactivées proprement là où
`animation-timeline` n'existe pas encore (Firefox, anciens Safari) : la règle est
inversée, le contenu est visible par défaut et ne devient animable que dans le
`@supports`. Le pire cas est donc une page statique, jamais une page blanche. Même
logique pour `prefers-reduced-motion` et pour l'impression.

### Les requêtes : 42 → 12

- Le contenu est incrusté dans le HTML : zéro appel d'API pour l'afficher.
- Une seule feuille de style (`cssCodeSplit: false`), mise en cache une fois pour
  toutes plutôt que découpée par section.
- Une seule page : la consultation entière tient en un aller-retour, et les liens de
  l'en-tête défilent au lieu de recharger un en-tête et une feuille de style déjà là.
- L'analytics est relayée en première partie : ni résolution DNS, ni poignée de main
  TCP, ni négociation TLS supplémentaires pour quelques centaines d'octets.
- `op1.js` est vendorisé dans `public/vendor/` au lieu d'être chargé depuis
  openpanel.dev.
- La police est préchargée en parallèle de la feuille de style qui la référence, au
  lieu d'être découverte après son analyse.
- `/favicon.ico` répond 204 au lieu de retomber sur une page HTML en 200.

### Le transport

`frontend/scripts/compress.mjs` précompresse le HTML, le CSS et le JS au niveau
maximum pendant le build, et nginx les sert avec `gzip_static`. Le travail a lieu une
fois sur un portable, pas à chaque requête sur le serveur : moins d'octets sur le fil
*et* moins de CPU par visite. Les images et la police en sont exclues, elles sont déjà
compressées — la woff2 l'est en brotli en interne.

Le cache est découpé selon ce qui peut changer : un an en `immutable` pour `/assets/`
dont Vite hashe les noms, une semaine pour les polices et images dont le nom est
stable, `no-cache` pour le HTML afin qu'un déploiement soit vu immédiatement.

### Ce qui n'a pas été fait

- **Brotli** ferait gagner environ 4 Ko sur une première visite, mais le module n'est
  pas dans l'image nginx officielle, et le servir à la main sans lui est une mauvaise
  affaire ici. Il faudrait une `location` par extension pour forcer le `Content-Type`,
  que `try_files` prendrait sinon sur le `.br` — et avec `nosniff` actif, un type
  erroné ne dégrade pas, il fait refuser le fichier par le navigateur. Quarante lignes
  de conf fragile qui peuvent blanchir la page, contre 4 Ko. Si on veut Brotli, la
  façon honnête est de construire une image nginx avec `ngx_brotli`, ce qui déplace le
  coût vers le build et la maintenance plutôt que vers le risque.
- **Inliner le CSS** supprimerait la seule requête bloquante de la première visite.
  Depuis le passage en page unique, l'arbitrage s'est resserré : il n'y a plus de
  seconde page sur laquelle réenvoyer la feuille. Mais le HTML est servi en
  `no-cache`, donc le CSS repartirait à chaque visite, alors qu'il est aujourd'hui
  mis en cache une fois. Le fichier externe gagne toujours au deuxième passage.

## Mesure d'audience

OpenPanel auto-hébergé, relayé en première partie. Le script est servi depuis
`/vendor/op1.js` et son point d'ingestion est `/op/`, que nginx relaie vers
l'instance : le navigateur ne parle donc qu'à une seule origine.

Trois conséquences, et ce sont les raisons du montage : aucune connexion
supplémentaire à ouvrir, une CSP qui reste `'self'` de bout en bout, et un script tiers
qui ne peut pas changer sous vos pieds sans un commit ici. Le fichier garde son nom
d'origine : il ne s'agit pas de passer sous le radar d'un bloqueur, et un visiteur qui
bloque la mesure d'audience a raison de continuer.

```bash
OPENPANEL_API_URL=https://opapi.athroniaeth.cloud   # dans .env, variables Coolify
```

C'est l'**API d'ingestion**, pas le tableau de bord — deux domaines distincts sur une
instance auto-hébergée. Le *Client ID* est public et vit dans `frontend/src/client.ts` :
le navigateur le lit de toute façon. Le **secret du projet ne doit pas s'y trouver** ;
il ne sert qu'aux événements envoyés depuis un serveur, et rien dans le frontend n'en a
l'usage.

L'instance valide l'`Origin` de chaque événement contre les domaines déclarés dans le
projet. `client.ts` n'initialise donc la mesure que sur le domaine de production : une
visite en local ou sur une préproduction recevrait un 401 de toute façon, autant ne pas
émettre la requête et garder les chiffres propres.

## Docker

Deux images, chacune buildable sans l'autre :

- `Dockerfile.api` — Python seul, sans Node ni outils de build. Ne contient que
  l'interpréteur, le venv et `backend/`, sous un utilisateur non privilégié.
- `Dockerfile.web` — étage Node qui dérive les types de `openapi.json` et build le
  bundle, puis nginx sans privilèges qui le sert.

```bash
docker compose up --build
```

L'app répond sur http://127.0.0.1:8000, servie par nginx. L'API n'est pas exposée
sur l'hôte : seul `web` l'atteint, par le réseau interne de compose. Le service
`web` attend que le healthcheck de `api` passe avant de démarrer.

### Coolify

`compose.prod.yml` est la variante pour un déploiement Coolify. Trois différences avec
`compose.yml`, toutes dues au fait de tourner derrière le Traefik de Coolify :

- **aucun `ports:`** — publier un port contournerait le proxy et exposerait le
  conteneur directement sur l'hôte ; Traefik joint `web` par le réseau du projet ;
- **`SERVICE_FQDN_WEB_8080`** — variable magique, volontairement sans valeur : Coolify
  génère un domaine, l'attache au service `web` et le route vers le port 8080 ;
- **`restart: unless-stopped`**, et `API_KEY` déclarée avec `:?` donc requise dans
  l'interface — une valeur vide bloque le déploiement.

`api` n'a ni domaine ni port publié : Coolify garde ces services privés au réseau du
projet, joignables seulement en `http://api:8000`, ce que fait nginx. Ne lui donnez un
domaine que pour ouvrir l'API à des tiers, et lisez la section sur la clé d'API avant.

nginx préserve les en-têtes `X-Forwarded-*` posés par le proxy amont au lieu de les
écraser : Traefik termine le TLS et parle à nginx en clair, donc transmettre `$scheme`
ferait croire à l'application que le visiteur n'est pas en HTTPS — de quoi casser les
cookies `Secure` et les redirections absolues. Sans proxy devant, en local, la valeur
retombe sur `$scheme`. Le module `real_ip` récupère par ailleurs l'adresse réelle du
client, en ne faisant confiance qu'aux plages privées : `X-Forwarded-For` est contrôlé
par l'appelant et ne doit jamais être cru s'il arrive directement d'Internet.

Coolify considère ce fichier comme la source de vérité : déclarez les variables ici,
pas seulement dans l'interface.

### Dimensionner

L'API porte la charge : le frontend est un bundle statique qu'un visiteur télécharge
une fois, puis met en cache (les noms sont hashés, nginx les sert en `immutable`).
C'est donc l'API qu'on dimensionne.

```bash
WEB_CONCURRENCY=4 docker compose up -d    # 4 workers Granian
```

Passer à l'horizontal ensuite ne demande que des répliques d'`api` derrière nginx —
à condition de n'avoir mis aucun état en mémoire dans le processus.

## Clé d'API

`/api/content` est protégée par une clé, `/api/health` reste publique (le healthcheck
de compose l'atteint directement, sans proxy). Le garde vit dans `backend/security.py`
et s'accroche au handler par `guards=[require_api_key]`.

À noter : **le site lui-même n'appelle jamais cette route**. Le contenu est incrusté
dans le HTML au build, donc un visiteur ne déclenche aucun appel d'API. La route existe
pour garder les structures typées et documentées dans `openapi.json`, et pour rester
joignable par un tiers ou par une future page qui, elle, en aurait besoin à l'exécution.

Le point important : **la clé n'entre jamais dans le navigateur**. nginx l'ajoute en
`proxy_set_header` côté serveur, et le proxy Vite fait de même en développement. Un
appelant depuis le site ne présente donc rien — inspectez les requêtes dans les
DevTools, il n'y a pas d'en-tête `X-API-Key`.

C'est délibéré : une variable `VITE_*` est inlinée en clair dans le bundle, donc une
clé embarquée dans un SPA est une clé publique.

```bash
API_KEY=… docker compose up -d          # ou API_KEY dans le .env
curl http://127.0.0.1:8000/api/content  # 200, via nginx qui injecte la clé
curl -H "X-API-Key: …" http://api:8000/api/content  # 200, client tiers
```

Sans `API_KEY`, rien ne démarre : `docker compose up` s'arrête à l'interpolation, et
l'application elle-même refuse de démarrer (`ensure_api_key_configured`, appelée par
`on_startup`). Le conteneur sort en code 1 avec la cause dans les logs, donc il ne
devient jamais *healthy* et `depends_on: service_healthy` garde le frontend éteint :
le déploiement signale l'échec au lieu de servir une application cassée.

Ce garde-fou existe parce que l'inverse a été observé : sur Coolify, `${API_KEY:?}`
ne bloque pas le déploiement comme le fait `docker compose` seul. La variable était
vide, nginx a alors **supprimé** l'en-tête — il ne transmet pas un en-tête dont la
valeur est vide — et l'API répondait 401 à chaque appel sans que rien n'indique
pourquoi. La configuration échoue en fermé, jamais en ouvert, et désormais elle
échoue bruyamment.

Ce que cela protège, et ce que cela ne protège pas : la route est réservée aux appels
passant par votre nginx ou porteurs de la clé, ce qui permet d'exposer un domaine
d'API à des clients tiers. Ce n'est **pas** de l'authentification utilisateur — tout
visiteur du site atteindrait `content` à travers le proxy s'il connaissait l'URL.
Ce contenu est de toute façon public : il est imprimé dans le HTML de chaque page. Pour cloisonner des données par
utilisateur, il faut une session (un cookie `HttpOnly` fonctionne sans CORS ici,
grâce à l'origine unique).

Swagger UI (`/schema/swagger`) affiche un bouton « Authorize » et un cadenas sur la
route : le schéma de sécurité est déclaré dans `openapi.json`, donc le contrat ne
présente pas la route comme libre d'accès.

### Documentation OpenAPI

`ENABLE_DOCS` (défaut `true`) commande les routes `/schema` — Swagger, Redoc,
`openapi.json`. `compose.prod.yml` la passe à `false` : `/schema` publie l'inventaire
complet des routes, et l'API disposant de son propre domaine sur Coolify, la masquer
dans nginx ne suffirait pas. La coupure se fait donc dans l'application, où elle vaut
pour tous les chemins d'accès. Mettez `ENABLE_DOCS=true` dans les variables du projet
pour la rétablir le temps d'un diagnostic.

Techniquement, `build_openapi_config` renvoie `None`, ce qui supprime le routeur
`/schema`. Le schéma quitte alors la mémoire : `litestar assets generate-types` en a
besoin, c'est pourquoi la recette `just types` force `ENABLE_DOCS=true`. Sans ce
forçage, la commande n'exporterait plus rien — sans erreur — et le contrat dériverait
sans que personne ne le voie.

## Durcissement HTTP

nginx pose cinq en-têtes sur les réponses du site (`deploy/security-headers.conf`) :
`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, une `Referrer-Policy`
stricte, une `Permissions-Policy` qui refuse caméra, micro, géolocalisation et paiement,
et une `Content-Security-Policy` entièrement en `'self'`. Tout est auto-hébergé — la
police, les images, le script d'analytics et jusqu'à son point d'ingestion, que nginx
relaie — donc aucune origine tierce n'est autorisée, ni pour les scripts ni pour les
connexions.

Une exception, et elle est nommée : le script inline qui applique le thème avant le
premier rendu. Il doit être inline pour éviter le clignotement, alors la CSP l'autorise
par son **hash sha256** plutôt que par un `'unsafe-inline'` qui ouvrirait la porte à
tout le reste. Ce hash est calculé par le prégénérateur et écrit dans
`deploy/csp-script-hash.conf` ; `Dockerfile.web` le reprend depuis l'étage de build, si
bien que l'en-tête correspond toujours au script réellement présent dans la page — un
hash périmé est structurellement impossible.

Ce fichier est inclus dans chaque `location` plutôt que déclaré une fois sur le bloc
`server` : nginx n'hérite pas des `add_header` dans un bloc enfant qui en déclare
lui-même, et `/assets/` en pose un pour le cache — il perdrait donc silencieusement
tous les autres. `/api`, `/schema` et `/op` en sont exclus : une CSP ne concerne pas une
réponse JSON, et Swagger UI a besoin de styles inline.

L'API applique un quota de 120 requêtes par minute et par client
(`build_rate_limit_config`), avec `/api/health` exempté pour ne jamais gêner le
healthcheck. Le comptage n'utilise pas le client de la connexion — derrière nginx, ce
serait le proxy pour tout le monde, donc un quota partagé — mais l'en-tête `X-Real-IP`,
que nginx écrase et qu'un appelant ne peut donc pas forger.

À savoir : le compteur vit dans le magasin en mémoire, propre à chaque worker. Avec
`WEB_CONCURRENCY=4`, le quota effectif est donc quadruple. Le rendre exact, et le faire
survivre à plusieurs répliques d'API, demande un magasin partagé comme Redis.

## Qualité

Le lint, le typage et les tests couvrent backend et frontend d'un seul point :

```bash
just lint             # ruff, pyrefly, eslint, prettier, svelte-check
just test             # pytest + couverture
```

Les mêmes vérifications tournent à chaque commit via [prek](https://github.com/j178/prek)
(ou pre-commit) — lancez `prek install` une fois — et dans la CI GitHub Actions.

## Développement

Lancez toujours `litestar` depuis la racine du dépôt. Depuis `frontend/`, Python ne
trouve pas le package `backend` et la commande échoue.

### Types TypeScript

Après avoir touché à une route ou à un type de réponse :

```bash
just types      # uv run litestar assets generate-types
```

La commande écrit `openapi.json` à la racine, puis en tire les types, les schémas
Zod, un client d'API et un helper de routage dans `frontend/src/generated/`.

**Committez `openapi.json`.** C'est le contrat : il rend le frontend buildable sans
Python, et tout changement d'API devient un diff lisible en revue. `just check`
(donc la CI) régénère le fichier et échoue s'il a dérivé des handlers.

Le frontend peut se régénérer seul, sans Python :

```bash
pnpm -C frontend generate-types
```

Un détail qui compte : annotez les réponses avec une dataclass ou un
`msgspec.Struct`. Un `dict[str, str]` donne un `{ [key: string]: string }`,
c'est-à-dire à peu près rien.

### Commits

Commits au format [Conventional Commits](https://www.conventionalcommits.org), via
[Commitizen](https://commitizen-tools.github.io/commitizen/) configuré dans `cz.toml`.

```bash
uv run cz commit     # rédaction guidée
uv run cz bump       # version, tag et CHANGELOG
```

Le format est aussi vérifié automatiquement à chaque commit : le hook `commitizen`
(étape `commit-msg`) rejette un message non conforme. Il s'installe avec le reste
via `prek install` (voir `default_install_hook_types` dans `.pre-commit-config.yaml`).

`cz bump` lit et écrit la version dans `pyproject.toml` via uv. Tant que
`major_version_zero` est actif, le projet ne dépasse pas `0.x`.

### Travailler sur le frontend seul

```bash
just dev-front            # Vite seul, sans backend
just build                # site de production dans frontend/dist
just preview              # build puis sert dist/ comme le fera nginx
```

Le site étant prégénéré, le dev server n'a pas d'`index.html` à servir : un middleware
dans `vite.config.ts` rend les pages à la volée avec le même `entry-server.ts` et le
même gabarit HTML que le build (`frontend/scripts/document.mjs`). C'est délibéré — une
erreur dans le gabarit apparaît sur localhost, pas sur le domaine.

Comme le contenu est incrusté au build, le frontend se développe entièrement sans
backend. Les appels `/api` restent proxifiés vers `http://127.0.0.1:8000` si vous en
ajoutez ; pointez `API_URL` ailleurs dans le `.env` si l'API écoute sur un autre port.

## Branches et CI

Le dépôt suit [Gitflow](https://nvie.com/posts/a-successful-git-branching-model/) :
`main` (production, taguée), `develop` (intégration), et des branches `feature/*`,
`release/*`, `hotfix/*`. La CI (`.github/workflows/ci.yml`) valide le contrat, le lint
et les tests sur `main` et `develop`.

Elle ne construit pas les images : elles ne sont poussées vers aucun registre, et la
plateforme de déploiement les rebâtit depuis le dépôt — un build en CI ne ferait que
dupliquer, quelques minutes plus tôt, un échec qui apparaîtrait de toute façon au
déploiement. Pour les vérifier en local : `docker compose build`.
