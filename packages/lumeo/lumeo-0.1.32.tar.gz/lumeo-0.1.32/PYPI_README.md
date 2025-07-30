<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/lumeo.svg?branch=main)](https://cirrus-ci.com/github/<USER>/lumeo)
[![ReadTheDocs](https://readthedocs.org/projects/lumeo/badge/?version=latest)](https://lumeo.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/lumeo/main.svg)](https://coveralls.io/r/<USER>/lumeo)
[![PyPI-Server](https://img.shields.io/pypi/v/lumeo.svg)](https://pypi.org/project/lumeo/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/lumeo.svg)](https://anaconda.org/conda-forge/lumeo)
[![Monthly Downloads](https://pepy.tech/badge/lumeo/month)](https://pepy.tech/project/lumeo)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/lumeo)
-->
# lumeo

>Helper library for Lumeo video analytics platform

Lumeo is a flexible, open no/low code video analytics platform that enables you to generate actionable insights and alerts using AI-based video analytics.
This package provides :
1) a set of helpers to be used within Lumeo's [custom function node](https://docs.lumeo.com/docs/custom-function-node)
2) a set of scripts that make it easy to use Lumeo's API for importing cameras, bulk processing video, etc.

## Useful Links

- [Lumeo](https://lumeo.com/)
- [Lumeo Documentation Hub](https://docs.lumeo.com/)
- [API Reference](https://docs.lumeo.com/reference)


## Lumeo Custom Function Node install & usage

From within a Lumeo [custom function node](https://docs.lumeo.com/docs/custom-function-node), you install and use the package as follows:

```python
# This code will only work within a Lumeo custom function node.
from lumeopipeline import VideoFrame, Utils

# Replace version x.x.x with the version you want to install
lumeo = Utils.install_import('lumeo', version='x.x.x')
from lumeo.pipeline.display import write_label_on_frame

def process_frame(frame: VideoFrame, **kwargs):
     with frame.data() as mat:
         write_label_on_frame(mat, 50, 50, 'hello world')
     return True
```  

> Note that `lumeo.pipeline`'s submodules are not usable outside of a Lumeo custom function node.

Refer to Lumeo docs for details on available helpers and methods.



## Local install & usage

You can install the package locally to use the scripts that it provides.

### Install

```bash
pip install lumeo
```

```bash
pip install lumeo==x.x.x
```

### Scripts

See list of available scripts:

```bash
lumeo-scripts
```

Currently available scripts:

*Bulk Processing*
- `lumeo-media-download` : Download media from Lumeo
- `lumeo-bulk-process` : Bulk process media in Lumeo

*Gateway Testing*
- `lumeo-load-test` : Test a gateway's performance

*Camera Import*
- `lumeo-avigilon-import-cameras` : Import Avigilon cameras
- `lumeo-verkada-import-cameras` : Import Verkada cameras
- `lumeo-hanwhawave-import-cameras` : Import Hanwha Wave cameras
- `lumeo-rhombus-copy-footage` : Copy footage from Rhombus to Lumeo  

*Custom Function*
- `lumeo-custom-function-create-repo` : Create a custom function repository


