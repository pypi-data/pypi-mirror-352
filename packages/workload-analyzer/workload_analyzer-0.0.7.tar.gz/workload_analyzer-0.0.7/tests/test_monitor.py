from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from workload_analyzer.gpu_stats import GPUStat
from workload_analyzer.monitor import Monitor


@pytest.fixture
def mock_gpu_stats() -> list[GPUStat]:
    """Fixture to provide mock GPU statistics."""
    return [
        GPUStat(
            timestamp="2023/01/01 00:00:00.000000",
            index=0,
            name="GPU 0",
            uuid="uuid-0",
            driver_version="460.32",
            gpu_serial="serial-0",
            display_active="Enabled",
            display_mode="Active",
            compute_mode="Default",
            memory_total=8192,
            memory_used=4096,
            memory_free=4096,
            utilization_gpu=50.0,
            utilization_memory=25.0,
            temperature=70,
            power_draw=150.0,
            power_limit=200.0,
            fan_speed=50.0,
            clocks_sm=1500.0,
            pstate="P2",
        ),
        GPUStat(
            timestamp="2023/01/01 00:00:01.000000",
            index=1,
            name="GPU 1",
            uuid="uuid-1",
            driver_version="460.32",
            gpu_serial="serial-1",
            display_active="Enabled",
            display_mode="Active",
            compute_mode="Default",
            memory_total=8192,
            memory_used=2048,
            memory_free=6144,
            utilization_gpu=25.0,
            utilization_memory=12.5,
            temperature=65,
            power_draw=100.0,
            power_limit=200.0,
            fan_speed=40.0,
            clocks_sm=1400.0,
            pstate="P2",
        ),
    ]


@patch("workload_analyzer.monitor.get_gpu_stats")
def test_monitor_init(mock_get_gpu_stats: MagicMock, mock_gpu_stats: list[GPUStat]) -> None:
    """Test the initialization of the Monitor class."""
    mock_get_gpu_stats.return_value = mock_gpu_stats
    monitor = Monitor()
    assert monitor.num_gpus == 2
    assert "gpu0" in monitor.gpu_stats
    assert "gpu1" in monitor.gpu_stats
    assert len(monitor.gpu_stats["gpu0"]) == 0


@patch("workload_analyzer.monitor.get_gpu_stats")
def test_monitor_log(mock_get_gpu_stats: MagicMock, mock_gpu_stats: list[GPUStat]) -> None:
    """Test the log method of the Monitor class."""
    mock_get_gpu_stats.return_value = mock_gpu_stats
    monitor = Monitor()
    monitor.log()
    assert len(monitor.gpu_stats["gpu0"]) == 1
    assert len(monitor.gpu_stats["gpu1"]) == 1
    assert monitor.gpu_stats["gpu0"][0].memory_used == 4096


@patch("workload_analyzer.monitor.get_gpu_stats")
def test_monitor_get_gpu_info(mock_get_gpu_stats: MagicMock, mock_gpu_stats: list[GPUStat]) -> None:
    """Test the get_gpu_info method of the Monitor class."""
    mock_get_gpu_stats.return_value = mock_gpu_stats
    monitor = Monitor()
    gpu_info = monitor.get_gpu_info()
    assert "Index: 0, Name: GPU 0, Memory Total: 8192 MB" in gpu_info
    assert "Index: 1, Name: GPU 1, Memory Total: 8192 MB" in gpu_info


@patch("workload_analyzer.monitor.get_gpu_stats")
@patch("matplotlib.pyplot.savefig")
def test_monitor_visualize(
    mock_savefig: MagicMock, mock_get_gpu_stats: MagicMock, mock_gpu_stats: list[GPUStat], tmp_path: Path
) -> None:
    """Test the visualize method of the Monitor class."""
    mock_get_gpu_stats.return_value = mock_gpu_stats
    monitor = Monitor()
    monitor.log()
    output_dir = tmp_path / "plots"
    output_dir.mkdir()
    monitor.visualize(output_dir)
    mock_savefig.assert_called()


@patch("workload_analyzer.monitor.get_gpu_stats")
@patch("pathlib.Path.open")
def test_monitor_save(
    mock_open: MagicMock, mock_get_gpu_stats: MagicMock, mock_gpu_stats: list[GPUStat], tmp_path: Path
) -> None:
    """Test the save method of the Monitor class."""
    mock_get_gpu_stats.return_value = mock_gpu_stats
    monitor = Monitor()
    monitor.log()
    output_dir = tmp_path / "stats"
    output_dir.mkdir()
    monitor.save(output_dir)
    mock_open.assert_called_once()
