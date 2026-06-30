# Spec 001: Core CLI Implementation

**Feature ID**: SPEC-001  
**Status**: Implemented  
**Created**: 2024-01-01  
**Last Updated**: 2024-01-01  
**Author**: DocScan Team  
**Reviewers**: DocScan Team

---

## Overview

Implement the core command-line interface for Offline DocScan using Typer, providing a user-friendly interface for document scanning and structured data extraction.

---

## Problem Statement

### What problem does this solve?

Users need a simple, intuitive command-line interface to:
- Scan documents (PDFs, images, text files)
- Extract structured data using local LLM inference
- Save results in JSON format
- Configure extraction schemas

### Why is this important?

A well-designed CLI is the primary user interface for Offline DocScan. It must be:
- Easy to use for non-technical users
- Powerful enough for advanced users
- Consistent with Unix philosophy
- Well-documented with helpful error messages

### Who benefits from this?

- End users scanning documents
- Developers integrating DocScan into workflows
- System administrators automating document processing

---

## Requirements

### Functional Requirements

1. **FR-001**: Implement `scan` command
   - Priority: High
   - Acceptance Criteria: Command accepts file path, schema, and output options

2. **FR-002**: Implement `version` command
   - Priority: Medium
   - Acceptance Criteria: Command displays version information

3. **FR-003**: Support multiple schemas
   - Priority: High
   - Acceptance Criteria: receipt, medical, and generic schemas available

4. **FR-004**: Verbose output mode
   - Priority: Medium
   - Acceptance Criteria: Shows extracted text before inference

5. **FR-005**: Custom model path
   - Priority: Medium
   - Acceptance Criteria: Users can specify alternative GGUF models

### Non-Functional Requirements

1. **NFR-001**: Response time
   - Priority: High
   - Acceptance Criteria: CLI starts in <2 seconds

2. **NFR-002**: Error handling
   - Priority: High
   - Acceptance Criteria: Clear error messages for all failure modes

3. **NFR-003**: Help documentation
   - Priority: High
   - Acceptance Criteria: Auto-generated help for all commands

### Constraints

- Must use Typer for CLI framework
- Must support Python 3.11+
- Must work on Windows, macOS, and Linux
- Must be CPU-only (no GPU dependencies)

---

## Design

### Architecture

```
docscan/cli.py (Typer app)
    ├── scan command
    │   ├── File validation
    │   ├── Text extraction (calls extractor)
    │   ├── LLM inference (calls inference)
    │   └── Output formatting
    └── version command
        └── Display version info
```

### Components

1. **CLI Module** (`docscan/cli.py`)
   - Location: `docscan/cli.py`
   - Responsibility: Command-line interface and user interaction
   - Dependencies: typer, rich, extractor, inference, schemas

2. **Text Extractor** (`docscan/extractor.py`)
   - Location: `docscan/extractor.py`
   - Responsibility: Extract text from PDFs, images, and text files
   - Dependencies: pdfplumber, pytesseract, Pillow

3. **LLM Inference** (`docscan/inference.py`)
   - Location: `docscan/inference.py`
   - Responsibility: Run local LLM inference using llama-cpp-python
   - Dependencies: llama-cpp-python, schemas

4. **Schemas** (`docscan/schemas.py`)
   - Location: `docscan/schemas.py`
   - Responsibility: Define output schemas (receipt, medical, generic)
   - Dependencies: pydantic

### Data Flow

```
User Input (CLI)
    ↓
File Path Validation
    ↓
Text Extraction (PDF/Image/TXT)
    ↓
LLM Inference (CPU-only)
    ↓
Schema Validation (Pydantic)
    ↓
JSON Output (stdout or file)
```

### API Changes

No external API. CLI commands:
```bash
docscan scan <file> --schema <type> --output <file>
docscan version
```

---

## Implementation Plan

### Tasks

