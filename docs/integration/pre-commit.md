---
sidebar_position: 2
title: Pre-commit
---

# Pre-commit Hook

Run ignition-lint before commits using the [pre-commit](https://pre-commit.com/)
framework.

## Recommended Hook

Add this to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/amperesand/ignition-lint
    rev: codex/ignition-compat-fixes
    hooks:
      - id: ignition-lint
```

Then install the hooks:

```bash
pre-commit install
```

The `ignition-lint` hook runs:

```bash
ignition-lint --target . --profile full --schema-mode robust --fail-on error
```

That is the same enforcement mode recommended for CI: warnings remain visible,
but only `error` severity blocks a commit.

## Perspective-Only Hook

For a lighter local gate that skips standalone scripts:

```yaml
repos:
  - repo: https://github.com/amperesand/ignition-lint
    rev: codex/ignition-compat-fixes
    hooks:
      - id: ignition-perspective-lint
```

This hook runs:

```bash
ignition-lint --target . --profile perspective-only --schema-mode robust --fail-on error
```

## Customizing Arguments

Override `args` in your project config:

```yaml
repos:
  - repo: https://github.com/amperesand/ignition-lint
    rev: codex/ignition-compat-fixes
    hooks:
      - id: ignition-lint
        args:
          - --target
          - projects/pilot_line
          - --profile
          - full
          - --schema-mode
          - robust
          - --fail-on
          - error
```

## Notes

- The shipped hooks use `pass_filenames: false` because Ignition views and
  scripts can reference sibling files and shared project state.
- Use `.ignition-lintignore` or `--ignore-codes` for temporary adoption
  suppressions.
- For very large gateway repositories, point `--target` at the project or folder
  you actively work on locally, and keep full `--target projects` enforcement in
  CI.
