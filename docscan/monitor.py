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

"""monitor.py — System resource monitoring for Offline DocScan.

Collects CPU, memory, disk, and process metrics using psutil.
Falls back gracefully when psutil is unavailable.
"""

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any

from docscan.inference import _MODEL_INSTANCE


@dataclass
class SystemSnapshot:
    cpu_percent: float = 0.0
    cpu_cores: int = 0
    memory_used_mb: float = 0.0
    memory_total_mb: float = 0.0
    memory_percent: float = 0.0
    process_cpu_percent: float = 0.0
    process_ram_mb: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    disk_percent: float = 0.0
    active_threads: int = 0
    network_status: str = "Offline"
    inference_engine: str = "N/A"
    inference_details: str = "Offline Inference"
    gpu_used: bool = False
    timestamp: str = ""


@dataclass
class MetricsHistory:
    cpu: list[float] = field(default_factory=list)
    memory: list[float] = field(default_factory=list)
    timestamps: list[str] = field(default_factory=list)
    max_points: int = 60

    def add(self, cpu: float, memory: float, timestamp: str) -> None:
        self.cpu.append(cpu)
        self.memory.append(memory)
        self.timestamps.append(timestamp)
        if len(self.cpu) > self.max_points:
            self.cpu.pop(0)
            self.memory.pop(0)
            self.timestamps.pop(0)


_history = MetricsHistory()
_history_lock = threading.Lock()


def _get_inference_info() -> tuple[str, str, bool]:
    engine = "N/A"
    details = "Offline Inference"
    gpu_used = False

    try:
        if _MODEL_INSTANCE is not None:
            model_path = getattr(_MODEL_INSTANCE, "model_path", "")
            if "phi3" in model_path.lower():
                engine = "Phi-3 Mini"
            elif "llama" in model_path.lower():
                engine = "llama.cpp"
            elif "whisper" in model_path.lower():
                engine = "Whisper.cpp"
            elif "onnx" in model_path.lower():
                engine = "ONNX Runtime"
            else:
                engine = "llama.cpp"

            n_gpu_layers = getattr(_MODEL_INSTANCE, "n_gpu_layers", 0)
            gpu_used = n_gpu_layers > 0

            if gpu_used:
                details = "GPU Accelerated"
            else:
                details = "CPU Processing"
        else:
            engine = "llama.cpp"
            details = "Ready"
    except Exception:
        engine = "llama.cpp"
        details = "Offline"

    return engine, details, gpu_used


def _check_psutil() -> bool:
    try:
        import psutil  # noqa: F401

        return True
    except ImportError:
        return False


def collect_snapshot() -> SystemSnapshot:
    snapshot = SystemSnapshot()
    snapshot.timestamp = time.strftime("%H:%M:%S")

    if not _check_psutil():
        snapshot.cpu_cores = os.cpu_count() or 4
        snapshot.network_status = "Offline"
        _, details, gpu_used = _get_inference_info()
        snapshot.inference_details = details
        snapshot.gpu_used = gpu_used
        return snapshot

    import psutil

    snapshot.cpu_percent = psutil.cpu_percent(interval=0.1)
    snapshot.cpu_cores = psutil.cpu_count(logical=True) or 4

    mem = psutil.virtual_memory()
    snapshot.memory_used_mb = round(mem.used / 1024 / 1024, 1)
    snapshot.memory_total_mb = round(mem.total / 1024 / 1024, 1)
    snapshot.memory_percent = round(mem.percent, 1)

    try:
        process = psutil.Process()
        snapshot.process_cpu_percent = round(process.cpu_percent(interval=0.05), 1)
        proc_mem = process.memory_info()
        snapshot.process_ram_mb = round(proc_mem.rss / 1024 / 1024, 1)
        snapshot.active_threads = process.num_threads()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    disk = psutil.disk_usage("/")
    snapshot.disk_used_gb = round(disk.used / 1024 / 1024 / 1024, 2)
    snapshot.disk_total_gb = round(disk.total / 1024 / 1024 / 1024, 2)
    snapshot.disk_percent = round(disk.percent, 1)

    snapshot.network_status = "Offline"

    engine, details, gpu_used = _get_inference_info()
    snapshot.inference_engine = engine
    snapshot.inference_details = details
    snapshot.gpu_used = gpu_used

    return snapshot


def get_snapshot() -> SystemSnapshot:
    return collect_snapshot()


def get_history() -> dict[str, Any]:
    with _history_lock:
        return {
            "cpu": list(_history.cpu),
            "memory": list(_history.memory),
            "timestamps": list(_history.timestamps),
        }


def record_metrics() -> SystemSnapshot:
    snapshot = collect_snapshot()
    with _history_lock:
        _history.add(snapshot.cpu_percent, snapshot.memory_percent, snapshot.timestamp)
    return snapshot
