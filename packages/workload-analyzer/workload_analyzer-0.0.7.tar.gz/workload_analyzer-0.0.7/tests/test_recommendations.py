from unittest.mock import patch

import pytest

from workload_analyzer.gpu_stats import GPUStat
from workload_analyzer.recommendations import (
    recommend,
    recommend_from_cpu_usage,
    recommend_from_disk_usage,
    recommend_from_gpu_compute_utilization,
    recommend_from_gpu_memory_bandwidth_utilization,
    recommend_from_gpu_memory_usage,
    recommend_from_network_usage,
)
from workload_analyzer.system_stats import MemoryStat, NetworkStat, ProcessStat, SystemStat


@pytest.fixture
def sample_gpu_stats() -> dict[str, list[GPUStat]]:
    """Fixture providing sample GPU statistics."""
    return {
        "gpu0": [
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
    }


@pytest.fixture
def sample_system_stats() -> list[SystemStat]:
    """Fixture providing sample system statistics."""
    return [
        SystemStat(
            timestamp="2025/05/19 12:00:00.000",
            memory=MemoryStat(total=8 * 1024**3, used=5 * 1024**3, available=3 * 1024**3, percent=62.5),
            cpu_percent=25.0,
            disk_percent=55.0,
            proc_mem=ProcessStat(rss=150.0, percent=1.2, threads=5),
            network=NetworkStat(sent=12345678, recv=87654321),
        ),
        SystemStat(
            timestamp="2025/05/19 12:05:00.000",
            memory=MemoryStat(total=16 * 1024**3, used=10 * 1024**3, available=6 * 1024**3, percent=62.5),
            cpu_percent=45.0,
            disk_percent=70.0,
            proc_mem=ProcessStat(rss=300.0, percent=2.5, threads=10),
            network=NetworkStat(sent=22334455, recv=55443322),
        ),
    ]


def test_recommend(sample_gpu_stats: dict[str, list[GPUStat]], sample_system_stats: list[SystemStat]) -> None:
    """Test that the main recommend function calls all sub-functions."""
    with (
        patch("workload_analyzer.recommendations.recommend_from_gpu_memory_usage") as mock_gpu_mem,
        patch("workload_analyzer.recommendations.recommend_from_gpu_compute_utilization") as mock_gpu_compute,
        patch(
            "workload_analyzer.recommendations.recommend_from_gpu_memory_bandwidth_utilization"
        ) as mock_gpu_bandwidth,
        patch("workload_analyzer.recommendations.recommend_from_disk_usage") as mock_disk,
        patch("workload_analyzer.recommendations.recommend_from_cpu_usage") as mock_cpu,
        patch("workload_analyzer.recommendations.recommend_from_network_usage") as mock_network,
    ):
        recommend(sample_gpu_stats, sample_system_stats)

        mock_gpu_mem.assert_called_once_with(sample_gpu_stats)
        mock_gpu_compute.assert_called_once_with(sample_gpu_stats)
        mock_gpu_bandwidth.assert_called_once_with(sample_gpu_stats)
        mock_disk.assert_called_once_with(sample_system_stats)
        mock_cpu.assert_called_once_with(sample_system_stats)
        mock_network.assert_called_once_with(sample_system_stats)


def test_recommend_from_gpu_memory_usage(
    sample_gpu_stats: dict[str, list[GPUStat]], capsys: pytest.CaptureFixture
) -> None:
    """Test the GPU memory usage recommendation function."""
    # Test with default breakpoints
    recommend_from_gpu_memory_usage(sample_gpu_stats)
    captured = capsys.readouterr()

    # Check for expected output fragments
    assert "GPU0" in captured.out
    assert "Average Memory Utilization" in captured.out
    assert "Max Memory Used" in captured.out

    # Test with custom breakpoints
    recommend_from_gpu_memory_usage(sample_gpu_stats, [4, 8, 16])
    captured = capsys.readouterr()
    assert "Suggestion:" in captured.out

    # Test with empty stats
    recommend_from_gpu_memory_usage({})
    captured = capsys.readouterr()
    assert "No GPU statistics provided" in captured.out

    # Test with empty stat list
    recommend_from_gpu_memory_usage({"empty_gpu": []})
    captured = capsys.readouterr()
    assert "No stats recorded for empty_gpu" in captured.out


def test_recommend_from_gpu_compute_utilization(
    sample_gpu_stats: dict[str, list[GPUStat]], capsys: pytest.CaptureFixture
) -> None:
    """Test the GPU compute utilization recommendation function."""
    recommend_from_gpu_compute_utilization(sample_gpu_stats)
    captured = capsys.readouterr()

    assert "GPU0" in captured.out
    assert "Average Compute Utilization" in captured.out

    # Test with empty stat list
    recommend_from_gpu_compute_utilization({"empty_gpu": []})
    captured = capsys.readouterr()
    assert "No stats recorded for empty_gpu" in captured.out


def test_recommend_from_gpu_memory_bandwidth_utilization(
    sample_gpu_stats: dict[str, list[GPUStat]], capsys: pytest.CaptureFixture
) -> None:
    """Test the GPU memory bandwidth utilization recommendation function."""
    recommend_from_gpu_memory_bandwidth_utilization(sample_gpu_stats)
    captured = capsys.readouterr()

    assert "GPU0" in captured.out
    assert "Average Memory Bandwidth Utilization" in captured.out

    # Test with empty stat list
    recommend_from_gpu_memory_bandwidth_utilization({"empty_gpu": []})
    captured = capsys.readouterr()
    assert "No stats recorded for empty_gpu" in captured.out


def test_recommend_from_disk_usage(sample_system_stats: list[SystemStat], capsys: pytest.CaptureFixture) -> None:
    """Test the disk usage recommendation function."""
    recommend_from_disk_usage(sample_system_stats)
    captured = capsys.readouterr()

    assert "Average Disk Usage" in captured.out

    # Test for different disk usage levels
    high_disk_stat = [
        SystemStat(
            timestamp="2025/05/19 12:00:00.000",
            memory=MemoryStat(total=8 * 1024**3, used=5 * 1024**3, available=3 * 1024**3, percent=62.5),
            cpu_percent=25.0,
            disk_percent=85.0,  # High disk usage
            proc_mem=ProcessStat(rss=150.0, percent=1.2, threads=5),
            network=NetworkStat(sent=12345678, recv=87654321),
        )
    ]

    recommend_from_disk_usage(high_disk_stat)
    captured = capsys.readouterr()
    assert "High disk usage detected" in captured.out

    # Test with empty stats
    recommend_from_disk_usage([])
    captured = capsys.readouterr()
    assert "No system statistics provided" in captured.out


def test_recommend_from_cpu_usage(sample_system_stats: list[SystemStat], capsys: pytest.CaptureFixture) -> None:
    """Test the CPU usage recommendation function."""
    recommend_from_cpu_usage(sample_system_stats)
    captured = capsys.readouterr()

    assert "Average CPU Utilization" in captured.out

    # Test for different CPU usage levels
    high_cpu_stat = [
        SystemStat(
            timestamp="2025/05/19 12:00:00.000",
            memory=MemoryStat(total=8 * 1024**3, used=5 * 1024**3, available=3 * 1024**3, percent=62.5),
            cpu_percent=90.0,  # High CPU usage
            disk_percent=55.0,
            proc_mem=ProcessStat(rss=150.0, percent=1.2, threads=5),
            network=NetworkStat(sent=12345678, recv=87654321),
        )
    ]

    recommend_from_cpu_usage(high_cpu_stat)
    captured = capsys.readouterr()
    assert "CPU is heavily utilized" in captured.out

    # Test with empty stats
    recommend_from_cpu_usage([])
    captured = capsys.readouterr()
    assert "No system statistics provided" in captured.out


def test_recommend_from_network_usage(sample_system_stats: list[SystemStat], capsys: pytest.CaptureFixture) -> None:
    """Test the network usage recommendation function."""
    recommend_from_network_usage(sample_system_stats)
    captured = capsys.readouterr()

    assert "Average Network Sent Rate" in captured.out
    assert "Average Network Recv Rate" in captured.out

    # Test with high network usage
    high_network_stats = [
        SystemStat(
            timestamp="2025/05/19 12:00:00.000",
            memory=MemoryStat(total=8 * 1024**3, used=5 * 1024**3, available=3 * 1024**3, percent=62.5),
            cpu_percent=25.0,
            disk_percent=55.0,
            proc_mem=ProcessStat(rss=150.0, percent=1.2, threads=5),
            network=NetworkStat(sent=0, recv=0),
        ),
        SystemStat(
            timestamp="2025/05/19 12:05:00.000",
            memory=MemoryStat(total=8 * 1024**3, used=5 * 1024**3, available=3 * 1024**3, percent=62.5),
            cpu_percent=25.0,
            disk_percent=55.0,
            proc_mem=ProcessStat(rss=150.0, percent=1.2, threads=5),
            network=NetworkStat(sent=10000000, recv=10000000),  # High network usage
        ),
    ]

    recommend_from_network_usage(high_network_stats)
    captured = capsys.readouterr()
    assert "High network input detected" in captured.out

    # Test with one stat (should return early)
    recommend_from_network_usage([sample_system_stats[0]])
    captured = capsys.readouterr()
    assert captured.out == ""

    # Test with empty stats
    recommend_from_network_usage([])
    captured = capsys.readouterr()
    assert captured.out == ""
