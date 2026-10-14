**The Benchmark uses Kubernetes pods of different sizes**

* Docker was allocated 16G of RAM to ensure container of 8G could easly spin
* Data to be sorted is of size ~5G, generated via python script on persistent volume (28000000 records of 16 bytes each) via Kubernetes Job

**Kubernetes Jobs**
* 1G, 2G, 4G and 8G spin sequentially on the generated data
* the resulting metrics are added to a common json file
* This file is served via http on http://localhost:9090/ at the end of process

**Scripts**
* > ****run_all****
  script executes the entire project end to end
* > ****run_all --sizes 1,2,4****
  can be used o limit run for specific sizes

**Docker Registry**
* Port 5000 of the system is assumed to be free
* You may have to stop Airplay to fee up this prit for docker registry
* Docker file in the project is used for building project (Sort + benchmark results)
* Result server servers the josn produced by sort jobs

__Note:__
We can monitor job status with

```
kubectl get pods -n sort-benchmark --watch
```

__Cleanup:__
 For cleaning up the system post comletion we can run following command

```
Kubectl delete namespace sort-benchmark
```


**File chunk size during merge step**

| RAM  | Records per chunk | Approx chunk size |
|------|-------------------|-------------------|
| 1 GB | 600,000           | ~11 MB            |
| 2 GB | 1,200,000         | ~22 MB            |
| 4 GB | 2,400,000         | ~44 MB            |
| 8 GB | 4,800,000         | ~88 MB            |
