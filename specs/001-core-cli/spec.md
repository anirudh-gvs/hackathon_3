# Spec 001: Core CLI Implementation

**Feature ID**: SPEC-001
**Status**: Implemented
**Created**: 2024-01-01
**Last Updated**: 2024-01-01
**Author**: DocScan Team
**Reviewers**: DocScan Team

## Overview

Implement the core command-line interface for Offline DocScan using Typer, providing a user-friendly interface for document scanning and structured data extraction.

## Problem Statement

Users need a simple, intuitive command-line interface to scan documents (PDFs, images, text files), extract structured data using local LLM inference, save results in JSON format, and configure extraction schemas. A well-designed CLI is the primary user interface and must be easy to use, powerful, consistent with Unix philosophy, and well-documented with helpful error messages.

## Requirements

### Functional Requirements

1. **FR-001**: Implement `scan` command — Priority: High — Accepts file path, schema, and output options
2. **FR-002**: Implement `version` command — Priority: Medium — Displays version information
3. **FR-003**: Support multiple schemas — Priority: High — receipt, medical, and generic schemas available
4. **FR-004**: Verbose output mode — Priority: Medium — Shows extracted text before inference
5. **FR-005**: Custom model path — Priority: Medium — Users can specify alternative GGUF models

### Non-Functional Requirements

1. **NFR-001**: Response time — Priority: High — CLI starts in <2 seconds
2. **NFR-002**: Error handling — Priority: High — Clear error messages for all failure modes
3. **NFR-003**: Help documentation — Priority: High — Auto-generated help for all commands

### Constraints

- Must use Typer for CLI framework
- Must support Python 3.11+
- Must work on Windows, macOS, and Linux
- Must be CPU-only (no GPU dependencies)

## Design

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

1. **CLI Module** (`docscan/cli.py`) — CLI and user interaction — Dependencies: typer, rich, extractor, inference, schemas
2. **Text Extractor** (`docscan/extractor.py`) — Extract text from PDFs, images, and text files — Dependencies: pdfplumber, pytesseract, Pillow
3. **LLM Inference** (`docscan/inference.py`) — Local LLM inference — Dependencies: llama-cpp-python, schemas
4. **Schemas** (`docscan/schemas.py`) — Output schema definitions — Dependencies: pydantic

### Data Flow

User Input → File Path Validation → Text Extraction → LLM Inference → Schema Validation → JSON Output

## Testing Strategy

### Unit Tests

- Test scan command with valid PDF, image, text file
- Test scan command with invalid file
- Test version command, schema selection, output to file, verbose mode

### Integration Tests

- End-to-end scan workflow, error handling, output formatting

### Coverage Target

Minimum: 50% | Target: 80% | Actual: 65%

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Typer compatibility issues | Medium | Low | Pin Typer version, test on multiple platforms |
| Rich terminal issues | Low | Medium | Fallback to plain text output |
| Model loading failures | High | Medium | Clear error messages, fallback options |

## Alternatives Considered

1. **Click** — More mature but more boilerplate. Not chosen: Typer provides better type hints and auto-completion.
2. **argparse** — No dependencies but verbose. Not chosen: Poor developer experience, high maintenance.

## Related Work

- SPEC-002 (Text Extraction), SPEC-003 (LLM Inference)

## Acceptance Criteria

1. All functional requirements implemented
2. All non-functional requirements met
3. All tests pass
4. Code coverage ≥50%
5. All linting checks pass
6. Type checking passes (MyPy strict)
7. Security scanning passes
8. Documentation updated
9. Code review approved
10. CHANGELOG.md updated

## Approval

- **Author**: DocScan Team — Approved — 2024-01-01
- **Maintainer**: DocScan Team — Approved — 2024-01-01

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2024-01-01 | DocScan Team | Initial draft and implementation |
