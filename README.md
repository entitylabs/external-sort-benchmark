# External Sort Benchmark

Runs an external merge sort on ~5 GB of data inside Kubernetes pods limited to 1, 2, 4 and 8 GB of RAM, and measures how pod size affects performance.

## Reference
https://www.gnu.org/software/coreutils/manual/html_node/sort-invocation.html
The sort is done by GNU `sort`, a C implementation of external merge sort. An earlier pure-Python version (based on https://github.com/melvilgit/external-Merge-Sort) was replaced because it was CPU-bound (see Results). (Python 3.12 does not support external merge sort out of box)

## Requirements

* Docker Desktop with Kubernetes enabled
* Docker given **16 GB of RAM**, so the 8 GB pod can be scheduled
* ~20 GB free disk (input, output, and the same amount again in temporary sorted runs)

## How it works

1. **Generate data:** a Kubernetes Job writes `/data/input.csv` to a persistent volume: 280,000,000 `(userid, score)` rows, ~20 bytes each, ~5 GB. It is skipped if the file already exists.
2. **Sort:** one Job per RAM size (1, 2, 4, 8 GB) runs one after another. Each one sorts the file by `score` with GNU `sort` ([`src/external_sort.py`](src/external_sort.py)), using 2 threads to match the pod's CPU limit:
   * **Pass 0:** fill the memory buffer, sort it, and write it to a temporary file (a sorted run); repeat until the input is read
   * **Merge passes:** merge the runs, at most 16 at a time, into `/data/output_<size>gb.csv`. More than 16 runs means extra merge passes
3. **Measure:** each Job adds its metrics to `/data/results.json`.
4. **Serve:** results are shown at http://localhost:9090 when all Jobs finish.

***Kubectl namespace is deleted as the first step to ensure all old data is erased***

The sort buffer (`--buffer-size`) is 40% of the pod's RAM. The rest is headroom for written data waiting in the page cache, which counts against the pod's limit (a 60% buffer was OOMKilled at 1 GB):

| RAM  | Sort buffer |
|------|-------------|
| 1 GB | 409 MB      |
| 2 GB | 819 MB      |
| 4 GB | 1,638 MB    |
| 8 GB | 3,276 MB    |

## Metrics

| Field                  | Meaning                                                        |
|------------------------|----------------------------------------------------------------|
| `total_time_s`         | Wall-clock time of the whole sort                              |
| `throughput_mb_s`      | Input size / total time                                        |
| `cpu_pct`              | CPU time / wall time (up to 200% with 2 threads; low means waiting on I/O) |
| `io_read_mb`           | Bytes read from disk (page-cache hits not counted)             |
| `io_write_mb`          | Bytes written to disk                                          |
| `peak_memory_mb`       | Highest memory used by the sort process                        |
| `buffer_mb`            | Sort buffer used for this run                                  |


## Running

```
bash scripts/run_all.sh                # all sizes
bash scripts/run_all.sh --sizes 1,2,4  # only some sizes
```

## Monitoring

```
kubectl get pods -n sort-benchmark --watch
kubectl top pod -n sort-benchmark       # needs 01_setup_dashboard.sh
```

## Cleanup

```
kubectl delete namespace sort-benchmark
docker rm -f local-registry
```

## Results

280,000,000 records (~5GB). Docker Desktop on macOS, 16 GB RAM, 8 CPUs.

| RAM  | Buffer (MB) | Total (s) | Throughput (MB/s) | CPU % | Disk read (MB) | Disk write (MB) | Peak memory (MB) |
|------|-------------|-----------|-------------------|-------|----------------|-----------------|------------------|
| 1 GB | 409         | 203.6     | 26.87             | 125.9 | 14,360         | 15,695          | 411              |
| 2 GB | 819         | 187.6     | 29.17             | 136.6 | 12,764         | 14,089          | 821              |
| 4 GB | 1,638       | 160.7     | 34.05             | 154.6 | 9,137          | 10,944          | 1,639            |
| 8 GB | 3,276       | 199.6     | 27.41             | 152.3 | 8,214          | 10,944          | 3,278            |

The 8 GB run was repeated and took 205.2 s (same I/O), confirming it is slower than 4 GB

**Observations**

* **1 GB → 4 GB gets faster (203.6 s → 160.7 s).** A bigger buffer produces fewer sorted runs, so fewer merge passes are needed and less data is written (15,695 MB → 10,944 MB).
* **4 GB and 8 GB both merge in one pass.** Both write exactly 10,944 MB, about 2× the input: once for the sorted runs, once for the output. The extra RAM at 8 GB saves no disk I/O.
* **8 GB is slower than 4 GB.** Larger buffers mean longer CPU-only sorting phases, with less overlap between sorting and background disk writes. More RAM stops helping once the data merges in one pass.
* **Peak memory matches the sort buffer**, so memory use is controlled by `--buffer-size`, not the pod limit to prevent OOM.
