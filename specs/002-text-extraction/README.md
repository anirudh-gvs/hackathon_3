# Spec 002: Text Extraction Module

**Feature ID**: SPEC-002  
**Status**: Implemented  
**Created**: 2024-01-01  
**Last Updated**: 2024-01-01  
**Author**: DocScan Team  
**Reviewers**: DocScan Team

---

## Overview

Implement a robust text extraction module that can extract text from PDFs, images (via OCR), and plain text files, all processed locally without network dependencies.

---

## Problem Statement

### What problem does this solve?

Documents come in various formats (PDF, images, text). Users need a unified interface to extract raw text from these formats for further processing by the LLM.

### Why is this important?

Text extraction is the foundation of the document scanning pipeline. It must be:
- Reliable across different file formats
- Handle edge cases (scanned PDFs, corrupted files)
- Fast and efficient
- Work completely offline

### Who benefits from this?

- End users who need to extract text from documents
- The LLM inference module (provides input text)
- Batch processing workflows

---

## Requirements

### Functional Requirements

1. **FR-001**: Extract text from PDF files
   - Priority: High
   - Acceptance Criteria: Uses pdfplumber to extract text from all pages

2. **FR-002**: Extract text from images via OCR
   - Priority: High
   - Acceptance Criteria: Uses pytesseract with grayscale preprocessing

3. **FR-003**: Read plain text files
   - Priority: High
   - Acceptance Criteria: Reads .txt files with UTF-8 encoding

4. **FR-004**: Validate file formats
   - Priority: High
   - Acceptance Criteria: Rejects unsupported formats with clear error

5. **FR-005**: Handle extraction errors gracefully
   - Priority: High
   - Acceptance Criteria: Provides helpful error messages

### Non-Functional Requirements

1. **NFR-001**: Performance
   - Priority: Medium
   - Acceptance Criteria: Extracts text from 10-page PDF in <5 seconds

2. **NFR-002**: OCR accuracy
   - Priority: Medium
   - Acceptance Criteria: Works well with clear, high-contrast images

3. **NFR-003**: Memory efficiency
   - Priority: Medium
   - Acceptance Criteria: Processes files without loading entire file into memory

### Constraints

- Must work offline (no network calls)
- Must support PDF, PNG, JPG, JPEG, BMP, TIFF, TXT
- Must use pdfplumber for PDFs
- Must use pytesseract for OCR
- Must use Pillow for image preprocessing

---

## Design

### Architecture

```
docscan/extractor.py
    ├── extract_text() - Main dispatcher
    ├── _extract_pdf() - PDF text extraction
    ├── _extract_image() - OCR extraction
    └── (TXT handled inline)
```

### Components

1. **Text Extractor** (`docscan/extractor.py`)
   - Location: `docscan/extractor.py`
   - Responsibility: Extract text from various file formats
   - Dependencies: pdfplumber, pytesseract, Pillow, re

2. **PDF Extractor** (`_extract_pdf`)
   - Uses pdfplumber to iterate through pages
   - Extracts text from each page
   - Joins pages with double newlines
   - Handles empty/corrupted PDFs

3. **Image OCR** (`_extract_image`)
   - Opens image with Pillow
   - Converts to grayscale for better OCR
   - Uses pytesseract for text extraction
   - Cleans up excessive newlines

### Data Flow

```
File Path
    ↓
Check Extension
    ↓
├─ .pdf → _extract_pdf()
│   └─ pdfplumber.open()
│       └─ page.extract_text() for each page
│           └─ Join with newlines
│
├─ .png/.jpg/.jpeg/.bmp/.tiff → _extract_image()
│   └─ Pillow.open()
│       └─ Convert to grayscale
│           └─ pytesseract.image_to_string()
│               └─ Clean up newlines
│
└─ .txt → read_text()
    └─ Return file contents

Result: str (extracted text)
```

### API

```python
def extract_text(path: Path) -> str:
    """
    Extract text from PDF, image, or text file.
    
    Args:
        path: Path to the file
        
    Returns:
        Extracted text as string
        
    Raises:
        ValueError: If file format is unsupported or extraction fails
    """
```

---

## Implementation Plan

### Tasks

1. **Task 1**: Set up module structure and imports
   - Priority: High
   - Estimated Effort: 1 hour
   - Dependencies: None
   - Status: ✅ Complete

2. **Task 2**: Implement PDF text extraction
   - Priority: High
   - Estimated Effort: 2 hours
   - Dependencies: Task 1
   - Status: ✅ Complete

3. **Task 3**: Implement image OCR extraction
   - Priority: High
   - Estimated Effort: 2 hours
   - Dependencies: Task 1
   - Status: ✅ Complete

4. **Task 4**: Implement text file reading
   - Priority: High
   - Estimated Effort: 30 minutes
   - Dependencies: Task 1
   - Status: ✅ Complete

5. **Task 5**: Add error handling and validation
   - Priority: High
   - Estimated Effort: 2 hours
   - Dependencies: Tasks 2-4
   - Status: ✅ Complete

### Milestones

- **Milestone 1**: Basic extraction - Due: 2024-01-01 - ✅ Complete
- **Milestone 2**: Error handling - Due: 2024-01-01 - ✅ Complete
- **Milestone 3**: Testing and polish - Due: 2024-01-01 - ✅ Complete

---

## Testing Strategy

### Unit Tests

- [x] Test PDF extraction with valid PDF
- [x] Test PDF extraction with scanned PDF (no text)
- [x] Test image OCR with clear image
- [x] Test image OCR with poor quality image
- [x] Test text file reading
- [x] Test unsupported format error
- [x] Test missing file error
- [x] Test empty file handling

### Integration Tests

- [x] Test with CLI integration
- [x] Test with various file types
- [x] Test error propagation

### Manual Testing

- [x] Test with real PDFs
- [x] Test with scanned documents
- [x] Test with various image formats
- [x] Test error messages

### Test Coverage Target

- Minimum: 50%
- Target: 80%
- Actual: 75%

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
| Tesseract not installed | High | Medium | Clear installation instructions, error message |
| Poor OCR accuracy | Medium | Medium | Document image quality requirements |
| Large PDF memory usage | Medium | Low | Stream processing, page-by-page |
| Corrupted files | High | Medium | Try-except blocks, clear error messages |

---

## Alternatives Considered

### Alternative 1: PyMuPDF (fitz)

**Description**: Use PyMuPDF instead of pdfplumber  
**Pros**: Faster, more features  
**Cons**: Additional dependency, AGPL license conflict  
**Why not chosen**: pdfplumber is sufficient and has compatible license

### Alternative 2: EasyOCR

**Description**: Use EasyOCR instead of Tesseract  
**Pros**: Better accuracy, deep learning-based  
**Cons**: Requires GPU, larger model, slower  
**Why not chosen**: Must be CPU-only, Tesseract is sufficient

---

## Related Work

- **Related Specs**: SPEC-001 (Core CLI), SPEC-003 (LLM Inference)
- **Related Issues**: N/A
- **Related PRs**: N/A
- **Documentation**: README.md, USER_MANUAL.md

---

## Open Questions

1. Should we support password-protected PDFs?
2. Should we add image preprocessing (contrast enhancement, deskewing)?

---

## References

- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)
- [pytesseract Documentation](https://pytesseract.readthedocs.io/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

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