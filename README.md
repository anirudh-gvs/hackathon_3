# Offline DocScan

[![pipeline status](https://code.swecha.org/Gvs_Anirudh/hackathon_3/badges/main/pipeline.svg)](https://code.swecha.org/Gvs_Anirudh/hackathon_3/-/commits/main)

### Live Links
🚀 **Live Tool (App)**: [https://docscan-i0k7.onrender.com](https://docscan-i0k7.onrender.com)  
🌐 **Project Landing Page (Website)**: [https://anirudh-gvs.github.io/hackathon_3/](https://anirudh-gvs.github.io/hackathon_3/)

Privacy-first, CPU-only document scanner. Extracts structured JSON from PDFs, images, and text files — fully offline using local LLM inference.

**Built for the CPU First Hackathon.**

---

## Quick Start

### Install

```bash
pip install -e ".[dev]"
```

### CLI Usage

```bash
# Scan a document (quick mode — keyword extraction, no model needed)
docscan scan receipt.pdf --schema receipt

# Full AI extraction (requires GGUF model in models/)
docscan scan invoice.pdf --schema receipt --mode ai -o output.json

# See help
docscan --help
```

### Web UI

```bash
python app.py
# Open http://localhost:5000
```

---

## Deploy to Render (free)

1. **Go to** https://dashboard.render.com/select-repo?type=web
2. Click **Public Git Repository** tab
3. Paste: `https://code.swecha.org/Gvs_Anirudh/cpu_first_hackathon.git`
4. Fill the form:
   - **Name**: `docscan`
   - **Region**: `Frankfurt` (EU) or `Oregon` (US) — closest to you
   - **Branch**: `main`
   - **Runtime**: `Docker`
   - **Plan**: **Free**
   - **Advanced** → **Health Check Path**: `/`
5. Click **Create Web Service**

Wait 5-7 minutes for build + deploy. Your URL will be: `https://docscan.onrender.com`

> **Note:** Default processing mode is `quick` (keyword-based, no model needed).
> For AI mode, upload a GGUF model to `models/` via the Render Shell, or set `MODE=ai` in the form.

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Flask SPA   │────▶│  extractor   │────▶│  inference   │
│  (web UI)    │     │  (pdfplumber │     │  (llama-cpp  │
│              │     │   + tesser)  │     │   or quick)  │
└─────────────┘     └──────────────┘     └──────────────┘
                           │
                     ┌─────▼──────┐
                     │   schemas   │
                     │  (Pydantic) │
                     └────────────┘
```

Input → Extract raw text → Run inference (AI or keyword) → Validate against Pydantic schema → Output JSON

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `docscan scan <file>` | Extract structured JSON from a document |
| `docscan scan --help` | All options (schema, model path, output file, verbose) |
| `docscan version` | Print version |

Options for `scan`:
- `--schema / -s` — `receipt`, `medical`, or `generic` (default)
- `--model / -m` — Path to GGUF model (default: `models/phi3-mini-q4.gguf`)
- `--output / -o` — Write JSON to file instead of stdout
- `--verbose / -v` — Show extracted text before inference

---

## Development

```bash
pip install -e ".[dev]"
ruff format docscan/ tests/
ruff check docscan/ tests/
pytest tests/ -v --cov=docscan
```

---

## License

AGPL-3.0-or-later
