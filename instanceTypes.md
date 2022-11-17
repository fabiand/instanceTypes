# CX Series
The CX Series provides exclusive compute resources for compute
intensive applications. The exclusive resources are given to the
compute threads of the VM. In order to ensure this, some additional
cores (depending on the number of disks and NICs) will be requested to
offload the IO threading from cores dedicated to the workload. In
addition, in this series, the NUMA topology of the used cores is
provided to the VM.

The following instance types are available in this series:

Name       | Cores | Memory
-----------|-------|-------
cx1.large  | 2     | 4Gi   
cx1.xlarge | 4     | 16Gi  


# M Series
The M Series provides resources for memory intensive applications.

The following instance types are available in this series:

Name      | Cores | Memory
----------|-------|-------
m1.large  | 2     | 16Gi  
m1.xlarge | 4     | 32Gi  


# N Series
The N Series is quite neutral and provides resources for general
purpose applications. VMs of instance types will share physical CPU
cores on a time-slice basis with other VMs.

The following instance types are available in this series:

Name      | Cores | Memory
----------|-------|-------
n1.small  | 1     | 1Gi   
n1.large  | 2     | 8Gi   
n1.xlarge | 4     | 16Gi  


# GN Series
The GN Series provides instances types intended for VMs with NVIDIA
GPU resources attached.

The following instance types are available in this series:

Name       | Cores | Memory
-----------|-------|-------
gn1.xlarge | 4     | 16Gi  


