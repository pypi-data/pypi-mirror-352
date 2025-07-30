import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from workload_analyzer import __version__
from workload_analyzer.monitor import Monitor
from workload_analyzer.recommendations import recommend

cli = typer.Typer()
IS_WINDOWS = sys.platform.startswith("win")


def version_callback(value: bool) -> None:
    """Callback function to print the version of the program."""
    if value:
        print(f"workload-analyzer {__version__} 🚀")
        raise typer.Exit


def start_process(command: str) -> subprocess.Popen:
    """Start a subprocess with the given command."""
    if IS_WINDOWS:
        # Create a new process group on Windows
        return subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)  # ty: ignore
    # Create a new session (process group) on Unix
    return subprocess.Popen(command, shell=True, preexec_fn=os.setsid)


def terminate_process(proc: subprocess.Popen, verbose: bool = False) -> None:
    """Terminate the subprocess and its group.

    Args:
        proc (subprocess.Popen): The subprocess to terminate.
        verbose (bool): Whether to log the termination process.

    """
    try:
        if IS_WINDOWS:
            if verbose:
                logger.info("Sending CTRL-BREAK to subprocess group (Windows)...")
            proc.send_signal(signal.CTRL_BREAK_EVENT)  # ty: ignore
        else:
            if verbose:
                logger.info("Sending SIGTERM to subprocess group (Unix)...")
            os.killpg(proc.pid, signal.SIGTERM)

        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if verbose:
            logger.warning("Subprocess group did not terminate gracefully. Forcing kill.")
        try:
            if IS_WINDOWS:
                proc.kill()  # no group kill, but better than nothing
            else:
                os.killpg(proc.pid, signal.SIGKILL)
        finally:
            proc.wait()


@cli.command()
def run(
    command: Annotated[str, typer.Argument(..., help="Command to run e.g., 'python main.py'")],
    timeout: Annotated[int, typer.Option(help="Time to monitor in seconds (default: 120)")] = 120,
    interval: Annotated[int, typer.Option(help="Polling interval in seconds (default: 3.0)")] = 3,
    recommendations: Annotated[
        bool, typer.Option(help="Enable recommendations for workload optimization (default: True)")
    ] = True,
    output_dir: Annotated[
        Path, typer.Option(help="Directory to save the output files (default: workload_results/)")
    ] = Path("workload_results"),
    verbose: Annotated[bool, typer.Option(help="Enable verbose logging (default: True)")] = True,
    version: Annotated[  # noqa: ARG001
        bool | None, typer.Option("--version", callback=version_callback, help="Print version of program")
    ] = None,
) -> None:
    """Main entry point for the workload analyzer CLI."""
    if verbose:
        logger.info(f"Starting workload analyzer ({__version__}) 🚀")
        logger.info("" + "=" * 40)
        logger.info(f"{'Command to run:':<20}{command}")
        logger.info(f"{'Timeout:':<20}{timeout} seconds")
        logger.info(f"{'Polling interval:':<20}{interval} seconds")
        logger.info(f"{'Output directory:':<20}{output_dir}")
        logger.info("" + "=" * 40)

    # Create the output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the monitor
    monitor = Monitor()
    gpu_info = monitor.get_gpu_info()
    if not gpu_info:  # empty GPU info
        logger.error("No GPU information found. Please check that nvidia-smi is installed and the GPUs are available.")
        logger.error("Continuing without GPU monitoring.")
        logger.info("" + "=" * 40)
    elif gpu_info and verbose:
        logger.info(gpu_info)
        logger.info("" + "=" * 40)

    # Start the command in a separate thread
    proc = start_process(command)

    # Start the monitoring loop
    stop_monitoring = threading.Event()

    def monitor_loop() -> None:
        """Function to run the monitoring loop."""
        start_time = time.monotonic()
        while not stop_monitoring.is_set() and time.monotonic() - start_time < timeout and proc.poll() is None:
            monitor.log()
            time.sleep(interval)

    thread = threading.Thread(target=monitor_loop)
    thread.start()

    # Wait for the process to finish or timeout
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        logger.info("Timeout reached. Terminating subprocess.")
        terminate_process(proc, verbose=verbose)
    finally:
        stop_monitoring.set()
        thread.join()

    monitor.visualize(output_dir=output_dir, verbose=verbose)
    monitor.save(output_dir=output_dir, verbose=verbose)

    if verbose:
        logger.info("Workload analyzer finished. 📊")

    if recommendations:
        time.sleep(2)  # Give some time for the logging, thread and process to finish
        recommend(monitor.gpu_stats, monitor.system_stats)
