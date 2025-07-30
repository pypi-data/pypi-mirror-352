# Workload Analyzer 📊

A simple tool for monitoring and analyzing GPU and system resource usage during AI/ML workloads.

## 🌟 Features

- 📈 Real-time monitoring of GPU utilization, memory usage, and system resources
- 🔍 Detailed visualization of resource usage over time
- 💡 Intelligent recommendations for workload optimization
- 🚀 Easy-to-use CLI interface
- 📝 Comprehensive statistics export

## 🔧 Installation

### Using pip

```bash
pip install workload-analyzer
```

### Development setup

```bash
# Clone the repository
git clone https://github.com/yourusername/workload-analyzer
cd workload-analyzer

# Install using uv with development dependencies
uv sync --dev
```

## 📋 Requirements

- Python 3.12+
- NVIDIA GPU with nvidia-smi (for GPU monitoring)

## 🚀 Quick Start

```bash
# Run a command with default settings
workload-analyzer "python train_model.py"

# Specify timeout and polling interval
workload-analyzer "python train_model.py" --timeout 300 --interval 5
```

## 📊 Output

The tool generates:

1. **Statistics file**: JSON format data with all recorded measurements
2. **Visualizations**:
   - GPU memory usage over time
   - System memory consumption
   - CPU and disk utilization
   - Network usage
   - Process memory statistics

3. **Optimization recommendations** based on resource utilization patterns:
   - GPU memory sizing recommendations
   - Compute utilization insights
   - Memory bandwidth analysis
   - System resource optimization tips

All outputs are saved to `workload_results/` by default (configurable with `--output-dir`).

## 🛠️ Configuration options

```txt
--timeout           Time to monitor in seconds (default: 120)
--interval          Polling interval in seconds (default: 3)
--recommendations   Enable workload optimization recommendations (default: True)
--output-dir        Directory to save outputs (default: workload_results/)
--verbose           Enable verbose logging (default: True)
--version           Print version information
```

## ❕ License

Package is licensed under Apache 2.0 license. Free to use as you like, but a cite of the package is welcome:

```bibtex
@misc{skafte_workload_analyzer,
    author       = {Nicki Skafte Detlefsen},
    title        = {Workload-Analyzer},
    howpublished = {\url{https://github.com/SkafteNicki/workload_analyzer}},
    year         = {2025}
}
```
