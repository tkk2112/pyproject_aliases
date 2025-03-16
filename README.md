# pyproject_aliases

A simple tool to manage aliases in pyproject.toml

### pyproject.toml
```toml
[tool.uv.sources]
pyproject-aliases = { git = "https://github.com/tkk2112/pyproject_aliases.git" }

[dependency-groups]
dev = [
    "pre-commit>=4.1.0",
    "pyproject-aliases",
]

[tool.aliases]
check = "uv run pre-commit run --all-files"
test = "uv run pytest"
```

### examples:
```shell
$ uv run alias
You must choose one of the available aliases:
  check (uv run pre-commit run --all-files)
  test (uv run pytest)
```

```shell
$ uv run alias check
...
```

