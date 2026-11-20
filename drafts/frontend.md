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
