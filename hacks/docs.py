#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import yaml
import textwrap
import io
import re

from pprint import pprint

def is_valid_instancetype_name(s):
    return bool(re.match("^((u|uo|cx|m|n)|(g([nia])))1\.(small|medium|large|(2|4|8)?xlarge)$", s))

def buildOne(doc, cols):
    return [f(doc) for f in cols]

class InstanceType:
    name = None
    series = None
    seriesnv = None
    cores = None
    memory = None

    def from_doc(doc):
        i = InstanceType()
        i.name = doc["metadata"]["name"]
        assert is_valid_instancetype_name(i.name), f"{i.name} is invalid"
        i.series = doc["metadata"]["annotations"]["series.name"]
        i.seriesnv = doc["metadata"]["annotations"]["series.nv"]
        i.cores = doc["spec"]["cpu"]["guest"]
        i.memory = doc["spec"]["memory"]["guest"]
        i.doc = doc
        return i

class Series:
    _docs = None
    name = None
    name_expanded = None
    cls = None
    description = None

    def from_doc(doc, docs):
        s = Series()
        s._docs = docs
        s.name = doc["metadata"]["annotations"]["series.name"]
        s.name_expanded = doc["metadata"]["annotations"]["series.name_expanded"]
        s.nv = doc["metadata"]["annotations"]["series.nv"]
        s.cls = doc["metadata"]["annotations"]["series.class"]
        s.description = doc["metadata"]["annotations"]["series.description"]
        s.doc = doc
        return s

    def instanceTypes(self):
        series = self
        return sorted(list(filter(lambda i: i.series == series.name, (InstanceType.from_doc(doc) for doc in self._docs))), key=lambda i: i.name)

    def __repr__(self):
        return f"<Series {self.name}>"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, o):
        return hash(self) == hash(o)

class Seriess:
    items = None

    def from_list(docs):
        s = Seriess()
        s.items = sorted(list(set(Series.from_doc(d, docs) for d in docs)), key=lambda i: i.name)
        return s

def buildMarkdownTable(hdr, rows):
    colMaxLens = [-1 for _ in range(0, len(rows[0]))]
    for row in [hdr] + rows:
        for idx, val in enumerate(row):
            colMaxLens[idx] = max(colMaxLens[idx], len(str(row[idx])))

    def formatRow(row):
        return " | ".join(str(val).ljust(colMaxLens[idx]) for idx, val in enumerate(row)).rstrip()

    out = []
    out.append(formatRow(hdr))
    out.append(formatRow("-" * colMaxLens[idx] for idx,_ in enumerate(hdr)).replace(" ", "-"))
    for row in rows:
        out.append(formatRow(row))

    return "\n".join(out)

class MarkdownifySeriess:
    """Generate a markdown represenattion of our internal model

    https://github.blog/2022-02-14-include-diagrams-markdown-files-mermaid/
    """
    seriess = None

    def __init__(self, seriess):
        self.seriess = seriess

    def build(self):
        out = []

        out.append("""
# Introduction

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
""")

        for s in sorted(self.seriess.items, key=lambda i: i.name):
            nd, ndTxt = (s.cls.replace(" ", ""), s.cls)
            # FIXME to get groups from def
            if ndTxt in ("General purpose", "Oversubscribed"):
                out.append(f"nwrkld:::grp --> {nd}:::series")
            else:
                out.append(f"wrkld:::grp --> {nd}:::series")
            out.append(f"{nd}([{ndTxt}]):::series --> {s.nv}:::instancetype")
            out.append("")

        out.append("""
```

### Schema

<details><summary>Click in order to view the instanceType names schema</summary>

```ebnf
instanceTypeName = seriesName , "." , size;

seriesName = ( class | vendorClass ) , version;

class = "u" | "uo" | "cx" | "m" | "n";
vendorClass = "g" , vendorHint;
vendorHint = "n" | "i" | "a";
version = "1";

size = "small" | "medium" | "large" | [( "2" | "4" | "8" )] , "xlarge";
```
</details>

""")

        out.append("# Series\n")
        out.append(self.buildSeriesComparisonTable())
        out.append("")

        for s in sorted(self.seriess.items, key=lambda i: i.name):
            out.append(MarkdownifySeries(s).build())
            out.append("")

        return "\n".join(out)

    def __str__(self):
        return self.build()

    def print(self):
        print(self)

    def buildSeriesComparisonTable(self):
        CHECKMARK = " ✓ "
        cha = characteristics()

        sortedSeriesItems = sorted(self.seriess.items, key=lambda i: i.name)

        hdr = ["."] + [" %s " % s.name.upper() for s in sortedSeriesItems]

        rows = []
        for c in cha.keys():
            row = [f"*{c}*"] + ["   " for s in sortedSeriesItems]
            for series_idx, series in enumerate(sortedSeriesItems):
                series_idx += 1
                for instanceType in series.instanceTypes():
                    ratio_match = re.search("(.*)\s+\((.*)\)", c)
                    try:
                        # Is the characteristic persent in the yaml?
                        if cha[c][0](instanceType.doc):
                            if ratio_match:
                                row[0] = "*%s*" % ratio_match.group(1)
                                row[series_idx] = " %s " % ratio_match.group(2).rjust(2)
                            else:
                                row[series_idx] = CHECKMARK
                    except:
                        raise

            # Only add this row if this characteristic is used at all
            if len("".join(row[1:]).strip()) > 0:
                rows.append(row)

        # Dirty stuff to handle memory ratio
        new_rows = []
        row_hdrs = [r[0] for r in rows]
        same_rows_visited = []
        for row in rows:
            row_hdr = row[0]
            if row_hdr in same_rows_visited:
                continue
            same_rows_idx = [rhidx for rhidx, rh in enumerate(row_hdrs) if rh == row_hdr]
            same_rows = [rows[rhidx][1:] for rhidx in same_rows_idx]
            if len(same_rows) > 1:
                new_row = [row_hdr] + (["".join(list(z)).strip() for z in zip(*same_rows)])
                new_rows.append(new_row)
                same_rows_visited.append(row_hdr)
            else:
                new_rows.append(row)

        rows = new_rows

        return buildMarkdownTable(hdr, rows)


