# Tasks

## style

> Commands related to style

This section is used to manage the style of the codebase. It includes commands for linting and formatting the code.

### lint

> Linting

Lints the codebase using various linters. This command will lint YAML, GitHub Actions, Markdown, and TOML files as well as check for typos.

```sh
mise exec yamllint -- yamllint .
mise exec actionlint -- actionlint
mise exec action-validator -- action-validator
mise exec markdownlint-cli2 -- markdownlint-cli2 .
mise exec taplo -- taplo lint pyproject.toml
mise exec typos -- typos .
```

### format

> Formatting

Formats the codebase using various formatters. This command will format YAML, and TOML files.

```sh
mise exec yamlfmt -- yamlfmt .
mise exec taplo -- taplo format .
```

## docs

> Commands related to documentation

This section is used to manage the documentation of the project.

### serve

> Serve the documentation

Serves the documentation using mkdocs. This command will start a local server that you can access in your browser.

```sh
mise exec pipx:mkdocs -- mkdocs serve
```

### build

> Build the documentation

Builds the documentation using mkdocs. This command will clean the build directory before building.

```sh
mise exec pipx:mkdocs -- mkdocs build --clean
```
