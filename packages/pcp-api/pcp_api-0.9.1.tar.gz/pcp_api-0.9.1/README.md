<h1>PCP API</h1>

- [Description](#description)
- [Getting Started](#getting-started)
  - [Create a wheel package](#create-a-wheel-package)
  - [Installation](#installation)
  - [Usage as a package](#usage-as-a-package)
  - [CLI](#cli)
- [Contributors](#contributors)
- [References](#references)
  - [Internal](#internal)
  - [External](#external)

# Description 

Python API for Pulsar PCP communication.


# Getting Started

The strategy is to compile using Cython and then create a wheel package for distribution. Also include .pyi stubs for IDE introspection.


## Create a wheel package

```powershell
python generate_stubs.py  # Generate or review stub files
python -m build  # Build both sdist and wheel so .pyi stub files are included in the wheel
```


## Installation

```sh
pip install dist/pcp_api-0.1.0-cp312-cp312-win_amd64.whl .  #add --force-reinstall if needed
```


## Usage as a package

```python
from pcp_api import CANoverUSB, PulsarActuator
```


## CLI

```sh
 pulsar-cli -h
 ```


# Contributors

-  Daniel Alvarez - daeusebio@arquimea.com


# References

## Internal

- [Azure DevOps](https://dev.azure.com/ArquimeaRC/Pulsar/_git/PCP_API_python)
- [Confluence CAN API](https://arquimeagroup.atlassian.net/wiki/spaces/HU/pages/2132475908/R002_09_02_04_03+-+CAN+API)


## External
