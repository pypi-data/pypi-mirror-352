# nccapy

[![Python package](https://github.com/NCCA/nccapy/actions/workflows/python-package.yml/badge.svg)](https://github.com/NCCA/nccapy/actions/workflows/python-package.yml) [![Test pip install](https://github.com/NCCA/nccapy/actions/workflows/test-pip.yml/badge.svg)](https://github.com/NCCA/nccapy/actions/workflows/test-pip.yml) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=NCCA_nccapy&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=NCCA_nccapy) [![Bugs](https://sonarcloud.io/api/project_badges/measure?project=NCCA_nccapy&metric=bugs)](https://sonarcloud.io/summary/new_code?id=NCCA_nccapy) [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=NCCA_nccapy&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=NCCA_nccapy) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=NCCA_nccapy&metric=coverage)](https://sonarcloud.io/summary/new_code?id=NCCA_nccapy) [![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=NCCA_nccapy&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=NCCA_nccapy)

The code in this python package is used in various units taught in the NCCA and in particlar [Jon's programming courses](https://nccastaff.bournemouth.ac.uk/jmacey/)

The aim of this repository is to teach not only about python [modules and packages](https://docs.python.org/3/tutorial/modules.html) but demonstrate other python code and techniques.

## Installation

This module is on [PyPi](https://pypi.org/project/nccapy/) so you can install it using pip

```bash
pip install nccapy
```



## Modules


## Developer notes

To build the package run the following command

```bash
python -m pip install build
python -m build
```

To run the tests use the following command

```
pytest -v .
```

for coverage reports use the following command

```bash
coverage run --source=src/nccapy -m pytest -v tests && coverage report -m
```

This will create a dist folder with the package in it. You can then install the package using pip

```bash
pip install dist/nccapy-0.0.1-py3-none-any.whl
```


Upload via twine

```bash
uvx twine upload --skip-existing dist/*
```
