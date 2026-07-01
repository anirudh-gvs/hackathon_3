# Spec 003: Local LLM Inference

**Feature ID**: SPEC-003  
**Status**: Implemented  
**Created**: 2024-01-01  
**Last Updated**: 2024-01-01  
**Author**: DocScan Team  
**Reviewers**: DocScan Team

---

## Overview

Implement local LLM inference using llama-cpp-python with GGUF models, enabling CPU-only structured data extraction from documents without network dependencies.

---

## Problem Statement

### What problem does this solve?

After extracting text from documents, we need to intelligently parse and structure that text into JSON format. This requires an LLM that can:
- Understand document context
- Extract structured data according to schemas
- Run completely offline (no API calls)
- Work on CPU only (no GPU required)

### Why is this important?

LLM inference is the "brain" of DocScan. It transforms raw text into structured, actionable data. It must be:
- 100% offline (privacy requirement)
- CPU-only (accessibility requirement)
- Fast enough for practical use
- Accurate enough for production use

### Who benefits from this?

- End users who get structured data from documents
- The CLI module (provides structured output)
- Automation workflows (reliable JSON output)

---

## Requirements

### Functional Requirements

1. **FR-001**: Load GGUF models
   - Priority: High
   - Acceptance Criteria: Supports phi3-mini-q4.gguf and similar models

2. **FR-002**: Run inference on CPU
   - Priority: High
   - Acceptance Criteria: Uses llama-cpp-python with n_gpu_layers=0

3. **FR-003**: Support multiple schemas
   - Priority: High
   - Acceptance Criteria: receipt, medical, and generic schemas

4. **FR-004**: Parse LLM output to JSON
   - Priority: High
   - Acceptance Criteria: Extracts valid JSON from model response

5. **FR-005**: Validate output against schema
   - Priority: High
   - Acceptance Criteria: Uses Pydantic for validation

6. **FR-006**: Model caching
   - Priority: Medium
   - Acceptance Criteria: Loads model once, reuses for multiple inferences

### Non-Functional Requirements

1. **NFR-001**: Inference speed
   - Priority: Medium
   - Acceptance Criteria: Processes document in 10-30 seconds

2. **NFR-002**: Memory efficiency
   - Priority: Medium
   - Acceptance Criteria: Model stays in memory for reuse

3. **NFR-003**: Error handling
   - Priority: High
   - Acceptance Criteria: Clear errors for model not found, parse failures

### Constraints

- Must use llama-cpp-python
- Must use GGUF format models
- Must be CPU-only (n_gpu_layers=0)
- Must work offline (no network calls)
- Must support Python 3.11+

---

## Design

### Architecture

```
docscan/inference.py
    ├── load_model() - Load and cache GGUF model
    ├── build_prompt() - Construct extraction prompt
    ├── run_inference() - Main inference function
    ├── _fallback_extract() - Fallback without model
    └── _parse_json() - Parse JSON from response
```

### Components

1. **Inference Module** (`docscan/inference.py`)
   - Location: `docscan/inference.py`
   - Responsibility: LLM inference and output parsing
   - Dependencies: llama-cpp-python, schemas, json, re

2. **Model Loader** (`load_model`)
   - Loads GGUF model into memory
   - Caches model instance globally
   - Configures CPU-only inference
   - Sets context window and threads

3. **Prompt Builder** (`build_prompt`)
   - Constructs extraction prompt
   - Includes schema definition
   - Limits document text to 3000 chars
   - Uses Phi-3 chat format

4. **JSON Parser** (`_parse_json`)
   - Extracts JSON from model output
   - Handles malformed responses
   - Provides fallback on parse failure

### Data Flow

```
Extracted Text (from extractor)
    ↓
Schema Name (receipt/medical/generic)
    ↓
Build Prompt (schema + text)
    ↓
LLM Inference (CPU-only)
    ↓
Raw Response (text with JSON)
    ↓
Parse JSON (extract valid JSON)
    ↓
Validate Schema (Pydantic)
    ↓
Structured Dict (output)
```

### Prompt Format

