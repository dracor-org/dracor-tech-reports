# Guide for coding agents: build a DraCor spin-off

You are helping a person build a **DraCor spin-off**: a corpus of TEI files,
an API that makes it programmable, and a website to browse it, in the way
DraCor, EcoCor and ELTeC are built. Work through the steps below in order.
Each step ends with a check; do not start the next step before it passes.

The documentation behind this guide (read the page of a step before you start it):

| Step | Page | Machine-readable |
|---|---|---|
| overview | https://dracor-org.github.io/dracor-tech-reports/spinoffs/ | |
| 1. API | https://dracor-org.github.io/dracor-tech-reports/spinoffs/api/ | https://dracor-org.github.io/dracor-tech-reports/spinoffs/spinoff-api.yaml |
| 2. Frontend | https://dracor-org.github.io/dracor-tech-reports/spinoffs/frontend/ | |
| 3. Deployment | https://dracor-org.github.io/dracor-tech-reports/spinoffs/deploy/ | https://github.com/dracor-org/dracor-eosc-eu-node-deploy (its own AGENTS.md) |

Status: draft (November 2026). The specification and the code examples were
tested; this guide as a whole has not yet been run by an agent from start to finish.
Tell the person so at the start.

## Rules for you, the agent

- **The person decides; you build and explain.** Before each step, say in two or
  three sentences what you will do and what it will produce. Ask before anything
  that leaves the machine: creating repositories, pushing, publishing images,
  deploying.
- **Follow the specification.** The API implements `spinoff-api.yaml` exactly;
  additions are allowed, changes to the shared operations are not. If the
  corpus seems to need a change, explain why and let the person decide.
- **Never handle secrets in plain text.** The admin password goes into an
  environment variable or a platform Secret, never into a file in a repository
  and never into the chat. Use test credentials only for local development.
- **Check, don't assume.** Run the checks named in each step and report the
  result honestly, including failures.
- **Small steps.** Commit after each working step (if the person wants Git),
  with a message that says what works now.
- **Pin what you use.** Library versions in the lock file, images by digest,
  links to code as permalinks (commit SHA and line numbers).

## Step 0: the conversation

Find out, in a normal conversation (not a questionnaire):

1. **The texts.** What kind (novels, plays, poems, letters, …), how many, which
   language(s). Where the TEI files are (ideally a Git repository, one file per
   text). Look at two or three files together with the person.
2. **The name** of the spin-off and of its first corpus (short, lowercase, e.g. `eng`).
3. **What to count** for the corpus cards and the table: always texts, authors,
   words; plus what matters for this kind of text (stanzas, chapters, letters
   per correspondent, …). These become extra `numOf…` metrics.
4. **The citation structure** for DTS (if wanted): which parts of a text can be
   cited (chapters; acts and scenes; stanzas and lines). Check in the TEI files
   that this structure is encoded consistently; if not, say so now.
5. **What is special** about this kind of text that the website should show
   beyond the basics (a later step; note it, don't build it yet).
6. **Where it will run**: only locally, or on the EOSC EU Node (Step 3).

Summarise the answers in a short `SPINOFF.md` in the project folder and let the
person confirm it.

## Step 1: the API

Read the API page. Then choose the implementation with the person:

- **eXist-db and XQuery, starting from [eltec-api](https://github.com/clscor-io/eltec-api)**:
  the way EcoCor and ELTeC are built, and closest to the specification. Adapt
  names and fields to the spin-off; note that eltec-api uploads texts with
  `PUT …/texts/{textname}`, the specification with `PUT …/texts/{textname}/tei`.
- **A small server in another language** (e.g. Python with FastAPI, TEI files on
  disk): quicker for a prototype; the specification was tested with such a server.

Implement all public and admin operations of the specification; DTS if the
person wants it (Step 0, point 4). Extract the metadata from the TEI header:
`id` from `TEI/@xml:id`, title, authors with their `@ref` as `refs`
(`viaf:…`, `wikidata:…`, never URLs), a reference year, and the counts.

**Check:**

```sh
openapi-spec-validator spinoff-api.yaml          # if you extended the specification
schemathesis run spinoff-api.yaml --url http://localhost:<port>/api/v1 \
  --include-method GET --checks all              # read operations, with real names in the config
```

Run the admin operations by hand (create a corpus, upload a text under a name
you choose, load, delete) and check that an uploaded text appears under the
name from the URL. Known false alarms: Schemathesis sends non-TEI XML as "TEI"
and reports the 400 response as a problem; ignore that. A wrong `Allow` header
on 405 responses is not a problem of the specification either.

## Step 2: the website

Read the Frontend page and follow its checklist: start from
[eltec-frontend](https://github.com/clscor-io/eltec-frontend); Vite, React 19,
TypeScript, TanStack Router, Tailwind 4; `@dracor/react` 1.11.0 or later; the
three CSS lines; types from the schemas of the specification; links as route
IDs with `params`, never relative (`./…`, `../…` pass at runtime but fail the
type check).

Pages: corpus cards (`CorpusCard` with the metrics from Step 0), the table of
texts (`Table`), the text view with tabs (`Tabs`): full text (`TEIText` on
`…/tei`), downloads (`DownloadButton` for TEI and plain text), and an API page
(`ApiDoc` on the specification of the spin-off).

**Check:** `tsc` without errors, `vite build`, and every page in the browser
against the running API from Step 1, with an empty console.

## Step 3: deployment (optional)

Read the Deployment page. For the EOSC EU Node, use
[dracor-eosc-eu-node-deploy](https://github.com/dracor-org/dracor-eosc-eu-node-deploy)
as the template: its AGENTS.md covers booking, the web console, the Secret
and the manifests. Replace the DraCor images with the spin-off's (built so
that they run under a random user ID, web servers on port 8080, pinned by
digest), keep the platform steps. Load the corpus with `POST /corpora` and
`POST /corpora/{corpusname}`.

**Check:** the public website shows the corpus; `GET /info` answers; the
Schemathesis check from Step 1 passes against the public address.

## At the end

- A README for each repository: what the spin-off is, how to run it, where it
  runs; a licence (code) and the licence of the texts; a `CITATION.cff`.
- Tell the person what works, what was not tested, and what you would do next.
- Offer to draft feedback on this guide (what was missing, where you got stuck)
  for an issue in https://github.com/dracor-org/dracor-tech-reports. Send
  nothing yourself.

## Progress table

Keep this table in `SPINOFF.md` and update it after each step.

| Step | Status | Check | Notes |
|---|---|---|---|
| 0 conversation | | person confirmed SPINOFF.md | |
| 1 API | | schemathesis, admin by hand | |
| 2 website | | tsc, build, browser | |
| 3 deployment | | public site, /info | |
