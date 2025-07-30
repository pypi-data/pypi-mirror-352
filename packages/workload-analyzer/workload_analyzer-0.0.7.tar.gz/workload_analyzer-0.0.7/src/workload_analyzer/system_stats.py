import datetime

import psutil
from pydantic import BaseModel, computed_field, field_validator


class MemoryStat(BaseModel):
    """Memory statistics in bytes and percent."""

    total: float
    used: float
    available: float
    percent: float

    @computed_field
    def total_gb(self) -> float:
        """Return total memory in GB."""
        return self.total / (1024**3)

    @computed_field
    def used_gb(self) -> float:
        """Return used memory in GB."""
        return self.used / (1024**3)

    @computed_field
    def available_gb(self) -> float:
        """Return available memory in GB."""
        return self.available / (1024**3)


class NetworkStat(BaseModel):
    """Network I/O stats since boot."""

    sent: int
    recv: int


class ProcessStat(BaseModel):
    """Stats for the current process."""

    rss: float | None = None  # Resident Set Size in MB
    percent: float | None = None
    threads: int | None = None


class SystemStat(BaseModel):
    """Full system statistics."""

    timestamp: str | datetime.datetime
    memory: MemoryStat
    cpu_percent: float
    disk_percent: float
    proc_mem: ProcessStat
    network: NetworkStat

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_custom_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        """Parse timestamp to datetime object."""
        if isinstance(v, str):
            return datetime.datetime.strptime(v, "%Y/%m/%d %H:%M:%S.%f")
        return v


def get_system_stats(proc: psutil.Process | None = None, net_init: dict[str, int] | None = None) -> SystemStat:
    """Collect full system statistics using psutil."""
    now = datetime.datetime.now()
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent()
    disk = psutil.disk_usage("/").percent
    net = psutil.net_io_counters()

    # Use self.proc if passed
    proc_stats = ProcessStat()
    if proc is None:
        try:
            proc = psutil.Process()
        except psutil.NoSuchProcess:
            proc = None

    if proc:
        try:
            proc_stats.rss = proc.memory_info().rss / 1048576.0
            proc_stats.percent = proc.memory_percent()
            proc_stats.threads = proc.num_threads()
        except psutil.NoSuchProcess:
            pass

    # Optional: subtract network init values
    net_sent = net.bytes_sent
    net_recv = net.bytes_recv
    if net_init:
        net_sent -= net_init.get("sent", 0)
        net_recv -= net_init.get("recv", 0)

    return SystemStat(
        timestamp=now,
        memory=MemoryStat(total=mem.total, used=mem.used, available=mem.available, percent=mem.percent),
        cpu_percent=cpu,
        disk_percent=disk,
        proc_mem=proc_stats,
        network=NetworkStat(sent=net_sent, recv=net_recv),
    )
