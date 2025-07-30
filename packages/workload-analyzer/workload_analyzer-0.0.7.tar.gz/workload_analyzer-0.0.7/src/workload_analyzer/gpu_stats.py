import datetime
import os
from subprocess import PIPE, Popen

from pydantic import BaseModel, computed_field, field_validator


class GPUStat(BaseModel):
    """Class to represent GPU statistics."""

    # Identity
    timestamp: str | datetime.datetime
    index: int
    name: str
    uuid: str
    driver_version: str
    gpu_serial: str
    display_active: str
    display_mode: str
    compute_mode: str

    # Memory
    memory_total: int
    memory_used: int
    memory_free: int

    # Utilization
    utilization_gpu: float | None
    utilization_memory: float | None

    # Thermals & Power
    temperature: int
    power_draw: None | float
    power_limit: None | float
    fan_speed: None | float

    # Clock speed & performance state
    clocks_sm: None | float
    pstate: str

    @computed_field
    @property
    def memory_percentage(self) -> float:
        """Calculate the memory usage percentage.

        Computes the percentage of GPU memory currently in use based on the ratio
        of memory_used to memory_total.

        Returns:
            float: The percentage of GPU memory in use (0.0 to 100.0).
                Returns 0.0 if memory_total is 0 to avoid division by zero errors.

        Example:
            >>> gpu = GPUStat(memory_used=5000, memory_total=10000, ...)
            >>> gpu.memory_percentage
            50.0
        """
        if self.memory_total == 0:
            return 0.0
        return 100.0 * self.memory_used / self.memory_total

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_custom_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        """Convert the timestamp string to a datetime object.

        This validator ensures that the timestamp field is always a datetime object,
        converting from string if necessary using a specific format.

        Args:
            v (str | datetime.datetime): The timestamp value to parse. Can be either a
                string in the format 'YYYY/MM/DD HH:MM:SS.fff' or an existing datetime object.

        Returns:
            datetime.datetime: The parsed datetime object.

        Raises:
            ValueError: If the string timestamp is not in the expected format.
        """
        if isinstance(v, str):
            return datetime.datetime.strptime(v, "%Y/%m/%d %H:%M:%S.%f")
        return v


def safe_float(value: str | None) -> float | None:
    """Convert a value to float safely, returning None if conversion fails.

    This utility function attempts to convert a string to a float value,
    handling potential errors by returning None instead of raising exceptions.

    Args:
        value (str | None): The string value to convert to float.
            Can be None, in which case None is returned.

    Returns:
        float | None: The float representation of the input string if conversion
            is successful, or None if conversion fails or input is None.

    Examples:
        >>> safe_float("42.5")
        42.5
        >>> safe_float("N/A")
        None
        >>> safe_float(None)
        None
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def get_gpu_stats(query_params: list[str] | None = None) -> list[GPUStat]:
    """Get detailed statistics for all available NVIDIA GPUs on the system.

    This function uses the nvidia-smi tool to query various GPU statistics
    and returns them as a list of structured GPUStat objects. It captures a
    comprehensive set of metrics including device identity, memory usage,
    utilization rates, thermal information, power usage, and performance state.

    Args:
        query_params (list[str] | None, optional): List of specific parameters to query
            from nvidia-smi. If None, a comprehensive default set of parameters will be used.
            Each parameter should match the nvidia-smi query naming format. Defaults to None.

    Returns:
        list[GPUStat]: A list of GPUStat objects, each representing statistics
            for one GPU device. Returns an empty list if nvidia-smi command fails
            or no GPUs are available.

    Example:
        >>> gpu_stats = get_gpu_stats()
        >>> for gpu in gpu_stats:
        ...     print(f"GPU {gpu.index}: {gpu.name})

    Note:
        This function requires the nvidia-smi tool to be installed and accessible
        in the system path. It will fail silently and return an empty list if
        nvidia-smi is not available or fails to execute.

    Inspired by:
        https://github.com/anderskm/gputil
    """
    if query_params is None:
        query_params = [
            "timestamp",
            "index",
            "name",
            "uuid",
            "driver_version",
            "gpu_serial",
            "display_active",
            "display_mode",
            "compute_mode",
            "memory.total",
            "memory.used",
            "memory.free",
            "utilization.gpu",
            "utilization.memory",
            "temperature.gpu",
            "power.draw",
            "power.limit",
            "fan.speed",
            "clocks.sm",
            "pstate",
        ]
    nvidia_smi = "nvidia-smi"
    # Get ID, processing and memory utilization for all GPUs
    try:
        p = Popen([nvidia_smi, "--query-gpu=" + ",".join(query_params), "--format=csv,noheader,nounits"], stdout=PIPE)
        stdout, stderror = p.communicate()
    except:  # noqa: E722
        return []
    output = stdout.decode("UTF-8")
    lines = output.split(os.linesep)
    num_devices = len(lines) - 1
    gpus = []
    for g in range(num_devices):
        line = lines[g].split(", ")
        gpus.append(
            GPUStat(
                timestamp=line[0],
                index=int(line[1]),
                name=line[2],
                uuid=line[3],
                driver_version=line[4],
                gpu_serial=line[5],
                display_active=line[6],
                display_mode=line[7],
                compute_mode=line[8],
                memory_total=int(line[9]),
                memory_used=int(line[10]),
                memory_free=int(line[11]),
                utilization_gpu=safe_float(line[12]),
                utilization_memory=safe_float(line[13]),
                temperature=int(line[14]),
                power_draw=safe_float(line[15]),
                power_limit=safe_float(line[16]),
                fan_speed=safe_float(line[17]),
                clocks_sm=safe_float(line[18]),
                pstate=line[19],
            )
        )
    return gpus


if __name__ == "__main__":
    gpu_stats = get_gpu_stats()