```
<|user|>
You are a data extraction assistant. Extract structured information from the document below.
The document is a {doc_type}.

Return ONLY a valid JSON object matching this exact schema (no explanation, no markdown, no extra text):
{schema_json}

If a field cannot be determined from the document, use null for optional fields or empty lists for arrays.

DOCUMENT:
{document_text[:3000]}
<|end|>
<|assistant|>
{
```

---

## Implementation Plan

### Tasks

1. **Task 1**: Set up module structure
   - Priority: High
   - Estimated Effort: 1 hour
   - Dependencies: None
   - Status: ✅ Complete

2. **Task 2**: Implement model loading with caching
   - Priority: High
   - Estimated Effort: 2 hours
   - Dependencies: Task 1
   - Status: ✅ Complete

3. **Task 3**: Implement prompt building
   - Priority: High
   - Estimated Effort: 2 hours
   - Dependencies: Task 1
   - Status: ✅ Complete

4. **Task 4**: Implement inference execution
   - Priority: High
   - Estimated Effort: 3 hours
   - Dependencies: Tasks 2-3
   - Status: ✅ Complete

5. **Task 5**: Implement JSON parsing and validation
   - Priority: High
   - Estimated Effort: 2 hours
   - Dependencies: Task 4
   - Status: ✅ Complete

6. **Task 6**: Add fallback extraction
   - Priority: Medium
   - Estimated Effort: 1 hour
   - Dependencies: Task 5
   - Status: ✅ Complete

### Milestones

- **Milestone 1**: Model loading - Due: 2024-01-01 - ✅ Complete
- **Milestone 2**: Basic inference - Due: 2024-01-01 - ✅ Complete
- **Milestone 3**: JSON parsing - Due: 2024-01-01 - ✅ Complete
- **Milestone 4**: Error handling - Due: 2024-01-01 - ✅ Complete

---

## Testing Strategy

### Unit Tests

- [x] Test model loading
- [x] Test model caching
- [x] Test prompt building for each schema
- [x] Test JSON parsing (valid JSON)
- [x] Test JSON parsing (invalid JSON)
- [x] Test schema validation
- [x] Test fallback extraction
- [x] Test error handling (model not found)

### Integration Tests

- [x] Test with CLI integration
- [x] Test with all schemas
- [x] Test with real documents
- [x] Test error propagation

### Manual Testing

- [x] Test inference speed
- [x] Test output quality
- [x] Test memory usage
- [x] Test with different models

### Test Coverage Target

- Minimum: 50%
- Target: 80%
- Actual: 70%

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
| Model not found | High | Medium | Clear error message, download instructions |
| Slow inference | Medium | Medium | Optimize threads, document expected times |
| Memory usage | Medium | Low | Model caching, configurable context size |
| JSON parse failures | High | Medium | Robust regex, fallback extraction |

---

## Alternatives Considered

### Alternative 1: OpenAI API

**Description**: Use OpenAI API for inference  
**Pros**: Better accuracy, faster  
**Cons**: Requires internet, costs money, privacy violation  
**Why not chosen**: Must be offline and CPU-only

### Alternative 2: Hugging Face Transformers

**Description**: Use HF Transformers with PyTorch  
**Pros**: More model options, better CPU support  
**Cons**: Larger dependencies, slower than llama.cpp  
**Why not chosen**: llama-cpp-python is faster and lighter

### Alternative 3: Ollama

**Description**: Use Ollama for model management  
**Pros**: Easy model management, good API  
**Cons**: Additional dependency, overkill for CLI  
**Why not chosen**: Direct llama-cpp-python usage is simpler

---

## Related Work

- **Related Specs**: SPEC-001 (Core CLI), SPEC-002 (Text Extraction)
- **Related Issues**: N/A
- **Related PRs**: N/A
- **Documentation**: README.md, USER_MANUAL.md

---

## Open Questions

1. Should we support streaming output for long documents?
2. Should we add model quantization options (q4, q5, q8)?
3. Should we support custom system prompts?

---

## References

- [llama-cpp-python Documentation](https://github.com/abetlen/llama-cpp-python)
- [GGUF Format](https://github.com/ggerganov/gguf)
- [Phi-3 Model Card](https://huggingface.co/microsoft/phi-3-mini-4k-instruct-gguf)
- [Pydantic Documentation](https://docs.pydantic.dev/)

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