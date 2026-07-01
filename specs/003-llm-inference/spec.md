# Spec 003: Local LLM Inference

**Feature ID**: SPEC-003
**Status**: Implemented
**Created**: 2024-01-01
**Last Updated**: 2024-01-01
**Author**: DocScan Team
**Reviewers**: DocScan Team

## Overview

Implement local LLM inference using llama-cpp-python with GGUF models, enabling CPU-only structured data extraction from documents without network dependencies.

## Problem Statement

After extracting text from documents, we need to intelligently parse and structure that text into JSON format. The LLM must understand document context, extract structured data according to schemas, run completely offline, and work on CPU only.

## Requirements

### Functional Requirements

1. **FR-001**: Load GGUF models — Priority: High — Supports phi3-mini-q4.gguf and similar models
2. **FR-002**: Run inference on CPU — Priority: High — Uses llama-cpp-python with n_gpu_layers=0
3. **FR-003**: Support multiple schemas — Priority: High — receipt, medical, and generic schemas
4. **FR-004**: Parse LLM output to JSON — Priority: High — Extracts valid JSON from model response
5. **FR-005**: Validate output against schema — Priority: High — Uses Pydantic for validation
6. **FR-006**: Model caching — Priority: Medium — Loads model once, reuses for multiple inferences

### Non-Functional Requirements

1. **NFR-001**: Inference speed — Priority: Medium — Processes document in 10-30 seconds
2. **NFR-002**: Memory efficiency — Priority: Medium — Model stays in memory for reuse
3. **NFR-003**: Error handling — Priority: High — Clear errors for model not found, parse failures

### Constraints

- Must use llama-cpp-python with GGUF format models
- Must be CPU-only (n_gpu_layers=0)
- Must work offline
- Must support Python 3.11+

## Design

```
docscan/inference.py
    ├── load_model() - Load and cache GGUF model
    ├── build_prompt() - Construct extraction prompt
    ├── run_inference() - Main inference function
    ├── _fallback_extract() - Fallback without model
    └── _parse_json() - Parse JSON from response
```

### Components

1. **Inference Module** (`docscan/inference.py`) — LLM inference and output parsing — Dependencies: llama-cpp-python, schemas
2. **Model Loader** — Loads GGUF model, caches globally, configures CPU-only inference
3. **Prompt Builder** — Constructs extraction prompt with schema definition, limits text to 3000 chars
4. **JSON Parser** — Extracts JSON from model output, handles malformed responses, provides fallback

### Data Flow

Extracted Text + Schema Name → Build Prompt → LLM Inference (CPU) → Raw Response → Parse JSON → Validate Schema → Structured Dict

## Testing Strategy

### Unit Tests

- Model loading and caching
- Prompt building for each schema
- JSON parsing (valid and invalid)
- Schema validation
- Fallback extraction
- Error handling (model not found)

### Coverage Target

Minimum: 50% | Target: 80% | Actual: 70%

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Model not found | High | Medium | Clear error, download instructions |
| Slow inference | Medium | Medium | Optimize threads, document expected times |
| Memory usage | Medium | Low | Model caching, configurable context size |
| JSON parse failures | High | Medium | Robust regex, fallback extraction |

## Alternatives Considered

1. **OpenAI API** — Better accuracy but requires internet, costs money, privacy violation. Not chosen: Must be offline.
2. **Hugging Face Transformers** — More model options but larger dependencies, slower. Not chosen: llama-cpp-python is faster.
3. **Ollama** — Easy model management but additional dependency. Not chosen: Direct llama-cpp-python is simpler.

## Related Work

- SPEC-001 (Core CLI), SPEC-002 (Text Extraction)

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
