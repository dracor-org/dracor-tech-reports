---
kernelspec:
  name: python3
  display_name: Python 3
---
# DraCor Technical Reports

*Working title. Under construction.*

This book provides executable, updatable editions of the reports produced by work package 7 of the
[CLS INFRA](https://clsinfra.io) project, which document the [DraCor](https://dracor.org) system.

Version 1 aims to be faithful to the published reports (archived on Zenodo); later versions may
evolve into maintained documentation.

| Report | Year | Archived version |
|---|---|---|
| D7.1 On Programmable Corpora | 2023 | [10.5281/zenodo.7664964](https://doi.org/10.5281/zenodo.7664964) |
| D7.2 API Libraries for R and Python: rdracor and pydracor | 2023 | [10.5281/zenodo.15302236](https://doi.org/10.5281/zenodo.15302236) |
| D7.3 On Versioning Living and Programmable Corpora | 2024 | [10.5281/zenodo.11081934](https://doi.org/10.5281/zenodo.11081934) |
| D7.4 Report on the Implementation of Programmable Corpora | 2025 | [10.5281/zenodo.15301341](https://doi.org/10.5281/zenodo.15301341) |

```{code-cell} python
# Build-time execution check: live DraCor API
import requests
info = requests.get("https://dracor.org/api/v1/info", timeout=30).json()
print(info.get("name"), info.get("version"))
```
