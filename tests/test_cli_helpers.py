from ignition_lint.action_entry import build_cli_args
from ignition_lint.cli import determine_checks
from ignition_lint.json_linter import JsonLinter


def test_determine_checks_profile_defaults():
    assert determine_checks("default", None, False) == {
        "perspective",
        "naming",
        "scripts",
    }


def test_determine_checks_naming_only():
    assert determine_checks("default", None, True) == {"naming"}


def test_determine_checks_explicit():
    assert determine_checks("default", "perspective,scripts", False) == {
        "perspective",
        "scripts",
    }


def test_action_args_support_target_full_profile():
    args = build_cli_args(
        {
            "INPUT_TARGET": "projects",
            "INPUT_PROFILE": "full",
            "INPUT_SCHEMA_MODE": "robust",
            "INPUT_FAIL_ON": "error",
            "INPUT_REPORT_FORMAT": "json",
        }
    )

    assert args == [
        "--target",
        "projects",
        "--profile",
        "full",
        "--schema-mode",
        "robust",
        "--fail-on",
        "error",
        "--report-format",
        "json",
    ]


def test_action_args_preserve_legacy_lint_type_all():
    args = build_cli_args(
        {
            "INPUT_PROJECT_PATH": "projects/pilot_line",
            "INPUT_LINT_TYPE": "all",
            "INPUT_NAMING_ONLY": "false",
        }
    )

    assert args == ["--project", "projects/pilot_line", "--profile", "full"]


def test_action_args_include_legacy_naming_only_when_requested():
    args = build_cli_args(
        {
            "INPUT_PROJECT_PATH": "projects/pilot_line",
            "INPUT_LINT_TYPE": "perspective",
            "INPUT_NAMING_ONLY": "true",
        }
    )

    assert args == [
        "--project",
        "projects/pilot_line",
        "--profile",
        "perspective-only",
        "--naming-only",
    ]


class TestRootComponentNaming:
    """The 'root' component name is Ignition-assigned and should not be flagged."""

    def test_root_name_not_flagged(self):
        linter = JsonLinter(component_style="PascalCase")
        data = {
            "root": {
                "type": "ia.container.flex",
                "meta": {"name": "root"},
                "children": [],
            }
        }
        linter._check_json_structure(data, "test.json")
        component_errors = [e for e in linter.errors if e.error_type == "component"]
        flagged_names = {e.name for e in component_errors}
        assert "root" not in flagged_names

    def test_non_pascalcase_name_still_flagged(self):
        linter = JsonLinter(component_style="PascalCase")
        data = {
            "root": {
                "type": "ia.container.flex",
                "meta": {"name": "bad_name"},
                "children": [],
            }
        }
        linter._check_json_structure(data, "test.json")
        component_errors = [e for e in linter.errors if e.error_type == "component"]
        flagged_names = {e.name for e in component_errors}
        assert "bad_name" in flagged_names

    def test_pascalcase_name_passes(self):
        linter = JsonLinter(component_style="PascalCase")
        data = {
            "root": {
                "type": "ia.container.flex",
                "meta": {"name": "MyContainer"},
                "children": [],
            }
        }
        linter._check_json_structure(data, "test.json")
        component_errors = [e for e in linter.errors if e.error_type == "component"]
        assert len(component_errors) == 0
