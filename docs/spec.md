# DocScan CLI — Full Specification (Spec-Kit Workflow)

> Generated via the [Spec Kit 7-step workflow](https://github.com/github/spec-kit).

---

## 0. Project Identity

**DocScan CLI** — Extract structured JSON from unstructured documents offline, on CPU only.

---

## 1. Constitution — Project Principles

These principles govern all design and implementation decisions.

| # | Principle | Rationale |
|---|-----------|-----------|
| P-01 | **Offline-first** — zero network calls after model download | Privacy/air-gap requirements; no telemetry, no API keys |
| P-02 | **CPU-only inference** — no CUDA/ROCm/Metal required | Hackathon constraint; maximises accessibility on commodity hardware |
| P-03 | **AGPL-3.0 licensed** — no MIT/Apache | Ensure the project stays free; copyleft protects users |
| P-04 | **Python 3.11+ minimum** — no older runtimes | Leverage `str | None` syntax, `pathlib`, modern typing |
| P-05 | **No cloud dependency** — no fallback to any external API | Architecture must work in air-gapped/classified environments |
| P-06 | **Structured output by schema** — receipts, medical reports, generic | User selects schema via `--schema` flag; prompt and validation adapt |
| P-07 | **Fail explicitly** — validation errors are surfaced, not silently swallowed | JSON output must be reliable; Pydantic catches type mismatches |

---

## 2. Specify — WHAT & WHY (Requirements)

> No tech stack decisions yet. These are purely WHAT the system must do and WHY.

### FR-01: Parse PDF Documents

**What:** Extract all text content from PDF files.

**Why:** PDFs are the most common document format for receipts, invoices, and reports. The user drops in a PDF and expects structured data back.

**Acceptance:** Given a PDF with an embedded text layer, the system returns concatenated text of all pages. For scanned (image-only) PDFs, the system falls back to OCR.

### FR-02: Parse Image Documents via OCR

**What:** Extract text from PNG and JPEG images.

**Why:** Many receipts and handwritten notes are photographed on phones. Users need to process images without converting to PDF first.

**Acceptance:** Given a PNG or JPEG of a printed document, the system returns the recognized text after basic image preprocessing.

### FR-03: Parse Plain Text Files

**What:** Read `.txt` files directly as UTF-8.

**Why:** Sometimes the source material is already text (e.g., a pasted email, a log file). No extraction needed — pass straight to inference.

**Acceptance:** Given a `.txt` file, the system returns its contents verbatim.

### FR-04: Run Local LLM Inference

**What:** Load a local LLM and run inference on extracted text to produce structured JSON.

**Why:** Rule-based extraction is brittle and doesn't generalise across document layouts. An LLM can understand semantics and map free text to a schema.

**Acceptance:** Given extracted plain text and a schema name, the system constructs a prompt, runs inference, and returns a JSON string matching the requested schema.

### FR-05: Return Structured JSON Output

**What:** Output valid JSON to stdout or a file.

**Why:** The whole point — unstructured → structured. JSON is universal and pipeable into other tools.

**Acceptance:** Output is valid JSON parseable by any JSON parser. Fields match the selected Pydantic schema exactly.

### FR-06: Support `--schema` Flag

**What:** User picks output shape via `--schema receipt | medical | generic`.

**Why:** Different document types have different fields. A receipt has `vendor`, `total`, `line_items`; a medical report has `diagnosis`, `medications`.

**Acceptance:** Changing `--schema` changes both the LLM prompt and the Pydantic validator used.

### FR-07: Support `--output` Flag

**What:** Write JSON to a file instead of stdout.

**Why:** Users want to save results for later processing or pipe into other systems.

**Acceptance:** When `--output path/to/file.json` is given, the JSON is written to that path. When omitted, JSON goes to stdout.

### FR-08: Support `--verbose` Flag

**What:** Print debug logs: extracted text (truncated), prompt sent, raw model response, validation result.

**Why:** Debugging LLM output requires visibility into what the model received and returned.

**Acceptance:** Without `--verbose`, output is only the JSON. With `--verbose`, detailed logs appear on stderr.

---

## 3. Clarify — Structured Q&A

> Questions that naturally arise from the requirements, answered.

**Q1: What happens if the PDF is a scanned image with no text layer?**

A1: Phase 1 extracts whatever `pdfplumber` finds (may be empty). Phase 2 will add a fallback: detect image-only pages and route them through the OCR pipeline (FR-02).

**Q2: Which image formats are supported?**

A2: PNG and JPEG (`.jpg`, `.jpeg`). Other formats (TIFF, BMP, WebP) are not in scope for Phase 1 but could be added via Pillow's universal loader.

**Q3: Does the LLM need a GPU?**

A3: No. The system uses a 4-bit quantised model (Q4_K_M) that runs on CPU. Expect ~10–30s per page on a modern 4-core laptop.

**Q4: Can the user bring their own model?**

A4: Yes — the `--model PATH` flag accepts any GGUF file. Default is Mistral-7B-Instruct-v0.2 Q4_K_M, but any instruct-tuned GGUF should work.

**Q5: What if the LLM outputs invalid JSON or hallucinates?**

A5: Pydantic validation (FR-05) catches type errors. If validation fails, the error is printed in verbose mode and a non-zero exit code is returned. The raw model output is preserved for debugging.

**Q6: How are multi-page documents handled?**

A6: Phase 1 concatenates all pages into a single text string before inference. No per-page splitting. Phase 2 may add intelligent chunking.

**Q7: Is there a batch mode?**

A7: Not in Phase 1. Each invocation processes exactly one file. Phase 2 stretch goal.

**Q8: What about non-English documents?**

A8: The Mistral model has reasonable multilingual capability. Tesseract can be configured with language packs. Not explicitly tested in Phase 1.

---

## 4. Plan — Tech Blueprint (Architecture + Stack)

> NOW we add the technology stack.

### Stack Decisions

| Concern | Choice | Rationale |
|---------|--------|-----------|
| CLI framework | `typer` | Built on Click, auto `--help`, type-coercion, minimal boilerplate |
| PDF extraction | `pdfplumber` | Pure Python, handles text layers well, easy to install |
| Image OCR | `pytesseract` + `tesseract` | Mature, offline, supports preprocessing via Pillow |
| LLM runtime | `llama-cpp-python` | CPU-first GGUF inference, no GPU required, wide model support |
| Model | Mistral-7B-Instruct-v0.2 Q4_K_M | Strong instruction-following, small enough for CPU, ~4.1 GB |
| Schema validation | `pydantic` v2 | First-class type coercion, JSON schema generation, strict mode |
| Output formatting | `rich` | Pretty-print JSON, coloured logs in verbose mode |
| Packaging | `setuptools` with pyproject.toml | Standard Python packaging, `docscan` CLI entry point |

### Architecture

```
                           ┌──────────────────┐
                           │     CLI Layer     │
                           │   (docscan.cli)   │
                           └────────┬─────────┘
                                    │ input path + flags
                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     EXTRACTOR LAYER                         │
│                   (docscan.extractor)                       │
│                                                             │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  pdfplumber    │  │  tesseract   │  │   raw read     │  │
│  │  (PDF files)   │  │  (PNG/JPG)   │  │  (TXT files)   │  │
│  └────────┬───────┘  └──────┬───────┘  └───────┬────────┘  │
│           │                  │                  │           │
│           └──────────────────┼──────────────────┘           │
│                              ▼                              │
│                     plain text string                       │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     INFERENCE LAYER                         │
│                   (docscan.inference)                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  llama-cpp-python (CPU, Q4_K_M)                     │   │
│  │                                                     │   │
│  │  1. Build prompt: <system> + <schema> + <text>      │   │
│  │  2. Run inference                                   │   │
│  │  3. Parse response as JSON                          │   │
│  └──────────────────────────┬───────────────────────────┘   │
│                             │ raw JSON string                │
└─────────────────────────────┬────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     VALIDATION LAYER                        │
│                    (docscan.schemas)                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Pydantic schema validator                           │   │
│  │                                                     │   │
│  │  1. Validate JSON against selected schema           │   │
│  │  2. Coerce types (str→float, str→date, etc.)        │   │
│  │  3. Return validated model or raise validation err   │   │
│  └──────────────────────────┬───────────────────────────┘   │
│                             │ validated dict                 │
└─────────────────────────────┬────────────────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │  JSON OUTPUT     │
                    │  stdout / file   │
                    └──────────────────┘
```

### Data Flow

1. **CLI** receives `INPUT_PATH` and flags (`--schema`, `--output`, `--verbose`, `--model`).
2. **Router** (in `extractor.py`) inspects the file extension and dispatches:
   - `.pdf` → `pdfplumber` text extraction
   - `.png`, `.jpg`, `.jpeg` → Pillow preprocessing → `pytesseract` OCR
   - `.txt` → raw UTF-8 read
3. **Extractor** returns a `str` of plain text.
4. **Inference engine** (`inference.py`) constructs a structured prompt:
   - System: "You are a data extraction assistant. Output ONLY valid JSON."
   - Schema: serialised Pydantic model fields and types
   - Document: the extracted text
   - Instruction: "Respond with JSON matching the schema above. No explanation."
5. **`llama-cpp-python`** runs the model on CPU with the prompt, returns a string.
6. **Response parser** extracts the first `{...}` JSON block from the model output.
7. **Pydantic validator** parses and validates the JSON against the selected schema (`ReceiptSchema`, `MedicalSchema`, or `GenericSchema`).
8. **CLI** prints validated JSON to stdout (or writes to `--output` path).

### Prompt Template (Conceptual)

```
<system>
You are a data extraction assistant. Extract structured information
from the document text below. Output ONLY valid JSON — no markdown,
no explanation, no preamble.
</system>

<schema>
{serialised_pydantic_schema}
</schema>

<document>
{extracted_text}
</document>

<instruction>
Respond with a single JSON object conforming exactly to the schema above.
</instruction>
```

---

## 5. Tasks — Ordered Execution Plan

> See [docs/issues.md](./issues.md) for full details. Summary:

| # | Task | Est. | Owner | Depends On |
|---|------|------|-------|------------|
| T-01 | Setup project scaffold (pyproject.toml, folders, LICENSE) | 2h | Person A | — |
| T-02 | Implement PDF text extraction (pdfplumber) | 3h | Person A | T-01 |
| T-03 | Implement image OCR extraction (tesseract + Pillow) | 3h | Person A | T-01 |
| T-04 | Integrate llama-cpp-python (load model, run inference) | 4h | Person B | T-01 |
| T-05 | Define Pydantic output schemas (receipt, medical, generic) | 2h | Person B | T-01 |
| T-06 | Wire CLI interface (typer, scan command, flags) | 2h | Both | T-02, T-03, T-04, T-05 |
| T-07 | Write integration tests with sample docs | 3h | Person B | T-06 |
| T-08 | Write README + spec (Phase 1 deliverable) | 1h | Person A | — |

**Parallelism:** T-02, T-03 (Person A) and T-04, T-05 (Person B) can run in parallel. T-06 merges all four. T-07 and T-08 are the final polish.

---

## 6. Implement — Execution Notes

### Order of Implementation

1. **Scaffold** (T-01) first — establish structure, pyproject.toml, `.gitignore`, stub files
2. **Extraction** (T-02, T-03) and **Inference core** (T-04, T-05) run in parallel
3. **Integration** (T-06) wires everything into a working `docscan scan` command
4. **Test** (T-07) with real fixture documents
5. **Document** (T-08) — this spec, README, issues

### Validation Gate

Before marking any task complete, run:

```bash
cd docscan-cli
pip install -e ".[dev]"
pytest tests/ -v
ruff check docscan/
mypy docscan/
```

### Deliverable Structure

```
docscan-cli/
├── docscan/
│   ├── __init__.py
│   ├── cli.py           # typer app, scan command
│   ├── extractor.py     # pdfplumber / tesseract / txt readers
│   ├── inference.py     # llama-cpp-python prompt + inference
│   └── schemas.py       # Pydantic models
├── docs/
│   ├── spec.md          # this file
│   ├── issues.md        # GitLab issues table
│   └── work-division.md # 2-person team plan
├── tests/               # pytest fixtures + test files
├── pyproject.toml
├── README.md
└── LICENSE              # AGPL-3.0
```

---

## Out of Scope (Phase 1)

- GPU acceleration (CUDA / ROCm / Metal)
- Cloud API fallbacks or hybrid mode
- GUI or web interface
- Batch processing of multiple files (Phase 2 stretch goal)
- Fine-tuning or custom model training
- Document layout analysis / table extraction beyond LLM capability
- Multi-page document support beyond simple concatenation
- Digital signatures or encryption

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Model size (~4.1 GB)** | Large download, disk usage | Use Q4_K_M quantization (smallest viable); document in README; provide `wget` command |
| **Tesseract OCR accuracy** | Garbage in → garbage out | Apply grayscale + threshold + deskew preprocessing; only use OCR when no text layer exists |
| **LLM hallucinations** | Invalid/made-up data in output | Prompt engineering (strict JSON-only instruction); Pydantic validation catches type errors; schema constrains output space |
| **Slow inference on CPU** | >30s per page | Use Q4_K_M quant; restrict context length; benchmark and document expected times |
| **pdfplumber fails on scanned PDFs** | No text extracted | Fall back to OCR pipeline; detect page image content via pixel analysis |

---

## Appendix: Spec-Kit Commands Reference

```bash
# Commands used during this project
specify init docscan-cli --integration claude

# /speckit.constitution    → Section 1 (Constitution)
# /speckit.specify         → Section 2 (Specify)
# /speckit.clarify         → Section 3 (Clarify)
# /speckit.plan            → Section 4 (Plan)
# /speckit.tasks           → Section 5 (Tasks)
# /speckit.implement       → Section 6 (Implement)
# /speckit.analyze         → Consistency cross-check (post-implementation)
# /speckit.checklist       → Quality gate (before release)
# /speckit.taskstoissues   → Export to GitLab/GitHub Issues
```
