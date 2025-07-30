import itertools

from workload_analyzer.gpu_stats import GPUStat
from workload_analyzer.system_stats import SystemStat


def recommend(gpu_stats_dict: dict[str, list[GPUStat]], system_stats: list[SystemStat]) -> None:
    """Analyzes GPU and system statistics and prints recommendations based on the analysis."""
    print("💡 Recommendations based on workload analysis:")
    print("=" * 50)

    # GPU recommendations
    recommend_from_gpu_memory_usage(gpu_stats_dict)
    recommend_from_gpu_compute_utilization(gpu_stats_dict)
    recommend_from_gpu_memory_bandwidth_utilization(gpu_stats_dict)

    # # System recommendations
    recommend_from_disk_usage(system_stats)
    recommend_from_cpu_usage(system_stats)
    recommend_from_network_usage(system_stats)

    print("=" * 50)


def recommend_from_gpu_memory_usage(
    gpu_stats_dict: dict[str, list[GPUStat]],
    gpu_memory_breakpoints: list[int] | None = None,
) -> None:
    """
    Analyzes GPU memory utilization from a dict of GPUStat lists and prints recommendations per GPU.

    Args:
        gpu_stats_dict (dict[str, list[GPUStat]]): Mapping of GPU names (e.g., "gpu0") to lists of GPUStat objects.
        gpu_memory_breakpoints (list[int], optional): List of memory breakpoints in GB for recommendations.
    """
    if gpu_memory_breakpoints is None:
        gpu_memory_breakpoints = [8, 12, 16, 24, 48, 80, 140]
    if not gpu_stats_dict:
        print("No GPU statistics provided.")
        return

    for gpu_name, stats in gpu_stats_dict.items():
        if not stats:
            print(f"\n ⚠️ No stats recorded for {gpu_name}.")
            continue

        avg_util = sum(stat.memory_percentage for stat in stats) / len(stats) if len(stats) else 0.0
        max_used_mb = max(stat.memory_used for stat in stats)
        memory_total_mb = stats[0].memory_total
        max_used_gb = max_used_mb / 1024
        memory_total_gb = memory_total_mb / 1024

        print(f"\n🧠 {gpu_name.upper()} - Average Memory Utilization: {avg_util:.2f}%")
        print(f"📈 Max Memory Used: {max_used_gb:.2f} GB | 💾 Total Memory Available: {memory_total_gb:.2f} GB")

        if avg_util < 10:
            print("🔍 Very low GPU memory usage.")
            print("👉 Consider increasing the batch size or using a larger model.")
        elif avg_util < 40:
            print("🟡 Low GPU memory usage.")
            print("👉 There's room to increase batch size for better GPU throughput.")
        elif avg_util < 80:
            print("🟢 Moderate GPU memory usage.")
            print("✅ Looks well-balanced. You might fine-tune batch size or model complexity.")
        elif avg_util < 95:
            print("🟠 High GPU memory usage.")
            print("✅ Good utilization. Monitor for potential memory spikes.")
        else:
            print("🔴 Critical GPU memory usage.")
            print("""
                ⚠️ Risk of out-of-memory (OOM) errors.
                Consider memory-efficient strategies like gradient checkpointing or reducing batch size.
                """)

        # Hardware recommendation
        suitable_gpu = next((size for size in gpu_memory_breakpoints if max_used_gb <= size), None)
        if suitable_gpu:
            print(f"💡 Suggestion: This workload could run on a {suitable_gpu} GB GPU.")
        else:
            print("💡 Suggestion: This workload exceeds available GPU breakpoints. Use highest-memory GPU.")


def recommend_from_gpu_compute_utilization(gpu_stats_dict: dict[str, list[GPUStat]]) -> None:
    """
    Analyzes GPU compute utilization and prints recommendations per GPU.

    Args:
        gpu_stats_dict (dict[str, list[GPUStat]]): Mapping of GPU names to lists of GPUStat objects.
    """
    for gpu_name, stats in gpu_stats_dict.items():
        if not stats:
            print(f"\n ⚠️ No stats recorded for {gpu_name}.")
            continue

        avg_util = sum(stat.utilization_gpu for stat in stats) / len(stats) if len(stats) else 0.0
        print(f"\n🧠 {gpu_name.upper()} - Average Compute Utilization: {avg_util:.2f}%")

        if avg_util < 10:
            print("🔍 Very low GPU compute usage.")
            print("👉 Model might be too small, or data loading could be slowing things down.")
        elif avg_util < 30:
            print("🟡 Low GPU compute usage.")
            print("👉 Consider profiling data pipeline and increasing batch size.")
        elif avg_util < 70:
            print("🟢 Moderate GPU compute usage.")
            print("✅ Reasonable, but review for opportunities to boost throughput.")
        else:
            print("🟢 High GPU compute usage.")
            print("✅ Excellent utilization. GPU is being kept busy effectively.")


