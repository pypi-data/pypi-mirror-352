import datetime
from unittest.mock import MagicMock, patch

import psutil

from workload_analyzer.system_stats import MemoryStat, NetworkStat, ProcessStat, SystemStat, get_system_stats


def test_memory_stat_computed_fields() -> None:
    """Test that the computed fields in MemoryStat work correctly."""
    memory_stat = MemoryStat(
        total=16 * (1024**3),  # 16 GB
        used=8 * (1024**3),  # 8 GB
        available=8 * (1024**3),  # 8 GB
        percent=50.0,
    )
    assert memory_stat.total_gb == 16.0
    assert memory_stat.used_gb == 8.0
    assert memory_stat.available_gb == 8.0
    assert memory_stat.percent == 50.0


def test_system_stat_timestamp_validator() -> None:
    """Test that the custom field validator for SystemStat works correctly."""
    timestamp_str = "2023/01/01 00:00:00.000000"
    system_stat = SystemStat(
        timestamp=timestamp_str,
        memory=MemoryStat(total=16 * (1024**3), used=8 * (1024**3), available=8 * (1024**3), percent=50.0),
        cpu_percent=25.0,
        disk_percent=60.0,
        proc_mem=ProcessStat(),
        network=NetworkStat(sent=1000, recv=2000),
    )
    assert system_stat.timestamp == datetime.datetime(2023, 1, 1, 0, 0, 0)

    # Test with datetime object directly
    now = datetime.datetime.now()
    system_stat = SystemStat(
        timestamp=now,
        memory=MemoryStat(total=16 * (1024**3), used=8 * (1024**3), available=8 * (1024**3), percent=50.0),
        cpu_percent=25.0,
        disk_percent=60.0,
        proc_mem=ProcessStat(),
        network=NetworkStat(sent=1000, recv=2000),
    )
    assert system_stat.timestamp == now


@patch("workload_analyzer.system_stats.datetime.datetime")
@patch("psutil.virtual_memory")
@patch("psutil.cpu_percent")
@patch("psutil.disk_usage")
@patch("psutil.net_io_counters")
@patch("psutil.Process")
def test_get_system_stats(
    mock_process: MagicMock,
    mock_net_io: MagicMock,
    mock_disk_usage: MagicMock,
    mock_cpu_percent: MagicMock,
    mock_virtual_memory: MagicMock,
    mock_datetime: MagicMock,
) -> None:
    """Test the get_system_stats function."""
    # Set up mocks
    mock_now = datetime.datetime(2023, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = mock_now

    # Mock memory stats
    mock_memory = MagicMock()
    mock_memory.total = 16 * (1024**3)
    mock_memory.used = 8 * (1024**3)
    mock_memory.available = 8 * (1024**3)
    mock_memory.percent = 50.0
    mock_virtual_memory.return_value = mock_memory

    # Mock CPU percent
    mock_cpu_percent.return_value = 25.0

    # Mock disk usage
    mock_disk = MagicMock()
    mock_disk.percent = 60.0
    mock_disk_usage.return_value = mock_disk

    # Mock network I/O
    mock_net = MagicMock()
    mock_net.bytes_sent = 1000
    mock_net.bytes_recv = 2000
    mock_net_io.return_value = mock_net

    # Mock process
    mock_process_instance = MagicMock()
    mock_process_instance.memory_info.return_value.rss = 200 * 1048576  # 200 MB
    mock_process_instance.memory_percent.return_value = 10.0
    mock_process_instance.num_threads.return_value = 5
    mock_process.return_value = mock_process_instance

    # Call the function
    system_stat = get_system_stats()

    # Assertions
    assert system_stat.memory.total == mock_memory.total
    assert system_stat.memory.used == mock_memory.used
    assert system_stat.memory.available == mock_memory.available
    assert system_stat.memory.percent == mock_memory.percent
    assert system_stat.cpu_percent == 25.0
    assert system_stat.disk_percent == 60.0
    assert system_stat.network.sent == 1000
    assert system_stat.network.recv == 2000
    assert system_stat.proc_mem.rss == 200.0
    assert system_stat.proc_mem.percent == 10.0
    assert system_stat.proc_mem.threads == 5


@patch("psutil.virtual_memory")
@patch("psutil.cpu_percent")
@patch("psutil.disk_usage")
@patch("psutil.net_io_counters")
@patch("psutil.Process")
def test_get_system_stats_with_process_exception(
    mock_process: MagicMock,
    mock_net_io: MagicMock,
    mock_disk_usage: MagicMock,
    mock_cpu_percent: MagicMock,
    mock_virtual_memory: MagicMock,
) -> None:
    """Test handling of NoSuchProcess exception in get_system_stats."""
    # Set up basic mocks
    mock_memory = MagicMock()
    mock_memory.total = 16 * (1024**3)
    mock_memory.used = 8 * (1024**3)
    mock_memory.available = 8 * (1024**3)
    mock_memory.percent = 50.0
    mock_virtual_memory.return_value = mock_memory

    mock_cpu_percent.return_value = 25.0

    mock_disk = MagicMock()
    mock_disk.percent = 60.0
    mock_disk_usage.return_value = mock_disk

    mock_net = MagicMock()
    mock_net.bytes_sent = 1000
    mock_net.bytes_recv = 2000
    mock_net_io.return_value = mock_net

    # Make Process raise an exception
    mock_process.side_effect = psutil.NoSuchProcess(1)

    # Call the function
    system_stat = get_system_stats()

    # Verify Process stats are default values
    assert system_stat.proc_mem.rss is None
    assert system_stat.proc_mem.percent is None
    assert system_stat.proc_mem.threads is None


@patch("psutil.virtual_memory")
@patch("psutil.cpu_percent")
@patch("psutil.disk_usage")
@patch("psutil.net_io_counters")
@patch("psutil.Process")
def test_get_system_stats_with_net_init(
    mock_process: MagicMock,  # noqa: ARG001
    mock_net_io: MagicMock,
    mock_disk_usage: MagicMock,
    mock_cpu_percent: MagicMock,
    mock_virtual_memory: MagicMock,
) -> None:
    """Test get_system_stats with net_init parameter."""
    # Set up basic mocks
    mock_memory = MagicMock()
    mock_memory.total = 16 * (1024**3)
    mock_memory.used = 8 * (1024**3)
    mock_memory.available = 8 * (1024**3)
    mock_memory.percent = 50.0
    mock_virtual_memory.return_value = mock_memory

    mock_cpu_percent.return_value = 25.0

    mock_disk = MagicMock()
    mock_disk.percent = 60.0
    mock_disk_usage.return_value = mock_disk

    # Network values with initial values
    mock_net = MagicMock()
    mock_net.bytes_sent = 5000
    mock_net.bytes_recv = 8000
    mock_net_io.return_value = mock_net

    # Initial network values
    net_init = {"sent": 3000, "recv": 4000}

    # Call the function with net_init
    system_stat = get_system_stats(net_init=net_init)

    # Expected network values after subtracting initial values
    assert system_stat.network.sent == 2000  # 5000 - 3000
    assert system_stat.network.recv == 4000  # 8000 - 4000
