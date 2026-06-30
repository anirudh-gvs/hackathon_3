# 🤖 AGENTS.md — Offline DocScan Project Guidelines

## Project Overview

**Offline DocScan** is a privacy-first, CPU-only document scanning application developed for the **CPU First Hackathon**. The project extracts structured data from unstructured documents (PDFs, images, text) using local LLM inference.

### Core Principles

- 🔒 **Privacy First**: All processing happens offline, no data leaves the device
- 🚀 **CPU Only**: No GPU required, runs on any modern CPU
- 📦 **Local Inference**: Uses GGUF models for on-device LLM inference
- 🧪 **Quality First**: Comprehensive testing and code quality checks
- 🔄 **CI/CD Ready**: Automated pipelines for linting, testing, and security

---

## Project Structure

```
cpu_first_hackathon/
├── docscan/                    # Main package source code
│   ├── __init__.py
│   ├── cli.py                  # CLI entry point (Typer)
│   ├── extractor.py            # Text extraction from documents
│   ├── inference.py            # Local LLM inference
│   ├── schemas.py              # Output schema definitions
│   ├── storage.py              # Data storage utilities
│   ├── secret_scan.py          # Secret scanning for CI
│   ├── ci_checks.py            # CI validation scripts
│   └── check_commit.py         # Commit message validation
├── tests/                      # Test suite
│   ├── test_cli.py
│   ├── test_extractor.py
│   ├── test_inference.py
│   ├── test_schemas.py
│   ├── test_storage.py
│   └── fixtures/               # Test data
├── docs/                       # Documentation
│   ├── spec.md
│   ├── issues.md
│   └── work-division.md
├── scripts/                    # Utility scripts
│   └── download_model.sh
├── models/                     # GGUF model files (gitignored)
├── .gitlab-ci.yml              # CI/CD pipeline configuration
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # Project README
├── USER_MANUAL.md              # User documentation
├── PIPELINE_STATUS.md          # Pipeline status tracking
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
└── LICENSE                     # AGPL-3.0 License
```

---

## Development Environment Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

```bash
# 1. Clone the repository
git clone https://code.swecha.org/Gvs_Anirudh/cpu_first_hackathon.git
cd cpu_first_hackathon

# 2. Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install package with development dependencies
pip install -e ".[dev]"

# 4. Verify installation
docscan --help
```

---

## Code Style and Standards

### Python Code Style

- **Formatter**: Ruff (line length: 100)
- **Linter**: Ruff (rules: E, F, I, N, W, UP)
- **Type Checker**: Mypy (strict mode enabled)
- **Python Version**: 3.11+

### Code Quality Requirements

All code must pass the following checks before merging:

1. **Formatting**: `ruff format --check docscan/ tests/`
2. **Linting**: `ruff check --line-length 100 docscan/ tests/`
3. **Type Checking**: `mypy docscan/ --ignore-missing-imports --strict-optional`
4. **Security**: `bandit -r docscan/ -ll -f txt`
5. **Tests**: `pytest tests/ -v --cov=docscan --cov-report=term-missing --cov-fail-under=50`
6. **YAML Validation**: `yamllint .gitlab-ci.yml`

### Running Quality Checks Locally

```bash
# Format code
ruff format docscan/ tests/

# Lint code
ruff check docscan/ tests/

# Type check
mypy docscan/ --ignore-missing-imports --strict-optional

# Run tests with coverage
pytest tests/ -v --cov=docscan --cov-report=term-missing

# Run security scan
bandit -r docscan/ -ll

# Validate YAML
yamllint -d "{extends: default, rules: {line-length: {max: 200}, truthy: {check-keys: false}}}" .gitlab-ci.yml
```

---

## Git Workflow

### Branch Naming

- `main` - Production-ready code
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

### Commit Message Format

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(cli): add support for BMP image format
fix(extractor): handle corrupted PDF files gracefully
docs(manual): update installation instructions
test(inference): add tests for model loading
```

### Commit Quality Checks

The CI pipeline validates:
- Commit message format
- Commit message length
- No merge commits in feature branches

---

## CI/CD Pipeline

### Pipeline Stages

1. **lint** - Code quality checks
   - JSON syntax validation
   - Python formatting & linting (Ruff)
   - YAML syntax validation

2. **type-check** - Static type analysis
   - MyPy strict mode

3. **security** - Security scanning
   - Bandit security linter
   - Dependency audit (pip-audit)
   - Secret scanning

4. **test** - Unit and integration tests
   - pytest with coverage (50% minimum)
   - All tests must pass

5. **commit-quality** - Git commit validation
   - Commit message format
   - Commit history quality

### Runner Configuration

- **Tag**: `hackthon_3`
- **Platform**: Windows/PowerShell
- **Python**: 3.11
- **Path**: `C:\Users\aniru\AppData\Local\Programs\Python\Python311\python.exe`

### Pipeline Status

Check `PIPELINE_STATUS.md` for current pipeline state and known issues.

---

## Testing Guidelines

### Test Structure

- Unit tests for all modules
- Integration tests for CLI commands
- Fixtures in `tests/fixtures/`
- Minimum 50% code coverage required

### Writing Tests

```python
# Example test structure
import pytest
from docscan.module import function

def test_function_basic():
    """Test basic functionality."""
    result = function(input_data)
    assert result == expected_output

