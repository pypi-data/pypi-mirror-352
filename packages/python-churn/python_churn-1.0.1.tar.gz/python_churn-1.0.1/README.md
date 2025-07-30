# Churn

Churn(corruption of Charm, **Cha**in SLU**RM**) is a simple Python batch job runner. It automates the process of creating parametrized batch jobs and submitting multiple dependent jobs.

## Installation

### PyPI

Via pip:
```bash
pip install python-churn
```
### From source

Via uv:
```bash
uv sync
uv build
```

## Usage

Churn can either be used as a command line tool or as a Python library. The command line tool runs a set of jobs using a YAML configuration file, whereas the library makes it easier to dispatch related jobs with varying parameters from within Python code.

You may find an exemplary configuration in the ```examples/basic directroy```. This may either be run using 
```bash
python -m churn examples/basic
```
or by executing the equivalent python file that does the required library calls:
```bash
python examples/basic.py
```

### Schema

To make writing `run.yaml` files easier, Churn provides a schema that can be used to validate the configuration. The schema is located in `schema/schema.json`. You can use it with a YAML validator or editor that supports JSON Schema validation. For example in VSCode, you can add the following to your settings:
```json
"yaml.schemas": {
    "https://git.rwth-aachen.de/cats-gitolite/public/tools/churn/-/raw/main/schema/schema.json?ref_type=heads": "run.yaml"
}
```
