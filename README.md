[//]: # (x-release-please-start-version)
# pyproject_aliases 0.2.0
[//]: # (x-release-please-end)

A simple tool to manage aliases in pyproject.toml

## Installation

```bash
pip install pyproject_aliases
```

## Usage

The tool reads alias definitions from your `pyproject.toml` file and allows you to run them via the `uv run alias` command. Simply add or modify the aliases in the `[tool.aliases]` section, and then invoke an alias from the command line.

For example, to add an alias for pre-commit checks and pytests, update your `pyproject.toml`:

```toml
[tool.aliases]
check = "uv run pre-commit run --all-files"
test = "uv run pytest"
```

Then run:

```shell
$ uv run alias check
...
```

```shell
$ uv run alias
You must choose one of the available aliases:
  check (uv run pre-commit run --all-files)
  test (uv run pytest)
```
