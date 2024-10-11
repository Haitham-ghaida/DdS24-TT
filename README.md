# Team Trash

quotes of the week: 
- "something went wrong" - TJ
- "just give me 10 minutes" - TJ

you can find documentation of the model in [here](https://dds24-tt.readthedocs.io/en/latest/)

## TODO

### Vocabs
- [x] link to DDS vocabs
- [x] link to https://op.europa.eu/en/web/eu-vocabularies/concept-scheme/-/resource?uri=http://data.europa.eu/6p8/ewc4-stat/scheme

### Model
- [X] Extract model
- [X] Add model to the repo

### Python
- [ ] Datapackage schema

### Integration
- [ ] Vocab, model, DP

## Documentation
- [X] Add documentation to the repo
- [X] Add mermaid diagrams
- [X] publish readthedocs













-----
[![PyPI](https://img.shields.io/pypi/v/tt.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/tt.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/tt)][pypi status]
[![License](https://img.shields.io/pypi/l/tt)][license]

[![Read the documentation at https://tt.readthedocs.io/](https://img.shields.io/readthedocs/tt/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/haitham-ghaida/tt/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/haitham-ghaida/tt/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/tt/
[read the docs]: https://tt.readthedocs.io/
[tests]: https://github.com/haitham-ghaida/tt/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/haitham-ghaida/tt
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Installation

You can install _trash_ via [pip] ~~from [PyPI]~~:

```console
$ pip install git+https://github.com/Haitham-ghaida/DdS24-TT.git@main
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [MIT license][License],
_trash_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://tt.readthedocs.io/en/latest/usage.html
[License]: https://github.com/haitham-ghaida/tt/blob/main/LICENSE
[Contributor Guide]: https://github.com/haitham-ghaida/tt/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/haitham-ghaida/tt/issues


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_tt
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```
