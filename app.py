# Copyright (C) 2024 DocScan Team
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from datetime import UTC, datetime

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from docscan.extractor import extract_text
from docscan.inference import run_inference, quick_extract
from docscan.monitor import record_metrics, get_history
from docscan.schemas import SchemaName
from docscan.storage import init_db, save_result, get_results, delete_result

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = Path("uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"].mkdir(exist_ok=True)

_cwd = os.path.abspath(".")
if _cwd.startswith("\\\\"):
    DB_PATH = os.path.join(tempfile.gettempdir(), "docscan_history.db")
else:
    DB_PATH = "docscan_history.db"
init_db(DB_PATH)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".txt"}


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def get_file_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return "PDF"
    elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
        return "Image"
    elif suffix == ".txt":
        return "Text"
    return "Unknown"


def infer_doc_type(schema_name: str, result: dict) -> str:
    if schema_name == "receipt":
        vendor = (result.get("vendor") or "")
        title = (result.get("title") or "")
        combined = (vendor + " " + title).lower()
        if "invoice" in combined or "bill" in combined:
            return "Invoice"
        return "Receipt"
    elif schema_name == "medical":
        return "Medical Report"
    elif schema_name == "generic":
        title = result.get("title", "")
        if title:
            lower = title.lower()
            if "invoice" in lower or "bill" in lower:
                return "Invoice"
            elif "receipt" in lower:
                return "Receipt"
            elif "report" in lower:
                return "Report"
        return "Document"
    return "Document"


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan() -> str:
    """Legacy endpoint — returns JSON. Kept for backward compatibility."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing file"}), 400

    schema_name = request.form.get("schema", "generic")
    try:
        schema = SchemaName(schema_name)
    except ValueError:
        return jsonify({"error": f"Unknown schema: {schema_name}"}), 400

    filename = secure_filename(file.filename)
    save_path = app.config["UPLOAD_FOLDER"] / filename
    file.save(str(save_path))

    try:
        text = extract_text(save_path)
        result = run_inference(text, schema, max_tokens=2048)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scan", methods=["POST"])
def api_scan() -> str:
    """Enhanced JSON API endpoint for the new SPA frontend."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing file"}), 400

    schema_name = request.form.get("schema", "generic")
    mode = request.form.get("mode", "quick")
    try:
        schema = SchemaName(schema_name)
    except ValueError:
        return jsonify({"error": f"Unknown schema: {schema_name}"}), 400

    filename = secure_filename(file.filename)
    save_path = app.config["UPLOAD_FOLDER"] / filename
    file.save(str(save_path))

    start_time = datetime.now(UTC)

    try:
        text = extract_text(save_path)
        
        if mode == "quick":
            # Instant keyword-based extraction - no AI model needed
            result = quick_extract(text, schema)
        else:
            # Full AI extraction using local LLM
            result = run_inference(text, schema, max_tokens=2048)
            
        duration = (datetime.now(UTC) - start_time).total_seconds()

        history_record = {
            "id": None,
            "source_file": filename,
            "file_type": get_file_type(filename),
            "doc_type": infer_doc_type(schema_name, result),
            "schema": schema_name,
            "mode": mode,
            "result": result,
            "status": "success",
            "duration_seconds": round(duration, 2),
            "created_at": datetime.now(UTC).isoformat(),
        }
        save_result(DB_PATH, filename, history_record)

        return jsonify({"success": True, "result": result, "record": history_record, "mode": mode})
    except Exception as e:
        duration = (datetime.now(UTC) - start_time).total_seconds()
        history_record = {
            "id": None,
            "source_file": filename,
            "file_type": get_file_type(filename),
            "doc_type": "Unknown",
            "schema": schema_name,
            "mode": mode,
            "result": {},
            "status": "failed",
            "error": str(e),
            "duration_seconds": round(duration, 2),
            "created_at": datetime.now(UTC).isoformat(),
        }
        save_result(DB_PATH, filename, history_record)
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def api_history() -> str:
    """Return extraction history."""
    rows = get_results(DB_PATH)
    cleaned = []
    for row in rows:
        result_data = row.get("result", {}) if isinstance(row.get("result"), dict) else {}
        rec = {
            "id": row.get("id"),
            "source_file": result_data.get("source_file", row.get("source_file")),
            "created_at": row.get("created_at"),
            "file_type": result_data.get("file_type", "Unknown"),
            "doc_type": result_data.get("doc_type", "Document"),
            "schema": result_data.get("schema", "generic"),
            "status": result_data.get("status", "unknown"),
            "duration_seconds": result_data.get("duration_seconds"),
            "error": result_data.get("error"),
            "extraction": result_data.get("result", {}),
        }
        cleaned.append(rec)
    return jsonify(cleaned)


