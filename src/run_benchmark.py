"""
Sort the input file with a memory buffer scaled to the pod's RAM, and record the metrics.
"""

import argparse
import json
import os
from datetime import datetime, timezone

from external_sort import external_sort
from metrics import calculate_metrics, take_snapshot

BUFFER_SHARE_OF_RAM = 0.4  # leaves room for dirty page cache from writes (0.6 was OOMKilled at 1 GB)
SORT_THREADS = 2           # matches the pod's CPU limit
RESULTS_PATH = "/data/results.json"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ram-gb", type=float, required=True)
    parser.add_argument("--data-path", default="/data/input.csv")
    return parser.parse_args()


def run_sort(input_path, output_path, buffer_mb):
    start = take_snapshot()
    external_sort(input_path, output_path, buffer_mb, SORT_THREADS)
    end = take_snapshot()
    return calculate_metrics(start, end, os.path.getsize(input_path))


def load_results():
    if not os.path.exists(RESULTS_PATH):
        return []
    with open(RESULTS_PATH) as results_file:
        return json.load(results_file)


def save_result(result):
    """Replace any earlier result for the same RAM size."""
    results = [existing for existing in load_results() if existing["ram_gb"] != result["ram_gb"]]
    results.append(result)
    results.sort(key=lambda entry: entry["ram_gb"])
    with open(RESULTS_PATH, "w") as results_file:
        json.dump(results, results_file, indent=2)


def main():
    args = parse_args()
    buffer_mb = int(args.ram_gb * 1024 * BUFFER_SHARE_OF_RAM)
    output_path = f"/data/output_{args.ram_gb:g}gb.csv"

    metrics = run_sort(args.data_path, output_path, buffer_mb)

    save_result({
        "ram_gb": args.ram_gb,
        "buffer_mb": buffer_mb,
        "input_size_mb": round(os.path.getsize(args.data_path) / 1024 ** 2, 1),
        **metrics,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # The sorted output is not needed after measuring, and frees space for the next run
    os.remove(output_path)


if __name__ == "__main__":
    main()
