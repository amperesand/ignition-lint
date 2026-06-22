# Getting Started Guide (Deprecated)

> **This page is outdated.** Please refer to the current documentation:
> - [Installation](./getting-started/installation.md)
> - [Basic Usage](./getting-started/basic-usage.md)
> - [CLI Reference](./guides/cli-reference.md)

**Quick setup guide for using the Empirical Ignition Perspective Component Schema validation tools.**

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or newer** installed
- **UV package manager** (recommended) or pip
- Access to **Ignition Perspective project files**
- Basic familiarity with **Ignition development**

## 🛠️ Installation

### Option 1: Using UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup the project
git clone <repository-url>
cd empirical-ignition-perspective-component-schema

# Install dependencies
uv sync
```

### Option 2: Using pip

```bash
# Clone the project
git clone <repository-url>
cd empirical-ignition-perspective-component-schema

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Basic Usage

### 1. Lint Any Directory

Point the linter at any directory and it recursively finds `view.json` and `.py` files:

```bash
# Lint everything under a folder
ignition-lint --target /path/to/any/folder

# With detailed output
ignition-lint -t /path/to/any/folder --verbose

# JSON output for programmatic use
ignition-lint -t /path/to/any/folder --report-format json
```

### 2. Lint a Full Ignition Project

If your directory follows the standard Ignition layout:

```bash
# All checks (Perspective, naming, scripts)
ignition-lint --project /path/to/ignition/project --profile full
```

### 3. Lint a Subdirectory

Focus on just one part of the project:

```bash
# Only Perspective views in a specific folder
ignition-lint -t /path/to/views/MyScreen --checks perspective

# Only scripts
ignition-lint -t /path/to/scripts --checks scripts
```

## 📊 Understanding Results

### Severity Levels

- **❌ ERROR**: Critical issues that will cause runtime failures
- **⚠️ WARNING**: Compatibility or best practice issues
- **ℹ️ INFO**: Informational insights and suggestions
- **💄 STYLE**: Code style and documentation improvements

### Common Issues and Fixes

#### Component Schema Violations
```bash
# Example error
❌ SCHEMA_VALIDATION: 'style-list' is not one of ['scalar', 'color', 'object']

# Fix: Update the binding transform outputType
"outputType": "scalar"  // Instead of "style-list"
```

#### Jython Script Issues
```bash
# Example error
❌ JYTHON_IGNITION_INDENTATION_REQUIRED: Lines [1, 2] have no indentation

# Fix: Ensure ALL lines in Ignition inline scripts are indented
if value == -1:     # ❌ No indentation
    return False

    if value == -1:     # ✅ Properly indented
        return False
```

#### Python Syntax Issues
```bash
# Example error
❌ SYNTAX_ERROR: Missing parentheses in call to 'print'

# Fix: Use function syntax instead of statement
print 'hello'       # ❌ Python 2 style
print('hello')      # ✅ Python 3 compatible
```

## 🔧 Configuration

### Project-Specific Configuration

Create a `.ignition-lint.json` file in your project root:

```json
{
  "perspective": {
    "views_directory": "com.inductiveautomation.perspective/views",
    "strict_mode": true,
    "ignore_patterns": ["**/temp/**", "**/backup/**"]
  },
  "scripts": {
    "script_directory": "ignition/script-python",
    "python_version": "2.7",
    "check_imports": true
  },
  "output": {
    "format": "json",
    "include_suggestions": true,
    "verbose": false
  }
}
```

### IDE Integration

#### VSCode Setup

1. Install the Python extension
2. Add to your `settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "files.associations": {
    "*.json": "jsonc"
  },
  "json.schemas": [
    {
      "fileMatch": ["**/perspective/views/**/view.json"],
      "url": "./schemas/core-ia-components-schema-robust.json"
    }
  ]
}
```

#### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/amperesand/ignition-lint
    rev: main
    hooks:
      - id: ignition-lint
```

## 🎯 Common Workflows

### Development Workflow
```bash
# 1. Edit your Perspective views or scripts
# 2. Validate changes
ignition-lint --target path/to/modified/views --profile full --fail-on error

# 3. Fix any issues found
# 4. Re-validate to confirm fixes
# 5. Commit your changes
```

### CI/CD Integration
```bash
# Add to your CI pipeline
name: Validate Ignition Project
run: |
  ignition-lint --target projects --profile full --schema-mode robust --fail-on error
```

### Code Review Process
```bash
# Before creating a pull request
uv run python tools/ignition-perspective-linter.py --target . --output pr-validation.json

# Share the validation results with your team
# Address any ERROR or WARNING level issues
# Document any intentional deviations
```

## 🐛 Troubleshooting

### Common Installation Issues

**UV not found**:
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart your terminal
```

**Permission errors**:
```bash
# Use user installation
pip install --user -r requirements.txt
```

**Module not found errors**:
```bash
# Ensure you're in the right directory and environment
cd empirical-ignition-perspective-component-schema
uv sync  # or pip install -r requirements.txt
```

### Common Validation Issues

**Too many style issues**:
```bash
# Suppress noisy rules during initial adoption
ignition-lint -p ./my-project --profile full --ignore-codes NAMING_PARAMETER,MISSING_DOCSTRING,LONG_LINE

# Or create a .ignition-lintignore file for path-based suppression
# See docs/SUPPRESSION.md for the full guide
```

**False positives on valid code**:
- Suppress individual lines with `# ignition-lint: disable=CODE` (Python scripts only)
- Use `.ignition-lintignore` to exclude generated or template directories
- Check if your Ignition version is supported
- Report persistent false positives as GitHub issues

**Performance with large projects**:
```bash
# Process directories in smaller batches
uv run python tools/ignition-perspective-linter.py --target ./views/specific-folder
```

## 📚 Next Steps

1. **Read the Documentation**: Explore `docs/` for detailed guides
2. **Review Examples**: Check `examples/` for real-world usage patterns  
3. **Integrate with Your Workflow**: Set up pre-commit hooks and CI/CD
4. **Customize for Your Project**: Configure validation rules for your needs
5. **Contribute Back**: Share improvements and report issues

## 🤝 Getting Help

- **Documentation**: Check the `docs/` directory
- **Examples**: Review the `examples/` directory
- **Issues**: Open a GitHub issue for bugs or questions
- **Community**: Join the discussion in project issues

---

**Next: Read [LINTER_USAGE.md](LINTER_USAGE.md) for detailed tool documentation**
