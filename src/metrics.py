"""
Performance measurements for the sort: time, throughput, CPU, disk I/O and memory.

The sort runs as a child process, so CPU and memory come from RUSAGE_CHILDREN.
"""

import resource
import time

BYTES_PER_MB = 1024 ** 2


def read_process_io():
    """Bytes read from / written to disk, including finished child processes (Linux only)."""
    try:
        with open("/proc/self/io") as io_file:
            return {name: int(value) for name, value in (line.split(": ") for line in io_file)}
    except OSError:
        return {}


def take_snapshot():
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    io_counters = read_process_io()
    return {
        "time": time.perf_counter(),
        "cpu_seconds": usage.ru_utime + usage.ru_stime,
        "read_bytes": io_counters.get("read_bytes", 0),
        "write_bytes": io_counters.get("write_bytes", 0),
    }


def peak_memory_mb():
    # Largest child's peak memory; ru_maxrss is in kilobytes on Linux
    return resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024


def calculate_metrics(start, end, input_size_bytes):
    total_seconds = end["time"] - start["time"]
    cpu_seconds = end["cpu_seconds"] - start["cpu_seconds"]

    return {
        "total_time_s":    round(total_seconds, 3),
        "throughput_mb_s": round(input_size_bytes / BYTES_PER_MB / total_seconds, 2),
        "cpu_pct":         round(cpu_seconds / total_seconds * 100, 1),
        "io_read_mb":      round((end["read_bytes"] - start["read_bytes"]) / BYTES_PER_MB, 1),
        "io_write_mb":     round((end["write_bytes"] - start["write_bytes"]) / BYTES_PER_MB, 1),
        "peak_memory_mb":  round(peak_memory_mb(), 1),
    }
