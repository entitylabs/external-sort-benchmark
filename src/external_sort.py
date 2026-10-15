"""
External merge sort of a (userid, score) CSV file by score, using GNU sort.

GNU sort fills a memory buffer, sorts it and writes it to a temporary file (a sorted run),
repeats until the whole input is read, then merges the runs, at most 16 at a time.
"""

import os
import subprocess
import tempfile


def external_sort(input_path, output_path, buffer_mb, threads):
    subprocess.run(
        [
            "sort",
            "--field-separator=,",
            "--key=2,2n",
            f"--buffer-size={buffer_mb}M",
            f"--parallel={threads}",
            f"--temporary-directory={tempfile.gettempdir()}",
            f"--output={output_path}",
            input_path,
        ],
        # Compare plain bytes instead of locale rules: faster and the same on every machine
        env={**os.environ, "LC_ALL": "C"},
        check=True,
    )
