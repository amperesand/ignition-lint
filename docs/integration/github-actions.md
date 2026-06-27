---
sidebar_position: 1
title: GitHub Actions
---

# GitHub Actions Integration

ignition-lint ships as a composite GitHub Action that you can add to any
workflow.

## Quick Start

Create `.github/workflows/ignition-lint.yml`:

```yaml
name: Ignition Lint
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: amperesand/ignition-lint@main
        with:
          target: "."
          profile: "full"
          schema_mode: "robust"
          fail_on: "error"
```

## Action Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `files` | No | — | Comma-separated file globs for naming-only linting. Prefer `target` for enforcement |
| `target` | No | — | Any directory to recursively lint for `view.json` and `.py` files |
| `component_style` | No | `PascalCase` | Naming convention for components |
| `parameter_style` | No | `camelCase` | Naming convention for parameters |
| `component_style_rgx` | No | — | Custom regex for component names |
| `parameter_style_rgx` | No | — | Custom regex for parameter names |
| `allow_acronyms` | No | `false` | Allow acronyms in names |
| `project_path` | No | — | Legacy standard Ignition project directory path |
| `lint_type` | No | — | Legacy preset: `perspective`, `scripts`, `naming`, or `all` |
| `profile` | No | — | CLI profile: `default`, `full`, `perspective-only`, `scripts-only`, `naming-only` |
| `checks` | No | — | Comma-separated checks: `perspective,naming,scripts` |
| `naming_only` | No | `false` | Only run naming convention checks |
| `ignore_codes` | No | — | Comma-separated rule codes to suppress |
| `ignore_file` | No | — | Path to `.ignition-lintignore`-compatible ignore file |
| `schema_mode` | No | `robust` | Schema strictness: `strict`, `robust`, or `permissive` |
| `fail_on` | No | `error` | Minimum severity that causes a non-zero exit: `error`, `warning`, `info`, `style` |
| `include_advisory` | No | `false` | Include advisory `info` and `style` findings in output |
| `component` | No | — | Filter Perspective linting to a specific component type prefix |
| `report_format` | No | `text` | Output format: `text` or `json` |
| `version` | No | action checkout | Version of ignition-lint-toolkit to install from PyPI. Leave blank to install the checked-out action code |

## Action Outputs

| Output | Description |
|---|---|
| `result` | `success` or `failure` |

## Examples

### Full gateway data lint

```yaml
- uses: amperesand/ignition-lint@main
  with:
    target: projects
    profile: full
    schema_mode: robust
    fail_on: error
```

### Pilot line lint

```yaml
- uses: amperesand/ignition-lint@main
  with:
    target: projects/pilot_line
    profile: full
    schema_mode: robust
    fail_on: error
```

### JSON output for agent workflows

```yaml
- uses: amperesand/ignition-lint@main
  with:
    target: projects/pilot_line
    profile: full
    report_format: json
    fail_on: error
```

### Naming only with acronym support

```yaml
- uses: amperesand/ignition-lint@main
  with:
    files: "**/view.json"
    component_style: "PascalCase"
    parameter_style: "camelCase"
    allow_acronyms: "true"
```

### Suppress rules during adoption

```yaml
- uses: amperesand/ignition-lint@main
  with:
    target: .
    profile: full
    ignore_codes: "NAMING_PARAMETER,MISSING_DOCSTRING,LONG_LINE"
    fail_on: error
```

## How It Works

The action:

1. Sets up Python 3.10
2. Installs the checked-out action code, or installs ignition-lint-toolkit from PyPI when `version` is set
3. Translates action inputs into the same `ignition-lint` CLI flags used locally
4. Exits with code 0 on success or 1 on failure

The `target` input is preferred for CI, pre-commit, and LLM agent flows because
it recursively discovers Ignition `view.json` files and standalone `.py` scripts
without assuming a single standard project layout.
