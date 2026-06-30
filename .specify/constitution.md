# Constitution — Offline DocScan

## Project Identity
- **Name**: Offline DocScan (docscan-cli)
- **Version**: 0.1.0
- **License**: GNU Affero General Public License v3.0 or later (AGPLv3+)
- **Purpose**: Privacy-first, CPU-only document scanning that extracts structured data from unstructured documents (PDFs, images, text) using local LLM inference.

## Core Principles

1. **Privacy First** — All processing happens offline. No data leaves the device.
2. **CPU-Only Processing** — No GPU required. Runs on any modern CPU.
3. **Open Source Transparency** — Fully open source under AGPLv3. The community can audit, modify, and distribute.
4. **Quality First** — Comprehensive testing, type safety, and code quality enforcement (Black, Ruff, MyPy).
5. **Security by Design** — Secret scanning (Gitleaks), dependency auditing (pip-audit), and security linting (Bandit, Semgrep) are mandatory in CI.
6. **Documentation Excellence** — Every feature is documented in specs, README, and user manual before implementation.
7. **CI/CD Automation** — All checks (lint, type-check, security, test) run automatically. No manual gating.
8. **Spec-Driven Development** — Every feature starts as a spec under `specs/`. Implementation begins only after spec approval.

## Technical Standards

### Code Style
- **Formatter**: Black (line-length: 100)
- **Linter**: Ruff (rules: E, F, I, N, W, UP)
- **Type Checker**: MyPy (strict mode)
- **Python Version**: 3.11+

### Commit Convention
- Format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Enforced by conventional-pre-commit hook and CI commit-quality job.

### Branching Strategy
- `main` — Production-ready
- `feature/*` — New features
- `bugfix/*` — Bug fixes
- `hotfix/*` — Critical fixes

### Testing Requirements
- Framework: pytest
- Minimum coverage: 50%
- Coverage enforced in CI via --cov-fail-under=50

### Security Requirements
- Secret scanning: Gitleaks (100+ patterns)
- Dependency audit: pip-audit
- Static analysis: Bandit, Semgrep
- All security jobs must pass before merge.

## Governance

### Decision Making Process
- Technical decisions are documented in specs.
- Specs require team review and approval before implementation.
- Architectural changes require consensus among core contributors.

### Contribution Process
1. Fork or create a feature branch.
2. Write spec under `specs/NNN-feature-name/`.
3. Implement the feature.
4. Ensure all CI checks pass.
5. Submit merge request for review.

### Code Review Process
- All code must be reviewed before merging.
- Reviewers check: correctness, test coverage, adherence to standards, security.
- CI must be green before merge.