def characteristics():
    def MemoryPerCore(d):
        # We assume they are set
        cores = d["spec"].get("cpu").get("guest")
        mem = re.match("\d+", d["spec"].get("memory").get("guest")).group(0)
        r = int(mem) / int(cores)
        return int(r)

    knownPaths = {
        # Tuple fmt (match-fn, on-match-human-message)
        "Dedicated IO Threads":
            (lambda d: d["spec"].get("dedicatedIOThread", False) == True,
             "IO threads are isolated from the vCPUs in order to reduce IO related impact on the workload"),
        "vNIC Multi-Queue":
            (lambda d: "networkInterfaceMultiQueue" in d["spec"],
             "Multiqueueing is used for vNICs in order to increase network performance"),
        "Block Multi-Queue":
            (lambda d: "blockMultiQueue" in d["spec"],
             "Multiqueueing is used for disks in order to increase storage performance"),
        "Has GPUs":
            (lambda d: "gpus" in d["spec"],
             "Has GPUs predefined"),

        "Hugepages":
            (lambda d: "hugepages" in d["spec"].get("memory", {}),
             "Hugepages are used in order to improve memory performance"),
        "Compressed RAM":
            (lambda d: d["spec"].get("memory", {}).get("compressed", None) != None,
             "VM RAM is compressed in order to provide memory overcommit"),
        "Overcommitted Memory":
            (lambda d: d["spec"].get("memory", {}).get("overcommitPercent"),
             "Memory is over-committed in order to achieve a higher workload density"),

        "Dedicated CPU":
            (lambda d: d["spec"].get("cpu", {}).get("dedicatedCPUPlacement", False) == True,
             "Physical cores are exclusively assigned to every vCPU in order to provide fixed and high compute guarantees to the workload"),
        "Burstable CPU performance":
            (lambda d: d["spec"].get("cpu", {}).get("dedicatedCPUPlacement", False) == False,
             "The workload has a baseline compute performance but is permitted to burst beyond this baseline, if excess compute is available"),

        "Isolated emulator threads":
            (lambda d: d["spec"].get("cpu", {}).get("isolateEmulatorThread", False) == True,
             "Hypervisor emulator threads are isolated from the vCPUs in order to reduce emaulation related impact on the workload"),
        "vNUMA":
            (lambda d: "guestMappingPassthrough" in d["spec"].get("cpu", {}).get("numa", {}),
             "Physical NUMA topology is reflected in the guest in order to optimize guest sided cache utilization"),
        "vCPU-To-Memory Ratio (1:2)":
            (lambda d: MemoryPerCore(d) == 2, "A vCPU-to-Memory ratio of 1:2"),
        "vCPU-To-Memory Ratio (1:4)":
            (lambda d: MemoryPerCore(d) == 4, "A vCPU-to-Memory ratio of 1:4, for less noise per node"),
        "vCPU-To-Memory Ratio (1:8)":
            (lambda d: MemoryPerCore(d) == 8, "A vCPU-to-Memory ratio of 1:8, for much less noise per node"),
    }

    return knownPaths

class MarkdownifySeries:
    def __init__(self, series):
        self.series = series

    def build(self):
        s = self.series
        nU = s.name.upper()

        out = []

        out.append(f"## {nU} Series")
        out.append("")
        out.append(s.description)
        out.append("")
        out.append(f"### {nU} Series Characteristics")
        out.append("")
        out.append(self.buildCharacteristicsList(s))
        out.append("")
        out.append(f"### {nU} Series Instance Types")
        out.append("")
        out.append("The following instance types are available in this series:\n")
        out.append(self.buildSeriesInstanceTypesTable(s))

        out.append("")

        return "\n".join(out)

    def buildCharacteristicsList(self, s):
        knownPaths = characteristics()

        out = set([])

        for i in s.instanceTypes():
            for (t, (pf, m)) in knownPaths.items():
                try:
                    if pf(i.doc):
                        out.add(f"*{t}* - {m}")
                except:
                    raise

        if len(out) > 0:
            outTxt = "Specific characteristics of this series are:\n" \
                  + "\n".join("- " + "\n".join(textwrap.wrap(l, subsequent_indent="  ")) for l in sorted(out))

            # Poor mans mandatory field checks
            assert "Memory ratio" in outTxt, "Missing ration in: %s" % s.name
        else:
            outTxt = "This series has no specific characteristics."

        return outTxt

    def buildSeriesInstanceTypesTable(self, s):
        hdr = ["Name", "Cores", "Memory"]

        # Fix natural sort for GiB
        rows = sorted([[i.name, i.cores, i.memory] for i in s.instanceTypes()], key=lambda e: (e[1], e[2]))

        out = []
        out.append(buildMarkdownTable(hdr, rows))

        return "\n".join(out)


def dumpAll(g):
    docs = list(g)

    ss = Seriess.from_list(docs)
    MarkdownifySeriess(ss).print()

if __name__ == "__main__":
    with open("instanceTypes.yaml", "r") as f:
        dumpAll(yaml.safe_load_all(f))