def test_function_edge_case():
    """Test edge case."""
    with pytest.raises(ValueError):
        function(invalid_input)
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=docscan --cov-report=term-missing

# Run specific test file
pytest tests/test_cli.py -v

# Run specific test
pytest tests/test_cli.py::test_scan_command -v
```

---

## Dependencies

### Core Dependencies

- `llama-cpp-python>=0.2.0` - LLM inference
- `pdfplumber>=0.10.0` - PDF text extraction
- `pytesseract>=0.3.10` - OCR functionality
- `Pillow>=10.0.0` - Image processing
- `pydantic>=2.0.0` - Data validation
- `typer>=0.9.0` - CLI framework
- `rich>=13.0.0` - Terminal formatting

### Development Dependencies

- `pytest>=8.0.0` - Testing framework
- `ruff>=0.3.0` - Code formatter & linter
- `mypy>=1.8.0` - Type checker

### Adding New Dependencies

1. Add to `pyproject.toml` under `[project.dependencies]` or `[project.optional-dependencies]`
2. Update documentation if needed
3. Test installation: `pip install -e .`
4. Ensure CI pipeline passes

---

## Important Notes

### Model Files

- GGUF model files are **not** tracked in git (see `.gitignore`)
- Default model: `models/phi3-mini-q4.gguf`
- Models should be downloaded separately
- See `scripts/download_model.sh` for model download script

### Sensitive Data

- **Never** commit API keys, tokens, or credentials
- Use `docscan/secret_scan.py` to check for secrets
- CI pipeline includes secret scanning
- Report any accidentally committed secrets immediately

### Documentation

- Update `README.md` for user-facing changes
- Update `USER_MANUAL.md` for usage instructions
- Update `docs/spec.md` for technical specifications
- Update `CHANGELOG.md` for version changes

### Windows Compatibility

- All CI jobs run on Windows/PowerShell runners
- Use PowerShell syntax in scripts
- Test on Windows before submitting PRs
- Use raw strings for Windows paths: `r"C:\path\to\file"`

---

## Common Tasks

### Adding a New CLI Command

1. Add command function in `docscan/cli.py`
2. Decorate with `@app.command()`
3. Add type hints and docstrings
4. Update `USER_MANUAL.md` with command documentation
5. Add tests in `tests/test_cli.py`
6. Run quality checks

### Adding a New Schema

1. Define schema in `docscan/schemas.py`
2. Add to `SchemaName` enum
3. Create schema validation logic
4. Add tests in `tests/test_schemas.py`
5. Update documentation

### Fixing a Bug

1. Create a test that reproduces the bug
2. Fix the bug
3. Verify test passes
4. Run full test suite
5. Update `CHANGELOG.md`

### Updating Dependencies

1. Update version in `pyproject.toml`
2. Test locally: `pip install -e ".[dev]"`
3. Run full test suite
4. Update `CHANGELOG.md` if needed

---

## Troubleshooting for Agents

### Common Issues

**Issue**: Tests fail with import errors
**Solution**: Ensure package is installed in development mode: `pip install -e .`

**Issue**: MyPy reports missing imports
**Solution**: Check `ignore_missing_imports = true` in `pyproject.toml` or add type stubs

**Issue**: Ruff linting errors
**Solution**: Run `ruff check docscan/ tests/` to see specific errors

**Issue**: Pipeline fails on Windows but works locally
**Solution**: Check for Unix-specific commands, use PowerShell-compatible syntax

**Issue**: Model not found during tests
**Solution**: Ensure test fixtures include mock models or skip model-dependent tests

---

## Resources

### Documentation

- **README.md** - Project overview and quick start
- **USER_MANUAL.md** - Comprehensive user guide
- **docs/spec.md** - Technical specifications
- **docs/issues.md** - Known issues and solutions
- **CONTRIBUTING.md** - Contribution guidelines
- **CHANGELOG.md** - Version history

### External Resources

- **Typer**: https://typer.tiangolo.com/
- **Rich**: https://rich.readthedocs.io/
- **Pydantic**: https://docs.pydantic.dev/
- **llama-cpp-python**: https://github.com/abetlen/llama-cpp-python
- **GitLab CI**: https://docs.gitlab.com/ee/ci/

---

## Contact and Support

- **Repository**: https://code.swecha.org/Gvs_Anirudh/cpu_first_hackathon
- **Issues**: Report bugs via GitLab Issues
- **Team**: CPU First Hackathon Team

---

## Quick Reference

### Essential Commands

```bash
# Install package
pip install -e ".[dev]"

# Run CLI
docscan --help
docscan scan <file> --schema receipt

# Run tests
pytest tests/ -v

# Format code
ruff format docscan/ tests/

# Lint code
ruff check docscan/ tests/

# Type check
mypy docscan/ --ignore-missing-imports --strict-optional

# Security scan
bandit -r docscan/ -ll
```

### File Locations

- Source code: `docscan/`
- Tests: `tests/`
- Documentation: `docs/`, `README.md`, `USER_MANUAL.md`
- Config: `pyproject.toml`, `.gitlab-ci.yml`
- Models: `models/` (not tracked in git)

---

**Last Updated**: 2024
**Version**: 0.1.0
**Maintainer**: DocScan Team
**License**: AGPL-3.0-or-later