def recommend_from_gpu_memory_bandwidth_utilization(gpu_stats_dict: dict[str, list[GPUStat]]) -> None:
    """
    Analyzes GPU memory bandwidth utilization and prints recommendations per GPU.

    Args:
        gpu_stats_dict (dict[str, list[GPUStat]]): Mapping of GPU names to lists of GPUStat objects.
    """
    for gpu_name, stats in gpu_stats_dict.items():
        if not stats:
            print(f"\n ⚠️ No stats recorded for {gpu_name}.")
            continue

        avg_util = sum(stat.utilization_memory for stat in stats) / len(stats) if len(stats) else 0.0
        print(f"\n🧠 {gpu_name.upper()} - Average Memory Bandwidth Utilization: {avg_util:.2f}%")

        if avg_util < 10:
            print("🔍 Very low memory bandwidth usage.")
            print("👉 Likely compute-bound workload. No immediate issue unless GPU is underutilized.")
        elif avg_util < 40:
            print("🟡 Low to moderate memory bandwidth usage.")
            print("✅ Balanced usage. Check for memory bottlenecks only if training is slow.")
        else:
            print("🟠 High memory bandwidth usage.")
            print("⚠️ May be memory-bound. Consider reducing input size or optimizing memory access.")


def recommend_from_disk_usage(system_stats: list[SystemStat]) -> None:
    """
    Analyzes disk usage and prints recommendations.

    Args:
        system_stats (list[SystemStat]): List of SystemStat objects containing disk statistics.
    """
    if not system_stats:
        print("No system statistics provided.")
        return

    avg_disk = sum(stat.disk_percent for stat in system_stats) / len(system_stats) if len(system_stats) else 0.0
    print(f"\n💾 Average Disk Usage: {avg_disk:.2f}%")

    if avg_disk < 50:
        print("🟢 Disk usage is low. No storage-related issues expected.")
    elif avg_disk < 80:
        print("🟡 Disk usage is moderate.")
        print("👉 Monitor disk space and I/O performance, especially if logging/checkpointing frequently.")
    else:
        print("🔴 High disk usage detected.")
        print("⚠️ Consider cleaning temporary files, reducing logging frequency, or using faster/more spacious storage.")


def recommend_from_cpu_usage(system_stats: list[SystemStat]) -> None:
    """
    Analyzes CPU usage and prints recommendations.

    Args:
        system_stats (list[SystemStat]): List of SystemStat objects containing CPU statistics.
    """
    if not system_stats:
        print("No system statistics provided.")
        return

    avg_cpu = sum(stat.cpu_percent for stat in system_stats) / len(system_stats) if len(system_stats) else 0.0
    print(f"\n🧠 Average CPU Utilization: {avg_cpu:.2f}%")

    if avg_cpu < 30:
        print("🟡 CPU is underutilized.")
        print("👉 Possible bottleneck in the data pipeline. Consider using more `num_workers` in data loaders.")
    elif avg_cpu < 80:
        print("🟢 CPU usage is balanced.")
        print("✅ Looks optimal. No major bottlenecks expected from CPU.")
    else:
        print("🔴 CPU is heavily utilized.")
        print("⚠️ CPU may be a bottleneck. Profile data preprocessing or I/O threads.")


def recommend_from_network_usage(system_stats: list[SystemStat]) -> None:
    """
    Analyzes network usage and prints recommendations.

    Args:
        system_stats (list[SystemStat]): List of SystemStat objects containing network statistics.

    """
    if len(system_stats) < 2:
        return

    sent_deltas = [b.network.sent - a.network.sent for a, b in itertools.pairwise(system_stats)]
    recv_deltas = [b.network.recv - a.network.recv for a, b in itertools.pairwise(system_stats)]

    avg_sent = sum(sent_deltas) / len(sent_deltas) if sent_deltas else 0.0
    avg_recv = sum(recv_deltas) / len(recv_deltas) if recv_deltas else 0.0

    print(f"\n🌐 Average Network Sent Rate: {avg_sent:.2f} bytes/sample")
    print(f"🌐 Average Network Recv Rate: {avg_recv:.2f} bytes/sample")

    if avg_recv < 1024:
        print("🟢 Low network usage. Likely local data.")
    elif avg_recv < 5 * 1024 * 1024:
        print("🟡 Moderate network usage.")
        print("👉 If training on streamed/remote datasets, check for latency or throttling.")
    else:
        print("🔴 High network input detected.")
        print("⚠️ Model may be bottlenecked by remote data loading. Consider local caching or dataset sharding.")
