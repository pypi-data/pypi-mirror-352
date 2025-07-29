# PySTIXView
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) [![PyPI version](https://badge.fury.io/py/PySTIXview.svg)](https://badge.fury.io/py/PySTIXview) [![codecov](https://codecov.io/gh/vincenzocaputo/PySTIXView/graph/badge.svg?token=812G6NT5JP)](https://codecov.io/gh/vincenzocaputo/PySTIXView) [![Documentation Status](https://readthedocs.org/projects/pystixview/badge/?version=latest)](https://pystixview.readthedocs.io/en/latest/?badge=latest) [![Super-Linter](https://github.com/vincenzocaputo/PySTIXView/actions/workflows/lint.yml/badge.svg)](https://github.com/marketplace/actions/super-linter) [![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

PySTXIView is a Python library to create and display STIX2 graphs.

PySTIXView is based on [pyvis](https://github.com/WestHealth/pyvis/) that allows you to create graph and visualize them in your browser or in Jupyter Notebook.

![](https://raw.githubusercontent.com/vincenzocaputo/PySTIXView/main/_media/graph_example.png)

## Installation

### Requirements
- python3 (tested on python 3.12)
- pyvis
- [stix2](https://github.com/oasis-open/cti-python-stix2)

### Install from pip
```
pip install PySTIXview
```

### Install from source code

```
git clone https://github.com/vincenzocaputo/PySTIXView
cd PySTIXView
python3 setup.py install
```

## Usage

Below is a simple example to create a graph from the STIX2 Bundle [Threat Actor Leveraging Attack Patterns and Malware](https://oasis-open.github.io/cti-documentation/examples/threat-actor-leveraging-attack-patterns-and-malware). (The JSON file is available at https://github.com/oasis-open/cti-documentation/blob/main/examples/example_json/threat-actor-leveraging-attack-patterns-and-malware.json)

```python
from pystixview import PySTIXView

stix_graph = PySTIXView()
with open("threat-actor-leveraging-attack-patterns-and-malware.json", "r") as fd:
    stix_graph.add_bundle(fd.read())
stix_graph.save_graph("threat-actor-leveraging-attack-patterns-and-malware.html", width="100%", height="600px")
```

PySTIXView can be used also in Jupyter Notebook:

![](https://raw.githubusercontent.com/vincenzocaputo/PySTIXView/main/_media/jupyter_example.png)

## Documentation

Documentation is available [here](https://pystixview.readthedocs.io/en/latest/)

## Credits

- The resources used for examples and library tests are taken from https://oasis-open.github.io/cti-documentation/stix/examples.html.
- The images used in the library for the node icons are taken from https://github.com/freetaxii/stix2-graphics
