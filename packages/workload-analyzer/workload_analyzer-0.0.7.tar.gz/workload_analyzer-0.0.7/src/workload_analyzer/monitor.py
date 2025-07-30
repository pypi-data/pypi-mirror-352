import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from loguru import logger

from workload_analyzer.gpu_stats import GPUStat, get_gpu_stats
from workload_analyzer.system_stats import SystemStat, get_system_stats


class Monitor:
    """A class to monitor GPU statistics."""

    def __init__(self) -> None:
        gpus = get_gpu_stats()
        self.num_gpus = len(gpus)
        self.gpu_stats: dict[str, list[GPUStat]] = {f"gpu{gpu.index}": [] for gpu in gpus}
        self.system_stats: list[SystemStat] = []

    def log(self) -> None:
        """Log the GPU statistics."""
        gpus = get_gpu_stats()
        for gpu in gpus:
            self.gpu_stats[f"gpu{gpu.index}"].append(gpu)
        self.system_stats.append(get_system_stats())

    def get_gpu_info(self) -> str:
        """Get information about the GPUs."""
        gpus = get_gpu_stats()
        gpu_info = ""
        for gpu in gpus:
            gpu_info += f"Index: {gpu.index}, Name: {gpu.name}, Memory Total: {gpu.memory_total} MB\n"
        return gpu_info

    def save(self, output_dir: Path, verbose: bool = False) -> None:
        """Save the GPU statistics to a file.

        Args:
            output_dir (str): The directory where the statistics will be saved.
            verbose (bool): If True, print the path of the saved file.

        """
        path = output_dir / "stats.json"
        data = {
            "gpu_stats": {
                gpu_name: [stat.model_dump() for stat in stats] for gpu_name, stats in self.gpu_stats.items()
            },
            "system_stats": [stat.model_dump() for stat in self.system_stats],
        }

        with Path(path).open("w") as f:
            json.dump(data, f, indent=4, default=str)

        if verbose:
            logger.info(f"Saved GPU statistics to {path}")

    def visualize(self, output_dir: Path, verbose: bool = False) -> None:
        """Visualize the GPU statistics.

        Args:
            output_dir (str): The directory where the plots will be saved.
            verbose (bool): If True, print the paths of the saved plots.
        """
        sns.set_theme()

        # Visualize GPU stats
        self._visualize_gpu_stats(output_dir, verbose)

        # Visualize system stats
        self._visualize_system_stats(output_dir, verbose)

    def _visualize_gpu_stats(self, output_dir: Path, verbose: bool = False) -> None:
        """Visualize the GPU statistics.

        Args:
            output_dir (Path): The directory where the plots will be saved.
            verbose (bool): If True, print the paths of the saved plots.
        """
        for name, gpu in self.gpu_stats.items():
            # Create a new figure and axes
            fig, ax1 = plt.subplots()

            # Convert GPU stats to DataFrame
            dataframe = pd.DataFrame([stat.model_dump() for stat in gpu])
            dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"])
            start_time = dataframe["timestamp"].iloc[0]
            dataframe["elapsed_seconds"] = (dataframe["timestamp"] - start_time).dt.total_seconds()

            # Plot memory metrics on primary y-axis
            sns.lineplot(
                data=dataframe, x="elapsed_seconds", y="memory_used", ax=ax1, label="Memory Used (MB)", color="blue"
            )
            sns.lineplot(
                data=dataframe, x="elapsed_seconds", y="memory_free", ax=ax1, label="Memory Free (MB)", color="green"
            )
            sns.lineplot(
                data=dataframe, x="elapsed_seconds", y="memory_total", ax=ax1, label="Memory Total (MB)", color="red"
            )
            ax1.set_ylabel("Memory (MB)")
            ax1.legend_.remove()
            # Plot memory utilization on secondary y-axis
            ax2 = ax1.twinx()
            sns.lineplot(
                data=dataframe,
                x="elapsed_seconds",
                y="memory_percentage",
                ax=ax2,
                label="Memory Utilization (%)",
                color="purple",
            )
            ax2.set_ylabel("Memory Utilization (%)")
            ax2.legend_.remove()

            # Combine legends from both axes
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(
                lines1 + lines2,
                labels1 + labels2,
                loc="lower center",
                bbox_to_anchor=(0.5, -0.4),
                ncol=2,
            )

            ax1.set_xlabel("Time Elapsed (s)")
            plt.title(f"GPU Memory Statistics: {name}")
            plt.tight_layout()

            path = output_dir / f"gpu_memory_{name}.png"
            plt.savefig(path, dpi=300, bbox_inches="tight")
            plt.close(fig)
            if verbose:
                logger.info(f"Saved GPU memory statistics plot to {path}")

    def _visualize_system_stats(self, output_dir: Path, verbose: bool = False) -> None:
        """Visualize the system statistics.

        Args:
            output_dir (Path): The directory where the plots will be saved.
            verbose (bool): If True, print the paths of the saved plots.
        """
        if not self.system_stats:
            logger.warning("No system statistics to visualize.")
            return

        # Convert system stats to DataFrame
        dataframe = pd.DataFrame([stat.model_dump() for stat in self.system_stats])
        dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"])
        start_time = dataframe["timestamp"].iloc[0]
        dataframe["elapsed_seconds"] = (dataframe["timestamp"] - start_time).dt.total_seconds()

        # Extract memory data for easier access
        dataframe["memory_total_gb"] = dataframe["memory"].apply(lambda x: x["total"] / (1024**3))
        dataframe["memory_used_gb"] = dataframe["memory"].apply(lambda x: x["used"] / (1024**3))
        dataframe["memory_available_gb"] = dataframe["memory"].apply(lambda x: x["available"] / (1024**3))
        dataframe["memory_percent"] = dataframe["memory"].apply(lambda x: x["percent"])

        # Extract process memory data
        dataframe["proc_rss"] = dataframe["proc_mem"].apply(lambda x: x["rss"] if x["rss"] is not None else 0)
        dataframe["proc_percent"] = dataframe["proc_mem"].apply(
            lambda x: x["percent"] if x["percent"] is not None else 0
        )

        # Extract network data
        dataframe["net_sent_mb"] = dataframe["network"].apply(lambda x: x["sent"] / (1024**2))
        dataframe["net_recv_mb"] = dataframe["network"].apply(lambda x: x["recv"] / (1024**2))

        # Visualize system memory
        self._plot_system_memory(dataframe, output_dir, verbose)

        # Visualize CPU and disk usage
        self._plot_cpu_disk_usage(dataframe, output_dir, verbose)

        # Visualize process memory
        self._plot_process_memory(dataframe, output_dir, verbose)

        # Visualize network usage
        self._plot_network_usage(dataframe, output_dir, verbose)

    def _plot_system_memory(self, dataframe: pd.DataFrame, output_dir: Path, verbose: bool) -> None:
        """Plot system memory statistics."""
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot memory metrics on primary y-axis (GB)
        sns.lineplot(
            data=dataframe, x="elapsed_seconds", y="memory_total_gb", ax=ax1, label="Total Memory (GB)", color="red"
        )
        sns.lineplot(
            data=dataframe, x="elapsed_seconds", y="memory_used_gb", ax=ax1, label="Used Memory (GB)", color="blue"
        )
        sns.lineplot(
            data=dataframe,
            x="elapsed_seconds",
            y="memory_available_gb",
            ax=ax1,
            label="Available Memory (GB)",
            color="green",
        )
        ax1.set_ylabel("Memory (GB)")
        ax1.legend_.remove()

        # Plot memory utilization on secondary y-axis
        ax2 = ax1.twinx()
        sns.lineplot(
            data=dataframe,
            x="elapsed_seconds",
            y="memory_percent",
            ax=ax2,
            label="Memory Utilization (%)",
            color="purple",
        )
        ax2.set_ylabel("Memory Utilization (%)")
        ax2.legend_.remove()

        # Combine legends from both axes
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(
            lines1 + lines2,
            labels1 + labels2,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.3),
            ncol=2,
        )

        ax1.set_xlabel("Time Elapsed (s)")
        plt.title("System Memory Statistics")
        plt.tight_layout()

        path = output_dir / "system_memory.png"
        plt.savefig(path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        if verbose:
            logger.info(f"Saved system memory statistics plot to {path}")

    def _plot_cpu_disk_usage(self, dataframe: pd.DataFrame, output_dir: Path, verbose: bool) -> None:
        """Plot CPU and disk usage statistics."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot CPU and disk usage percentage
        sns.lineplot(data=dataframe, x="elapsed_seconds", y="cpu_percent", ax=ax, label="CPU Usage (%)", color="orange")
        sns.lineplot(
            data=dataframe, x="elapsed_seconds", y="disk_percent", ax=ax, label="Disk Usage (%)", color="brown"
        )

        ax.set_ylabel("Usage (%)")
        ax.set_xlabel("Time Elapsed (s)")
        ax.set_ylim(0, 100)  # Percentage values should be between 0 and 100
        plt.title("CPU and Disk Usage")
        plt.legend(loc="best")
        plt.tight_layout()

        path = output_dir / "cpu_disk_usage.png"
        plt.savefig(path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        if verbose:
            logger.info(f"Saved CPU and disk usage plot to {path}")

    def _plot_process_memory(self, dataframe: pd.DataFrame, output_dir: Path, verbose: bool) -> None:
        """Plot process memory statistics."""
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot process RSS memory
        sns.lineplot(data=dataframe, x="elapsed_seconds", y="proc_rss", ax=ax1, label="Process RSS (MB)", color="teal")
        ax1.set_ylabel("Memory (MB)")
        ax1.legend_.remove()

        # Plot process memory percentage
        ax2 = ax1.twinx()
        sns.lineplot(
            data=dataframe,
            x="elapsed_seconds",
            y="proc_percent",
            ax=ax2,
            label="Process Memory (%)",
            color="magenta",
        )
        ax2.set_ylabel("Memory Usage (%)")
        ax2.legend_.remove()

        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(
            lines1 + lines2,
            labels1 + labels2,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.3),
            ncol=2,
        )

        ax1.set_xlabel("Time Elapsed (s)")
        plt.title("Process Memory Usage")
        plt.tight_layout()

        path = output_dir / "process_memory.png"
        plt.savefig(path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        if verbose:
            logger.info(f"Saved process memory statistics plot to {path}")

    def _plot_network_usage(self, dataframe: pd.DataFrame, output_dir: Path, verbose: bool) -> None:
        """Plot network usage statistics."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot network sent and received
        sns.lineplot(data=dataframe, x="elapsed_seconds", y="net_sent_mb", ax=ax, label="Data Sent (MB)", color="blue")
        sns.lineplot(
            data=dataframe, x="elapsed_seconds", y="net_recv_mb", ax=ax, label="Data Received (MB)", color="green"
        )

        ax.set_ylabel("Data Transfer (MB)")
        ax.set_xlabel("Time Elapsed (s)")
        plt.title("Network Usage")
        plt.legend(loc="best")
        plt.tight_layout()

        path = output_dir / "network_usage.png"
        plt.savefig(path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        if verbose:
            logger.info(f"Saved network usage plot to {path}")
