---
title: "Step 3: Deployment"
subtitle: Running a DraCor Spin-off on the EOSC EU Node
short_title: "3. Deployment"
label: spinoffs-deploy
---

:::{note} Draft
:class: editorial
This page adapts the tested DraCor deployment guide to DraCor Spin-offs. A DraCor Spin-off has not been deployed this way yet.
:::

A DraCor Spin-off runs as two containers, the API and the website. DraCor already has a guide for deploying it, step by step and with a coding agent, on the Cloud Container Platform of the [EOSC EU Node](https://open-science-cloud.ec.europa.eu/): [dracor-eosc-eu-node-deploy](https://github.com/dracor-org/dracor-eosc-eu-node-deploy) (background: [blog post](https://blog.dracor.org/posts/cloud-credits-coding-agent-own-dracor-eosc-eu-node/)). A DraCor Spin-off is deployed the same way: take that repository as the template and replace the DraCor components with the DraCor Spin-off's.

## What gets deployed

| DraCor (in the guide) | DraCor Spin-off |
|---|---|
| API (`dracor-api`, eXist-db) | the API of the DraCor Spin-off (implements the [DraCor Spin-off API](#spinoffs-api)) |
| metrics service | only if the DraCor Spin-off API needs one |
| frontend (`dracor-frontend`, nginx) | the DraCor Spin-off website ([Step 2](#spinoffs-frontend)), served by nginx, which passes `/api/v1` to the API |
| MCP server (optional) | optional; an MCP server for the DraCor Spin-off API |
| volume for the database, Secret for the admin password, route | the same |

## Adapting the template

The DraCor guide shows what the platform requires. A DraCor Spin-off has to meet the same requirements:

1. **Images that run under a random user ID.** The platform (OKD 4) starts containers with an arbitrary, unprivileged user ID. Every path the container writes to must be writable for group 0 (`chgrp -R 0 … && chmod -R g=u …`), and web servers must listen on an unprivileged port (8080, e.g. with `nginx-unprivileged`). The [Dockerfiles in the template](https://github.com/dracor-org/dracor-eosc-eu-node-deploy/tree/02c74f114dd71780348952c4847c9760463f5b3e/images) show these changes for the DraCor images; an eXist-db-based DraCor Spin-off API needs the same ones as the DraCor API.
2. **Images pinned by digest** (`image:tag@sha256:…`), so that a deployment can be reproduced.
3. **Manifests** for the volume, the API, the frontend and the route: copy [`manifests/`](https://github.com/dracor-org/dracor-eosc-eu-node-deploy/tree/02c74f114dd71780348952c4847c9760463f5b3e/manifests) and replace image names, ports and environment variables. The health checks call `GET /info`, which every DraCor Spin-off API has.
4. **The admin password as a Secret.** The API's admin operations (HTTP Basic authentication) read it from there; nobody types it into a file.
5. **Loading data** with the admin operations of the DraCor Spin-off API: `POST /corpora` creates a corpus, `POST /corpora/{corpusname}` loads its TEI files from the repository.
6. **Check:** the website shows the corpora; `GET /info` answers; optionally run the Schemathesis check from [Step 1](#spinoffs-api-tested) against the public address.

## Where the template's AGENTS.md helps

The template contains an [`AGENTS.md`](https://github.com/dracor-org/dracor-eosc-eu-node-deploy/blob/02c74f114dd71780348952c4847c9760463f5b3e/AGENTS.md#L1-L586) that a coding agent follows to guide a person through booking resources, creating the Secret, pasting the manifests and loading a corpus; the person clicks in the web console, the agent never sees the password. For a DraCor Spin-off, the platform part of this guide stays the same; the parts that name DraCor components (images, routes, the corpus to load) have to be replaced.

## Limits

As the DraCor guide says: good for a demo, teaching or project instance with public data, not for unattended long-term operation. The admin password is the only protection of the write operations; pinned images get no security fixes by themselves; there are no backups (corpora from GitHub can be reloaded); there is no monitoring.
