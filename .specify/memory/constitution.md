# Constitution — Offline DocScan (Memory)

## Project Identity
- **Name**: Offline DocScan (docscan-cli)
- **Version**: 0.1.0
- **License**: GNU Affero General Public License v3.0 or later (AGPLv3+)
- **Purpose**: Privacy-first, CPU-only document scanning that extracts structured data from unstructured documents (PDFs, images, text) using local LLM inference.

## Core Principles

1. **Privacy First** — All processing happens offline. No data leaves the device.
2. **CPU-Only Processing** — No GPU required. Runs on any modern CPU.
3. **Open Source Transparency** — Fully open source under AGPLv3.
4. **Quality First** — Comprehensive testing, type safety, and code quality enforcement.
5. **Security by Design** — Secret scanning, dependency auditing, and security linting in CI.
6. **Documentation Excellence** — Features documented in specs, README, and user manual.
7. **CI/CD Automation** — All checks run automatically. No manual gating.
8. **Spec-Driven Development** — Every feature starts as a spec under `specs/`.

## Technical Standards
- **Formatter**: Black (line-length: 100)
- **Linter**: Ruff (rules: E, F, I, N, W, UP)
- **Type Checker**: MyPy (strict mode)
- **Python Version**: 3.11+
- **Commits**: Conventional Commits — `type(scope): description`
- **Testing**: pytest, minimum 50% coverage
- **Security**: Gitleaks, pip-audit, Bandit, Semgrep

## Governance
- Technical decisions documented in specs with team approval.
- Feature branches: `feature/*`, `bugfix/*`, `hotfix/*`.
- All code reviewed before merging to `main`.
- CI must be green before merge.
