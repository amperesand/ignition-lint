# Ampersand Ignition Lint Agent Guide

This repository is the Ampersand-maintained fork of `ignition-lint`.
Prefer changes that make the CLI, GitHub Action, pre-commit hooks, and agent
workflows behave consistently.

## Core Runtime Assumptions

- Ignition 8.3 Perspective scripts run on Ignition's Jython 2.7 environment.
- Valid Jython/Python 2 syntax must not be treated as a CI-blocking Python 3
  syntax error.
- Python 3 portability hints are useful, but should be `info` or `style` unless
  they indicate real runtime breakage in Ignition.
- Perspective schemas and component catalogs can lag Designer exports. Schema
  drift should be visible, but not a default `--fail-on error` blocker.

## Preferred Validation Commands

Run these before pushing lint behavior changes:

```bash
ruff check src tests
pytest -q
python -m build
```

When the `C:\Github\ignition-test` gateway data repo is available, also run:

```bash
ignition-lint --target projects\pilot_line --profile full --schema-mode robust --fail-on error
ignition-lint --target projects --profile full --schema-mode robust --fail-on error
```

For agent-readable output, add `--report-format json`.

## Integration Contract

- Prefer `--target` for CI, pre-commit, and agents. It works with gateway
  `data/` repositories and recursively discovers `view.json` and `.py` files.
- Use `--profile full --schema-mode robust --fail-on error` as the default
  enforcement mode.
- Keep warnings useful but non-blocking during rollout.
- Keep the GitHub Action as a thin adapter over the CLI; do not duplicate lint
  behavior in `action_entry.py`.
- Keep pre-commit hooks copy-pasteable and aligned with real CLI flags.
