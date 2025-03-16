== pyproject_aliases ==

A simple tool to manage aliases in pyproject.toml

```toml
[tool.aliases]
check = "uv run pre-commit run --all-files"
test = "uv run pytest"
```

```shell
$ uv run alias check
...
```

```shell
$ uv run alias
...
```
