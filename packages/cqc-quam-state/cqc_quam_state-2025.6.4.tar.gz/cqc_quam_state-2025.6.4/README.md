# CQC QUAM State

A command-line tool for managing CQC QuAM state.

## Features

The `cqc-quam-state` CLI provides the following commands:

- `set`: Set configuration values for IP and calibration db location
- `info`: Display information about the current state
- `load`: Set the environment $QUAM_STATE to the current state

## Installation

You can install this package using `uv` or `pip`:

```fish
# Using uv
uv venv
source .venv/bin/activate.fish
uv pip install -e .

# Using pip
pip install -e .
```

## Usage

Once installed, you can use the CLI as follows:

### Get Help

```bash
cqc-quam-state --help
```

This will display all available commands and options.

### Set Command

Use this command to set configuration values:

```bash
cqc-quam-state set
```

### Info Command

Use this command to display information about the current state:

```bash
cqc-quam-state info
```

### Load Command

Use this command to load data or configuration:

```bash
cqc-quam-state load
```
