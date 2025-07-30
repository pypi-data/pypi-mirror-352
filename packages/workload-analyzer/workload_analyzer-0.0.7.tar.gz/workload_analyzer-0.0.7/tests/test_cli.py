import signal
import subprocess
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from workload_analyzer.cli import (
    IS_WINDOWS,
    cli,
    start_process,
    terminate_process,
    version_callback,
)


@pytest.fixture
def mock_process() -> MagicMock:
    """Fixture for a mock subprocess.Popen object."""
    proc = MagicMock()
    proc.pid = 12345
    proc.poll.return_value = None
    return proc


@pytest.fixture
def mock_monitor() -> MagicMock:
    """Fixture for a mock Monitor object."""
    monitor = MagicMock()
    monitor.gpu_stats = [{"gpu_utilization": 50}]
    monitor.system_stats = [{"cpu_percent": 30}]
    monitor.get_gpu_info.return_value = {"gpu": "test_gpu"}
    return monitor


# Setup the CLI runner
runner = CliRunner()


def test_version_callback() -> None:
    """Test that version callback prints version and exits."""
    with pytest.raises(typer.Exit):
        version_callback(True)


@pytest.mark.skipif(not IS_WINDOWS, reason="Windows specific test")
@patch("subprocess.Popen")
def test_start_process_windows(mock_popen: MagicMock) -> None:
    """Test start_process function on Windows."""
    with patch("workload_analyzer.cli.IS_WINDOWS", True):
        start_process("echo test")

        # Check if Popen was called with the right parameters
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == "echo test"
        assert kwargs["shell"] is True
        assert "creationflags" in kwargs
        assert kwargs["creationflags"] == subprocess.CREATE_NEW_PROCESS_GROUP  # ty: ignore


@pytest.mark.skipif(IS_WINDOWS, reason="Unix specific test")
@patch("subprocess.Popen")
def test_start_process_unix(mock_popen: MagicMock) -> None:
    """Test start_process function on Unix."""
    with patch("workload_analyzer.cli.IS_WINDOWS", False):
        start_process("echo test")

        # Check if Popen was called with the right parameters
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == "echo test"
        assert kwargs["shell"] is True
        assert "preexec_fn" in kwargs


@pytest.mark.skipif(IS_WINDOWS, reason="Unix specific test")
@patch("os.killpg")
def test_terminate_process_unix(mock_killpg: MagicMock) -> None:
    """Test terminate_process function on Unix."""
    with patch("workload_analyzer.cli.IS_WINDOWS", False):
        mock_proc = MagicMock()
        mock_proc.pid = 12345

        terminate_process(mock_proc, verbose=True)

        # Check if killpg was called with SIGTERM
        mock_killpg.assert_called_with(12345, signal.SIGTERM)
        mock_proc.wait.assert_called_once()


@pytest.mark.skipif(not IS_WINDOWS, reason="Windows specific test")
@patch("workload_analyzer.cli.IS_WINDOWS", True)
def test_terminate_process_windows() -> None:
    """Test terminate_process function on Windows."""
    mock_proc = MagicMock()

    terminate_process(mock_proc, verbose=True)

    # Check if send_signal was called with CTRL_BREAK_EVENT
    mock_proc.send_signal.assert_called_with(signal.CTRL_BREAK_EVENT)  # ty: ignore
    mock_proc.wait.assert_called_once()


@patch("workload_analyzer.cli.terminate_process")
@patch("workload_analyzer.cli.start_process")
@patch("threading.Thread")
@patch("workload_analyzer.cli.Monitor")
def test_run_command(
    mock_monitor_class: MagicMock,
    mock_thread: MagicMock,
    mock_start_process: MagicMock,
    mock_terminate_process: MagicMock,  # noqa: ARG001
) -> None:
    """Test the run command functionality."""
    # Setup mocks
    mock_monitor = MagicMock()
    mock_monitor_class.return_value = mock_monitor
    mock_monitor.get_gpu_info.return_value = {"gpu": "test_gpu"}

    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    mock_start_process.return_value = mock_proc

    mock_thread_instance = MagicMock()
    mock_thread.return_value = mock_thread_instance

    # Run the command
    result = runner.invoke(cli, ["echo test", "--timeout", "10", "--interval", "1", "--output-dir", "test_dir"])

    # Check results
    assert result.exit_code == 0
    mock_start_process.assert_called_once_with("echo test")
    mock_thread.assert_called_once()
    mock_thread_instance.start.assert_called_once()
    mock_thread_instance.join.assert_called_once()
    mock_monitor.visualize.assert_called_once()
    mock_monitor.save.assert_called_once()


@patch("workload_analyzer.cli.terminate_process")
@patch("workload_analyzer.cli.start_process")
@patch("threading.Thread")
@patch("workload_analyzer.cli.Monitor")
def test_run_command_timeout(
    mock_monitor_class: MagicMock,
    mock_thread: MagicMock,
    mock_start_process: MagicMock,
    mock_terminate_process: MagicMock,
) -> None:
    """Test the run command with timeout expiration."""
    # Setup mocks
    mock_monitor = MagicMock()
    mock_monitor_class.return_value = mock_monitor
    mock_monitor.get_gpu_info.return_value = {"gpu": "test_gpu"}

    mock_proc = MagicMock()
    mock_proc.wait.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=10)
    mock_start_process.return_value = mock_proc

    mock_thread_instance = MagicMock()
    mock_thread.return_value = mock_thread_instance

    # Run the command
    result = runner.invoke(cli, ["echo test", "--timeout", "10", "--interval", "1", "--no-recommendations"])

    # Check results
    assert result.exit_code == 0
    mock_terminate_process.assert_called_once_with(mock_proc, verbose=True)
    mock_monitor.visualize.assert_called_once()
    mock_monitor.save.assert_called_once()


@patch("workload_analyzer.cli.terminate_process")
@patch("workload_analyzer.cli.start_process")
@patch("threading.Thread")
@patch("workload_analyzer.cli.Monitor")
def test_run_command_no_gpu(
    mock_monitor_class: MagicMock,
    mock_thread: MagicMock,
    mock_start_process: MagicMock,
    mock_terminate_process: MagicMock,  # noqa: ARG001
) -> None:
    """Test the run command when no GPU is available."""
    # Setup mocks
    mock_monitor = MagicMock()
    mock_monitor_class.return_value = mock_monitor
    mock_monitor.get_gpu_info.return_value = {}  # Empty GPU info

    mock_proc = MagicMock()
    mock_start_process.return_value = mock_proc

    mock_thread_instance = MagicMock()
    mock_thread.return_value = mock_thread_instance

    # Run the command
    result = runner.invoke(cli, ["echo test", "--timeout", "10", "--interval", "1", "--no-recommendations"])

    # Check results
    assert result.exit_code == 0
    mock_monitor.visualize.assert_called_once()
    mock_monitor.save.assert_called_once()
