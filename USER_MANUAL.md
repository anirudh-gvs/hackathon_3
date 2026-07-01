# 📖 User Manual — Offline DocScan

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Command Reference](#command-reference)
6. [Usage Examples](#usage-examples)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

**Offline DocScan** is a privacy-first, CPU-only command-line tool that extracts structured data from unstructured documents (PDFs, images, text files) using local LLM inference. All processing happens on your machine—no internet connection required, no data leaves your device.

### Key Features

- 🔒 **100% Offline**: No cloud uploads, no internet required
- 🚀 **CPU-Only**: Runs on any machine without GPU
- 📄 **Multiple Formats**: Supports PDF, PNG, JPG, JPEG, BMP, and TXT
- 🎯 **Structured Output**: Extracts data into JSON using predefined schemas
- ⚡ **Fast Processing**: Optimized for CPU inference
- 🔧 **Customizable**: Choose from multiple output schemas

---

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB for application and models
- **Processor**: Any modern CPU (x86_64 or ARM64)

### Recommended Requirements

- **RAM**: 8GB or more
- **Disk Space**: 5GB+ (for multiple model files)
- **Processor**: Multi-core CPU (4+ cores recommended)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://code.swecha.org/Gvs_Anirudh/cpu_first_hackathon.git
cd cpu_first_hackathon
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install the Package

```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Or install production version only
pip install -e .
```

### Step 4: Verify Installation

```bash
docscan --help
```

You should see the help message with available commands.

---

## Quick Start

### Basic Usage

Extract structured data from a document in 3 simple steps:

```bash
# 1. Scan a document with default settings
docscan scan my_document.pdf

# 2. Specify a schema for structured output
docscan scan receipt.jpg --schema receipt

# 3. Save output to a file
docscan scan invoice.pdf --schema receipt --output result.json
```

### Your First Scan

Let's scan a sample receipt image:

```bash
# Scan a receipt image
docscan scan samples/receipt.jpg --schema receipt --verbose

# View the extracted JSON
cat result.json
```

---

## Command Reference

### Main Command: `scan`

Extract structured JSON data from documents.

#### Syntax

```bash
docscan scan <file> [OPTIONS]
```

#### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `<file>` | Path to PDF, image (PNG/JPG/JPEG/BMP), or TXT file | Yes |

#### Options

| Option | Short | Description | Default | Example |
|--------|-------|-------------|---------|---------|
| `--schema` | `-s` | Output schema: `receipt`, `medical`, or `generic` | `generic` | `--schema receipt` |
| `--output` | `-o` | Write JSON output to file instead of stdout | stdout | `--output result.json` |
| `--model` | `-m` | Path to GGUF model file | `models/phi3-mini-q4.gguf` | `--model models/custom.gguf` |
| `--verbose` | `-v` | Show extracted text before inference | False | `--verbose` |
| `--help` | | Show help message | | |

### Secondary Command: `version`

Print version information.

```bash
docscan version
```

---

## Usage Examples

### Example 1: Extract Data from a Receipt

```bash
docscan scan grocery_receipt.jpg --schema receipt --output receipt.json
```

**Output (receipt.json)**:
```json
{
  "store_name": "Fresh Mart",
  "date": "2024-01-15",
  "items": [
    {
      "name": "Apples",
      "quantity": 2,
      "price": 5.99
    }
  ],
  "total": 15.47,
  "payment_method": "Credit Card"
}
```

### Example 2: Process a Medical Prescription

```bash
docscan scan prescription.pdf --schema medical --verbose
```

### Example 3: Batch Process Multiple Documents

```bash
# Process all PDFs in a directory
for file in documents/*.pdf; do
    docscan scan "$file" --schema generic --output "results/$(basename "$file" .pdf).json"
done
```

### Example 4: Use a Custom Model

```bash
docscan scan document.pdf --model models/llama-2-7b-q4.gguf --schema generic
```

### Example 5: View Extracted Text Before Inference

```bash
docscan scan scanned_doc.png --verbose --schema generic
```

This shows the raw extracted text before the LLM processes it, useful for debugging.

---

## Configuration

### Model Configuration

DocScan uses GGUF format models for local inference. The default model is `phi3-mini-q4.gguf`.

#### Default Model Location

```
models/
└── phi3-mini-q4.gguf
```

#### Using Custom Models

Place your GGUF model in the `models/` directory or specify the full path:

```bash
docscan scan doc.pdf --model /path/to/your/model.gguf
```

#### Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| phi3-mini-q4.gguf | ~2GB | Fast | Good | General purpose (default) |
| llama-2-7b-q4.gguf | ~4GB | Medium | Better | Complex documents |
| mistral-7b-q4.gguf | ~4GB | Medium | Better | Multi-language docs |

### Schema Selection

Choose the appropriate schema for your document type:

#### 1. `receipt` Schema
Best for: Retail receipts, invoices, bills
- Extracts: store name, date, items, prices, totals, payment method

#### 2. `medical` Schema
Best for: Prescriptions, medical reports, lab results
- Extracts: patient info, medications, dosages, dates, doctor info

#### 3. `generic` Schema
Best for: Any document type
- Extracts: key-value pairs, main content, metadata

### Environment Variables

Optional configuration via environment variables:

```bash
# Set custom model directory
export DOCSCAN_MODEL_DIR=/path/to/models

# Set default schema
export DOCSCAN_DEFAULT_SCHEMA=receipt

# Enable verbose logging
export DOCSCAN_VERBOSE=true
```

---

## Troubleshooting

### Common Issues

#### 1. "File not found" Error

**Problem**: The specified file path doesn't exist.

**Solution**:
```bash
# Use absolute path
docscan scan C:\Users\Name\Documents\file.pdf

# Or check current directory
dir  # Windows
ls   # macOS/Linux
```

#### 2. "Model not found" Error

**Problem**: The GGUF model file is missing.

**Solution**:
```bash
# Download the default model
# Place it in the models/ directory
mkdir models
# Download phi3-mini-q4.gguf to models/

# Or specify model path explicitly
docscan scan doc.pdf --model /full/path/to/model.gguf
```

#### 3. "Extraction failed" Error

**Problem**: Cannot extract text from the document.

**Solution**:
- Ensure the file is not corrupted
- Check if the file format is supported (PDF, PNG, JPG, JPEG, BMP, TXT)
- For scanned PDFs, ensure they contain embedded text or are OCR-readable

#### 4. Slow Processing

**Problem**: Inference takes too long.

**Solution**:
- Use a smaller model (phi3-mini instead of larger models)
- Close other CPU-intensive applications
- Increase virtual memory/swap space
- Use `--verbose` to see progress

#### 5. Out of Memory Error

**Problem**: System runs out of RAM during processing.

**Solution**:
- Close other applications
- Use a smaller quantized model (q4 instead of q8)
- Process smaller documents
- Increase system swap space

### Performance Tips

1. **Use SSD**: Store models and documents on SSD for faster loading
2. **Close Background Apps**: Free up RAM and CPU
3. **Smaller Models**: Use quantized models (q4) for better speed
4. **Batch Processing**: Process multiple files in sequence, not parallel

---

## FAQ

### General Questions

**Q: Is DocScan really 100% offline?**

A: Yes! All processing happens locally on your machine. No data is sent to external servers.

**Q: What file formats are supported?**

A: PDF, PNG, JPG, JPEG, BMP, and TXT files.

**Q: Do I need an internet connection?**

A: No, except for the initial installation and model download.

**Q: Is my data safe?**

A: Absolutely. All document processing happens on your device. No data leaves your computer.

### Technical Questions

**Q: What is a GGUF model?**

A: GGUF (GPT-Generated Unified Format) is a file format for LLM weights optimized for CPU inference.

**Q: Can I use my own LLM model?**

A: Yes, as long as it's in GGUF format. Use the `--model` option to specify it.

**Q: How accurate is the extraction?**

A: Accuracy depends on document quality and the model used. Clear, well-formatted documents yield the best results.

**Q: Can I run DocScan on a Raspberry Pi?**

A: Yes, if it runs Python 3.11+ and has enough RAM (4GB+ recommended).

### Troubleshooting Questions

**Q: Why is processing so slow?**

A: CPU inference is slower than GPU. Use smaller models and close other applications.

**Q: Can I speed up processing?**

A: Use quantized models (q4), ensure documents are high-quality, and use a faster CPU.

**Q: What if the extraction is incorrect?**

A: Try a different schema, use a larger/better model, or ensure the document is clear and readable.

---

## Getting Help

### Documentation

- **README.md**: Project overview and setup
- **docs/spec.md**: Technical specifications
- **docs/issues.md**: Known issues and solutions
- **CONTRIBUTING.md**: Contribution guidelines

### Support

- **GitLab Issues**: Report bugs at https://code.swecha.org/Gvs_Anirudh/cpu_first_hackathon/-/issues
- **Changelog**: See CHANGELOG.md for version history

---

## Appendix

### Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based or scanned (OCR) |
| PNG | `.png` | Color or grayscale |
| JPEG | `.jpg`, `.jpeg` | Compressed images |
| BMP | `.bmp` | Uncompressed images |
| Text | `.txt` | Plain text files |

### Output Schema Fields

#### Receipt Schema
- `store_name`: String
- `date`: String (YYYY-MM-DD)
- `items`: Array of objects (name, quantity, price)
- `total`: Float
- `payment_method`: String

#### Medical Schema
- `patient_name`: String
- `date`: String
- `medications`: Array of objects
- `doctor_name`: String
- `diagnosis`: String

#### Generic Schema
- `title`: String
- `content`: String
- `key_value_pairs`: Object
- `metadata`: Object

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 or later (AGPLv3+)**.

See the LICENSE file for full details.

---

## Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

---

**Last Updated**: 2024
**Version**: 0.1.0
**Maintainer**: DocScan Team