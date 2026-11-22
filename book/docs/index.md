---
title: System Documentation
short_title: About
label: docs-index
---

This part documents the **current** DraCor system. Unlike the [CLS INFRA reports](../index.md), which are reproduced as published, these pages are kept up to date with DraCor releases. Each page names the release it describes and the report sections it updates.

| Topic | Contents | Updates | Status |
|---|---|---|---|
| [Overview](#docs-overview) | the components of the system, how they connect, where DraCor runs | D7.1 Fig. 08, ch. 5 | draft |
| Corpora and encoding | TEI encoding, ODD, corpus registry, corpus versions and DOIs | D7.1 §5.1–5.2, D7.3 | planned |
| [API](#dracor-api) | architecture, endpoints, versions, loading data, services, DTS, specification and tests | D7.1 §5.3–5.5, D7.4 §3.2–3.4 | draft |
| [Metrics service](#dracor-metrics) | the service that computes the network metrics; networkx versions; mapping to the API fields and features | D7.1 §5.4 | draft |
| [Frontend](#dracor-frontend) | the DraCor website and the component library `@dracor/react` | D7.1 §5.6 | draft |
| Libraries and tools | pydracor, rdracor, DraCor Notebooks | D7.1 §5.3.4, D7.2 | planned |
| Agents and Linked Data | MCP server, DraCor Open Knowledge Graph | D7.1 §5.5, D7.4 | planned |

For learning to use DraCor, see the [DraCor Textbook](https://dracor-org.github.io/dracor-textbook/); for hands-on code, the [DraCor Notebooks](https://github.com/dracor-org/dracor-notebooks).

How to build a new DraCor Spin-off (API, frontend, deployment) is described in a separate section: [Building DraCor Spin-offs](#spinoffs).
