import argparse
import json
import os
from datetime import datetime, timezone

from external_sort import external_sort

RECORDS_PER_GB = 600_000
RESULTS_FILE   = "/data/results.json"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ram-gb",    type=float, required=True)
    parser.add_argument("--data-path", default="/data/input.csv")
    return parser.parse_args()


def output_path_for(ram_gb):
    return f"/data/output_{ram_gb}gb.csv"


def attach_run_metadata(metrics, ram_gb, size_mb):
    metrics["ram_gb"]            = ram_gb
    metrics["records_per_chunk"] = int(ram_gb * RECORDS_PER_GB)
    metrics["input_size_mb"]     = round(size_mb, 1)
    metrics["cpu_pct"]           = metrics.pop("cpu_utilisation_pct", 0)
    metrics["ts"]                = datetime.now(timezone.utc).isoformat()
    return metrics


def load_results():
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE) as f:
        return json.load(f)


def save_result(result):
    existing = [r for r in load_results() if r.get("ram_gb") != result["ram_gb"]]
    existing.append(result)
    existing.sort(key=lambda r: r["ram_gb"])
    with open(RESULTS_FILE, "w") as f:
        json.dump(existing, f, indent=2)


def delete_output_file(path):
    try:
        os.unlink(path)
    except OSError:
        pass


def main():
    args           = parse_args()
    size_mb        = os.path.getsize(args.data_path) / 1024**2
    output         = output_path_for(args.ram_gb)
    partition_size = int(args.ram_gb * RECORDS_PER_GB)

    metrics = external_sort(args.data_path, output, partition_size)
    metrics = attach_run_metadata(metrics, args.ram_gb, size_mb)
    save_result(metrics)
    delete_output_file(output)


if __name__ == "__main__":
    main()
