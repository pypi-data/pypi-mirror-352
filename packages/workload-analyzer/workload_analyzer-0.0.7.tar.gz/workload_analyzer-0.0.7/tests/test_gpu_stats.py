import datetime
from unittest.mock import MagicMock, patch

from workload_analyzer.gpu_stats import GPUStat, get_gpu_stats, safe_float


def test_gpu_stat_init_class() -> None:
    """Test that the custom field validator and computed field for GPUStat works correctly."""
    gpu_stat = GPUStat(
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
    )
    assert gpu_stat.timestamp == datetime.datetime(2023, 1, 1, 0, 0, 0)
    assert gpu_stat.memory_percentage == 50.0


def test_safe_float() -> None:
    """Test the safe_float function."""
    assert safe_float("123.45") == 123.45
    assert safe_float(None) is None
    assert safe_float("invalid") is None


@patch("workload_analyzer.gpu_stats.Popen")
def test_get_gpu_stats(mock_popen: MagicMock) -> None:
    """Test the get_gpu_stats function."""
    mock_process = MagicMock()
    mock_process.communicate.return_value = (
        b"2023/01/01 00:00:00.000000, 0, GPU 0, uuid-0, 460.32, serial-0,"
        b" Enabled, Active, Default, 8192, 4096, 4096, 50.0, 25.0,"
        b" 70, 150.0, 200.0, 50.0, 1500.0, P2\n",
        b"",
    )
    mock_popen.return_value = mock_process

    gpu_stats = get_gpu_stats()
    assert len(gpu_stats) == 1
    gpu = gpu_stats[0]
    assert gpu.index == 0
    assert gpu.name == "GPU 0"
    assert gpu.memory_total == 8192
    assert gpu.memory_used == 4096
    assert gpu.memory_percentage == 50.0


@patch("workload_analyzer.gpu_stats.Popen")
def test_get_gpu_stats_nvidia_smi_not_available(mock_popen: MagicMock) -> None:
    """Test the get_gpu_stats function when nvidia-smi is not available."""
    mock_popen.side_effect = OSError("nvidia-smi not found")

    gpu_stats = get_gpu_stats()
    assert gpu_stats == []
