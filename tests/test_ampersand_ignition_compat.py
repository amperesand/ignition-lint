import json

from jsonschema import validate

from ignition_lint.perspective.linter import IgnitionPerspectiveLinter
from ignition_lint.reporting import LintSeverity
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


def _lint_view(view_data: dict) -> list:
    linter = IgnitionPerspectiveLinter()
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "view.json"
        path.write_text(json.dumps(view_data), encoding="utf-8")
        linter.lint_file(str(path))
    return linter.issues


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


def test_case_is_a_known_ignition_expression_function():
    expression = "case({view.custom.state}, 'idle', '#AAA', 'run', '#0F0', '#F00')"

    assert "EXPR_UNKNOWN_FUNCTION" not in _expression_codes(expression)


def test_ignition_color_expression_functions_are_known():
    expression = "gradient({this.custom.temp}, 55, 100, color(196,227,236), darker(color(245,196,194)))"

    assert "EXPR_UNKNOWN_FUNCTION" not in _expression_codes(expression)


def test_double_quoted_strings_and_comments_do_not_create_adjacent_errors():
    expression = """// Convert to Celsius if necessary
if({session.props.locale} = "en-US",
    {value},
    ({value} - 32) * 0.5556)"""

    codes = _expression_codes(expression)
    assert "EXPR_ADJACENT_EXPRESSIONS" not in codes
    assert "EXPR_UNMATCHED_QUOTE" not in codes


def test_exported_value_index_expression_is_not_a_syntax_error():
    expression = """"Selected Value: " +
if(len({value}) > 0 && indexOf({value}[0], "/") > -1,
    tag({value}[0]),
    '')"""

    assert "EXPR_EXTERNAL_INDEX_ACCESS" not in _expression_codes(expression)


def test_function_like_text_inside_strings_is_not_validated_as_expression_code():
    expression = (
        "if({view.custom.active}, 'rgba(42, 197, 127, 0.10)', "
        "'url(/system/images/manuals/step(1).png)')"
    )

    codes = _expression_codes(expression)
    assert "EXPR_UNKNOWN_FUNCTION" not in codes
    assert "EXPR_UNMATCHED_PAREN" not in codes


def test_property_like_text_inside_strings_is_not_validated_as_expression_code():
    expression = "'Use {root.custom.path} only in docs, not as a binding ref'"

    assert "EXPR_ROOT_PROPERTY_REF" not in _expression_codes(expression)


def test_http_binding_type_is_valid_perspective_export():
    issues = _lint_view(
        {
            "custom": {},
            "root": {
                "type": "ia.container.flex",
                "meta": {"name": "Root"},
                "propConfig": {
                    "custom.response": {
                        "binding": {
                            "type": "http",
                            "config": {
                                "url": '"https://example.com/api/status"',
                                "method": "GET",
                            },
                        }
                    }
                },
            },
        }
    )

    assert "INVALID_BINDING_TYPE" not in {i.code for i in issues}


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


def test_schema_validation_drift_is_warning_not_ci_error():
    issues = _lint_view(
        {
            "custom": {},
            "root": {
                "type": "ia.vendor.custom-widget",
                "meta": {"name": "VendorWidget"},
                "props": {"moduleSpecific": True},
            },
        }
    )

    schema_issues = [i for i in issues if i.code == "SCHEMA_VALIDATION"]
    assert schema_issues
    assert all(i.severity == LintSeverity.WARNING for i in schema_issues)


def test_flex_children_do_not_require_position_objects():
    issues = _lint_view(
        {
            "custom": {},
            "root": {
                "type": "ia.container.flex",
                "meta": {"name": "Root"},
                "children": [
                    {"type": "ia.display.label", "meta": {"name": "StatusLabel"}}
                ],
            },
        }
    )

    assert "MISSING_CHILD_POSITION" not in {i.code for i in issues}


def test_coordinate_children_without_position_remain_warning():
    issues = _lint_view(
        {
            "custom": {},
            "root": {
                "type": "ia.container.coord",
                "meta": {"name": "Root"},
                "children": [
                    {"type": "ia.display.label", "meta": {"name": "StatusLabel"}}
                ],
            },
        }
    )

    matching = [i for i in issues if i.code == "MISSING_CHILD_POSITION"]
    assert matching
    assert all(i.severity == LintSeverity.WARNING for i in matching)
