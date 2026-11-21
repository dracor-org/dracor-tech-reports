---
title: "Step 1: API"
subtitle: A minimal OpenAPI specification for spin-off APIs
short_title: "1. API"
label: spinoffs-api
---

<!--
DRAFT 2026-11-21. Spec abstracted from dracor-api 1.5.0-rc.1, ecocor-api 1.0.1, eltec-api 1.0.0, poecor-api 2026-11-16-archive.
Tested: openapi-spec-validator (OK); test server (scratchpad spinoff-server, FastAPI) checked with Schemathesis 4.33
(all GET operations, 470 generated requests, no issues); admin operations by hand; front end (scratchpad spinoff-poc) on top.
-->

:::{note} Draft
:class: editorial
A recommendation for new spin-offs, not a standard that existing ones have to follow. Download: [`spinoff-api.yaml`](./spinoff-api.yaml); stable address: `https://dracor-org.github.io/dracor-tech-reports/spinoffs/spinoff-api.yaml`.
:::

Every spin-off needs an API: the website is built on it, and it makes the corpus programmable (scripts, notebooks, agents). The [spin-off API](./spinoff-api.yaml) is the smallest set of operations such an API should offer. A spin-off adds its own endpoints and fields on top (DraCor its networks, EcoCor its entities).

## What it contains

| Group | Operations | Notes |
|---|---|---|
| **public** | `GET /info`, `/corpora`, `/corpora/{corpusname}`, `/corpora/{corpusname}/texts`, `/corpora/{corpusname}/texts/{textname}`, `…/tei`, `…/plaintext` | read access, no authentication |
| **admin** | `POST /corpora` (new corpus), `PUT /corpora/{corpusname}` (corpus description), `POST /corpora/{corpusname}` (load texts from the repository), `DELETE /corpora/{corpusname}`, `PUT …/texts/{textname}/tei` (add or replace a text), `DELETE …/texts/{textname}` | HTTP Basic authentication |
| **dts** (optional) | `GET /dts`, `/dts/collection`, `/dts/navigation`, `/dts/document` | [Distributed Text Services 1.0](https://dtsapi.org/specifications/versions/v1.0/); collections are the corpora, resources the texts |

The schemas are `Info`, `Corpus` (with `CorpusMetrics`), `Text` (with `TextMetrics`, `Author`, `Source`) and `Error`. Metrics are open: `numOfTexts` is required for a corpus, and a spin-off adds its own counts as further `numOf…` fields (`numOfAnimals` in EcoCor, `numOfStanzas` for poetry). Authority identifiers (`refs`) are prefixed strings such as `wikidata:Q1001` or `viaf:34551336`, the form the [`IdLink`](#dracor-frontend) component expects.

## Decisions

Where the existing APIs differ, the specification decides as follows:

| Question | DraCor | EcoCor, ELTeC | Spin-off API | Why |
|---|---|---|---|---|
| name of the texts | `plays` | `texts` | `texts` | neutral; used by the later spin-offs |
| plain text | `…/txt` | `…/plaintext` | `…/plaintext` | as EcoCor and ELTeC |
| list of texts | inside `/corpora/{corpusname}` | own endpoint `…/texts` | own endpoint | keeps the corpus record small |
| metrics in `/corpora` | only with `?include=metrics` | always | always | the corpus cards need them |
| upload a text | `PUT …/plays/{playname}/tei` | `PUT …/texts/{textname}` | `PUT …/texts/{textname}/tei` | the TEI goes where `GET …/tei` reads it; `GET …/texts/{textname}` stays JSON |
| name of an uploaded text | from the URL | from the URL | from the URL (`id` from `TEI/@xml:id`) | the client must know where its upload went |
| authentication | HTTP Basic, declared | not declared in the spec (401 responses only) | HTTP Basic, declared | |
| TEI media type | `application/xml` | `application/tei+xml` | `application/tei+xml` | the registered type for TEI |

Not included: search (ELTeC), entities (EcoCor), networks, metrics endpoints and character data (DraCor), the GitHub webhook (DraCor), paging (PoeCor). They are good candidates for spin-off-specific extensions.

(spinoffs-api-dts)=
## DTS

[DTS 1.0](https://dtsapi.org/specifications/versions/v1.0/) is a standard API for citable parts of texts; DraCor and ELTeC implement it with the same parameters. The spin-off API lists the four endpoints and their parameters and leaves everything else to the DTS specification.

The hard part is not the endpoints but the **citation tree**: which parts of a text can be cited, and how they are numbered. It depends on the kind of text: chapters for novels, acts and scenes for plays, stanzas and lines for poems. A spin-off has to decide this and describe it in `citeStructure`, and the TEI files have to support it consistently (every chapter a `div[@type="chapter"]`, for example). The test server uses chapters as the only level; DraCor and ELTeC can serve as models for deeper trees.

(spinoffs-api-comparison)=
## The four APIs compared

The specification abstracts from what the four APIs have in common. Their front ends ask for nearly the same things, with different names:

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

The spin-off API takes the EcoCor/ELTeC names (`texts`, `plaintext`, `numOf…`), which are also what the later spin-offs converged on.

(spinoffs-api-tested)=
## How the specification was tested

The specification was checked in three ways (21 November 2026):

1. **Valid OpenAPI 3.1** (`openapi-spec-validator`).
2. **A test server built only from the specification** (Python, FastAPI; three ELTeC-eng novels as data). [Schemathesis](https://schemathesis.io) generated 470 requests to all read operations, including DTS, and found no response that contradicts the specification. The admin operations were run by hand: create a corpus, upload a text, load, delete. The tests led to two corrections in the specification: an uploaded text takes the name from the URL, and `refs` must not be URLs.
3. **A front end on top** (built as described in [Step 2](#spinoffs-frontend)): corpus card, table of texts, text view with the TEI rendered by `TEIText`, downloads. No errors.

Schemathesis can be used in the same way to check a new spin-off API against the specification:

```sh
schemathesis run spinoff-api.yaml --url https://<your-host>/api/v1 --checks all
```

## The specification

```{literalinclude} spinoff-api.yaml
:language: yaml
```
