import json

from jsonschema import validate

from ignition_lint.schemas import schema_path_for
from ignition_lint.scripts.linter import IgnitionScriptLinter
from ignition_lint.validators.expression import ExpressionValidator


def _script_codes(linter: IgnitionScriptLinter) -> set[str]:
    return {issue.code for issue in linter.issues}


def _expression_codes(expression: str) -> set[str]:
    validator = ExpressionValidator()
    issues = validator.validate_expression(
        expression,
        "binding",
        "view.json",
        "view.custom.ts",
        "view",
    )
    return {issue.code for issue in issues}


def test_standalone_script_linter_accepts_jython_exception_syntax(tmp_path):
    script_dir = tmp_path / "script-python"
    script_dir.mkdir()
    (script_dir / "code.py").write_text(
        "\n".join(
            [
                "def run():",
                "    try:",
                "        return system.date.now()",
                "    except Exception, err:",
                "        print err",
            ]
        ),
        encoding="utf-8",
    )

    linter = IgnitionScriptLinter()
    linter.lint_directory(str(script_dir))

    codes = _script_codes(linter)
    assert "SYNTAX_ERROR" not in codes
    assert "JYTHON_PRINT_STATEMENT" in codes


def test_expression_escaped_quotes_inside_date_format_are_one_string():
    expression = r"dateFormat(addDays(now(0), -7), 'yyyy-MM-dd\'T\'00:00:00')"

    assert "EXPR_ADJACENT_EXPRESSIONS" not in _expression_codes(expression)


def test_robust_schema_accepts_gateway_component_types_and_null_scripts():
    with schema_path_for("robust").open(encoding="utf-8") as handle:
        schema = json.load(handle)

    for component_type in [
        "ia.display.pdf-viewer",
        "ia.input.barcodescannerinput",
        "ia.navigation.link",
        "ia.shapes.svg",
    ]:
        validate({"type": component_type}, schema)

    validate(
        {
            "type": "ia.container.flex",
            "scripts": {
                "customMethods": None,
                "extensionFunctions": None,
                "messageHandlers": [],
            },
        },
        schema,
    )
