---
sidebar_position: 1
title: GitHub Actions
---

# GitHub Actions Integration

ignition-lint ships as a composite GitHub Action that you can add to any workflow.

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
      - uses: TheThoughtagen/ignition-lint@v1
        with:
          files: "**/view.json"
          component_style: "PascalCase"
          parameter_style: "camelCase"
```

## Action Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `files` | No | `**/view.json` | Comma-separated file globs to lint |
| `component_style` | No | `PascalCase` | Naming convention for components |
| `parameter_style` | No | `camelCase` | Naming convention for parameters |
| `component_style_rgx` | No | — | Custom regex for component names |
| `parameter_style_rgx` | No | — | Custom regex for parameter names |
| `allow_acronyms` | No | `false` | Allow acronyms in names |
| `project_path` | No | — | Path to Ignition project directory |
| `lint_type` | No | `perspective` | Type of linting: `perspective`, `scripts`, or `all` |
| `naming_only` | No | `true` | Only run naming convention checks |
| `ignore_codes` | No | — | Comma-separated rule codes to suppress |
| `schema_mode` | No | `robust` | Schema strictness: `strict`, `robust`, or `permissive` |
| `fail_on` | No | `error` | Minimum severity that causes a non-zero exit: `error`, `warning`, `info`, `style` |
| `component` | No | — | Filter Perspective linting to a specific component type prefix |
| `version` | No | action checkout | Version of ignition-lint-toolkit to install from PyPI. Leave blank to install the checked-out action code. |

## Action Outputs

| Output | Description |
|---|---|
| `result` | `success` or `failure` |

## Examples

### Full project lint

```yaml
- uses: TheThoughtagen/ignition-lint@v1
  with:
    project_path: .
    lint_type: all
    naming_only: "false"
```

### Ampersand fork enforcement

When using the Ampersand fork, leave `version` blank. The action will install
the checked-out fork code, including Ampersand compatibility fixes, instead of
the upstream PyPI package.

```yaml
- uses: amperesand/ignition-lint@main
  with:
    project_path: projects/pilot_line
    lint_type: all
    naming_only: "false"
    schema_mode: robust
    fail_on: error
```

For a gateway `data/` repository with many projects, run the CLI directly:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
- run: pip install git+https://github.com/amperesand/ignition-lint.git@main
- run: ignition-lint --target projects --profile full --schema-mode robust --fail-on error
```

### Naming only with acronym support

```yaml
- uses: TheThoughtagen/ignition-lint@v1
  with:
    files: "**/view.json"
    component_style: "PascalCase"
    parameter_style: "camelCase"
    allow_acronyms: "true"
```

### Custom regex patterns

```yaml
- uses: TheThoughtagen/ignition-lint@v1
  with:
    files: "**/view.json"
    component_style_rgx: "^[A-Z][a-zA-Z0-9]*$"
    parameter_style_rgx: "^[a-z][a-zA-Z0-9]*$"
```

### Suppress rules during adoption

```yaml
- uses: TheThoughtagen/ignition-lint@v1
  with:
    project_path: .
    lint_type: all
    ignore_codes: "NAMING_PARAMETER,MISSING_DOCSTRING,LONG_LINE"
```

## How It Works

The action:

1. Sets up Python 3.10
2. Installs the checked-out action code, or installs ignition-lint-toolkit from PyPI when `version` is set
3. Runs `ignition-lint-action` with environment variables mapped from the action inputs
4. Exits with code 0 on success or 1 on failure

## Environment Variables

The action entry point reads inputs from `INPUT_*` environment variables. You can also invoke it directly:

```bash
export INPUT_FILES="**/view.json"
export INPUT_COMPONENT_STYLE="PascalCase"
export INPUT_PARAMETER_STYLE="camelCase"
export INPUT_IGNORE_CODES="NAMING_PARAMETER"
ignition-lint-action
```
