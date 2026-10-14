"""
Aggregate per-run JSON results into a comparison table and CSV.

Usage:
    python scripts/collect_results.py
"""

import csv
import glob
import json
import os
import sys

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

# Matches the lecture's focus: time and I/O are the two key metrics
COLUMNS = [
    ("ram_gb",            "RAM Limit (GB)"),
    ("total_time_s",      "Total Time (s)"),
    ("throughput_mb_s",   "Throughput (MB/s)"),
    ("cpu_pct",           "CPU Utilisation (%)"),
    ("io_read_mb",        "I/O Read (MB)"),
    ("io_write_mb",       "I/O Write (MB)"),
    ("input_size_mb",     "Input Size (MB)"),
    ("records_per_chunk", "Records per Chunk"),
]


def load_results():
    paths = sorted(glob.glob(os.path.join(RESULTS_DIR, "results_*gb.json")))
    if not paths:
        print(f"No result files found in {RESULTS_DIR}/")
        print("Run 04_run_benchmarks.sh first.")
        sys.exit(1)

    rows = []
    for path in paths:
        with open(path) as f:
            rows.append(json.load(f))
    rows.sort(key=lambda r: r.get("ram_gb", 0))
    return rows


def fmt(val) -> str:
    if val is None:
        return "N/A"
    if isinstance(val, float):
        return f"{val:.2f}"
    return str(val)


def print_table(rows):
    col_w = 30
    val_w = 14
    total_w = col_w + val_w * len(rows)

    print()
    print("=" * total_w)
    print("  BENCHMARK COMPARISON  (aligned with Lecture 2 metrics)")
    print("=" * total_w)
    header = f"{'Metric':<{col_w}}" + "".join(
        f"{'  ' + str(r.get('ram_gb', '?')) + ' GB':<{val_w}}" for r in rows
    )
    print(header)
    print("─" * total_w)

    for key, label in COLUMNS:
        line = f"{label:<{col_w}}"
        for r in rows:
            line += f"{fmt(r.get(key)):<{val_w}}"
        print(line)

    print("=" * total_w)
    print()


def write_csv(rows, out_path):
    fieldnames = [key for key, _ in COLUMNS]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV written → {out_path}")


def main() -> None:
    rows = load_results()
    print_table(rows)
    csv_path = os.path.join(RESULTS_DIR, "comparison_table.csv")
    write_csv(rows, csv_path)
    top_path = os.path.join(RESULTS_DIR, "metrics_top.csv")
    if os.path.exists(top_path):
        print(f"kubectl-top time series → {top_path}")


if __name__ == "__main__":
    main()
