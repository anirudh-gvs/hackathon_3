# GitLab Issues — DocScan CLI Phase 1

The following issues should be created manually in the GitLab project board.

| ID | Title | Description | Assignee | Estimate | Due Date | Label |
|----|-------|-------------|----------|----------|----------|-------|
| #1 | Setup project scaffold | Create `pyproject.toml`, folder structure (`docscan/`, `docs/`, `tests/`), and `LICENSE` (AGPL-3.0). Initialise git repo. | @me | 2h | Day 1 | `infra` |
| #2 | Implement PDF text extraction | Integrate `pdfplumber` in `docscan/extractor.py`. Write function `extract_text_from_pdf(path) -> str`. Handle multi-page. Return concatenated text. | @me | 3h | Day 1 | `feature` |
| #3 | Implement image OCR extraction | Integrate `pytesseract` + `Pillow` in `docscan/extractor.py`. Write function `extract_text_from_image(path) -> str`. Add preprocessing: grayscale, threshold, deskew. | @me | 3h | Day 1 | `feature` |
| #4 | Integrate llama-cpp-python | Load GGUF model in `docscan/inference.py`. Implement `run_inference(text, schema_name) -> dict`. Build prompt template with system instruction, schema, and document text. Parse JSON from response. | @me | 4h | Day 1 | `feature` |
| #5 | Define Pydantic output schemas | Create `docscan/schemas.py` with `ReceiptSchema`, `MedicalSchema`, `GenericSchema`. Each with typed fields and example values. Include JSON-schema serialisation for prompt building. | @me | 2h | Day 1 | `feature` |
| #6 | Wire CLI interface | Set up `typer` app in `docscan/cli.py`. Implement `scan` command with `INPUT_PATH` argument and `--schema`, `--output`, `--model`, `--verbose` options. Route file type to correct extractor. | @me | 2h | Day 1 | `feature` |
| #7 | Write integration tests with sample docs | Create 3 fixture files: `sample-receipt.pdf`, `sample-letter.txt`, `sample-prescription.png`. Write pytest integration tests that verify the full pipeline outputs valid JSON matching the expected schema. | @me | 3h | Day 2 | `testing` |
| #8 | Write README + spec | Complete README.md, docs/spec.md, docs/issues.md, docs/work-division.md. Ensure all Phase 1 documentation is ready for judge review. | @me | 1h | Day 1 | `docs` |
