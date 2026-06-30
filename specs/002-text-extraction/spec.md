# Spec 002: Text Extraction Module

**Feature ID**: SPEC-002
**Status**: Implemented
**Created**: 2024-01-01
**Last Updated**: 2024-01-01
**Author**: DocScan Team
**Reviewers**: DocScan Team

## Overview

Implement a robust text extraction module that can extract text from PDFs, images (via OCR), and plain text files, all processed locally without network dependencies.

## Problem Statement

Documents come in various formats (PDF, images, text). Users need a unified interface to extract raw text for further processing by the LLM. Text extraction must be reliable across formats, handle edge cases, be fast, and work completely offline.

## Requirements

### Functional Requirements

1. **FR-001**: Extract text from PDF files — Priority: High — Uses pdfplumber to extract text from all pages
2. **FR-002**: Extract text from images via OCR — Priority: High — Uses pytesseract with grayscale preprocessing
3. **FR-003**: Read plain text files — Priority: High — Reads .txt files with UTF-8 encoding
4. **FR-004**: Validate file formats — Priority: High — Rejects unsupported formats with clear error
5. **FR-005**: Handle extraction errors gracefully — Priority: High — Provides helpful error messages

### Non-Functional Requirements

1. **NFR-001**: Performance — Priority: Medium — Extracts 10-page PDF in <5 seconds
2. **NFR-002**: OCR accuracy — Priority: Medium — Works well with clear, high-contrast images
3. **NFR-003**: Memory efficiency — Priority: Medium — Processes files without loading entirely into memory

### Constraints

- Must work offline
- Supports PDF, PNG, JPG, JPEG, BMP, TIFF, TXT
- Must use pdfplumber for PDFs, pytesseract for OCR, Pillow for image preprocessing

## Design

```
docscan/extractor.py
    ├── extract_text() - Main dispatcher
    ├── _extract_pdf() - PDF text extraction
    ├── _extract_image() - OCR extraction
    └── (TXT handled inline)
```

### Components

1. **Text Extractor** (`docscan/extractor.py`) — Extract text from various file formats — Dependencies: pdfplumber, pytesseract, Pillow
2. **PDF Extractor** — Uses pdfplumber page-by-page, joins with newlines, handles empty/corrupted PDFs
3. **Image OCR** — Opens with Pillow, grayscale conversion, pytesseract extraction, newline cleanup

### Data Flow

File Path → Check Extension → PDF (_extract_pdf) / Image (_extract_image) / TXT (read_text) → Extracted Text

## Testing Strategy

### Unit Tests

- PDF extraction with valid and scanned PDFs
- Image OCR with clear and poor quality images
- Text file reading, unsupported format, missing file, empty file

### Coverage Target

Minimum: 50% | Target: 80% | Actual: 75%

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Tesseract not installed | High | Medium | Clear installation instructions, error message |
| Poor OCR accuracy | Medium | Medium | Document image quality requirements |
| Large PDF memory usage | Medium | Low | Stream processing, page-by-page |
| Corrupted files | High | Medium | Try-except blocks, clear error messages |

## Alternatives Considered

1. **PyMuPDF** — Faster but additional dependency and AGPL license conflict. Not chosen: pdfplumber is sufficient.
2. **EasyOCR** — Better accuracy but requires GPU. Not chosen: Must be CPU-only.

## Related Work

- SPEC-001 (Core CLI), SPEC-003 (LLM Inference)

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