1. **Task 1**: Set up Typer CLI structure
   - Priority: High
   - Estimated Effort: 2 hours
   - Dependencies: None
   - Status: ✅ Complete

2. **Task 2**: Implement scan command
   - Priority: High
   - Estimated Effort: 4 hours
   - Dependencies: Task 1
   - Status: ✅ Complete

3. **Task 3**: Implement version command
   - Priority: Medium
   - Estimated Effort: 1 hour
   - Dependencies: Task 1
   - Status: ✅ Complete

4. **Task 4**: Add Rich terminal formatting
   - Priority: Medium
   - Estimated Effort: 2 hours
   - Dependencies: Task 2
   - Status: ✅ Complete

5. **Task 5**: Add error handling and validation
   - Priority: High
   - Estimated Effort: 3 hours
   - Dependencies: Task 2
   - Status: ✅ Complete

### Milestones

- **Milestone 1**: Basic CLI structure - Due: 2024-01-01 - ✅ Complete
- **Milestone 2**: Scan command implementation - Due: 2024-01-01 - ✅ Complete
- **Milestone 3**: Error handling and polish - Due: 2024-01-01 - ✅ Complete

---

## Testing Strategy

### Unit Tests

- [x] Test scan command with valid PDF
- [x] Test scan command with valid image
- [x] Test scan command with valid text file
- [x] Test scan command with invalid file
- [x] Test version command
- [x] Test schema selection
- [x] Test output to file
- [x] Test verbose mode

### Integration Tests

- [x] Test end-to-end scan workflow
- [x] Test error handling
- [x] Test output formatting

### Manual Testing

- [x] Test on Windows
- [x] Test on Linux
- [x] Test help output
- [x] Test error messages

### Test Coverage Target

- Minimum: 50%
- Target: 80%
- Actual: 65%

---

## Acceptance Criteria

This feature is considered complete when:

1. ✅ All functional requirements are implemented
2. ✅ All non-functional requirements are met
3. ✅ All tests pass (unit, integration, manual)
4. ✅ Code coverage meets target (≥50%)
5. ✅ All linting checks pass (Black, Ruff, Pylint ≥7.0, Flake8)
6. ✅ Type checking passes (MyPy strict mode)
7. ✅ Security scanning passes (Semgrep, Bandit, Gitleaks)
8. ✅ Documentation is updated (README, USER_MANUAL, inline docs)
9. ✅ Code review is approved
10. ✅ CHANGELOG.md is updated (via git-cliff)

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Typer compatibility issues | Medium | Low | Pin Typer version, test on multiple platforms |
| Rich terminal issues | Low | Medium | Fallback to plain text output |
| Model loading failures | High | Medium | Clear error messages, fallback options |

---

## Alternatives Considered

### Alternative 1: Click

**Description**: Use Click instead of Typer  
**Pros**: More mature, larger community  
**Cons**: More boilerplate, less intuitive  
**Why not chosen**: Typer provides better type hints and auto-completion

### Alternative 2: argparse

**Description**: Use Python's built-in argparse  
**Pros**: No dependencies, standard library  
**Cons**: Verbose, poor help generation, no type validation  
**Why not chosen**: Poor developer experience, high maintenance

---

## Related Work

- **Related Specs**: SPEC-002 (Text Extraction), SPEC-003 (LLM Inference)
- **Related Issues**: N/A
- **Related PRs**: N/A
- **Documentation**: README.md, USER_MANUAL.md

---

## Open Questions

1. Should we add a `--quiet` flag to suppress all output except errors?
2. Should we support configuration files for default options?

---

## References

- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## Approval

### Reviewers

- [x] **Reviewer 1**: DocScan Team - Approved - 2024-01-01
- [x] **Maintainer**: DocScan Team - Approved - 2024-01-01

### Sign-off

- **Author**: DocScan Team - Approved - 2024-01-01
- **Lead Maintainer**: DocScan Team - Approved - 2024-01-01

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2024-01-01 | DocScan Team | Initial draft and implementation |