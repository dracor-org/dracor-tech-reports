# DraCor Technical Reports

HTML editions of the four technical reports on [DraCor](https://dracor.org) written in work package 7 of the EU project [CLS INFRA](https://clsinfra.io) (Computational Literary Studies Infrastructure, 2021–2025).

Together, the reports document the DraCor system (corpora, API, front end, metrics, versioning and research software) at different points in time. Until now they were only available as PDFs on Zenodo. This repository makes them readable on the web, searchable and linkable section by section, and is meant to grow into up-to-date documentation of DraCor.

| Report | Title | Year | Archived version |
|---|---|---|---|
| D7.1 | On Programmable Corpora. Report and Prototype (DraCor) | 2023 | [10.5281/zenodo.7664964](https://doi.org/10.5281/zenodo.7664964) |
| D7.2 | API Libraries for R and Python for the Programmable Corpora Prototype “DraCor”: “rdracor” and “pydracor” | 2023 | [10.5281/zenodo.15302236](https://doi.org/10.5281/zenodo.15302236) |
| D7.3 | On Versioning Living and Programmable Corpora | 2024 | [10.5281/zenodo.11081934](https://doi.org/10.5281/zenodo.11081934) |
| D7.4 | Report on the Implementation of Programmable Corpora | 2025 | [10.5281/zenodo.15301341](https://doi.org/10.5281/zenodo.15301341) |

The archived PDFs remain the version of record; please cite the Zenodo records.

## Status

- **0.9.0:** all four reports converted automatically from their original sources and checked against the published PDFs (text, footnote numbering, figures). **Not yet reviewed.**
- **1.0.0** (after review): faithful editions of the reports as published at the end of CLS INFRA.
- **Afterwards:** the content will be updated to the current state of DraCor (current API, MCP access, etc.) and may be restructured into topic-based documentation. Tutorial-style code goes to [dracor-notebooks](https://github.com/dracor-org/dracor-notebooks) rather than being duplicated here. The 1.0.0 tag preserves the state of the reports for reference.

## What the 1.0 editions contain

- The full text of each report, with its footnotes (numbered as in the PDF), figures, tables and code, as published, including typos.
- Code is shown with its original output as of the report date; it is not re-executed.
- Not reproduced: page layout, page numbers, the tables of contents and the lists of figures/tables (the site has its own navigation), and the appendices of D7.2 (generated documentation of rdracor 0.7.2 and pydracor 1.0.0, which are only in the PDF).
- Each report has a start page with metadata from Zenodo (authors with ORCID, DOI, licence) and a note on the edition.

## Building the book

The book uses [Jupyter Book 2](https://jupyterbook.org) (MyST).

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv -r requirements.txt
cd book
../.venv/bin/jupyter-book start           # live preview at http://localhost:3000
../.venv/bin/jupyter-book build --html    # static site in book/_build/html
```

## Repository layout

```
book/          the Jupyter Book: myst.yml, start page, reports/d7-N/ (one page per chapter or section)
tools/         conversion scripts (docx -> MyST)
alignment/     recorded corrections that align the converted text with the published PDFs
input/         drop zone for the original sources (not part of the repository)
```

### How the editions were made

The original sources (Word files and Google Docs exports) are not part of the repository. `tools/convert_report.sh` converts a source into MyST pages:

1. marks monospaced text as code (`tools/docx_mark_code.py`)
2. runs pandoc with a Lua filter (`tools/gdocs_cleanup.lua`): code blocks, section labels, internal links, tables
3. splits the result into pages with their footnotes and figures (`tools/split_report.py`)
4. applies the recorded corrections in `alignment/<report>_*.json`, i.e. exact replacements where the published PDF differs from the source (`tools/apply_edits.py`)
5. renumbers the footnotes as in the PDF (`tools/renumber_footnotes.py`)

Every deviation from the source is therefore recorded in `alignment/` and reapplied when a report is converted again.

## Related resources

- [DraCor](https://dracor.org) and its [API documentation](https://dracor.org/doc/api)
- [DraCor Textbook](https://github.com/dracor-org/dracor-textbook): learning path for working with DraCor
- [dracor-notebooks](https://github.com/dracor-org/dracor-notebooks): hands-on Jupyter notebooks
- [dracor-explorecor](https://github.com/dracor-org/dracor-explorecor): teaching material of the CLS INFRA Training School “ExploreCor” (Vienna, June 2024). The four showcases of D7.1 (chapter 4, “The DraCor Prototype in Action”) were reused as an executable notebook there: [1-3_DraCor_Showcase.ipynb](https://github.com/dracor-org/dracor-explorecor/blob/main/notebooks/1_Introduction/1-3_DraCor_Showcase.ipynb)
- [Executable version of D7.3](https://github.com/dh-network/clsinfra-d73)

## Licence

The text and figures of the reports are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), as are the Zenodo records. The licence for the conversion scripts in `tools/` has not been decided yet.

## Acknowledgement

The HTML editions of the DraCor Technical Reports have been developed in the context of “[DraCorOS. Fostering Open Science in Digital Humanities by connecting the ‘DraCor’ Ecosystem to EOSC](https://oscars-project.eu/projects/dracoros-fostering-open-science-digital-humanities-connecting-dracor-ecosystem-eosc)”, a project funded by [OSCARS](https://oscars-project.eu/). We acknowledge the [OSCARS project](https://oscars-project.eu/), which has received funding from the European Commission’s Horizon Europe Research and Innovation programme under grant agreement Nº. [101129751](https://cordis.europa.eu/project/id/101129751).

The reports were written in the [CLS INFRA](https://clsinfra.io) project, which has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 101004984.
