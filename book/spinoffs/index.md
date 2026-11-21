---
title: Building DraCor Spin-offs
subtitle: How the DraCor Spin-offs were built, and how to build a new one
short_title: Overview
label: spinoffs
---

<!--
DRAFT 2026-11-21. Section set up at Ingo's request ("instructions on how DraCor Spin-offs were built and how to do it").
DraCorOS: this documentation is the delivery instead of a configurable "generic DraCor" (Ingo's decision 2026-11-21).
-->

:::{note} Draft
:class: editorial
This section is a draft. It is based on the code of the existing DraCor Spin-offs (as of November 2026); the API specification and the code examples were tested.
:::

A **DraCor Spin-off** applies the DraCor approach to another kind of text: a corpus of TEI files, an API that makes it programmable, and a website to browse it. Three DraCor Spin-offs exist so far:

| DraCor Spin-off | Texts | Website | API | Since |
|---|---|---|---|---|
| PoeCor | Spanish poetry (POSTDATA) | poecor.org (offline since November 2026, [archived](https://github.com/dracor-org/poecor-frontend)) | Python, on the POSTDATA knowledge graph | 2022 |
| EcoCor | ecocritically relevant narrative texts | [ecocor.org](https://ecocor.org) | [ecocor-api](https://github.com/EcoCor/ecocor-api) (eXist-db, XQuery) | 2023 |
| ELTeC | European novels (ELTeC) | [eltec.clscor.io](https://eltec.clscor.io) | [eltec-api](https://github.com/clscor-io/eltec-api) (eXist-db, XQuery) | 2025 |

Instead of one configurable "generic DraCor", the DraCor Spin-offs share **parts**: an API with the same basic structure, the component library [`@dracor/react`](#dracor-frontend) for the website, and the same way of deploying. This section describes these parts in the order in which a new DraCor Spin-off is built:

1. [**API**](#spinoffs-api): a minimal OpenAPI specification that every DraCor Spin-off API should implement (read access, loading data, DTS).
2. [**Frontend**](#spinoffs-frontend): the website, built with `@dracor/react` against that API.
3. [**Deployment**](#spinoffs-deploy): running both on the EOSC EU Node.

The pages are written for people and for coding agents: each has a checklist or a specification that can be followed step by step, and all code examples were tested.

**For coding agents:** [`AGENTS.md`](https://dracor-org.github.io/dracor-tech-reports/spinoffs/AGENTS.md) is a guide that an agent (e.g. Claude Code) follows to build a DraCor Spin-off together with a person: a conversation about the texts first, then API, website and deployment, each step with a check that has to pass. Put it into an empty project folder and start the agent there. It has not yet been run from start to finish.

(spinoffs-history)=
## How the DraCor Spin-offs were built

(spinoffs-history-apis)=
### APIs

- **PoeCor (2022/23)** was a demonstrator in CLS INFRA ([D7.1 §6.2](#clsinfra-d71-6-2)): a Python API on top of the POSTDATA knowledge graph, designed after the DraCor API (corpora, a list of poems, single poems). It had no admin operations; the data came from the triple store.
- **EcoCor (2023)** got a new eXist-db application in XQuery, like the DraCor API: [ecocor-api](https://github.com/EcoCor/ecocor-api) (first commit May 2023). It introduced the names that the later DraCor Spin-offs kept: `texts` instead of `plays`, `plaintext`, metrics named `numOf…`.
- **ELTeC (2025)** started from a copy of the EcoCor API ([eltec-api](https://github.com/clscor-io/eltec-api), second commit: "Copy adjust files from ecocor-api") and added DTS and a search endpoint.

So EcoCor and ELTeC share almost all basic operations, under the same names. The [DraCor Spin-off API](#spinoffs-api) writes these shared operations down as a specification.

(spinoffs-history-frontends)=
### Front ends

The DraCor Spin-offs and two DraCor tools, Einakter and ezlinavis, share DraCor's look and, increasingly, its code through the component library `@dracor/react`. None of them is a fork of dracor-frontend: they share no Git history with it.

| Front end | Site | Started | Stack today | `@dracor/react` (resolved) | From the library |
|---|---|---|---|---|---|
| [dracor-frontend](https://github.com/dracor-org/dracor-frontend) | dracor.org | 2017 | Vite, React 19, TanStack Router, Tailwind 4 (since 3.0) | 1.11.0 (3.0.0-rc.1) | all components |
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