@app.route("/api/history/<int:record_id>", methods=["DELETE"])
def api_history_delete(record_id: int) -> str:
    """Delete a history record."""
    delete_result(DB_PATH, record_id)
    return jsonify({"success": True})


@app.route("/api/stats", methods=["GET"])
def api_stats() -> str:
    """Return dashboard statistics."""
    rows = get_results(DB_PATH)
    total = len(rows)
    success = 0
    failed = 0

    schema_counts: dict[str, int] = {}
    doc_type_counts: dict[str, int] = {}
    total_duration = 0.0
    duration_count = 0

    for r in rows:
        result_data = r.get("result", {}) if isinstance(r.get("result"), dict) else {}
        status = result_data.get("status", "unknown")
        if status == "failed":
            failed += 1
        else:
            success += 1

        schema = result_data.get("schema", "generic")
        schema_counts[schema] = schema_counts.get(schema, 0) + 1

        doc_type = result_data.get("doc_type", "Document")
        doc_type_counts[doc_type] = doc_type_counts.get(doc_type, 0) + 1

        dur = result_data.get("duration_seconds")
        if dur:
            total_duration += dur
            duration_count += 1

    avg_duration = round(total_duration / duration_count, 2) if duration_count else 0
    success_rate = round((success / total * 100), 1) if total else 0

    return jsonify({
        "total_documents": total,
        "successful": success,
        "failed": failed,
        "success_rate": success_rate,
        "avg_processing_time": avg_duration,
        "by_schema": schema_counts,
        "by_doc_type": doc_type_counts,
    })


@app.route("/api/system/metrics", methods=["GET"])
def api_system_metrics() -> str:
    """Return live system metrics for the monitoring widget."""
    snapshot = record_metrics()
    return jsonify({
        "cpu_percent": snapshot.cpu_percent,
        "cpu_cores": snapshot.cpu_cores,
        "memory_used_mb": snapshot.memory_used_mb,
        "memory_total_mb": snapshot.memory_total_mb,
        "memory_percent": snapshot.memory_percent,
        "process_cpu_percent": snapshot.process_cpu_percent,
        "process_ram_mb": snapshot.process_ram_mb,
        "disk_used_gb": snapshot.disk_used_gb,
        "disk_total_gb": snapshot.disk_total_gb,
        "disk_percent": snapshot.disk_percent,
        "active_threads": snapshot.active_threads,
        "network_status": snapshot.network_status,
        "inference_engine": snapshot.inference_engine,
        "inference_details": snapshot.inference_details,
        "gpu_used": snapshot.gpu_used,
        "timestamp": snapshot.timestamp,
    })


@app.route("/api/system/history", methods=["GET"])
def api_system_history() -> str:
    """Return lightweight performance history for charting."""
    return jsonify(get_history())


@app.route("/api/download/<filename>", methods=["GET"])
def api_download(filename: str) -> str:
    """Download an uploaded file."""
    safe = secure_filename(filename)
    upload_dir = app.config["UPLOAD_FOLDER"]
    file_path = upload_dir / safe
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(upload_dir, safe, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
