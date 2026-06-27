from ignition_lint.action_entry import build_cli_args
from ignition_lint.cli import configure_console_encoding, determine_checks
from ignition_lint.json_linter import JsonLinter
from ignition_lint.reporting import LintIssue, LintReport, LintSeverity
from ignition_lint.style_checker import StyleChecker


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


def test_action_args_include_advisory_when_requested():
    args = build_cli_args(
        {
            "INPUT_TARGET": "projects",
            "INPUT_PROFILE": "full",
            "INPUT_INCLUDE_ADVISORY": "true",
        }
    )

    assert args == [
        "--target",
        "projects",
        "--profile",
        "full",
        "--include-advisory",
    ]


def test_report_drops_advisory_by_default():
    report = LintReport()
    report.add_issue(
        LintIssue(
            severity=LintSeverity.INFO,
            code="INFO",
            message="info",
            file_path="view.json",
        )
    )
    report.add_issue(
        LintIssue(
            severity=LintSeverity.STYLE,
            code="STYLE",
            message="style",
            file_path="view.json",
        )
    )

    assert report.issues == []
    assert report.summary == {}


def test_report_can_include_advisory():
    report = LintReport(include_advisory=True)
    report.add_issue(
        LintIssue(
            severity=LintSeverity.INFO,
            code="INFO",
            message="info",
            file_path="view.json",
        )
    )

    assert [issue.code for issue in report.issues] == ["INFO"]
    assert report.summary == {"info": 1}


def test_configure_console_encoding_uses_utf8_when_available(monkeypatch):
    calls = []

    class Stream:
        def reconfigure(self, **kwargs):
            calls.append(kwargs)

    monkeypatch.setattr("sys.stdout", Stream())
    monkeypatch.setattr("sys.stderr", Stream())

    configure_console_encoding()

    assert calls == [
        {"encoding": "utf-8", "errors": "replace"},
        {"encoding": "utf-8", "errors": "replace"},
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

    def test_title_case_component_name_passes_default_pascalcase_policy(self):
        linter = JsonLinter(component_style="PascalCase")
        data = {
            "root": {
                "type": "ia.container.flex",
                "meta": {"name": "MES Station ID Editor"},
                "children": [],
            }
        }
        linter._check_json_structure(data, "test.json")
        component_errors = [e for e in linter.errors if e.error_type == "component"]
        assert len(component_errors) == 0

    def test_custom_component_regex_does_not_allow_title_case_fallback(self):
        linter = JsonLinter(component_style_rgx=r"^[A-Z][a-z]+$")
        data = {
            "root": {
                "type": "ia.container.flex",
                "meta": {"name": "MES Station ID Editor"},
                "children": [],
            }
        }
        linter._check_json_structure(data, "test.json")
        component_errors = [e for e in linter.errors if e.error_type == "component"]
        assert {e.name for e in component_errors} == {"MES Station ID Editor"}

    def test_non_component_name_fields_are_not_component_names(self):
        linter = JsonLinter(component_style="PascalCase")
        data = {
            "root": {
                "type": "ia.container.flex",
                "meta": {"name": "Root"},
                "props": {
                    "breakpoints": [
                        {"name": "sm"},
                        {"name": "md"},
                    ],
                    "items": [{"name": "process step one"}],
                },
                "children": [],
            }
        }
        linter._check_json_structure(data, "test.json")
        component_errors = [e for e in linter.errors if e.error_type == "component"]
        assert len(component_errors) == 0


def test_style_checker_allows_numbered_pascalcase_names():
    checker = StyleChecker("PascalCase")

    assert checker.is_correct_style("Fastener1")
    assert checker.is_correct_style("Ref1Btn")
    assert checker.is_correct_style("CalibrationRef3Marker")


def test_style_checker_allows_numbered_camelcase_names():
    checker = StyleChecker("camelCase")

    assert checker.is_correct_style("station1Name")
    assert checker.is_correct_style("step330Result")
