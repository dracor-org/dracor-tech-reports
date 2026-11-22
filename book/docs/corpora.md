---
title: Corpora on GitHub
subtitle: Corpus repositories, the registry, versions, releases and DOIs
short_title: Corpora
label: docs-corpora
---

:::{note} Draft
:class: editorial
This page describes how DraCor corpora are kept and published as of November 2026. It updates [D7.1 §5.1](#clsinfra-d71-5-1) and [§5.2](#clsinfra-d71-5-2). The section on [releases and DOIs](#docs-corpora-releases) describes a procedure that is still being tried out.
:::

Every DraCor corpus lives in its own Git repository in the [dracor-org](https://github.com/dracor-org) organisation on GitHub. The repository is the place where the corpus is edited, reviewed and versioned; dracor.org shows a copy of it, loaded into the database of the [API](#dracor-api). GitHub is therefore not only a code host for DraCor but part of the infrastructure, as D7.1 §5.2.1 already put it: storage, versioning, issue tracking and discussion for the corpora as well as for the software.

(docs-corpora-encoding)=
## Encoding

The plays are encoded in TEI following the DraCor encoding guidelines, a customisation of TEI P5 described in an ODD. The guidelines are not repeated here:

- the rendered guidelines: [dracor.org/doc/odd](https://dracor.org/doc/odd);
- the source, the schemas generated from it and the releases: [dracor-schema](https://github.com/dracor-org/dracor-schema) (1.6.0; pre-release 1.7.0-alpha.1);
- their development is discussed in the [issues of dracor-schema](https://github.com/dracor-org/dracor-schema/issues).

For an introduction, see the [DraCor Textbook](https://textbook.dracor.org): chapter 2, [Corpus Building in DraCor](https://textbook.dracor.org/chapters/02-corpus-building-in-dracor.html), on how corpora are compiled and prepared, and chapter 3, [TEI Encoding: Preparing Texts for Programmable Corpora](https://textbook.dracor.org/chapters/03-tei-encoding-preparing-texts-for-programmable-corpora.html), on the encoding of plays for DraCor, both with exercises.

(docs-corpora-repository)=
## A corpus repository

| File | Content | Needed |
|---|---|---|
| `corpus.xml` | the description of the corpus (below) | required |
| `tei/*.xml` | one TEI file per play; the file name without `.xml` is the name of the play in DraCor, e.g. `tei/coriolanus.xml` → `/gersh/coriolanus` | required |
| `README.md` | what the corpus contains, its sources, how it was made, how to cite it | strongly recommended |
| `LICENSE` | the licence of the texts (CC0 for many corpora, Creative Commons licences with conditions for some) | recommended |
| `CITATION.cff` | how to cite the corpus; GitHub shows it as "Cite this repository", Zenodo takes its metadata from it | recommended, needed for [releases](#docs-corpora-releases) |
| `.github/workflows/validation.yml` | checks the TEI files on every push and pull request (below) | recommended |

Only `corpus.xml` and the files in `tei/` are loaded into DraCor; everything else stays in the repository ([`load.xqm`](https://github.com/dracor-org/dracor-api/blob/e93400b16e793b3600f4a91dca22790e9c12d868/modules/load.xqm#L54-L67)).

**`corpus.xml`** describes the corpus in a TEI header with the root element `dracorCorpus` (`teiCorpus` is still accepted, but deprecated since API 1.3.0). The API and the registry read from it:

| Element | Used for |
|---|---|
| `titleStmt/title`, `title[@type="acronym"]` | name of the corpus, short name on the corpus card |
| `publicationStmt/idno` | the short name of the corpus in URLs and the API (e.g. `gersh`) |
| `publicationStmt/idno[@type="repo"]` (or `ref[@type="repo"]`) | the repository; needed for loading and for the webhook |
| `availability/licence` | licence, shown on the corpus page |
| `encodingDesc/projectDesc` | description, shown on the corpus page |
| `revisionDesc` | the status of the corpus (`proposed`, `draft`, `published`; see [the registry](#docs-corpora-registry)) |
| `refsDecl/citeStructure` (optional) | which units count as segments for the network ([API › Loading data](#dracor-api-loading)) |

**Validation.** The workflow in each repository runs [dracor-validate-action](https://github.com/dracor-org/dracor-validate-action) on the TEI files that a push or pull request changes, against TEI-All and against the DraCor schema; it can also be started by hand for all files (example: [GerShDraCor](https://github.com/dracor-org/gershdracor/blob/c81b223c769a9dc6a946a315fc2075f75c068ea6/.github/workflows/validation.yml#L1-L59)). Errors show up as a failed check on the commit or pull request.

(docs-corpora-new)=
## Starting a new corpus

1. Create the repository from the template [newdracor](https://github.com/dracor-org/newdracor) ("Use this template"). It contains a `corpus.xml` to adapt, a README, a licence and the validation workflow.
2. In `corpus.xml`, replace "new" with the short name of the corpus, set the title and description, and set the status in `revisionDesc` (a new corpus starts as `proposed`).
3. Add the TEI files to `tei/`, one per play.
4. Add the corpus to the [registry](#docs-corpora-registry).
5. As `draft`, the corpus can be loaded on [staging.dracor.org](https://staging.dracor.org) for review; once it is `published`, it is loaded on dracor.org.

(docs-corpora-registry)=
## The registry

The [DraCor registry](https://github.com/dracor-org/dracor-registry) is the list of all DraCor corpora, published and planned (33 in November 2026: 24 `published`, 7 `draft`, 2 `proposed`). For each corpus it records name, title, repository, licence, description and status, taken from the corpus's `corpus.xml` by an update script. It is published as the npm package `@dracor/registry`.

| Status | Meaning | Where to see the corpus |
|---|---|---|
| `published` | stable | [dracor.org](https://dracor.org) |
| `draft` | under development | [staging.dracor.org](https://staging.dracor.org) |
| `proposed` | planned or in an early stage; the repository may not be public yet | only in the registry |

The status comes from `corpus.xml`: the `status` of `revisionDesc`, or else that of the latest `change`. On dracor.org the registry is shown on the page [Corpus Registry](https://dracor.org/doc/corpora); the front end includes the npm package when it is built, so changes to the registry appear there with the next front-end release.

(docs-corpora-loading)=
## From the repository to dracor.org

Changes to a corpus reach the servers in different ways (as already described in D7.1 §5.2.2):

- **staging.dracor.org** (and dev) receive a webhook on every push to `main` and update the changed plays automatically.
- **dracor.org** has no webhook: corpora are loaded by the administrators (`POST /corpora/{corpusname}`), so that only reviewed changes reach the production server.

How loading works in the API is described in [API › Loading data](#dracor-api-loading).

(docs-corpora-versions)=
## Versions: commits

Every state of a corpus is a Git commit, and the API records which one it loaded: each play is stored with the SHA of the commit it comes from, and the API returns it as `commit` for the play and, if all plays come from the same commit, for the corpus ([API › Loading data](#dracor-api-loading)). A play changed through the webhook or uploaded by hand no longer matches the corpus commit; in that case the corpus has no `commit`. How to use commits to cite and reconstruct a corpus version is the topic of [D7.3](#clsinfra-d73-index).

(docs-corpora-releases)=
## Releases and DOIs (being tried out)

:::{note} Tentative
:class: editorial
Corpus releases with DOIs are new (November 2026) and the procedure is still being discussed among the corpus maintainers. This section describes the current practice.
:::

For Living Corpora, which keep changing, citing the commit is the most precise way to refer to the data used: it identifies the exact version ([D7.3](#clsinfra-d73-index)). This practice, however, is not widely adopted; resources are commonly cited by a DOI. We therefore encourage corpus maintainers to release selected versions of their corpora on GitHub and to archive them on [Zenodo](https://zenodo.org) for the long term, where every release gets a DOI.

**How it works.** The GitHub–Zenodo integration is switched on for repositories of dracor-org by an administrator of the organisation; maintainers of a corpus cannot switch it on themselves. Then every GitHub release (including pre-releases) is archived on Zenodo automatically. The records belong in the Zenodo community [DraCor](https://zenodo.org/communities/dracor), which also holds the releases of the DraCor software and publications. Examples: [GerShDraCor 1.0.0](https://zenodo.org/records/24313493) and [ArDraCor 1.0.0](https://zenodo.org/records/19498450).

**Metadata.** Zenodo takes the metadata from `CITATION.cff` (title, authors, licence, keywords). Three fields had to be corrected by hand for GerShDraCor: the community (DraCor), the resource type (Dataset) and the publisher (DraCor). A `.zenodo.json` in the repository can set these as well; this is to be tested with the next release.

**Version numbers.** The first release is 1.0.0. A new major version (2.0.0) is meant for fundamental changes, e.g. a change of the encoding; adding plays encoded in the same way is not one. These rules are still being discussed.

**Concept DOI and version DOI.** Zenodo assigns two kinds of DOI:

| DOI | Identifies | Resolves to | Use it |
|---|---|---|---|
| **concept DOI** ("Cite all versions") | the corpus as such | always the latest version | **to refer to the corpus**: in `CITATION.cff`, `corpus.xml`, READMEs, the registry, on websites |
| version DOI | one release | that release only | to cite the exact data used, e.g. in a publication |

For GerShDraCor, the concept DOI is [10.5281/zenodo.24313492](https://hdl.handle.net/10.5281/zenodo.24313492) and the version DOI of 1.0.0 is 10.5281/zenodo.24313493. A version DOI should never be written into a file that is meant to stay valid, because it points to an outdated version as soon as the next one is released.

**The DOI in `corpus.xml`.** It is proposed to record the concept DOI in `corpus.xml` as `<idno type="DOI">` in the `publicationStmt`, so that the API, the registry and the front end can show it ([dracor-schema#207](https://github.com/dracor-org/dracor-schema/issues/207), open). To have the DOI already in the first release: publish `1.0.0-rc.1` as a pre-release first; Zenodo creates the concept DOI; add it to `corpus.xml`; then publish `1.0.0`.

(docs-corpora-database)=
## In the database

When a corpus is loaded, the API stores it in its database (eXist-db) in one collection per corpus, and within it one collection per play. Each play collection holds the TEI of the play and the files derived from it, always under the same names ([`dutil:filepaths`](https://github.com/dracor-org/dracor-api/blob/e93400b16e793b3600f4a91dca22790e9c12d868/modules/util.xqm#L43-L87)). For the German Drama Corpus and *Emilia Galotti*:

```
/db/dracor/
    corpora/
        ger/                           one collection per corpus
            corpus.xml                 the corpus description from the repository
            git.xml                    commit of the corpus (only if all plays come from the same commit)
            lessing-emilia-galotti/    one collection per play (the file name in tei/)
                tei.xml                the play, as loaded from the repository
                metrics.xml            word counts and network metrics
                rdf.xml                the play as RDF (also sent to the triple store)
                sitelinks.xml          number of Wikipedia articles on the play
                git.xml                commit of the play
            …
    webhook/                           webhook deliveries waiting to be processed
```

| File | Content | Written |
|---|---|---|
| `corpus.xml` | the corpus description, as in the repository | when the corpus is created or loaded |
| `git.xml` (corpus) | the commit SHA of the corpus; returned by the API as the corpus's `commit` | after loading, only if all plays share one commit; removed otherwise ([`dutil:get-corpus-sha`](https://github.com/dracor-org/dracor-api/blob/e93400b16e793b3600f4a91dca22790e9c12d868/modules/util.xqm#L2094-L2110)) |
| `tei.xml` | the TEI of the play, unchanged | when the play is loaded, uploaded or changed via the webhook |
| `metrics.xml` | word counts (`text`, `sp`, `stage`) and the network metrics from the metrics service ([details](#dracor-metrics-stored)) | by the database trigger, whenever `tei.xml` is stored |
| `rdf.xml` | the play as RDF; the same data is sent to the triple store (Fuseki) | by the trigger |
| `sitelinks.xml` | the number of Wikipedia articles on the play, from Wikidata | by the trigger |
| `git.xml` (play) | the commit SHA the play was loaded from; returned as the play's `commit` | when the play is loaded from the repository; removed if the play is uploaded by hand |

The API answers all requests from these files: the TEI for texts and structure, the derived files for metrics, RDF and Wikipedia counts ([API › Loading data](#dracor-api-loading)). The full-text indexes on speeches and stage directions are defined in [`data.xconf`](https://github.com/dracor-org/dracor-api/blob/e93400b16e793b3600f4a91dca22790e9c12d868/data.xconf#L5-L11).

**Before API 1.1.0** (the layout described in D7.1 §5.2.2), the database was organised by kind of data rather than by play: one collection per kind (`tei`, `metrics`, `rdf`, `sitelinks`, `webhook`) under `/db/data/dracor/`, each with a collection per corpus and one file per play, e.g. `/db/data/dracor/tei/ger/lessing-emilia-galotti.xml` and `/db/data/dracor/metrics/ger/lessing-emilia-galotti.xml`. The current layout was introduced in February 2024 (commit [4446437](https://github.com/dracor-org/dracor-api/commit/4446437a4fbced7718f93d97a3ec2a76021d2332), "Restructure file hierarchy") and released with API 1.1.0 (July 2025); D7.4 §3.3 already shows a `metrics.xml` stored in a play collection.

(docs-corpora-reports)=
## From D7.1 to this page

| D7.1 | Topic | Now |
|---|---|---|
| §5.1 | TEI, ODD, homogenisation, workflows | encoding: [the ODD](https://dracor.org/doc/odd); this page for the repositories. The strategies of corpus building described in §5.1 are still valid as background |
| §5.2.1 | GitHub repositories (`corpus.xml`, `tei/`, README) | [A corpus repository](#docs-corpora-repository), extended by validation, `CITATION.cff`, the template and the registry |
| §5.2.2 | eXist-db: layout, webhook for staging, manual loading for production | [From the repository to dracor.org](#docs-corpora-loading) (unchanged), [In the database](#docs-corpora-database) (new layout) |
| (new) | releases, Zenodo, DOIs | [Releases and DOIs](#docs-corpora-releases) |
