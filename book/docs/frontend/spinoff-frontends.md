---
title: Front ends of the spin-offs
subtitle: PoeCor, EcoCor, ELTeC and the reuse of the DraCor front end
short_title: Spin-off Frontends
label: spinoff-frontends
---

<!--
DRAFT (2026-11-21), split off from drafts/frontend.md at Ingo's request ("Front end > DraCor
front end, and then also Front end of spin-offs"). Facts from the repositories (git history,
package.json, pnpm-lock.yaml on main, 2026-11-20). Code links are permalinks (SHA + lines).
-->

:::{note} Draft
:class: editorial
This page shows how the DraCor front end has been adapted and reused for the DraCor spin-offs, and how such a front end would be built today with `@dracor/react`. The DraCor front end itself is described in [The DraCor front end](#dracor-frontend).
:::

(spinoff-frontends-overview)=
## Spin-offs and other projects using `@dracor/react`

DraCor's front end is not the only one built this way. The DraCor spin-offs, corpus browsers for other kinds of texts (PoeCor for poetry, EcoCor for ecocritically relevant narrative texts, ELTeC for European novels), together with two DraCor tools, Einakter and ezlinavis, share their look and, increasingly, their code through `@dracor/react`. None of them is a fork of dracor-frontend: they share no Git history with it.

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

1. **Einakter → PoeCor (2022).** poecor-frontend was set up as a new Create React App project in December 2022, not copied from dracor-frontend. It used Tailwind like Einakter (and Einakter's background image) and DraCor's page structure (corpus cards → table of texts → single text). Its own [`CorpusCard`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/CorpusCard.tsx#L36-L68), [`Table`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/Table.tsx#L21-L96) (TanStack Table) and [`DebouncedInput`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/DebouncedInput.tsx#L3-L35) are the earliest versions of components that later went into the library.
2. **PoeCor → EcoCor (2023).** ecocor-frontend starts from the same initial commit as poecor-frontend and repeats its first commits (with "poems" renamed to "works", later "texts"). It then grew its own views: entities, animals and plants, word clouds.
3. **The library (June 2023).** `@dracor/react` (first published as `@dracor.org/react`) was started in June 2023, with Einakter's top navigation as the model for `NavBar` and Einakter's Tailwind base. EcoCor used it from July 2023, `Table`/`DebouncedInput` arrived in September 2023.
4. **ELTeC (2025/26).** eltec-frontend was set up from scratch with Vite and TanStack Router in May 2025 and switched to the library in February 2026. Its text view (`Full text`, `Downloads`, `Tools` tabs) follows the DraCor play view, and its [`Tools.tsx`](https://github.com/clscor-io/eltec-frontend/blob/ee13aca9ff56583b4f85ff1c9a8b0572b8b38274/src/components/Tools.tsx#L11-L75) is a copy of dracor-frontend's [`ToolsTab.tsx`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/components/ToolsTab.tsx#L33-L123) (it still says "DraCor API").
5. **Back into DraCor (2026).** Components first written for the siblings returned to dracor.org with 3.0. The generic `CorpusCard` (1.3.0, July 2026, [e2d3e26](https://github.com/dracor-org/dracor-react/commit/e2d3e26ed5d215801725c8220dd0833c28752ee5)) was added "so eltec-frontend and ecocor-frontend can drop their near-duplicate local implementations". Both still have their own `CorpusCard.tsx` ([ELTeC](https://github.com/clscor-io/eltec-frontend/blob/ee13aca9ff56583b4f85ff1c9a8b0572b8b38274/src/components/CorpusCard.tsx#L1-L94), [EcoCor](https://github.com/EcoCor/ecocor-frontend/blob/c515890f85369917ba02b53a85edbe7dc26bef07/src/CorpusCard.tsx#L1-L91)) and pin older library versions, so that step is still open.

So the components move in both directions. Something is written for one project, proves itself, moves into `@dracor/react`, and then the other projects pick it up when they upgrade.

(spinoff-frontends-checklist)=
## Checklist: building a spin-off front end

For people and coding agents starting a new spin-off front end. Details and examples are in the [PoeCor example](#spinoff-frontends-poecor-example) below.

1. **Start from eltec-frontend, not from dracor-frontend.** [eltec-frontend](https://github.com/clscor-io/eltec-frontend/blob/ee13aca9ff56583b4f85ff1c9a8b0572b8b38274/src/loaders.ts#L1-L33) is the newest and smallest spin-off front end (about 650 lines) and already has corpus list, corpus table and a text view with tabs. dracor-frontend carries everything drama-specific (networks, speech distribution, segments).
2. **Stack:** Vite, React 19, TypeScript, TanStack Router (file-based routes, `@tanstack/router-plugin`), Tailwind CSS 4.
3. **Install `@dracor/react` 1.11.0 or later** and only the optional peers of the components you use (see the [component table](#dracor-frontend)): `@tanstack/react-router` (`NavBar`, `Tabs`, `CorpusCard`), `@tanstack/react-table` (`Table`), Font Awesome and Headless UI (`NavBar`, `IdCopy`, `Commit`), CETEIcean (`TEIText`), `@scalar/api-reference-react` (`ApiDoc`).
4. **CSS:** in the app's main CSS file, `@import 'tailwindcss';`, `@import '@dracor/react/dracor.css';` (and `tei.css` for `TEIText`), and `@source '../node_modules/@dracor/react';` so that Tailwind generates the classes the components use. Without the `@source` line most of the components' styling is missing.
5. **Respect the library's division of labour.** The components only display what they get as props: no data fetching, no global state ([CLAUDE.md of `@dracor/react`](https://github.com/dracor-org/dracor-react/blob/ffda3e07484b2eda1d0f312760ff12e787a682ed/CLAUDE.md#L27-L30)). Routing and loading are the app's job: one typed `loaders.ts` with a function per endpoint, called from route loaders (as in [dracor-frontend](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/loaders.ts#L1-L156) and [eltec-frontend](https://github.com/clscor-io/eltec-frontend/blob/ee13aca9ff56583b4f85ff1c9a8b0572b8b38274/src/loaders.ts#L1-L33)).
6. **Generic, not DraCor-specific components.** `CorpusCard` + `CorpusCardRow` (1.3.0 or later), not `DracorCorpusCard`; `TEIText` only for TEI.
7. **Links:** full route IDs with `params`, no relative paths (see the warning in the example).
8. **API base URL from an environment variable** (`VITE_…_API`), so that the same build runs against a local, staging or production API.
9. **Develop against mock data** when the API isn't ready: a mock service worker as in poecor-frontend and ecocor-frontend ([`handlers.ts`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/mocks/handlers.ts#L1-L40)), or a small Vite middleware that serves JSON files.
10. **Check with** `tsc` (type check), `vite build`, and a look at every page in the browser (console free of errors).

(spinoff-frontends-api)=
## What the front end expects from the API

A spin-off front end needs an API that answers a small set of requests. The three spin-offs and DraCor ask for nearly the same things, with different names:

| Purpose | DraCor (API v1) | ELTeC | EcoCor | PoeCor (2022) |
|---|---|---|---|---|
| API name and version (footer) | `/info` | `/` | `/info` | – |
| list of corpora, with counts for the cards | `/corpora?include=metrics` | `/corpora` | `/corpora` | `/corpora` |
| one corpus (title, description, licence, repository, commit) | `/corpora/{corpus}` | `/corpora/{corpus}` | `/corpora/{corpus}` | `/corpora/{corpus}` |
| the texts of a corpus, for the table | in `/corpora/{corpus}` (`plays`) | `/corpora/{corpus}/texts` | `/corpora/{corpus}/texts` | in `/corpora/{corpus}` (`poems`) |
| one text: metadata and computed values | `/corpora/{corpus}/plays/{play}` | `/corpora/{corpus}/texts/{text}` | `/corpora/{corpus}/texts/{text}` | `/corpora/{corpus}/poem/{poem}` |
| the text as TEI (full text, download) | `…/plays/{play}/tei` | `…/texts/{text}/tei` | `…/texts/{text}/tei` | – |
| the text as plain text (download, tools) | `…/plays/{play}/txt` | `…/texts/{text}/plaintext` | `…/texts/{text}/plaintext` | – |
| domain-specific data | metrics, network data, characters, … | – | `…/entities`, `/corpora/{corpus}/entities` | analysis inside the text record |
| OpenAPI specification (`ApiDoc`) | `/api/v1/openapi.yaml` | `/api/v1/openapi.yaml` | `/api/openapi.yaml` | – |

Sources: [dracor-frontend `loaders.ts`](https://github.com/dracor-org/dracor-frontend/blob/700071e9725b073303f10f801dd53b0ef4ac3ee1/src/loaders.ts#L1-L156), [eltec-frontend `loaders.ts`](https://github.com/clscor-io/eltec-frontend/blob/ee13aca9ff56583b4f85ff1c9a8b0572b8b38274/src/loaders.ts#L1-L33), [ecocor-frontend `api.ts`](https://github.com/EcoCor/ecocor-frontend/blob/c515890f85369917ba02b53a85edbe7dc26bef07/src/api.ts#L1-L84), [poecor-frontend `api.ts`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/api.ts#L1-L49).

For a new spin-off: use plural nouns (`texts`, as ELTeC and EcoCor do; DraCor switched from `/play/` to `/plays/` with API 1.0.0), give every corpus the fields the cards and the corpus page show (`name`, `title`, `acronym`, `description`, `licence`, `licenceUrl`, `repository`, `commit`, `updated`, `metrics`), and give every text a short `name` for its URL and an `id`. Offer TEI and plain text, and an OpenAPI specification for `ApiDoc`.

<!-- Not checked: whether the ELTeC and EcoCor APIs are derived from dracor-api (both report an eXist-db version in /info, like dracor-api). -->

(spinoff-frontends-poecor-example)=
## Example: a PoeCor front end with `@dracor/react` in 2026

PoeCor (D7.1 §6.2) showed that the DraCor approach carries over to poetry. Its front end listed the corpora, the poems of a corpus and, for a single poem, its metadata and POSTDATA's analysis results. This section shows how that front end would be built today, as an example of adapting DraCor's front end to a different kind of corpus. It is a sketch, not a tutorial. The three code examples below were tested (21 November 2026) in a minimal app with `@dracor/react` 1.11.0, React 19.3, TanStack Router 1.170, TanStack Table 8.21, Vite 8 and Tailwind 4.3, against PoeCor's archived mock data: they type-check, build and run.

### General approach

1. **Start a new app, don't fork.** Create a Vite + React + TypeScript project and add TanStack Router (file-based routes) and Tailwind 4, like the sibling projects. Forking dracor-frontend would bring in everything drama-specific (networks, speech distribution, segments).
2. **Install `@dracor/react` and only the peers you need.** For the example: `@tanstack/react-router`, `@tanstack/react-table`, Font Awesome, CETEIcean only if there is TEI to render. Import `@dracor/react/dracor.css` and add the `@source` line (see [The DraCor front end](#dracor-frontend)).
3. **Write a typed API layer** like dracor-frontend's `src/loaders.ts`: one function per endpoint, called from route loaders. The types describe your API (`Poem`, `CorpusMetrics`), not DraCor's.
4. **Use the generic components and leave the DraCor-specific ones.** `CorpusCard` instead of `DracorCorpusCard` (which expects plays and characters), `Table`, `Tabs`, `NavBar`, `DocPage`, `ApiDoc`, `IdCopy`/`IdLink`.
5. **Write the domain views yourself.** For PoeCor, the analysis of a poem (stanzas, rhyme schemes, metrical patterns) has no counterpart in DraCor.
6. **Mock the API during development** with a mock service worker, as poecor-frontend and ecocor-frontend do (`VITE_MOCK_API`). This lets the front end be developed before the API exists.

### What replaces what

| poecor-frontend (2022) | 2026 with `@dracor/react` |
|---|---|
| [`App.tsx`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/App.tsx#L8-L22) with `<Routes>` (React Router 6) | route files: `routes/index.tsx`, `routes/corpora/index.tsx`, `routes/corpora/$corpusId/index.tsx`, `routes/corpora/$corpusId/$poemId/…` |
| `useEffect` + `useState` + axios in every page, `alert()` on errors | route loaders calling `fetch` helpers; the router shows loading and error states |
| [`Topnav.tsx`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/Topnav.tsx#L6-L26) (title, version, GitHub icon) | `NavBar` with `title`, `version`, `gitHubUrl`, `navItems` |
| [`CorpusCard.tsx`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/CorpusCard.tsx#L36-L68) with its own `CorpusCardRow` | `CorpusCard` + `CorpusCardRow` (same row layout: they descend from this file) |
| [`Table.tsx`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/Table.tsx#L21-L96), [`DebouncedInput.tsx`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/DebouncedInput.tsx#L3-L35) | `Table` (includes the debounced filter) |
| [`Poem.tsx`](https://github.com/dracor-org/poecor-frontend/blob/62f707ba8d89986e013dca5a8be2b94572fbbf5c/src/Poem.tsx#L42-L156): one long page | a poem route with `Tabs` (e.g. "Analysis", "Downloads") and child routes |
| poem ID as plain text | `IdCopy` (copy button for the ID / URI) |
| no documentation pages | `DocPage` for Markdown pages, `ApiDoc` for the PoeCor API's OpenAPI spec |
| `react-helmet-async` for the page title | a `<title>` element in the component (React 19) |

### Three examples

The corpus card, with PoeCor's metrics as rows:

```tsx
// routes/corpora/index.tsx (excerpt; corpora come from the route loader)
import CorpusCard, {CorpusCardRow} from '@dracor/react/CorpusCard';

<CorpusCard title={corpus.title} to={`/corpora/${corpus.name}`}>
  <CorpusCardRow label="Poems" value={corpus.metrics.poems} valueClassName="text-2xl" />
  <CorpusCardRow label="Authors" value={corpus.metrics.authors} />
  <CorpusCardRow label="Stanzas" value={corpus.metrics.stanzas} />
  <CorpusCardRow label="Verses" value={corpus.metrics.verses} />
  <CorpusCardRow label="Words" value={corpus.metrics.words} />
</CorpusCard>
```

The list of poems: a loader fetches the corpus, `Table` renders it with a search field and sortable columns. The columns are built from the corpus name, so that the links to the poems can name both route parameters (dracor-frontend does the same in `buildColumns`).

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

function buildColumns(corpusId: string): ColumnDef<Poem>[] {
  return [
    {
      accessorKey: 'title',
      header: 'Title',
      cell: ({row}) => (
        <Link to="/corpora/$corpusId/$poemId" params={{corpusId, poemId: row.original.name}}>
          {row.original.title}
        </Link>
      ),
    },
    {
      id: 'authors',
      header: 'Author',
      accessorFn: (p) => p.authors.map((a) => a.name).join(', '),
    },
    {accessorKey: 'source', header: 'Source'},
  ];
}

function CorpusPage() {
  const corpus = Route.useLoaderData();
  return (
    <section>
      <title>{`${corpus.title} - PoeCor`}</title>
      <h1>{corpus.title}</h1>
      <Table data={corpus.poems} columns={buildColumns(corpus.name)} defaultSort={[{id: 'title', desc: false}]} />
    </section>
  );
}
```

The poem view with tabs. The layout route `routes/corpora/$corpusId/$poemId/route.tsx` loads the poem and renders this component; each tab is a child route (`analysis.tsx`, `downloads.tsx`). `params: (prev) => prev` keeps the current corpus and poem in the tab links. This needs `@dracor/react` 1.11.0 or later; older versions drop `params` (dracor-react#87).

```tsx
// components/PoemView.tsx
import {Outlet} from '@tanstack/react-router';
import IdCopy from '@dracor/react/IdCopy';
import Tabs from '@dracor/react/Tabs';
import type {Poem} from '../types';

export default function PoemView({poem}: {poem: Poem}) {
  return (
    <section>
      <h2>{poem.authors.map((a) => a.name).join(', ')}</h2>
      <h1>{poem.title}</h1>
      <IdCopy uri={poem.uri}>{poem.id}</IdCopy>
      <Tabs
        data={[
          {label: 'Analysis', to: '/corpora/$corpusId/$poemId/analysis', params: (prev) => prev},
          {label: 'Downloads', to: '/corpora/$corpusId/$poemId/downloads', params: (prev) => prev},
        ]}
      />
      <Outlet />
    </section>
  );
}
```

:::{warning} Relative links do not type-check
Relative targets such as `to="./$poemId"` or `to: '../analysis'` work at runtime, but TanStack Router's types reject them. eltec-frontend silences this with `// @ts-expect-error`. Use the full route ID with `params`, as above.
:::

What the library does not cover for PoeCor: the analysis tables (PoeCor-specific), and the poem text itself. POSTDATA stores the text as literals in the triple store, not as TEI, so `TEIText` does not apply and the text view would be a small custom component. Charts (e.g. metrical patterns per stanza) would use Recharts directly, as dracor-frontend does.

## Open questions

<!-- for Ingo / Carsten, not for publication -->

1. **D7.1 §6.2 wording.** D7.1 says the PoeCor front end "was built based on the DraCor front-end". The code shows a new project in the DraCor style (corpus cards → table → text view) that shares no code with dracor-frontend. Is that worth an Update box in §6.2, pointing to the [sibling section](#spinoff-frontends-overview)?
2. **Version pins.** ELTeC (1.1.0) and EcoCor (1.2.1) predate the generic `CorpusCard` (1.3.0) and Scalar in `ApiDoc` (1.5.0) and still use their own card. Is the migration planned (Carsten)? And should EcoCor and ELTeC appear in the DraCor documentation at all, or only as "other projects using `@dracor/react`"?
