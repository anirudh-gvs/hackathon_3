# 📄 Offline DocScan – Privacy-First Offline Document Scanner

## 📌 Project Overview

Offline DocScan is a privacy-focused document scanning application developed for the **CPU First Hackathon**. The application enables users to scan physical documents, automatically detect document boundaries, enhance image quality, and save documents as high-quality PDFs or images without requiring an internet connection.

Unlike many online scanning applications, Offline DocScan performs all document processing locally on the device, ensuring faster performance, complete privacy, and accessibility even in low-connectivity environments.

---

# 🚀 Features

## 👤 User Features

* Scan documents using the device camera
* Upload existing document images
* Automatic document edge detection
* Smart perspective correction
* Automatic cropping
* Image enhancement
* Brightness and contrast adjustment
* Generate high-quality PDF documents
* Save scanned images locally
* Works completely offline
* Fast document processing
* Privacy-first document handling

### 📄 Supported Input Formats

**Images**

* PNG
* JPG
* JPEG
* BMP

### 📤 Export Formats

* PDF
* PNG
* JPG

---

# 📸 Document Processing Workflow

```text
Capture / Upload Document
            │
            ▼
Automatic Edge Detection
            │
            ▼
Perspective Correction
            │
            ▼
Image Enhancement
            │
            ▼
Generate PDF / Image
            │
            ▼
Save Locally
```

---

# 🔒 Privacy & Offline Processing

Offline DocScan is designed with privacy as its primary goal.

### Features

* No internet connection required
* No cloud uploads
* Local image processing
* Secure document storage
* Fast on-device scanning

---

# 🏗️ Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript

## Backend

* Python

## Image Processing

* OpenCV
* Pillow
* NumPy

## PDF Generation

* ReportLab (or the PDF library your project uses)

## Version Control

* Git
* GitLab

---

# 📂 Project Structure

```text
offline-docscan/

│
├── app.py
├── scanner.py
├── image_processing.py
├── pdf_generator.py
├── utils.py
├── requirements.txt
├── README.md
├── uploads/
├── output/
├── static/
├── templates/
└── assets/
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone git@ssh.code.swecha.org:Gvs_Anirudh/cpu_first_hackathon.git
```

Move into the project directory:

```bash
cd cpu_first_hackathon
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Application

Start the application:

```bash
python app.py
```

Open the application in your browser (if applicable):

```text
http://localhost:5000
```

---

# 🖼️ How It Works

1. Open Offline DocScan.
2. Capture a document or upload an image.
3. The application automatically detects document edges.
4. The document is cropped and perspective corrected.
5. Image quality is enhanced for better readability.
6. Save the document as a PDF or image.

---

# 🧠 Core Functionalities

Implemented:

* Automatic document detection
* Smart cropping
* Perspective correction
* Image enhancement
* PDF generation
* Offline processing
* Local document storage

---

# 🌍 Use Cases

Offline DocScan is useful for:

* Students digitizing notes
* Teachers scanning assignments
* Office document management
* Government paperwork
* Receipts and invoices
* Identity documents
* Medical prescriptions
* Personal document archiving

---

# 🧪 Code Quality

Offline DocScan maintains production-quality code through comprehensive static analysis, linting, security scanning, and automated quality checks.

## Code Quality Tools

### 🔍 Static Analysis & Linting

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Ruff** | Code formatter & linter | Line length: 100, Rules: E, F, I, N, W, UP |
| **Pylint** | Deep code analysis | Comprehensive checks, 7.0+ score required |
| **Flake8** | Style guide enforcement | PEP 8 compliance, complexity checks |
| **MyPy** | Static type checker | Strict mode enabled |
| **Pyupgrade** | Python modernization | Auto-upgrade to Python 3.11+ syntax |
| **Vulture** | Dead code detection | Finds unused code, 60% confidence threshold |

### 🔒 Security Scanning

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Semgrep** | Security pattern matching | OWASP Top 10, secrets detection, custom rules |
| **Bandit** | Security linter | Common vulnerability patterns |
| **pip-audit** | Dependency vulnerability scanner | Checks for known CVEs |
| **Gitleaks** | Secret scanning | Detects 100+ secret types, prevents credential leaks |

### ✅ Testing & Coverage

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **pytest** | Test framework | Minimum 50% coverage required |
| **pytest-cov** | Coverage reporting | Term-missing output format |

## Running Quality Checks

### Install Development Dependencies

```bash
# Install with all development tools
pip install -e ".[dev]"

# Or install specific tools
pip install ruff pylint flake8 mypy semgrep pyupgrade bandit pytest
```

### Code Formatting

```bash
# Format code with Ruff
ruff format docscan/ tests/

# Check formatting without modifying files
ruff format --check docscan/ tests/
```

### Linting

```bash
# Run Ruff linter (fast)
ruff check docscan/ tests/

# Run Pylint (comprehensive analysis)
pylint docscan/ --rcfile=.pylintrc --fail-under=7.0

