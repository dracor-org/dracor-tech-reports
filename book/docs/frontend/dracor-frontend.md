---
title: The DraCor front end
subtitle: dracor-frontend 3 and the DraCor React component library
short_title: Frontend
label: dracor-frontend
---

:::{note} Draft
:class: editorial
This page describes the front end as of **dracor-frontend 3.0.0-rc.1** (release candidate, 31 October 2026, running on [staging.dracor.org](https://staging.dracor.org)) and **`@dracor/react` 1.11.0**. It updates the description in [D7.1 §5.6](#clsinfra-d71-5-6), which documents front end 1.x (JavaScript; 1.5.0, November 2022). For a guided tour of the website from a user's point of view, see [DraCor Textbook, ch. 4](https://textbook.dracor.org/chapters/04-front-end-navigating-dracor.html).
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
| Language | JavaScript, first TypeScript types | JavaScript and TypeScript (23 `.js`, 32 `.ts`/`.tsx` files) | TypeScript; shared types in [`src/types.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/types.ts#L1-L117) |
| Build and tests | Create React App 4, Jest | Vite, Vitest | Vite, Vitest, Testing Library, [MSW](https://mswjs.io) |
| React | 17 | 18 | 19 |
| Routing | React Router 5; play tabs as URL hash (`#network`) | React Router 6; hash tabs | [TanStack Router](https://tanstack.com/router), file-based; tabs are path segments (`/ger/lessing-emilia-galotti/network`) |
| Data loading | `fetch*` functions inside components | inside components | route loaders calling [`src/loaders.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/loaders.ts#L1-L156) |
| Styling | Bootstrap 4, reactstrap, SCSS | Bootstrap 4, reactstrap | [Tailwind CSS](https://tailwindcss.com) 4 with the DraCor theme from `@dracor/react` |
| Network graphs | react-sigma 1 (sigma.js 1) | react-sigma 1 | [sigma](https://www.sigmajs.org) 4 and [graphology](https://graphology.github.io) through `@react-sigma/core`; ForceAtlas2 layout in a web worker |
| Charts | Chart.js 2 (react-chartjs-2), Recharts 1 | Chart.js 2, Recharts 3 | [Recharts](https://recharts.org) 3 only |
| API documentation | Swagger UI (`swagger-ui-react`) | Swagger UI | [Scalar](https://scalar.com) (component `ApiDoc`); Swagger UI remains at [swagger.dracor.org](https://swagger.dracor.org) |
| Shared components | none | none | `@dracor/react` |

## Pages and routes

Routes are files under [`src/routes/`](https://github.com/dracor-org/dracor-frontend/tree/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes), and [`src/routeTree.gen.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routeTree.gen.ts#L1-L280) is generated from them. There is no `App` component: [`src/index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/index.tsx#L1-L25) mounts the router directly.

| URL | Route file | Loader (API calls) | Main components |
|---|---|---|---|
| *(every page)* | [`__root.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/__root.tsx#L1-L59) | `GET /info`, `GET /corpora`; the menu from `VITE_SITEMAP_URL` (on dracor.org: `/doc/sitemap.json`) | `TopNav` (→ `NavBar`), `RouteProgress`, `DracorContext` |
| `/` | [`index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/index.tsx#L1-L155) | `GET /corpora?include=metrics` | [`CorporaIntro`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/CorporaIntro.tsx#L36-L100), `DracorCorpusCard` |
| `/{corpus}` | [`$corpusId/index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/$corpusId/index.tsx#L1-L35) | `GET /corpora/{corpus}` | `Corpus`, `CorpusIndex` (→ `Table`, `IdLink`, `Years`, `Commit`) |
| `/{corpus}/{play}` | [`$corpusId/$playId/route.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/$corpusId/$playId/route.tsx#L1-L30) + [`index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/$corpusId/$playId/index.tsx#L1-L15) | `GET /corpora/{corpus}/plays/{play}`, `GET …/metrics` (optional) | `Play`, `PlayDetailsHeader` (→ `AuthorInfo`, `IdCopy`, `IdLink`, `Years`), `PlayDetailsNav` (→ `Tabs`) |
| `/{corpus}/{play}/{tab}` | [`$corpusId/$playId/$tab.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/$corpusId/$playId/$tab.tsx#L1-L36) | (the parent's data) | one of the six tabs, see below. An unknown tab redirects to `network`. |
| `/doc/api` | [`doc/api.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/doc/api.tsx#L1-L52) | `GET /openapi.yaml` (fetched by Scalar) | `ApiDoc`, lazy-loaded (~2 MB) |
| `/doc/legacy/api` | [`doc/legacy.api.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/doc/legacy.api.tsx#L1-L53) | the spec of the legacy API (on dracor.org `VITE_DRACOR_LEGACY_API=/api/v0`) | `ApiDoc` |
| `/doc/odd` | [`doc/odd.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/doc/odd.tsx#L1-L6) | the encoding guidelines from `VITE_DRACOR_GUIDELINES` (on dracor.org `/odd.html`) | `OddPage`, `Odd` |
| `/doc/corpora` | [`doc/corpora.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/doc/corpora.tsx#L1-L6) | none: the registry is bundled from the npm package [`@dracor/registry`](https://github.com/dracor-org/dracor-registry) | `CorpusRegistry` |
| `/doc/{slug}` | [`doc/$slug.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/doc/$slug.tsx#L1-L25) | `/doc/{slug}.md` (served from [dracor-docs](https://github.com/dracor-org/dracor-docs) since November 2025) | `DocPage` |
| `/sparql` | [`sparql.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/sparql.tsx#L1-L21) | none | `SparqlUi` (YASGUI, only with `VITE_WITH_SPARQL=yes`), otherwise `SparqlPlaceholder` |

DraCor IDs are resolved on the server: `https://dracor.org/id/ger000088` answers with a 303 redirect to the play page. In 2.x the front end resolved them itself (D7.1, Tab. 06, row `/id/{id}`).

Old play URLs with a tab in the hash (`/ger/lessing-emilia-galotti#network`) are rewritten to the new path form once, on the first page load ([`src/hashRedirect.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/hashRedirect.ts#L1-L28)). Links in the reports that use the hash form therefore keep working.

(dracor-frontend-menu)=
## Menu and footer

Every page has the top navigation ([`TopNav.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/TopNav.tsx#L90-L114) → `NavBar` from `@dracor/react`) and the footer ([`Footer.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/Footer.tsx#L15-L135)).

**The menu is no longer part of the front-end code.** It is read from a site map ([`sitemap.json`](https://staging.dracor.org/doc/sitemap.json), from `VITE_SITEMAP_URL`), which lives in dracor-docs together with the documentation pages. Only the "Corpora" drop-down is filled by the front end itself, from `/corpora`. Changing the menu therefore means editing dracor-docs, not releasing a new front end. On staging (2026-11-21) the menu has:

| Menu | Items |
|---|---|
| About | What Is DraCor?, Corpus Registry, Credits, Get in Touch, DraCor Moments, DraCor Summit 2025, Merch, Media Kit, Imprint |
| Corpora | one entry per corpus (from the API) |
| Documentation | API, API v0 (legacy), Encoding Guidelines (ODD), FAQs, Tutorials, DraCor Textbook |
| Tools | pydracor, rdracor, SPARQL, ezlinavis |
| Research | Research Bibliography, Posters, Card Games, DraCor in Science Communication |

Compared with D7.1 (Fig. 11): "How To" has become "Documentation" and "Research"; the API documentation moved from "Tools" to "Documentation" (and is rendered with Scalar instead of Swagger UI); Shiny DraCor is no longer in the menu, the API libraries are. A "Rahtz Prize 2022" badge can be switched on with `VITE_WITH_RAHTZ_PRIZE=yes`.

**The footer** has, as in D7.1, how to cite DraCor (BibTeX and RIS downloads and the DH2019 paper, [doi:10.5281/zenodo.4284002](https://doi.org/10.5281/zenodo.4284002)), the licence of the data (CC0), and version information from `/info`. The versions are now shown as small "pills": the front end (linked to its GitHub release), the API (linked to its release) and eXist-db.

:::{note} Screenshots needed
The open "About" menu and the footer, 2.7.2 and 3.0 (cf. D7.1 Fig. 11 and 12).
:::

(dracor-frontend-home)=
## The home page

The home page lists the published corpora as corpus cards. The way they are shown changed with 3.0.

**From July 2020 up to 2.7.2**, and so also at the time of D7.1 (its Fig. 13, "DraCor landing page"), the cards sat in a carousel ([`Corpora.jsx`](https://github.com/dracor-org/dracor-frontend/blob/a805ab275dd7c1ba911cf4591a3d8ef4dcad0bdb/src/components/Corpora.jsx#L75-L118), built with `react-slick`). Depending on the screen width it showed up to seven cards side by side, with arrows and dots to move through the corpora. On small screens it scrolled by itself, and below 767 px it became a plain list. The cards were sorted by number of plays.

**Since 3.0** ([`src/routes/index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/index.tsx#L1-L155)) there is no carousel. Commit [9d8ce68](https://github.com/dracor-org/dracor-frontend/commit/9d8ce68fe13927ccd149cb4a61395c25332bd270) removed `react-slick` along with swagger-ui. The page now has:

- **A grid of cards.** All corpora are visible at once, wrapping to as many columns as fit (one per row on phones). Each card is a `DracorCorpusCard` from `@dracor/react` and shows plays, characters by sex, word tokens and the last update. A link to the Git commit of the corpus version is included as well.
- **Sort buttons** above the grid: by number of plays (default), by name A–Z (using the acronym without "DraCor", i.e. what the card shows) or by last update. The choice is kept in the URL (`/?sort=name`, `/?sort=updated`), so a sorted view can be linked.
- **An introductory line** ([`CorporaIntro`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/CorporaIntro.tsx#L36-L100)) above the cards that points to the [research bibliography](https://dracor.org/doc/research) and counts its entries since 2024. It only appears on deployments whose site menu links `/doc/research`.
- **A clear message if the API is down** ("Could not load the corpus list …") instead of an empty or broken page.

:::{note} Screenshots needed
Fig. A: dracor.org home page with the carousel (front end 2.7.2, e.g. from the Internet Archive or a local 2.7.2 build).

Fig. B: the same page in 3.0 (staging.dracor.org), wide screen, default order.

Optional Fig. C: phone width, to show that the cards stack.

D7.1 Fig. 13 shows the carousel version; a caption could make the comparison explicit.
:::

(dracor-frontend-corpus)=
## The corpus page

Selecting a corpus (`/{corpus}`, e.g. [`/tat`](https://staging.dracor.org/tat)) shows its contents. The route loads `/corpora/{corpus}` and renders it with [`Corpus.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/Corpus.tsx#L11-L28) and [`CorpusIndex.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/CorpusIndex.tsx#L230-L288). An unknown corpus name now gives a "No such corpus" page (the API's 404 is turned into the router's not-found state).

From top to bottom, the page has:

1. **A corpus label** ([`CorpusLabel`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/CorpusLabel.tsx#L9-L29), new in 3.0): the corpus acronym as a small badge ("Tat DraCor") on the dark band below the menu, linking back to the corpus. The play pages show the same label.
2. **The title**, then **the description** from `corpus.xml` (rendered from Markdown), **the licence** of the corpus with a link, and **the Git commit** of the corpus version the API serves (`Commit`, linked to the repository; added in 2.3.0, June 2024).
3. **The two metadata downloads**, JSON and CSV, linking to `/corpora/{corpus}/metadata` and `/corpora/{corpus}/metadata/csv`, as in D7.1 Fig. 15.
4. **The table of plays** (`Table` from `@dracor/react`), sorted by normalized year, with a search field and these columns:

| Column | Shows | The search also finds (not visible in the cell) |
|---|---|---|
| Authors | names, Wikidata links (`IdLink`), translators as "transl. …" (since 2.7.0, July 2026) | author IDs (Wikidata etc.), alternative names (`alsoKnownAs`), translator names |
| Title | title (linked to the play), subtitle, Wikidata link of the play | the Wikidata ID |
| Year (normalized) | the normalized year, below it written / premiered / printed (`Years`); the info icon links to the FAQ entry on the normalized year | all four years |
| Network Size | number of characters in the network | |
| Source | the digital source (linked), and the "TEI version" link to `/corpora/{corpus}/plays/{play}/tei` | the source name |
| ID | the DraCor ID | |

What changed since D7.1 (front end 1.5.0, November 2022): the content of the page is largely the same. New are the Git commit of the corpus version (2.3.0), the translators (2.7.0) and the corpus label (3.0). In 3.0 the table is no longer `react-bootstrap-table-next` but the library's `Table` (TanStack Table), and the TEI link uses the plural path `/plays/` of API v1.
:::{note} Screenshots needed
The TatDraCor corpus page in 3.0, as in D7.1 Fig. 14, and the download links (Fig. 15). A larger corpus (e.g. GerDraCor) with a search term entered would show the filter.
:::

## Data flow

All API calls go through a few helpers in [`src/loaders.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/loaders.ts#L1-L156):

- [`apiGet`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/loaders.ts#L15-L26) sets `Accept: application/json` and throws an `ApiError` carrying the HTTP status.
- [`isNotFound`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/loaders.ts#L28-L30) lets routes turn a 404 into the "not found" page.

Route loaders call these helpers before a page renders, and components read the result with `Route.useLoaderData()`. The two calls every page needs (`/info` and `/corpora`) are made once by the root route and shared through a React context ([`src/context.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/context.ts#L1-L6)). A failing `/info` or `/corpora` does not break the site: the root loader catches the error, and the home page shows that the API is unavailable.

The base URL of the API is `VITE_DRACOR_API` or, if that is unset, the relative path `/api/v1` ([`src/config.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/config.ts#L1-L11)). In development Vite proxies `/api/v1` to a local API. In the Docker image nginx proxies it to `DRACOR_API_HOST` (see [Configuration and deployment](#dracor-frontend-config)). The same build can therefore run against dev, staging, production or a local API.

Several things are computed in the browser and not fetched as ready-made data:

- **Co-presence network:** [`src/network.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/network.ts#L1-L77) builds the graph from the `segments` of the play info ([`getCooccurrences`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/network.ts#L27-L53), [`makeGraph`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/network.ts#L58-L77)). It does not use the `/networkdata/*` endpoints, which are only offered as downloads.
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

The external tools on the "Tools" tab are [Voyant Tools](https://voyant-tools.org), the [CLARIN Language Resource Switchboard](https://switchboard.clarin.eu) and [Gephi Lite](https://gephi.org/gephi-lite/). They load the data directly from the API, so the tab only offers them when the API is publicly reachable (its host name contains `dracor.org`).

## The play view

The play view is the centre of the website. [`Play.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/Play.tsx#L51-L184) renders the header and the tab bar for all tabs. Each tab is a URL of its own (`/{corpus}/{play}/{tab}`), so tabs can be linked and bookmarked.

| Tab | Path | Content | Components (dracor-frontend unless noted) | D7.1 |
|---|---|---|---|---|
| Network | `network` (default) | co-presence network, cast list, network metrics | [`NetworkGraph`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/NetworkGraph.tsx#L95-L141) (lazy, sigma), [`CastList`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/CastList.tsx#L9-L66), [`PlayMetrics`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/PlayMetrics.tsx#L12-L66) | §5.6.3.1 |
| Relations | `relations` | kinship and other relations ([Wiedmer, Pagel, Reiter 2020](https://doi.org/10.5281/zenodo.4621778)); falls back to Network if the play has none | [`RelationsGraph`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/RelationsGraph.tsx#L83-L144) (lazy, sigma), [`CastList`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/CastList.tsx#L9-L66) | §5.6.3.2 |
| Speech distribution | `speech` | three chart types: Sapogov (default), Yarkho, Trilcke/Fischer | [`SpeechDistribution`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/SpeechDistribution.tsx#L86-L103), [`SpeechDistribution/`](https://github.com/dracor-org/dracor-frontend/tree/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/SpeechDistribution) [`Sapogov`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/SpeechDistribution/Sapogov.tsx#L26-L85), [`Yarkho`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/SpeechDistribution/Yarkho.tsx#L26-L117), [`TrilckeFischer`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/SpeechDistribution/TrilckeFischer.tsx#L41-L102) (Recharts) | §5.6.3.3 and excursus |
| Full text | `text` | the TEI rendered in the browser, source information, segment tree | [`TEIPanel`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/TEIPanel.tsx#L8-L16) → `TEIText` (`@dracor/react`, [CETEIcean](https://github.com/TEIC/CETEIcean)), [`SourceInfo`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/SourceInfo.tsx#L9-L33), [`Segments`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/Segments.tsx#L62-L83) | §5.6.3.4 |
| Downloads | `downloads` | download buttons for all data layers | [`DownloadLinks`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/DownloadLinks.tsx#L5-L132) → `DownloadButton` (`@dracor/react`) | §5.6.3.5 |
| Tools | `tools` | sends a text layer or the network to external tools | [`ToolsTab`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/ToolsTab.tsx#L33-L123) | new in 3.0 (2.x: links on the Downloads tab) |

The header ([`PlayDetailsHeader.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/PlayDetailsHeader.tsx#L24-L187)) shows the following:

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

The colours and type of the theme are shown on the Storybook's [Theme](https://dracor-org.github.io/dracor-react/?path=/docs/theme--docs) page.

The library is built one file per component, and every component also has its own subpath export (`import IdCopy from '@dracor/react/IdCopy'`). Unused components are therefore dropped from a bundle. dracor-frontend imports all components through subpaths. `react` and `react-dom` (19) are the only required peer dependencies. Everything else is an optional peer that only needs to be installed for the components that use it.

| Component | Purpose | Key props | Optional peers | Used in dracor-frontend | Storybook |
|---|---|---|---|---|---|
| [`ApiDoc`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/ApiDoc/ApiDoc.tsx#L139-L238) | renders an OpenAPI spec with Scalar; DraCor defaults (classic layout, no sidebar, no Scalar client/MCP/agent buttons); optional switch between the modern and classic layouts | `url`, `title`, `configuration`, `layoutSwitch`, `hidePoweredBy`, `plainVersion` | `@scalar/api-reference-react` | `/doc/api`, `/doc/legacy/api` | [Pages/ApiDoc](https://dracor-org.github.io/dracor-react/?path=/docs/pages-apidoc--docs) |
| [`AuthorInfo`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/AuthorInfo/AuthorInfo.tsx#L45-L150) | portrait, name, birth and death from Wikidata | `wikidataId`, `name`, `translator`, `fetcher` (default: [`wikidataSparqlFetcher`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/AuthorInfo/wikidataSparqlFetcher.ts#L24-L46)) | | play header | [Organisms/AuthorInfo](https://dracor-org.github.io/dracor-react/?path=/docs/organisms-authorinfo--docs) |
| [`Authors`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/Authors/Authors.tsx#L13-L33) | list of author names with ID links | `data` | | | [Atoms/Authors](https://dracor-org.github.io/dracor-react/?path=/docs/atoms-authors--docs) |
| [`Commit`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/Commit/Commit.tsx#L9-L29) | short Git commit hash linked to the repository | `repo`, `children` (hash) | Font Awesome | corpus page | [Atoms/Commit](https://dracor-org.github.io/dracor-react/?path=/docs/atoms-commit--docs) |
| [`CorpusCard`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/CorpusCard/CorpusCard.tsx#L67-L109), `CorpusCardRow` | generic corpus card with rows, commit and last update | `title`, `to`, `commit`, `repo`, `updated` | TanStack Router | | [Molecules/CorpusCard](https://dracor-org.github.io/dracor-react/?path=/docs/molecules-corpuscard--docs) |
| [`DracorCorpusCard`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/DracorCorpusCard/DracorCorpusCard.tsx#L32-L144) | the corpus card of the dracor.org home page (plays, characters by sex, tokens in `text`/`sp`/`stage`, last update) | `name`, `title`, `acronym`, `metrics` (from `/corpora?include=metrics`) | TanStack Router | home page | [Molecules/DracorCorpusCard](https://dracor-org.github.io/dracor-react/?path=/docs/molecules-dracorcorpuscard--docs) |
| [`DebouncedInput`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/DebouncedInput/DebouncedInput.tsx#L3-L38) | text input that reports changes after a delay (used for table filters) | `value`, `onChange`, `debounce` | | (inside `Table`) | [Atoms/DebouncedInput](https://dracor-org.github.io/dracor-react/?path=/docs/atoms-debouncedinput--docs) |
| [`DocPage`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/DocPage/DocPage.tsx#L12-L68) | fetches a Markdown file (`text/markdown`) and renders it; the first `#` heading becomes the page title | `url` or `match`, `components`, `rehypePlugins` | | `/doc/{slug}` | [Pages/DocPage](https://dracor-org.github.io/dracor-react/?path=/docs/pages-docpage--docs) |
| [`DownloadButton`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/DownloadButton/DownloadButton.tsx#L41-L87) | download link with a file-type icon (bibtex, csv, gexf, graphml, json, rdf, ris, tei, txt) | `href`, `name`, `type` | | Downloads tab | [Atoms/DownloadButton](https://dracor-org.github.io/dracor-react/?path=/docs/atoms-downloadbutton--docs) |
| [`IdCopy`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/IdCopy/IdCopy.tsx#L17-L46) | an ID with a button that copies its URI | `children`, `prefix`, `uri`, `icon` | Font Awesome | play header | [Atoms/IdCopy](https://dracor-org.github.io/dracor-react/?path=/docs/atoms-idcopy--docs) |
| [`IdLink`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/IdLink/IdLink.tsx#L52-L88) | turns `scheme:id` into a link with an icon; schemes: `wikidata`, `dracor`, `wega`, `isni`, `gnd`/`pnd`, `viaf` | `children`, `showLabel` | | corpus page, play header | [Atoms/IdLink](https://dracor-org.github.io/dracor-react/?path=/docs/atoms-idlink--docs) |
| [`LanguageMenu`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/LanguageMenu/LanguageMenu.tsx#L18-L58) | language switch | `languages`, `current`, `onSelect` | Headless UI, Font Awesome | | [Navigation/LanguageMenu](https://dracor-org.github.io/dracor-react/?path=/docs/navigation-languagemenu--docs) |
| [`NavBar`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/Navigation/NavBar.tsx#L21-L105) (folder `Navigation/`) | top navigation with logo, version, GitHub link, items and drop-down menus | `title`, `logo`, `version`, `gitHubUrl`, `navItems` | TanStack Router, Headless UI, Font Awesome | every page (`TopNav`) | [Navigation/NavBar](https://dracor-org.github.io/dracor-react/?path=/docs/navigation-navbar--docs), [NavItem](https://dracor-org.github.io/dracor-react/?path=/docs/navigation-navitem--docs), [NavMenu](https://dracor-org.github.io/dracor-react/?path=/docs/navigation-navmenu--docs) |
| [`Table`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/Table/Table.tsx#L20-L97) | sortable and filterable table | `data`, `columns`, `defaultSort` | TanStack Table | corpus page (list of plays) | [Organisms/Table](https://dracor-org.github.io/dracor-react/?path=/docs/organisms-table--docs) |
| [`Tabs`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/Tabs/Tabs.tsx#L22-L90) | tab bar whose tabs are router links | `data` (link props + `label`), `wrap` | TanStack Router | play view | [Organisms/Tabs](https://dracor-org.github.io/dracor-react/?path=/docs/organisms-tabs--docs) |
| [`TEIText`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/TEIText/TEIText.tsx#L10-L41) | renders a TEI document with CETEIcean; styles in `tei.css` | `url` | CETEIcean | Full text tab | [Pages/TEIText](https://dracor-org.github.io/dracor-react/?path=/docs/pages-teitext--docs) |
| [`Years`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/components/Years/Years.tsx#L19-L57) | years written, premiered and printed | `written`, `premiere`, `print`, labels | Font Awesome | corpus page, play header | [Atoms/Years](https://dracor-org.github.io/dracor-react/?path=/docs/atoms-years--docs) |
| [`utils`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/src/utils.ts#L1-L69) | `formatYear`, `formatEra`: render the API's year values (ranges, BCE, `>YYYY` "not before", `<YYYY` "not after", ISO dates) | | | corpus page |  |

The component tables in this draft follow the 1.11.0 sources. The Storybook links point to its docs page for each component, with live examples (stories) and a props table. The Storybook always shows the latest release of the library, not 1.11.0. For the current props, the Storybook is authoritative (#22: link the generated documentation instead of restating it). This section should therefore stay at the level of "which component does what, and where DraCor uses it".

The library is also used by the DraCor Spin-offs (EcoCor, ELTeC) and other DraCor tools (Einakter, ezlinavis), see [Building DraCor Spin-offs](#spinoffs).

(dracor-frontend-config)=
## Configuration and deployment

The front end is configured at build time through Vite environment variables ([`src/config.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/config.ts#L1-L11)):

| Variable | Effect | On dracor.org |
|---|---|---|
| `VITE_DRACOR_API` | base URL of the API; unset means relative `/api/v1` | unset (nginx proxy) |
| `VITE_SITEMAP_URL` | JSON file with the menu; otherwise the bundled [`src/sitemap.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/sitemap.ts#L1-L49) | `/doc/sitemap.json` (from dracor-docs) |
| `VITE_DRACOR_GUIDELINES` | URL of the ODD (encoding guidelines) | `/odd.html` |
| `VITE_DRACOR_LEGACY_API` | mounts `/doc/legacy/api` for a second API spec | `/api/v0` |
| `VITE_SPARQL_URL`, `VITE_WITH_SPARQL` | SPARQL endpoint and switch for the YASGUI page | |
| `VITE_EZLINAVIS_URL` | link to ezlinavis in the menu | |
| `VITE_WITH_RAHTZ_PRIZE` | shows the Rahtz Prize badge | `yes` |
| `VITE_VERSION` | version shown in the navigation bar, set by [`version.sh`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/version.sh#L1-L2) (`git describe`) | |

The Docker image ([`Dockerfile`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/Dockerfile#L1-L21), [`nginx.conf`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/nginx.conf#L1-L33)) serves the build with nginx and proxies `/api/v1` to the API. It is configured at run time:

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

Tests run against mocked API responses (MSW handlers and fixtures in [`src/mocks/`](https://github.com/dracor-org/dracor-frontend/tree/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/mocks)). Unmocked requests fail the test. Route-level tests mount the real route tree with `renderRoute(path)` from [`src/testUtils.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/testUtils.tsx#L1-L57). CI runs lint, the type check, the tests and a production build for every pull request.

To develop a component of `@dracor/react` together with the front end, build the library, pack it with `pnpm pack`, and install the `.tgz` in the front end (see the [dracor-react README](https://github.com/dracor-org/dracor-react#local-testing)).

## From D7.1 §5.6 to front end 3

Where the components described in D7.1 are now. The link-by-link mapping of all 97 front-end code references in D7.1 is in [`coderefs/code-links.csv`](https://github.com/dracor-org/dracor-tech-reports/blob/b5b8ffff42100d4a420f6b4499ad29d714119cd8/coderefs/code-links.csv).

| D7.1 | Then (1.5.0, November 2022, `.js`) | Now (3.0.0-rc.1) |
|---|---|---|
| §5.6 header and menu | [`TopNav.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/TopNav.js#L23-L82) | [`TopNav.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/TopNav.tsx#L90-L114) → `NavBar` (`@dracor/react`); menu from `sitemap.json` (dracor-docs) |
| §5.6.1 list of corpora | [`Home.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/Home.js#L6-L15), [`CorpusCard.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/CorpusCard.js#L9-L83) | [`routes/index.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/routes/index.tsx#L1-L155) → `DracorCorpusCard` (`@dracor/react`) |
| §5.6.2 corpus page | [`Corpus.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/Corpus.js#L17-L77), [`CorpusIndex.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/CorpusIndex.js#L127-L279) | [`Corpus.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/Corpus.tsx#L11-L28), [`CorpusIndex.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/CorpusIndex.tsx#L230-L288) → `Table` (`@dracor/react`, TanStack Table) |
| §5.6.3 play view | [`Play.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/Play.js#L1-L202), [`PlayDetailsHeader.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/PlayDetailsHeader.js#L16-L92), [`AuthorInfo.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/AuthorInfo.js#L11-L90) | [`Play.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/Play.tsx#L51-L184), [`PlayDetailsHeader.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/PlayDetailsHeader.tsx#L24-L187), `AuthorInfo` (`@dracor/react`) with the API's Wikidata proxy |
| §5.6.3.1 Network | [`NetworkGraph.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/NetworkGraph.js#L13-L64) (react-sigma 1), [`network.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/network.js#L1-L59) | [`NetworkGraph.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/NetworkGraph.tsx#L95-L141) (sigma 4, rewritten), [`network.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/network.ts#L1-L77) (`getCooccurrences`, `makeGraph` still close to the old code) |
| §5.6.3.2 Relations | [`RelationsGraph.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/RelationsGraph.js#L25-L87) | [`RelationsGraph.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/RelationsGraph.tsx#L83-L144) (rewritten) |
| §5.6.3.3 Speech distribution | [`SpeechDistribution.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/SpeechDistribution.js#L67-L84), [`Sapogov.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/SpeechDistribution/Sapogov.js#L5-L107), [`Yarkho.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/SpeechDistribution/Yarkho.js#L5-L149), [`TrilckeFischer.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/SpeechDistribution/TrilckeFischer.js#L42-L103) | the same names as `.tsx`; Sapogov and Yarkho largely rewritten (Recharts only), TrilckeFischer nearly unchanged |
| §5.6.3.4 Full text | CETEIcean in the front end | [`TEIPanel.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/TEIPanel.tsx#L8-L16) → `TEIText` (`@dracor/react`) |
| §5.6.3.5 Downloads | [`DownloadLinks.js`](https://github.com/dracor-org/dracor-frontend/blob/148756743ee7a26a9556464aed9fc861cfbd8869/src/components/DownloadLinks.js#L18-L154) | [`DownloadLinks.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/DownloadLinks.tsx#L5-L132) → `DownloadButton` (`@dracor/react`); external tools moved to a new "Tools" tab |
| Tab. 06 | endpoints × components | [this page](#dracor-frontend-endpoints) |
| play tabs as `#hash` | | path segments, old hashes redirected |
