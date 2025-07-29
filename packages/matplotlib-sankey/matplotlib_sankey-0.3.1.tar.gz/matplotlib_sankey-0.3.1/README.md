# matplotlib-sankey

[![codecov](https://codecov.io/gh/harryhaller001/matplotlib-sankey/graph/badge.svg?token=SPSPC7MSV0)](https://codecov.io/gh/harryhaller001/matplotlib-sankey)
[![Version](https://img.shields.io/pypi/v/matplotlib-sankey)](https://pypi.org/project/matplotlib-sankey/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/matplotlib-sankey)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/harryhaller001/matplotlib-sankey/testing.yml)
[![DOI](https://zenodo.org/badge/893904012.svg)](https://doi.org/10.5281/zenodo.15420062)

[Documentation](https://harryhaller001.github.io/matplotlib-sankey/) | [PyPI](https://pypi.org/project/matplotlib-sankey/) | [Github repository](https://github.com/harryhaller001/matplotlib-sankey) | [Codecov](https://codecov.io/gh/harryhaller001/matplotlib-sankey)

Sankey plot for matplotlib

### Installation

Install with pip:

`pip install matplotlib-sankey`

Install from source:

```bash
git clone https://github.com/harryhaller001/matplotlib-sankey
cd matplotlib-sankey
pip install .
```


### Example

```python
data = [
    # (source index, target index, weight)
    [(0, 2, 20), (0, 1, 10), (3, 4, 15), (3, 2, 10), (5, 1, 5), (5, 2, 50)],
    [(2, 6, 40), (1, 6, 15), (2, 7, 40), (4, 6, 15)],
    [(7, 8, 5), (7, 9, 5), (7, 10, 20), (7, 11, 10), (6, 11, 55), (6, 8, 15)],
]

fig, ax = plt.subplots(figsize=(10, 5))
fig.tight_layout()
sankey(
    data=data,
    cmap="tab20",
    annotate_columns=True,
    ax=ax,
    spacing=0.03,
)
```

![Sankey plot example](./docs/source/_static/images/example_sankey_plot.jpg)



### Development

```bash
python3.10 -m virtualenv venv
source venv/bin/activate

# Install dev dependencies
make install
```
