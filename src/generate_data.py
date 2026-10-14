"""
Generate a CSV dataset of (userid, score) tuples — matching Lecture 2 format.

Each record: userid = 'userN', score = random int in [1, 100000]
Default: 20,000,000 records ≈ 300 MB
"""

import argparse
import csv
import os
import random

SCORE_MIN = 1
SCORE_MAX = 100_000


def write_csv(output_path, n_records):
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        for i in range(n_records):
            writer.writerow([f"user{i}", random.randint(SCORE_MIN, SCORE_MAX)])


def generate(output_path, n_records):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    write_csv(output_path, n_records)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate (userid, score) CSV dataset")
    parser.add_argument("--output",  default="/data/input.csv",    help="Output CSV path")
    parser.add_argument("--records", type=int, default=280_000_000, help="Number of records")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not os.path.exists(args.output):
        generate(args.output, args.records)
