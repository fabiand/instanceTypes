
# Introduction

> **Note**
> Learn how to build in the [BUILD.md](BUILD.md) file.

This is the documentation for the instance types defined in [instanceTypes.yaml](instanceTypes.yaml).

> **Note**
> The follow instance types are provided by OpenShift by default.
> They can be easily build and installed from source with:
>
> ```bash session
> $ kubectl kustomize > instanceTypes.yaml
> $ kubectl apply -f instanceTypes.yaml
> ```

# Overview

## Structure

The available instance types are structured into two themes:

1. Workload agnostic - or general purpose
2. Workload specific

Instance Types of the first theme are a good starting point to run your workload.
Once you know more about the requirements of your workload, you can start choosing a
specific instance type of the second class.

The following diagram summarises the available instance types and their use-cases:

```mermaid
graph TD

classDef grp fill:white,stroke:lightgray,color:gray
classDef series fill:lightyellow,stroke:lightgray
classDef instancetype fill:

wrkld(Workload specific)
nwrkld(Workload agnostic)
class wrkld grp

wrkld:::grp --> Computeintensive:::series
Computeintensive([Compute intensive]):::series --> cx1:::instancetype

wrkld:::grp --> GPU:::series
GPU([GPU]):::series --> gn1:::instancetype

wrkld:::grp --> Memoryintensive:::series
Memoryintensive([Memory intensive]):::series --> m1:::instancetype

nwrkld:::grp --> Generalpurpose:::series
Generalpurpose([General purpose]):::series --> n1:::instancetype


```

### Schema

<details><summary>Click in order to view the instanceType names schema</summary>

```ebnf
instanceTypeName = seriesName , "." , size;

seriesName = ( class | vendorClass ) , version;

class = "n" | "cx" | "m";
vendorClass = "g" , vendorHint;
vendorHint = "n" | "i" | "a";
version = "1";

size = "small" | "medium" | "large" | [( "2" | "4" | "8" )] , "xlarge";
```
</details>


# Series

.                           |  CX   |  GN   |  M    |  N
----------------------------|-------|-------|-------|------
*Has GPUs*                  |       |  :x:  |       |
*Hugepages*                 |       |       |  :x:  |
*Dedicated CPUs*            |  :x:  |       |       |
*Isolated emulator threads* |  :x:  |       |       |
*vNUMA*                     |  :x:  |       |       |
*vCPU-To-Memory Ratio*      |  1:2  |  1:4  |  1:4  |  1:8

## CX Series

The CX Series provides exclusive compute resources for compute
intensive applications.

*CX* is the abbreviation of "Compute Exclusive".

The exclusive resources are given to the compute threads of the
VM. In order to ensure this, some additional cores (depending
on the number of disks and NICs) will be requestedto offload
the IO threading from cores dedicated to the workload.
In addition, in this series, the NUMA topology of the used
cores is provided to the VM.

### CX Characteristics

Specific characteristics of this series are:
- *Dedicated CPUs* - Dedicated physical cores are exclusively assigned
  to every vCPU in order to provide high compute guarantees to the
  workload
- *Isolated emulator threads* - Hypervisor emulator threads are isolated
  from the vCPUs in order to reduce emaulation related impact on the
  workload
- *vCPU-To-Memory Ratio (1:2)* - A vCPU-to-Memory ratio of 1:2
- *vNUMA* - Physical NUMA topology is reflected in the guest in order to
  optimize guest sided cache utilization

### CX Instance Types

The following instance types are available in this series:

Name        | Cores | Memory
------------|-------|-------
cx1.medium  | 1     | 2Gi
cx1.large   | 2     | 4Gi
cx1.xlarge  | 4     | 8Gi
cx1.2xlarge | 8     | 16Gi
cx1.4xlarge | 16    | 32Gi
cx1.8xlarge | 32    | 64Gi


## GN Series

The GN Series provides instances types intended for VMs with
NVIDIA GPU resources attached.

*GN* is the abbreviation of "GPU NVIDIA".

This series is intended to be used with VMs consuming GPUs
provided by the [NVIDIA GPU Operator](https://github.com/NVIDIA/gpu-operator)
which is made available on OpenShift via OperatorHub.

### GN Characteristics

Specific characteristics of this series are:
- *Has GPUs* - Has GPUs predefined
- *vCPU-To-Memory Ratio (1:4)* - A vCPU-to-Memory ratio of 1:4, for less
  noise per node

### GN Instance Types

The following instance types are available in this series:

Name        | Cores | Memory
------------|-------|-------
gn1.xlarge  | 4     | 16Gi
gn1.2xlarge | 8     | 32Gi
gn1.4xlarge | 16    | 64Gi
gn1.8xlarge | 32    | 128Gi


## M Series

The M Series provides resources for memory intensive
applications.

*M* is the abbreviation of "Memory".

### M Characteristics

Specific characteristics of this series are:
- *Hugepages* - Hugepages are used in order to improve memory
  performance
- *vCPU-To-Memory Ratio (1:8)* - A vCPU-to-Memory ratio of 1:8, for much
  less noise per node

### M Instance Types

The following instance types are available in this series:

Name       | Cores | Memory
-----------|-------|-------
m1.large   | 2     | 16Gi
m1.xlarge  | 4     | 32Gi
m1.2xlarge | 8     | 64Gi
m1.4xlarge | 16    | 128Gi
m1.8xlarge | 32    | 256Gi


## N Series

The N Series is quite neutral and provides resources for
general purpose applications.

*N* is the abbreviation for "Neutral", hinting at the neutral
attitude towards workloads.

VMs of instance types will share physical CPU cores on a
time-slice basis with other VMs.

### N Characteristics

Specific characteristics of this series are:
- *vCPU-To-Memory Ratio (1:4)* - A vCPU-to-Memory ratio of 1:4, for less
  noise per node

### N Instance Types

The following instance types are available in this series:

Name       | Cores | Memory
-----------|-------|-------
n1.medium  | 1     | 4Gi
n1.large   | 2     | 8Gi
n1.xlarge  | 4     | 16Gi
n1.2xlarge | 8     | 32Gi
n1.4xlarge | 16    | 64Gi
n1.8xlarge | 32    | 128Gi


