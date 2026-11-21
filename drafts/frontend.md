---
title: The DraCor front end
subtitle: dracor-frontend 3 and the DraCor React component library
short_title: Front end
label: dracor-frontend
---

<!--
DRAFT (2026-11-20), written autonomously by Claude from the code, for Ingo to review.
Not part of the book yet (drafts/ is outside book/ and not in the toc).
Intended for 2.0.0 ("Current documentation", #9/#11): replaces the code-level parts of
D7.1 §5.6 for the current state; the user-facing walkthrough is in DraCor Textbook ch. 4.
Based on: dracor-frontend 3.0.0-rc.1 (700071e, 2026-10-31; main bead72a differs only in
deploy workflows), `@dracor/react` 1.11.0 (ffda3e0, 2026-10-24), dracor-api 1.5.0-rc.1.
All code links are pinned to these tags. Check everything again when 3.0.0 is released.
Open questions for Ingo/Carsten are collected at the end.
-->

:::{note} Draft
:class: editorial
This page describes the front end as of **dracor-frontend 3.0.0-rc.1** (release candidate, 31 October 2026, running on [staging.dracor.org](https://staging.dracor.org)) and **`@dracor/react` 1.11.0**. It updates the description in [D7.1 §5.6](../book/clsinfra-d71/5-6.md), which documents front end 2.x (JavaScript, early 2023). For a guided tour of the website from a user's point of view, see [DraCor Textbook, ch. 4](https://textbook.dracor.org/chapters/04-front-end-navigating-dracor.html).
:::

## Overview

The website at [dracor.org](https://dracor.org) is a single-page application that gets all its data from the [DraCor API](https://dracor.org/doc/api). It does not hold any corpus data of its own. Every number, network and text it shows is fetched from the API or computed in the browser from the API's responses. Anything the website can show, a script can therefore also get from the API.

Since version 3.0 the front end is built from two repositories:

| Repository | What it is | Licence | Distribution |
|---|---|---|---|
| [dracor-org/dracor-frontend](https://github.com/dracor-org/dracor-frontend) | the web application: routes, pages, data loading, visualisations | MIT | Docker image [`dracor/frontend`](https://hub.docker.com/r/dracor/frontend), deployed to dev, staging and production |
| [dracor-org/dracor-react](https://github.com/dracor-org/dracor-react) | the *DraCor React Component Library*: reusable components, the DraCor Tailwind theme and the TEI stylesheet | MIT | npm package [`@dracor/react`](https://www.npmjs.com/package/@dracor/react), documented in a [Storybook](https://dracor-org.github.io/dracor-react/) |

The component library is shared with other DraCor-related applications: [Einakter](https://github.com/dracor-org/einakter) and [ezlinavis](https://github.com/dracor-org/ezlinavis) also depend on `@dracor/react`. Generic building blocks therefore live in the library: corpus cards, ID links, author info, tables, tabs, the API documentation and the TEI viewer. The DraCor-specific analysis views stay in the application: network and relations graphs, the speech distribution charts and the play metrics.

```{mermaid}
flowchart LR
  subgraph browser[Browser]
    FE["dracor-frontend 3<br/>(React 19, TanStack Router)"]
    LIB["@dracor/react<br/>(component library)"]
    FE -- imports --> LIB
  end
  API["DraCor API v1<br/>/api/v1"]
  DOCS["dracor-docs<br/>/doc/*.md, /doc/sitemap.json"]
  ODD["ODD<br/>/odd.html"]
  REG["@dracor/registry<br/>(npm, bundled)"]
  SPARQL["SPARQL endpoint<br/>(optional)"]
  WD["Wikidata"]
  FE -- "fetch JSON, TEI, OpenAPI" --> API
  FE -- "Markdown pages, menu" --> DOCS
  FE -- "Encoding guidelines" --> ODD
  FE -- "corpus registry" --> REG
  FE -. "YASGUI" .-> SPARQL
  API -- "/wikidata/author/{id} (cached)" --> WD
```

### Technology

The code links in D7.1 point to commits of the 1.x line (2021–2022). The 2.x line (December 2023 to September 2026, last release 2.7.2) changed the build tooling but kept most of the 1.x stack. Version 3.0 replaces it.

| | 1.x (D7.1) | 2.7.2 | 3.0.0-rc.1 |
|---|---|---|---|
| Language | JavaScript, first TypeScript types | JavaScript and TypeScript (23 `.js`, 32 `.ts`/`.tsx` files) | TypeScript; shared types in [`src/types.ts`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/types.ts) |
| Build and tests | Create React App 4, Jest | Vite, Vitest | Vite, Vitest, Testing Library, [MSW](https://mswjs.io) |
| React | 17 | 18 | 19 |
| Routing | React Router 5; play tabs as URL hash (`#network`) | React Router 6; hash tabs | [TanStack Router](https://tanstack.com/router), file-based; tabs are path segments (`/ger/lessing-emilia-galotti/network`) |
| Data loading | `fetch*` functions inside components | inside components | route loaders calling [`src/loaders.ts`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/loaders.ts) |
| Styling | Bootstrap 4, reactstrap, SCSS | Bootstrap 4, reactstrap | [Tailwind CSS](https://tailwindcss.com) 4 with the DraCor theme from `@dracor/react` |
| Network graphs | react-sigma 1 (sigma.js 1) | react-sigma 1 | [sigma](https://www.sigmajs.org) 4 and [graphology](https://graphology.github.io) through `@react-sigma/core`; ForceAtlas2 layout in a web worker |
| Charts | Chart.js 2 (react-chartjs-2), Recharts 1 | Chart.js 2, Recharts 3 | [Recharts](https://recharts.org) 3 only |
| API documentation | Swagger UI (`swagger-ui-react`) | Swagger UI | [Scalar](https://scalar.com) (component `ApiDoc`); Swagger UI remains at [swagger.dracor.org](https://swagger.dracor.org) |
| Shared components | none | none | `@dracor/react` |

## Pages and routes

Routes are files under [`src/routes/`](https://github.com/dracor-org/dracor-frontend/tree/3.0.0-rc.1/src/routes), and [`src/routeTree.gen.ts`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routeTree.gen.ts) is generated from them. There is no `App` component: [`src/index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/index.tsx) mounts the router directly.

| URL | Route file | Loader (API calls) | Main components |
|---|---|---|---|
| *(every page)* | [`__root.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/__root.tsx) | `GET /info`, `GET /corpora`; the menu from `VITE_SITEMAP_URL` (on dracor.org: `/doc/sitemap.json`) | `TopNav` (→ `NavBar`), `RouteProgress`, `DracorContext` |
| `/` | [`index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/index.tsx) | `GET /corpora?include=metrics` | `CorporaIntro`, `DracorCorpusCard` |
| `/{corpus}` | [`$corpusId/index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/$corpusId/index.tsx) | `GET /corpora/{corpus}` | `Corpus`, `CorpusIndex` (→ `Table`, `IdLink`, `Years`, `Commit`) |
| `/{corpus}/{play}` | [`$corpusId/$playId/route.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/$corpusId/$playId/route.tsx) + [`index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/$corpusId/$playId/index.tsx) | `GET /corpora/{corpus}/plays/{play}`, `GET …/metrics` (optional) | `Play`, `PlayDetailsHeader` (→ `AuthorInfo`, `IdCopy`, `IdLink`, `Years`), `PlayDetailsNav` (→ `Tabs`) |
| `/{corpus}/{play}/{tab}` | [`$corpusId/$playId/$tab.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/$corpusId/$playId/$tab.tsx) | (the parent's data) | one of the six tabs, see below. An unknown tab redirects to `network`. |
| `/doc/api` | [`doc/api.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/doc/api.tsx) | `GET /openapi.yaml` (fetched by Scalar) | `ApiDoc`, lazy-loaded (~2 MB) |
| `/doc/legacy/api` | [`doc/legacy.api.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/doc/legacy.api.tsx) | the spec of the legacy API (on dracor.org `VITE_DRACOR_LEGACY_API=/api/v0`) | `ApiDoc` |
| `/doc/odd` | [`doc/odd.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/doc/odd.tsx) | the encoding guidelines from `VITE_DRACOR_GUIDELINES` (on dracor.org `/odd.html`) | `OddPage`, `Odd` |
| `/doc/corpora` | [`doc/corpora.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/doc/corpora.tsx) | none: the registry is bundled from the npm package [`@dracor/registry`](https://github.com/dracor-org/dracor-registry) | `CorpusRegistry` |
| `/doc/{slug}` | [`doc/$slug.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/doc/$slug.tsx) | `/doc/{slug}.md` (served from [dracor-docs](https://github.com/dracor-org/dracor-docs) since November 2025) | `DocPage` |
| `/sparql` | [`sparql.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/sparql.tsx) | none | `SparqlUi` (YASGUI, only with `VITE_WITH_SPARQL=yes`), otherwise `SparqlPlaceholder` |

DraCor IDs are resolved on the server: `https://dracor.org/id/ger000088` answers with a 303 redirect to the play page. In 2.x the front end resolved them itself (D7.1, Tab. 06, row `/id/{id}`).

Old play URLs with a tab in the hash (`/ger/lessing-emilia-galotti#network`) are rewritten to the new path form once, on the first page load ([`src/hashRedirect.ts`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/hashRedirect.ts)). Links in the reports that use the hash form therefore keep working.

(dracor-frontend-home)=
## The home page

<!-- PLACEHOLDER section (Ingo, 2026-11-21): concrete description with before/after screenshots. Facts below are from the code; screenshots still to be taken. -->

The home page lists the published corpora as corpus cards. The way they are shown changed with 3.0.

**From July 2020 up to 2.7.2**, and so also at the time of D7.1 (its Fig. 13, "DraCor landing page"), the cards sat in a carousel ([`Corpora.jsx`](https://github.com/dracor-org/dracor-frontend/blob/2.7.2/src/components/Corpora.jsx), built with `react-slick`). Depending on the screen width it showed up to seven cards side by side, with arrows and dots to move through the corpora. On small screens it scrolled by itself, and below 767 px it became a plain list. The cards were sorted by number of plays.

**Since 3.0** ([`src/routes/index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/routes/index.tsx)) there is no carousel. Commit [9d8ce68](https://github.com/dracor-org/dracor-frontend/commit/9d8ce68) removed `react-slick` along with swagger-ui. The page now has:

- **A grid of cards.** All corpora are visible at once, wrapping to as many columns as fit (one per row on phones). Each card is a `DracorCorpusCard` from `@dracor/react` and shows plays, characters by sex, word tokens and the last update. A link to the Git commit of the corpus version is included as well.
- **Sort buttons** above the grid: by number of plays (default), by name A–Z (using the acronym without "DraCor", i.e. what the card shows) or by last update. The choice is kept in the URL (`/?sort=name`, `/?sort=updated`), so a sorted view can be linked.
- **An introductory line** (`CorporaIntro`) above the cards that points to the [research bibliography](https://dracor.org/doc/research) and counts its entries since 2024. It only appears on deployments whose site menu links `/doc/research`.
- **A clear message if the API is down** ("Could not load the corpus list …") instead of an empty or broken page.

:::{note} Screenshots needed
Fig. A: dracor.org home page with the carousel (front end 2.7.2, e.g. from the Internet Archive or a local 2.7.2 build).

Fig. B: the same page in 3.0 (staging.dracor.org), wide screen, default order.

Optional Fig. C: phone width, to show that the cards stack.

D7.1 Fig. 13 shows the carousel version; a caption could make the comparison explicit.
:::

## Data flow

All API calls go through a few helpers in [`src/loaders.ts`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/loaders.ts):

- `apiGet` sets `Accept: application/json` and throws an `ApiError` carrying the HTTP status.
- `isNotFound` lets routes turn a 404 into the "not found" page.

Route loaders call these helpers before a page renders, and components read the result with `Route.useLoaderData()`. The two calls every page needs (`/info` and `/corpora`) are made once by the root route and shared through a React context ([`src/context.ts`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/context.ts)). A failing `/info` or `/corpora` does not break the site: the root loader catches the error, and the home page shows that the API is unavailable.

The base URL of the API is `VITE_DRACOR_API` or, if that is unset, the relative path `/api/v1` ([`src/config.ts`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/config.ts)). In development Vite proxies `/api/v1` to a local API. In the Docker image nginx proxies it to `DRACOR_API_HOST` (see [Configuration and deployment](#dracor-frontend-config)). The same build can therefore run against dev, staging, production or a local API.

Several things are computed in the browser and not fetched as ready-made data:

- **Co-presence network:** [`src/network.ts`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/network.ts) builds the graph from the `segments` of the play info (`getCooccurrences`, `makeGraph`). It does not use the `/networkdata/*` endpoints, which are only offered as downloads.
- **Speech distribution charts:** computed from `segments`.
- **Relations graph:** built from the `relations` of the play info.
- **Segment tree on the "Full text" tab:** `Segments`, built from `segments` and `characters`.

(dracor-frontend-endpoints)=
### API endpoints used by the front end

This table replaces D7.1, Tab. 06, for front end 3.0.0-rc.1 and API 1.5.0-rc.1. It uses three kinds of use:

- **fetched:** the data is loaded and rendered;
- **linked:** the page offers a link or download button to the endpoint;
- **tool:** the endpoint URL is passed to an external tool.

| Endpoint (`/api/v1`…) | Home | Corpus page | Play: header, network, relations, speech | Full text | Downloads | Tools | API doc |
|---|---|---|---|---|---|---|---|
| `/info` | fetched (all pages) | | | | | version check | |
| `/openapi.yaml` | | | | | | | fetched |
| `/corpora` | fetched (all pages; home: `?include=metrics`) | | | | | | |
| `/corpora/{corpus}` | | fetched | | | | | |
| `/corpora/{corpus}/metadata` | | linked (JSON) | | | | | |
| `/corpora/{corpus}/metadata/csv` | | linked (CSV) | | | | | |
| `/corpora/{corpus}/plays/{play}` | | | fetched | fetched (segments) | | | |
| `…/metrics` | | | fetched (network tab) | | | | |
| `…/tei` | | linked (per play) | | fetched (CETEIcean) | linked | tool | |
| `…/txt` | | | | | | tool (API ≥ 1.1.0-beta.7) | |
| `…/characters`, `…/characters/csv` | | | | | linked | | |
| `…/networkdata/csv`, `/gexf`, `/graphml` | | | | | linked | tool (GEXF → Gephi Lite) | |
| `…/relations/csv`, `/gexf`, `/graphml` | | | | | linked (if the play has relations) | | |
| `…/spoken-text` | | | | | linked | tool | |
| `…/spoken-text-by-character` | | | | | linked (JSON) | | |
| `…/stage-directions` | | | | | linked | tool | |
| `…/stage-directions-with-speakers` | | | | | linked | | |
| `/wikidata/author/{id}` | | | fetched (author portrait) | | | | |
| `/id/{id}` | | | | | | | (resolved on the server) |
| `/characters`, `/character/{id}`, `/wikidata/mixnmatch`, `/dts/*` | not used | | | | | | |

<!-- TODO: generate this table from the code (grep of loaders.ts, DownloadLinks.tsx, ToolsTab.tsx, CorpusIndex.tsx, Play.tsx) as part of the drift check (#23), like coderefs/ -->

The external tools on the "Tools" tab are [Voyant Tools](https://voyant-tools.org), the [CLARIN Language Resource Switchboard](https://switchboard.clarin.eu) and [Gephi Lite](https://gephi.org/gephi-lite/). They load the data directly from the API, so the tab only offers them when the API is publicly reachable (its host name contains `dracor.org`).

## The play view

The play view is the centre of the website. [`Play.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/components/Play.tsx) renders the header and the tab bar for all tabs. Each tab is a URL of its own (`/{corpus}/{play}/{tab}`), so tabs can be linked and bookmarked.

| Tab | Path | Content | Components (dracor-frontend unless noted) | D7.1 |
|---|---|---|---|---|
| Network | `network` (default) | co-presence network, cast list, network metrics | `NetworkGraph` (lazy, sigma), `CastList`, `PlayMetrics` | §5.6.3.1 |
| Relations | `relations` | kinship and other relations ([Wiedmer, Pagel, Reiter 2020](https://doi.org/10.5281/zenodo.4621778)); falls back to Network if the play has none | `RelationsGraph` (lazy, sigma), `CastList` | §5.6.3.2 |
| Speech distribution | `speech` | three chart types: Sapogov (default), Yarkho, Trilcke/Fischer | `SpeechDistribution`, [`SpeechDistribution/`](https://github.com/dracor-org/dracor-frontend/tree/3.0.0-rc.1/src/components/SpeechDistribution) `Sapogov`, `Yarkho`, `TrilckeFischer` (Recharts) | §5.6.3.3 and excursus |
| Full text | `text` | the TEI rendered in the browser, source information, segment tree | `TEIPanel` → `TEIText` (`@dracor/react`, [CETEIcean](https://github.com/TEIC/CETEIcean)), `SourceInfo`, `Segments` | §5.6.3.4 |
| Downloads | `downloads` | download buttons for all data layers | `DownloadLinks` → `DownloadButton` (`@dracor/react`) | §5.6.3.5 |
| Tools | `tools` | sends a text layer or the network to external tools | `ToolsTab` | new in 3.0 (2.x: links on the Downloads tab) |

The header ([`PlayDetailsHeader.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/components/PlayDetailsHeader.tsx)) shows the following:

- title and subtitle;
- the authors, with portraits from Wikidata (`AuthorInfo`), with translators marked as such;
- the years written, premiered and printed (`Years`);
- the DraCor ID with a copy button (`IdCopy`, which copies the URI `https://dracor.org/id/{id}`);
- the Wikidata ID (`IdLink`).

`AuthorInfo` would query Wikidata's SPARQL endpoint directly. The front end passes it a `fetcher` that goes through the API endpoint `/wikidata/author/{id}` instead, so frequently viewed authors are served from the API's cache.

## The DraCor React component library

`@dracor/react` is published on npm by the [dracor organisation](https://www.npmjs.com/org/dracor). The [Storybook](https://dracor-org.github.io/dracor-react/) shows every component with examples and its props. Installation and set-up:

```sh
pnpm add @dracor/react      # or npm i / yarn add
```

```css
/* index.css */
@import '@dracor/react/dracor.css';     /* DraCor Tailwind theme (colours, spacing, icons) */
@import '@dracor/react/tei.css';        /* only if you render TEI with TEIText */
@source '../node_modules/@dracor/react'; /* let Tailwind see the classes the components use */
```

The library is built one file per component, and every component also has its own subpath export (`import IdCopy from '@dracor/react/IdCopy'`). Unused components are therefore dropped from a bundle. dracor-frontend imports all components through subpaths. `react` and `react-dom` (19) are the only required peer dependencies. Everything else is an optional peer that only needs to be installed for the components that use it.

| Component | Purpose | Key props | Optional peers | Used in dracor-frontend |
|---|---|---|---|---|
| [`ApiDoc`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/ApiDoc/ApiDoc.tsx) | renders an OpenAPI spec with Scalar; DraCor defaults (classic layout, no sidebar, no Scalar client/MCP/agent buttons); optional switch between the modern and classic layouts | `url`, `title`, `configuration`, `layoutSwitch`, `hidePoweredBy`, `plainVersion` | `@scalar/api-reference-react` | `/doc/api`, `/doc/legacy/api` |
| [`AuthorInfo`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/AuthorInfo/AuthorInfo.tsx) | portrait, name, birth and death from Wikidata | `wikidataId`, `name`, `translator`, `fetcher` (default: [`wikidataSparqlFetcher`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/AuthorInfo/wikidataSparqlFetcher.ts)) | | play header |
| [`Authors`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/Authors/Authors.tsx) | list of author names with ID links | `data` | | |
| [`Commit`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/Commit/Commit.tsx) | short Git commit hash linked to the repository | `repo`, `children` (hash) | Font Awesome | corpus page |
| [`CorpusCard`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/CorpusCard/CorpusCard.tsx), `CorpusCardRow` | generic corpus card with rows, commit and last update | `title`, `to`, `commit`, `repo`, `updated` | TanStack Router | |
| [`DracorCorpusCard`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/DracorCorpusCard/DracorCorpusCard.tsx) | the corpus card of the dracor.org home page (plays, characters by sex, tokens in `text`/`sp`/`stage`, last update) | `name`, `title`, `acronym`, `metrics` (from `/corpora?include=metrics`) | TanStack Router | home page |
| [`DebouncedInput`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/DebouncedInput/DebouncedInput.tsx) | text input that reports changes after a delay (used for table filters) | `value`, `onChange`, `debounce` | | (inside `Table`) |
| [`DocPage`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/DocPage/DocPage.tsx) | fetches a Markdown file (`text/markdown`) and renders it; the first `#` heading becomes the page title | `url` or `match`, `components`, `rehypePlugins` | | `/doc/{slug}` |
| [`DownloadButton`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/DownloadButton/DownloadButton.tsx) | download link with a file-type icon (bibtex, csv, gexf, graphml, json, rdf, ris, tei, txt) | `href`, `name`, `type` | | Downloads tab |
| [`IdCopy`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/IdCopy/IdCopy.tsx) | an ID with a button that copies its URI | `children`, `prefix`, `uri`, `icon` | Font Awesome | play header |
| [`IdLink`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/IdLink/IdLink.tsx) | turns `scheme:id` into a link with an icon; schemes: `wikidata`, `dracor`, `wega`, `isni`, `gnd`/`pnd`, `viaf` | `children`, `showLabel` | | corpus page, play header |
| [`LanguageMenu`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/LanguageMenu/LanguageMenu.tsx) | language switch | `languages`, `current`, `onSelect` | Headless UI, Font Awesome | |
| [`NavBar`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/Navigation/NavBar.tsx) (folder `Navigation/`) | top navigation with logo, version, GitHub link, items and drop-down menus | `title`, `logo`, `version`, `gitHubUrl`, `navItems` | TanStack Router, Headless UI, Font Awesome | every page (`TopNav`) |
| [`Table`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/Table/Table.tsx) | sortable and filterable table | `data`, `columns`, `defaultSort` | TanStack Table | corpus page (list of plays) |
| [`Tabs`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/Tabs/Tabs.tsx) | tab bar whose tabs are router links | `data` (link props + `label`), `wrap` | TanStack Router | play view |
| [`TEIText`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/TEIText/TEIText.tsx) | renders a TEI document with CETEIcean; styles in `tei.css` | `url` | CETEIcean | Full text tab |
| [`Years`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/components/Years/Years.tsx) | years written, premiered and printed | `written`, `premiere`, `print`, labels | Font Awesome | corpus page, play header |
| [`utils`](https://github.com/dracor-org/dracor-react/blob/1.11.0/src/utils.ts) | `formatYear`, `formatEra`: render the API's year values (ranges, BCE, `>YYYY` "not before", `<YYYY` "not after", ISO dates) | | | corpus page |

The component tables in this draft follow the 1.11.0 sources. For the current props, the Storybook is authoritative (#22: link the generated documentation instead of restating it). This section should therefore stay at the level of "which component does what, and where DraCor uses it".

(dracor-frontend-siblings)=
## Sibling front ends

DraCor's front end is not the only one built this way. Several corpus browsers with a DraCor-like interface share their look and, increasingly, their code through `@dracor/react`. None of them is a fork of dracor-frontend: they share no Git history with it.

| Front end | Site | Started | Stack today | `@dracor/react` (resolved) | From the library |
|---|---|---|---|---|---|
| [dracor-frontend](https://github.com/dracor-org/dracor-frontend) | dracor.org | 2017 | Vite, React 19, TanStack Router, Tailwind 4 (since 3.0) | 1.11.0 (3.0.0-rc.1) | all components (see above) |
| [einakter](https://github.com/dracor-org/einakter) | einakter.dracor.org | 2020 | Vite, React 19, TanStack Router, Tailwind 4 | ^1.4.0 (1.4.0) | `NavBar`, `LanguageMenu`, `Table`, `IdLink`, `IdCopy`, `AuthorInfo`, `Authors`, `Years`, `formatEra` (since 2026-08) |
| [ezlinavis](https://github.com/dracor-org/ezlinavis) | ezlinavis.dracor.org | 2017 | Vite, React 19, Tailwind 4 | ^1.2.1 (1.2.1) | `DownloadButton` |
| [poecor-frontend](https://github.com/dracor-org/poecor-frontend) (archived) | poecor.org (offline) | Dec. 2022 | Create React App, React 18, React Router 6, Tailwind 3 | none (predates it) | none |
| [ecocor-frontend](https://github.com/EcoCor/ecocor-frontend) | ecocor.org | Dec. 2022 (from PoeCor) | Vite, React 19, TanStack Router, Tailwind 4 | ^1.2.1 (1.2.1) | `NavBar`, `Table`, `Tabs`, `TEIText`, `DocPage`, `ApiDoc`, `DownloadButton`, `AuthorInfo`, `IdCopy`, `IdLink`, `Commit` |
| [eltec-frontend](https://github.com/clscor-io/eltec-frontend) | eltec.clscor.io | May 2025 | Vite, React 19, TanStack Router, Tailwind 4 | ^1.1.0 (1.1.0) | `NavBar`, `Table`, `Tabs`, `TEIText`, `DocPage`, `ApiDoc`, `DownloadButton`, `AuthorInfo`, `IdCopy`, `IdLink`, `Commit` |

<!-- "Started" = first commit of the repo. Resolved versions from pnpm-lock.yaml on main (2026-11-20). -->

How the code travelled:

1. **Einakter → PoeCor (2022).** poecor-frontend was set up as a new Create React App project in December 2022, not copied from dracor-frontend. It used Tailwind like Einakter (and Einakter's background image) and DraCor's page structure (corpus cards → table of texts → single text). Its own `CorpusCard`, `Table` (TanStack Table) and `DebouncedInput` are the earliest versions of components that later went into the library.
2. **PoeCor → EcoCor (2023).** ecocor-frontend starts from the same initial commit as poecor-frontend and repeats its first commits (with "poems" renamed to "works", later "texts"). It then grew its own views: entities, animals and plants, word clouds.
3. **The library (June 2023).** `@dracor/react` (first published as `@dracor.org/react`) was started in June 2023, with Einakter's top navigation as the model for `NavBar` and Einakter's Tailwind base. EcoCor used it from July 2023, `Table`/`DebouncedInput` arrived in September 2023.
4. **ELTeC (2025/26).** eltec-frontend was set up from scratch with Vite and TanStack Router in May 2025 and switched to the library in February 2026. Its text view (`Full text`, `Downloads`, `Tools` tabs) follows the DraCor play view, and its `Tools.tsx` is a copy of dracor-frontend's `ToolsTab.tsx` (it still says "DraCor API").
5. **Back into DraCor (2026).** Components first written for the siblings returned to dracor.org with 3.0. The generic `CorpusCard` (1.3.0, July 2026) was added "so eltec-frontend and ecocor-frontend can drop their near-duplicate local implementations". Both still have their own `CorpusCard.tsx` and pin older library versions, so that step is still open.

So the components move in both directions. Something is written for one project, proves itself, moves into `@dracor/react`, and then the other projects pick it up when they upgrade.

(dracor-frontend-poecor-example)=
## Example: a PoeCor front end with `@dracor/react` in 2026

PoeCor (D7.1 §6.2) showed that the DraCor approach carries over to poetry. Its front end listed the corpora, the poems of a corpus and, for a single poem, its metadata and POSTDATA's analysis results. This section shows how that front end would be built today, as an example of adapting DraCor's front end to a different kind of corpus. It is a sketch, not a tutorial. The code has not been run.

### General approach

1. **Start a new app, don't fork.** Create a Vite + React + TypeScript project and add TanStack Router (file-based routes) and Tailwind 4, like the sibling projects. Forking dracor-frontend would bring in everything drama-specific (networks, speech distribution, segments).
2. **Install `@dracor/react` and only the peers you need.** For the example: `@tanstack/react-router`, `@tanstack/react-table`, Font Awesome, CETEIcean only if there is TEI to render. Import `@dracor/react/dracor.css` and add the `@source` line (see [above](#dracor-frontend)).
3. **Write a typed API layer** like dracor-frontend's `src/loaders.ts`: one function per endpoint, called from route loaders. The types describe your API (`Poem`, `CorpusMetrics`), not DraCor's.
4. **Use the generic components and leave the DraCor-specific ones.** `CorpusCard` instead of `DracorCorpusCard` (which expects plays and characters), `Table`, `Tabs`, `NavBar`, `DocPage`, `ApiDoc`, `IdCopy`/`IdLink`.
5. **Write the domain views yourself.** For PoeCor, the analysis of a poem (stanzas, rhyme schemes, metrical patterns) has no counterpart in DraCor.
6. **Mock the API during development** with a mock service worker, as poecor-frontend and ecocor-frontend do (`VITE_MOCK_API`). This lets the front end be developed before the API exists.

### What replaces what

| poecor-frontend (2022) | 2026 with `@dracor/react` |
|---|---|
| `App.tsx` with `<Routes>` (React Router 6) | route files: `routes/index.tsx`, `routes/corpora/index.tsx`, `routes/corpora/$corpusId/index.tsx`, `routes/corpora/$corpusId/$poemId/…` |
| `useEffect` + `useState` + axios in every page, `alert()` on errors | route loaders calling `fetch` helpers; the router shows loading and error states |
| `Topnav.tsx` (title, version, GitHub icon) | `NavBar` with `title`, `version`, `gitHubUrl`, `navItems` |
| `CorpusCard.tsx` with its own `CorpusCardRow` | `CorpusCard` + `CorpusCardRow` (same row layout: they descend from this file) |
| `Table.tsx`, `DebouncedInput.tsx` | `Table` (includes the debounced filter) |
| `Poem.tsx`: one long page | a poem route with `Tabs` (e.g. "Analysis", "Downloads") and child routes |
| poem ID as plain text | `IdCopy` (copy button for the ID / URI) |
| no documentation pages | `DocPage` for Markdown pages, `ApiDoc` for the PoeCor API's OpenAPI spec |
| `react-helmet-async` for the page title | a `<title>` element in the component (React 19) |

### Three examples

The corpus card, with PoeCor's metrics as rows:

```tsx
// routes/corpora/index.tsx (excerpt)
import CorpusCard, {CorpusCardRow} from '@dracor/react/CorpusCard';

<CorpusCard title={corpus.title} to={`/corpora/${corpus.name}`}>
  <CorpusCardRow label="Poems" value={corpus.metrics.poems} valueClassName="text-2xl" />
  <CorpusCardRow label="Authors" value={corpus.metrics.authors} />
  <CorpusCardRow label="Stanzas" value={corpus.metrics.stanzas} />
  <CorpusCardRow label="Verses" value={corpus.metrics.verses} />
  <CorpusCardRow label="Words" value={corpus.metrics.words} />
</CorpusCard>
```

The list of poems: a loader fetches the corpus, `Table` renders it.

```tsx
// routes/corpora/$corpusId/index.tsx
import {createFileRoute, Link} from '@tanstack/react-router';
import type {ColumnDef} from '@tanstack/react-table';
import Table from '@dracor/react/Table';
import {fetchCorpus} from '../../../loaders';
import type {Poem} from '../../../types';

export const Route = createFileRoute('/corpora/$corpusId/')({
  loader: ({params}) => fetchCorpus(params.corpusId),
  component: CorpusPage,
});

const columns: ColumnDef<Poem>[] = [
  {
    accessorKey: 'title',
    header: 'Title',
    cell: ({row}) => <Link to="./$poemId" params={{poemId: row.original.name}}>{row.original.title}</Link>,
  },
  {
    id: 'authors',
    header: 'Author',
    accessorFn: (p) => p.authors.map((a) => a.name).join(', '),
  },
  {accessorKey: 'source', header: 'Source'},
];

function CorpusPage() {
  const corpus = Route.useLoaderData();
  return (
    <section>
      <title>{`${corpus.title} - PoeCor`}</title>
      <h1>{corpus.title}</h1>
      <Table data={corpus.poems} columns={columns} defaultSort={[{id: 'title', desc: false}]} />
    </section>
  );
}
```

The poem view as tabs, the way eltec-frontend builds its text view:

```tsx
// components/PoemView.tsx (excerpt)
import {Outlet} from '@tanstack/react-router';
import IdCopy from '@dracor/react/IdCopy';
import Tabs from '@dracor/react/Tabs';

<h2>{poem.authors.map((a) => a.name).join(', ')}</h2>
<h1>{poem.title}</h1>
<IdCopy uri={poem.uri}>{poem.id}</IdCopy>
<Tabs data={[{label: 'Analysis', to: '../analysis'}, {label: 'Downloads', to: '../downloads'}]} />
<Outlet />
```

What the library does not cover for PoeCor: the analysis tables (PoeCor-specific), and the poem text itself. POSTDATA stores the text as literals in the triple store, not as TEI, so `TEIText` does not apply and the text view would be a small custom component. Charts (e.g. metrical patterns per stanza) would use Recharts directly, as dracor-frontend does.

(dracor-frontend-config)=
## Configuration and deployment

The front end is configured at build time through Vite environment variables ([`src/config.ts`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/config.ts)):

| Variable | Effect | On dracor.org |
|---|---|---|
| `VITE_DRACOR_API` | base URL of the API; unset means relative `/api/v1` | unset (nginx proxy) |
| `VITE_SITEMAP_URL` | JSON file with the menu; otherwise the bundled [`src/sitemap.ts`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/sitemap.ts) | `/doc/sitemap.json` (from dracor-docs) |
| `VITE_DRACOR_GUIDELINES` | URL of the ODD (encoding guidelines) | `/odd.html` |
| `VITE_DRACOR_LEGACY_API` | mounts `/doc/legacy/api` for a second API spec | `/api/v0` |
| `VITE_SPARQL_URL`, `VITE_WITH_SPARQL` | SPARQL endpoint and switch for the YASGUI page | |
| `VITE_EZLINAVIS_URL` | link to ezlinavis in the menu | |
| `VITE_WITH_RAHTZ_PRIZE` | shows the Rahtz Prize badge | `yes` |
| `VITE_VERSION` | version shown in the navigation bar, set by [`version.sh`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/version.sh) (`git describe`) | |

The Docker image ([`Dockerfile`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/Dockerfile), [`nginx.conf`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/nginx.conf)) serves the build with nginx and proxies `/api/v1` to the API. It is configured at run time:

- `DRACOR_API_HOST` (default `https://dracor.org`);
- `DRACOR_API_PREFIX` (default `/api/v1`; e.g. `/exist/restxq/v1` for a bare eXist-db);
- `NGINX_RESOLVER`.

The published image can therefore be pointed at any API instance, for example staging:

```sh
docker run -it --rm -p 8088:8080 -e DRACOR_API_HOST=https://staging.dracor.org dracor/frontend
```

The GitHub workflows deploy as follows:

- **staging:** every push to `main` and every published release, including pre-releases. This is why staging runs 3.0.0-rc.1.
- **production:** full releases only.
- **dev:** on demand.

All three use the shared workflow `deployment.yml`, which syncs the build to the web server. It leaves untouched the files that other repositories deploy to the same server:

- the website documents in `/doc/` (`*.md`, `sitemap.json`), from [dracor-docs](https://github.com/dracor-org/dracor-docs);
- the ODD (`odd*.html`) and the schema files (`schema.rng`, `dracor.sch`).

<!-- assumption: dracor-docs deploys /doc/ itself (not verified) -->

Before November 2025 the documents lived in `public/doc/` of the front-end repository (commit [047250f](https://github.com/dracor-org/dracor-frontend/commit/047250f2b92fd40e8854d6039355b5194ca6f801)).

## Development

```sh
pnpm install
pnpm start                                         # http://localhost:5173, API proxied to localhost:8080
VITE_DRACOR_API=https://dracor.org/api/v1 pnpm start   # against a remote API
pnpm test                                          # Vitest
pnpm lint
pnpm build                                         # → build/
```

Tests run against mocked API responses (MSW handlers and fixtures in [`src/mocks/`](https://github.com/dracor-org/dracor-frontend/tree/3.0.0-rc.1/src/mocks)). Unmocked requests fail the test. Route-level tests mount the real route tree with `renderRoute(path)` from [`src/testUtils.tsx`](https://github.com/dracor-org/dracor-frontend/blob/3.0.0-rc.1/src/testUtils.tsx). CI runs lint, the type check, the tests and a production build for every pull request.

To develop a component of `@dracor/react` together with the front end, build the library, pack it with `pnpm pack`, and install the `.tgz` in the front end (see the [dracor-react README](https://github.com/dracor-org/dracor-react#local-testing)).

## From D7.1 §5.6 to front end 3

Where the components described in D7.1 are now. The link-by-link mapping of all 97 front-end code references in D7.1 is in [`coderefs/code-links.csv`](../coderefs/code-links.csv) (branch `coderefs-1.5`, not pushed yet).

| D7.1 | Then (2.x, `.js`) | Now (3.0.0-rc.1) |
|---|---|---|
| §5.6 header and menu | `TopNav.js` | `TopNav.tsx` → `NavBar` (`@dracor/react`); menu from `sitemap.json` (dracor-docs) |
| §5.6.1 list of corpora | `Home.js`, `CorpusCard` | `routes/index.tsx` → `DracorCorpusCard` (`@dracor/react`) |
| §5.6.2 corpus page | `Corpus.js`, `CorpusIndex.js` | `Corpus.tsx`, `CorpusIndex.tsx` → `Table` (`@dracor/react`, TanStack Table) |
| §5.6.3 play view | `Play.js`, `PlayDetailsHeader.js`, `AuthorInfo.js` | `Play.tsx`, `PlayDetailsHeader.tsx`, `AuthorInfo` (`@dracor/react`) with the API's Wikidata proxy |
| §5.6.3.1 Network | `NetworkGraph.js` (react-sigma 1), `network.js` | `NetworkGraph.tsx` (sigma 4, rewritten), `network.ts` (`getCooccurrences`, `makeGraph` still close to the old code) |
| §5.6.3.2 Relations | `RelationsGraph.js` | `RelationsGraph.tsx` (rewritten) |
| §5.6.3.3 Speech distribution | `SpeechDistribution.js`, `Sapogov.js`, `Yarkho.js`, `TrilckeFischer.js` | the same names as `.tsx`; Sapogov and Yarkho largely rewritten (Recharts only), TrilckeFischer nearly unchanged |
| §5.6.3.4 Full text | CETEIcean in the front end | `TEIPanel.tsx` → `TEIText` (`@dracor/react`) |
| §5.6.3.5 Downloads | `DownloadLinks.js` | `DownloadLinks.tsx` → `DownloadButton` (`@dracor/react`); external tools moved to a new "Tools" tab |
| Tab. 06 | endpoints × components | [this page](#dracor-frontend-endpoints) |
| play tabs as `#hash` | | path segments, old hashes redirected |

## Open questions

<!-- for Ingo / Carsten, not for publication -->

1. **Scope.** Should this page sit in the 2.0.0 documentation (#9/#11) or become a 1.x appendix to D7.1 §5.6? Should D7.1 §5.6 then get a short "Update" box pointing here (cf. #19)?
2. **Release.** All facts are from 3.0.0-rc.1. When 3.0.0 is out: repin the links, recheck the routes and env variables, and update the Swagger deep links (#14).
3. **Tab workaround.** `PlayDetailsNav.tsx` still works around `Tabs` dropping `params`. The fix (dracor-react#87) was merged on 2026-09-12 and is in 1.11.0, so the workaround can probably go. Ask Carsten whether that is intended.
4. **Repo CLAUDE.md.** The front end's `CLAUDE.md` mentions chart.js next to Recharts for the speech distribution, but only Recharts is a dependency. It also says the docs are in `public/doc/`, but they are in dracor-docs. Small things to mention to Carsten.
5. **Unused endpoints.** `/dts/*`, `/characters`, `/character/{id}` and `/wikidata/mixnmatch` are not used by the website. Is that worth a sentence ("the API offers more than the website shows"), with a pointer to the notebooks or the textbook?
6. **Legacy API docs.** `/doc/legacy/api` (v0) will go away with the v0 shutdown (#15).
7. **Generate instead of write.** The routes table and the endpoint table can be generated from the code (route files, `loaders.ts`, `DownloadLinks.tsx`, `ToolsTab.tsx`), like `coderefs/`. That would make this page cheap to keep current (#22, #23).
8. **D7.1 §6.2 wording.** D7.1 says the PoeCor front end "was built based on the DraCor front-end". The code shows a new project in the DraCor style (corpus cards → table → text view) that shares no code with dracor-frontend. Is that worth an Update box in §6.2, pointing to the [sibling section](#dracor-frontend-siblings)?
9. **Siblings and their version pins.** ELTeC (1.1.0) and EcoCor (1.2.1) predate the generic `CorpusCard` (1.3.0) and Scalar in `ApiDoc` (1.5.0) and still use their own card. Is the migration planned (Carsten)? And should EcoCor and ELTeC appear in the DraCor documentation at all, or only as "other projects using `@dracor/react`"?
10. **Screenshots** for the home page section (and possibly the siblings: one card each from dracor.org, ecocor.org, eltec.clscor.io).
