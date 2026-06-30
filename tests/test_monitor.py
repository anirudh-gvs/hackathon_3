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

from typing import Any

import pytest

from docscan.monitor import (
    MetricsHistory,
    SystemSnapshot,
    collect_snapshot,
    get_history,
    get_snapshot,
    record_metrics,
)


@pytest.fixture(autouse=True)
def _reset_history() -> None:
    import docscan.monitor as _m

    _m._history = MetricsHistory()


@pytest.fixture(autouse=True)
def _clean_psutil() -> Any:
    yield
    import sys

    sys.modules.pop("psutil", None)


def test_system_snapshot_defaults() -> None:
    snap = SystemSnapshot()
    assert snap.cpu_percent == 0.0
    assert snap.cpu_cores == 0
    assert snap.memory_used_mb == 0.0
    assert snap.memory_total_mb == 0.0
    assert snap.memory_percent == 0.0
    assert snap.process_cpu_percent == 0.0
    assert snap.process_ram_mb == 0.0
    assert snap.disk_used_gb == 0.0
    assert snap.disk_total_gb == 0.0
    assert snap.disk_percent == 0.0
    assert snap.active_threads == 0
    assert snap.network_status == "Offline"
    assert snap.inference_engine == "N/A"
    assert snap.inference_details == "Offline Inference"
    assert snap.gpu_used is False
    assert snap.timestamp == ""


def test_metrics_history_add() -> None:
    h = MetricsHistory()
    assert h.cpu == []
    assert h.memory == []
    assert h.timestamps == []
    h.add(50.0, 60.0, "12:00:00")
    assert h.cpu == [50.0]
    assert h.memory == [60.0]
    assert h.timestamps == ["12:00:00"]
    h.add(70.0, 80.0, "12:00:01")
    assert h.cpu == [50.0, 70.0]
    assert h.memory == [60.0, 80.0]
    assert h.timestamps == ["12:00:00", "12:00:01"]


def test_metrics_history_max_points() -> None:
    h = MetricsHistory(max_points=3)
    for i in range(5):
        h.add(float(i), float(i * 10), f"time_{i}")
    assert len(h.cpu) == 3
    assert h.cpu == [2.0, 3.0, 4.0]
    assert h.memory == [20.0, 30.0, 40.0]
    assert h.timestamps == ["time_2", "time_3", "time_4"]


def test_collect_snapshot_no_psutil(mocker: Any) -> None:
    mocker.patch("docscan.monitor._check_psutil", return_value=False)
    mocker.patch("docscan.monitor.os.cpu_count", return_value=8)
    snap = collect_snapshot()
    assert snap.cpu_cores == 8
    assert snap.cpu_percent == 0.0
    assert snap.network_status == "Offline"


def _mock_psutil(mocker: Any) -> Any:
    mock_psutil = mocker.MagicMock()
    mock_psutil.cpu_percent.return_value = 45.2
    mock_psutil.cpu_count.return_value = 4
    mock_mem = mocker.MagicMock()
    mock_mem.used = 8 * 1024 * 1024 * 1024
    mock_mem.total = 16 * 1024 * 1024 * 1024
    mock_mem.percent = 50.0
    mock_psutil.virtual_memory.return_value = mock_mem
    mock_process = mocker.MagicMock()
    mock_process.cpu_percent.return_value = 10.5
    mock_proc_mem = mocker.MagicMock()
    mock_proc_mem.rss = 500 * 1024 * 1024
    mock_process.memory_info.return_value = mock_proc_mem
    mock_process.num_threads.return_value = 12
    mock_psutil.Process.return_value = mock_process
    mock_disk = mocker.MagicMock()
    mock_disk.used = 100 * 1024 * 1024 * 1024
    mock_disk.total = 500 * 1024 * 1024 * 1024
    mock_disk.percent = 20.0
    mock_psutil.disk_usage.return_value = mock_disk
    return mock_psutil


