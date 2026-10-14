import csv
import os
import resource
import time

from xsorted import xsorter


def read_system_io() -> dict:
    try:
        with open("/proc/self/io") as f:
            return {k: int(v) for k, v in (line.split(": ") for line in f.read().splitlines())}
    except Exception:
        return {}


def take_performance_snapshot() -> dict:
    return {
        "time": time.perf_counter(),
        "cpu":  resource.getrusage(resource.RUSAGE_SELF),
        "io":   read_system_io(),
    }


def calculate_metrics(input_size_bytes, elapsed_seconds, cpu_before, cpu_after, io_before, io_after):
    cpu_seconds    = (cpu_after.ru_utime - cpu_before.ru_utime) + \
                     (cpu_after.ru_stime - cpu_before.ru_stime)
    io_read_bytes  = io_after.get("read_bytes",  0) - io_before.get("read_bytes",  0)
    io_write_bytes = io_after.get("write_bytes", 0) - io_before.get("write_bytes", 0)
    return {
        "total_time_s":        round(elapsed_seconds, 3),
        "throughput_mb_s":     round((input_size_bytes / 1024**2) / max(elapsed_seconds, 0.001), 2),
        "cpu_utilisation_pct": round(cpu_seconds / max(elapsed_seconds, 0.001) * 100, 1),
        "io_read_mb":          round(io_read_bytes  / 1024**2, 1),
        "io_write_mb":         round(io_write_bytes / 1024**2, 1),
    }


def external_sort(input_path, output_path, partition_size):
    input_size_bytes = os.path.getsize(input_path)
    before = take_performance_snapshot()

    sort_by_score = xsorter(partition_size=partition_size)
    with open(input_path,  "r", newline="") as infile, \
         open(output_path, "w", newline="") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        for row in sort_by_score(reader, key=lambda x: int(x[1])):
            writer.writerow(row)

    after = take_performance_snapshot()
    return calculate_metrics(
        input_size_bytes,
        after["time"] - before["time"],
        before["cpu"], after["cpu"],
        before["io"],  after["io"],
    )
