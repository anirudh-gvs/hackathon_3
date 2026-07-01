# Work Division Plan — 2-Person Team

| Area | Owner | Tasks |
|------|-------|-------|
| **Extraction layer** | Person A | PDF parsing with `pdfplumber` (FR-01), image OCR with `tesseract` + preprocessing (FR-02), plain text reading (FR-03), fallback logic for scanned PDFs |
| **Inference + schema** | Person B | `llama-cpp-python` model loading + inference (FR-04), prompt template engineering, Pydantic schema definitions (`ReceiptSchema`, `MedicalSchema`, `GenericSchema` — FR-05), response parsing + validation |
| **CLI + integration** | Both | `typer` CLI wiring (FR-06, FR-07, FR-08), end-to-end pipeline assembly, error handling, verbose logging |
| **Docs + CI** | Person A | README.md, docs/spec.md, `.gitlab-ci.yml` skeleton, issue tracker setup |
| **Testing** | Person B | `pytest` fixtures (3 sample documents), integration tests, unit tests for extractor + parser edge cases, coverage reporting |

## Communication

- Daily 15-min sync at standup
- Issues tracked in GitLab board (see `docs/issues.md`)
- Branch naming: `feature/<issue-number>-<kebab-case-description>`
- MR approval required from both team members before merging to `main`

## Milestone

**Phase 1 delivery**: End of Day 2 — all issues closed, CI green, README ready for judge review.
