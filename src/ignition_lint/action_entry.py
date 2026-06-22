#!/usr/bin/env python3
"""GitHub Actions entry point for Ignition Lint.

The action intentionally delegates to the CLI so CI, local pre-commit runs, and
LLM agent workflows all exercise the same linting behavior.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

from .cli import main as cli_main


def env_bool(env: Mapping[str, str], name: str, default: bool = False) -> bool:
    return env.get(name, str(default)).strip().lower() in {"1", "true", "yes"}


def _add_option(args: list[str], flag: str, value: str | None) -> None:
    if value:
        args.extend([flag, value])


def build_cli_args(env: Mapping[str, str] | None = None) -> list[str]:
    """Translate GitHub Action INPUT_* variables into ignition-lint CLI args."""
    env = os.environ if env is None else env
    args: list[str] = []

    files = env.get("INPUT_FILES")
    target = env.get("INPUT_TARGET")
    project_path = env.get("INPUT_PROJECT_PATH")

    if files:
        args.extend(["--files", files])
    elif target:
        args.extend(["--target", target])
    elif project_path:
        args.extend(["--project", project_path])

    lint_type = env.get("INPUT_LINT_TYPE")
    profile = env.get("INPUT_PROFILE")
    if profile:
        args.extend(["--profile", profile])
    elif lint_type:
        profile_by_lint_type = {
            "all": "full",
            "perspective": "perspective-only",
            "scripts": "scripts-only",
            "naming": "naming-only",
        }
        args.extend(["--profile", profile_by_lint_type.get(lint_type, lint_type)])

    if env_bool(env, "INPUT_NAMING_ONLY"):
        args.append("--naming-only")

    if env_bool(env, "INPUT_ALLOW_ACRONYMS"):
        args.append("--allow-acronyms")

    _add_option(args, "--checks", env.get("INPUT_CHECKS"))
    _add_option(args, "--component-style", env.get("INPUT_COMPONENT_STYLE"))
    _add_option(args, "--parameter-style", env.get("INPUT_PARAMETER_STYLE"))
    _add_option(args, "--component-style-rgx", env.get("INPUT_COMPONENT_STYLE_RGX"))
    _add_option(args, "--parameter-style-rgx", env.get("INPUT_PARAMETER_STYLE_RGX"))
    _add_option(args, "--schema-mode", env.get("INPUT_SCHEMA_MODE"))
    _add_option(args, "--fail-on", env.get("INPUT_FAIL_ON"))
    _add_option(args, "--report-format", env.get("INPUT_REPORT_FORMAT"))
    _add_option(args, "--ignore-codes", env.get("INPUT_IGNORE_CODES"))
    _add_option(args, "--ignore-file", env.get("INPUT_IGNORE_FILE"))
    _add_option(args, "--component", env.get("INPUT_COMPONENT"))

    return args


def main() -> None:
    args = build_cli_args()
    exit_code = cli_main(args)
    success = exit_code == 0

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
            handle.write(f"result={'success' if success else 'failure'}\n")

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