# Run Flake8 (PEP 8 compliance)
flake8 docscan/ --config=.flake8 --statistics --show-source
```

### Type Checking

```bash
# Run MyPy type checker
mypy docscan/ --ignore-missing-imports --strict-optional
```

### Security Scanning

```bash
# Run Semgrep security scanner
semgrep --config=.semgrep.yml --error docscan/

# Run Bandit security linter
bandit -r docscan/ -ll

# Scan dependencies for vulnerabilities
pip-audit --skip-editable

# Run Gitleaks secret scanner
gitleaks detect --config=.gitleaks.toml --source=. --report-path=gitleaks-report.json --report-format=json --redact
```

### Python Modernization

```bash
# Check for Python modernization opportunities
pyupgrade --py311-plus docscan/*.py

# Automatically apply safe upgrades
pyupgrade --py311-plus --exit-zero-even-if-changed docscan/*.py
```

### Dead Code Detection

```bash
# Find unused code with Vulture
vulture docscan/ tests/ --config=.vulture.toml --min-confidence 60

# Show verbose output
vulture docscan/ tests/ --config=.vulture.toml --verbose

# Sort by confidence (highest first)
vulture docscan/ tests/ --config=.vulture.toml --sort-by-confidence
```

### Run All Tests

```bash
# Run test suite with coverage
pytest tests/ -v --cov=docscan --cov-report=term-missing --cov-fail-under=50

# Run specific test file
pytest tests/test_cli.py -v

# Run specific test
pytest tests/test_cli.py::test_scan_command -v
```

## Quality Gates

All code must pass the following checks before merging:

1. ✅ **Formatting**: Ruff formatting check passes
2. ✅ **Linting**: Ruff, Pylint (≥7.0 score), and Flake8 checks pass
3. ✅ **Type Checking**: MyPy strict mode passes
4. ✅ **Security**: Semgrep and Bandit scans pass with no errors
5. ✅ **Dependencies**: No critical vulnerabilities in dependencies
6. ✅ **Tests**: All tests pass with ≥50% coverage
7. ✅ **Modernization**: Pyupgrade check passes (warnings allowed)

## CI/CD Integration

All quality checks run automatically in GitLab CI/CD on:
- Every push to main/develop branches
- Every merge request
- Manual pipeline triggers

View pipeline status in the GitLab CI/CD section of your repository.

## Code Style Guidelines

### Python Style

- **Line Length**: 100 characters
- **Indentation**: 4 spaces
- **Quotes**: Double quotes preferred
- **Type Hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions/classes
- **Imports**: Sorted with Ruff (isort)

### Best Practices

- Use `pathlib.Path` instead of `os.path`
- Use f-strings instead of % formatting or .format()
- Use context managers for file operations
- Avoid mutable default arguments
- Use explicit exception handling
- Write tests for all new functionality

## Pre-commit Hooks (Optional)

Install pre-commit hooks to run checks before each commit:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### What Pre-commit Hooks Do

Pre-commit hooks automatically run quality checks before each commit:

1. **File Checks**: Large files, merge conflicts, private keys, AWS credentials
2. **Formatting**: Ruff (code formatter)
3. **Linting**: Ruff (fast linter with auto-fix)
4. **Type Checking**: MyPy (static type analysis)
5. **Import Sorting**: isort (import organization)
6. **Deep Analysis**: Pylint (comprehensive code analysis)
7. **Style Guide**: Flake8 (PEP 8 compliance)
8. **Security**: Gitleaks (secret scanning)
9. **Modernization**: Pyupgrade (Python 3.11+ syntax)
10. **Dead Code**: Vulture (unused code detection)
11. **Markdown**: markdownlint (Markdown style)
12. **YAML**: yamllint (YAML syntax)
13. **Shell**: shellcheck (shell script linting)
14. **Commit Messages**: Conventional commits validation

### Bypassing Hooks (Not Recommended)

```bash
# Skip all hooks (use sparingly)
git commit -m "fix: urgent hotfix" --no-verify

# Skip specific hook
# Add .pre-commit-config.yaml to skip specific hooks
```

## Automated Changelog (Git-Cliff)

Offline DocScan uses [git-cliff](https://git-cliff.org/) to automatically generate changelogs from conventional commits.

### How It Works

Git-cliff parses git commit history and generates a formatted CHANGELOG.md file organized by:
- Commit type (feat, fix, docs, etc.)
- Scope (cli, extractor, inference, etc.)
- Breaking changes
- Issue references

### Generating Changelog

```bash
# Install git-cliff
pip install git-cliff

# Generate changelog from git history
git cliff --config .cliff.toml

# Generate and write to CHANGELOG.md
git cliff --config .cliff.toml -o CHANGELOG.md

# Preview unreleased changes
git cliff --config .cliff.toml --unreleased

# Generate for specific version
git cliff --config .cliff.toml --tag v0.1.0
```

### Commit Message Format

Use conventional commits for automatic changelog generation:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature (🚀 Features)
- `fix`: Bug fix (🐛 Bug Fixes)
- `docs`: Documentation (📚 Documentation)
- `style`: Code style (🎨 Style)
- `refactor`: Refactoring (♻️ Refactoring)
- `perf`: Performance (⚡ Performance)
- `test`: Tests (🧪 Tests)
- `build`: Build system (🔧 Build System)
- `ci`: CI/CD changes (🔧 Build System)
- `security`: Security (🔒 Security)
- `chore`: Maintenance (🧹 Chores)
- `break`: Breaking changes (💥 Breaking Changes)

**Scopes** (optional):
- `cli`: Command line interface
- `extractor`: Text extraction
- `inference`: LLM inference
- `schemas`: Data schemas
- `storage`: Data storage
- `security`: Security scanning
- `ci`: CI/CD
- `deps`: Dependencies
- `docs`: Documentation
- `tests`: Tests

**Examples**:
```bash
# Feature
git commit -m "feat(cli): add support for BMP image format"

# Bug fix
git commit -m "fix(extractor): handle corrupted PDF files gracefully"

# Documentation
git commit -m "docs(manual): update installation instructions"

# Breaking change
git commit -m "feat(api)!: change output schema structure

BREAKING CHANGE: The output schema now uses nested objects instead of flat structure."
```

### Changelog Structure

Generated CHANGELOG.md includes:
- Version numbers with dates
- Categorized changes (Features, Bug Fixes, etc.)
- Scope indicators
- Issue/PR links
- Breaking change warnings
- Contributor credits (optional)

### CI/CD Integration

Git-cliff can be integrated into CI/CD to automatically update CHANGELOG.md on releases:

```bash
# In .gitlab-ci.yml (example)
generate-changelog:
  stage: deploy
  script:
    - git cliff --config .cliff.toml -o CHANGELOG.md
    - git add CHANGELOG.md
    - git commit -m "chore: update changelog [skip ci]"
    - git push
```

### Configuration

See `.cliff.toml` for full configuration:
- Commit group definitions
- Scope mappings
- Template customization
- Version bumping rules
- Release notes generation

## Troubleshooting

### Pylint Score Too Low

If Pylint reports a score below 7.0:
1. Review the reported issues
2. Fix critical errors and warnings
3. Some warnings can be justified (see `.pylintrc`)
4. Run `pylint docscan/ --rcfile=.pylintrc` for details

### Flake8 Conflicts with Ruff

Some Flake8 rules conflict with Ruff formatting. We've configured `.flake8` to ignore:
- E501: Line too long (Ruff handles this)
- W503: Line break before binary operator (Ruff style)
- E203: Whitespace before ':' (Ruff style)

### Semgrep False Positives

If Semgrep reports false positives:
1. Review the rule in `.semgrep.yml`
2. Add exception comments if justified
3. Report false positives to the security team

## Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pylint Documentation](https://pylint.pycqa.org/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Semgrep Documentation](https://semgrep.dev/docs/)
- [Pyupgrade Documentation](https://github.com/asottleresearch/pyupgrade)

---

# 🚀 Deployment

The project can be deployed on:

* Local Machine
* Docker
* Linux Server
* Windows
* Raspberry Pi

---

# 🔒 Security Practices

Implemented:

* Offline document processing
* No cloud dependency
* Local file storage
* No sensitive data transmission
* Privacy-first architecture

---

# 📚 Skills Learned

* Python Development
* Computer Vision
* OpenCV
* Image Processing
* PDF Generation
* Git Workflow
* GitLab CI/CD
* UI Development
* Offline Application Design
* Privacy-Focused Software Development

---

# 🚀 Future Improvements

Planned Features:

* OCR (Optical Character Recognition)
* Searchable PDFs
* Multi-page document scanning
* QR & Barcode Scanner
* Digital Signature Support
* Password-Protected PDFs
* Batch Scanning
* Mobile Application
* Multi-language Interface
* AI-based document enhancement

---

# 📸 Screenshots

Add screenshots here.

```text
docs/home.png
docs/scanner.png
docs/output.png
```

---

# 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 or later (AGPLv3+)**.

This project was developed as part of the **CPU First Hackathon**.

## Why AGPLv3?

* **Network Interaction Compliance**: Ensures that if the software is run on a server, users can access the source code
* **User Freedom**: Protects the freedom to use, study, share, and modify the software
* **Copyleft**: Ensures that derivative works remain open source
* **Community**: Encourages collaboration and contributions back to the community

## License Details

* **License**: GNU Affero General Public License v3.0 or later (AGPLv3+)
* **Copyright**: DocScan Team
* **Year**: 2024

For the full license text, see the [LICENSE](LICENSE) file in this repository.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

---

# 👨‍💻 Team

Developed by:

* Gvs Anirudh
* Md Afsar
* CPU First Hackathon Team

---

# 📌 Project Status

✅ Active Development

Completed:

* Offline document scanning
* Automatic edge detection
* Image enhancement
* PDF generation
* Local document storage

Upcoming Features:

* OCR Integration
* Cloud Sync (Optional)
* AI Enhancement
* Mobile Version
* Digital Signatures
* Batch Document Processing

---

# 🙏 Acknowledgements

We sincerely thank the **CPU First Hackathon** organizers, mentors, and the open-source community for providing the guidance, resources, and inspiration that made this project possible.