def test_collect_snapshot_with_psutil(mocker: Any) -> None:
    import sys

    mock_psutil = _mock_psutil(mocker)
    sys.modules["psutil"] = mock_psutil
    mocker.patch("docscan.monitor._check_psutil", return_value=True)
    mocker.patch(
        "docscan.monitor._get_inference_info", return_value=("Phi-3 Mini", "CPU Processing", False)
    )
    snap = collect_snapshot()
    assert snap.cpu_percent == 45.2
    assert snap.cpu_cores == 4
    assert snap.memory_used_mb == 8192.0
    assert snap.memory_total_mb == 16384.0
    assert snap.memory_percent == 50.0
    assert snap.process_cpu_percent == 10.5
    assert snap.process_ram_mb == 500.0
    assert snap.active_threads == 12
    assert snap.network_status == "Offline"
    assert snap.disk_used_gb == 100.0
    assert snap.disk_total_gb == 500.0
    assert snap.disk_percent == 20.0


def test_collect_snapshot_psutil_no_process(mocker: Any) -> None:
    import sys

    class FakeNoSuchProcessError(Exception):
        pass

    class FakeAccessDeniedError(Exception):
        pass

    mock_psutil = mocker.MagicMock()
    mock_psutil.cpu_percent.return_value = 10.0
    mock_psutil.cpu_count.return_value = 8
    mock_mem = mocker.MagicMock()
    mock_mem.used = 4 * 1024 * 1024 * 1024
    mock_mem.total = 8 * 1024 * 1024 * 1024
    mock_mem.percent = 50.0
    mock_psutil.virtual_memory.return_value = mock_mem
    mock_psutil.Process.side_effect = FakeNoSuchProcessError(123)
    mock_psutil.NoSuchProcess = FakeNoSuchProcessError
    mock_psutil.AccessDenied = FakeAccessDeniedError
    mock_disk = mocker.MagicMock()
    mock_disk.used = 50 * 1024 * 1024 * 1024
    mock_disk.total = 200 * 1024 * 1024 * 1024
    mock_disk.percent = 25.0
    mock_psutil.disk_usage.return_value = mock_disk
    sys.modules["psutil"] = mock_psutil
    mocker.patch("docscan.monitor._check_psutil", return_value=True)
    mocker.patch(
        "docscan.monitor._get_inference_info",
        return_value=("llama.cpp", "Offline Inference", False),
    )
    snap = collect_snapshot()
    assert snap.cpu_percent == 10.0
    assert snap.process_cpu_percent == 0.0
    assert snap.process_ram_mb == 0.0
    assert snap.active_threads == 0


def test_get_snapshot(mocker: Any) -> None:
    mocker.patch("docscan.monitor._check_psutil", return_value=False)
    mocker.patch("docscan.monitor.os.cpu_count", return_value=4)
    snap = get_snapshot()
    assert isinstance(snap, SystemSnapshot)


def test_get_history_empty() -> None:
    h = get_history()
    assert h == {"cpu": [], "memory": [], "timestamps": []}


def test_record_metrics(mocker: Any) -> None:
    mocker.patch("docscan.monitor._check_psutil", return_value=False)
    mocker.patch("docscan.monitor.os.cpu_count", return_value=4)
    snap = record_metrics()
    assert isinstance(snap, SystemSnapshot)
    h = get_history()
    assert len(h["cpu"]) == 1
    assert h["cpu"][0] == 0.0
    assert len(h["timestamps"]) == 1


def test_record_metrics_appends(mocker: Any) -> None:
    import sys

    mock_psutil = _mock_psutil(mocker)
    sys.modules["psutil"] = mock_psutil
    mocker.patch("docscan.monitor._check_psutil", return_value=True)
    mocker.patch(
        "docscan.monitor._get_inference_info", return_value=("llama.cpp", "CPU Processing", False)
    )
    record_metrics()
    record_metrics()
    h = get_history()
    assert len(h["cpu"]) == 2
    assert h["cpu"] == [45.2, 45.2]
