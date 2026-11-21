---
title: Front ends of the spin-offs
subtitle: PoeCor, EcoCor, ELTeC and the reuse of the DraCor front end
short_title: Spin-off front ends
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

(spinoff-frontends-poecor-example)=
## Example: a PoeCor front end with `@dracor/react` in 2026

PoeCor (D7.1 §6.2) showed that the DraCor approach carries over to poetry. Its front end listed the corpora, the poems of a corpus and, for a single poem, its metadata and POSTDATA's analysis results. This section shows how that front end would be built today, as an example of adapting DraCor's front end to a different kind of corpus. It is a sketch, not a tutorial. The code has not been run.

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

## Open questions

<!-- for Ingo / Carsten, not for publication -->

1. **D7.1 §6.2 wording.** D7.1 says the PoeCor front end "was built based on the DraCor front-end". The code shows a new project in the DraCor style (corpus cards → table → text view) that shares no code with dracor-frontend. Is that worth an Update box in §6.2, pointing to the [sibling section](#spinoff-frontends-overview)?
2. **Version pins.** ELTeC (1.1.0) and EcoCor (1.2.1) predate the generic `CorpusCard` (1.3.0) and Scalar in `ApiDoc` (1.5.0) and still use their own card. Is the migration planned (Carsten)? And should EcoCor and ELTeC appear in the DraCor documentation at all, or only as "other projects using `@dracor/react`"?
