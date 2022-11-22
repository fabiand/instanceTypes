#!/usr/bin/env python

import yaml
import textwrap
import io


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
        i.series = doc["metadata"]["annotations"]["series.name"]
        i.seriesnv = doc["metadata"]["annotations"]["series.nv"]
        i.cores = doc["spec"]["cpu"]["cores"]
        i.memory = doc["spec"]["memory"]["guest"]
        return i

class Series:
    _docs = None
    name = None
    cls = None
    description = None
    

    def from_doc(doc, docs):
        s = Series()
        s._docs = docs
        s.name = doc["metadata"]["annotations"]["series.name"]
        s.nv = doc["metadata"]["annotations"]["series.nv"]
        s.cls = doc["metadata"]["annotations"]["series.class"]
        s.description = doc["metadata"]["annotations"]["series.description"]
        return s

    def instanceTypes(self):
        series = self
        return sorted(list(filter(lambda i: i.series == series.name, (InstanceType.from_doc(doc) for doc in self._docs))), key=lambda i: i.name)

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

class MarkdownifySeriess:
    """Generate a markdown represenattion of our internal model

    https://github.blog/2022-02-14-include-diagrams-markdown-files-mermaid/
    """
    seriess = None

    def __init__(self, seriess):
        self.seriess = seriess

    def build(self):
        out = []

        out.append("# Overview")
        out.append("""
The available instance types are structured into two themes:

1. General purpose
2. Workload specific

Instance Types of the first theme are a good starting point to run your workload.
Once you know more about the requirements of your workload, you can start choosing a
specific instance type of the second class.

The following diagram summarises the available instance types and the use-cases:
""")
        out.append("""
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
            if ndTxt == "General purpose":
                out.append(f"nwrkld:::grp --> {nd}:::series")
            else:
                out.append(f"wrkld:::grp --> {nd}:::series")
            out.append(f"{nd}([{ndTxt}]):::series --> {s.nv}:::instancetype")
            out.append("")
        out.append("```")

        for s in sorted(self.seriess.items, key=lambda i: i.name):
            out.append(self.buildSeries(s))
            out.append("")

        return "\n".join(out)

    def buildSeries(self, s):
        out = []

        out.append("# %s Series" % s.name.upper())
        out.append("\n".join(textwrap.wrap(s.description)))
        out.append("")
        out.append("The following instance types are available in this series:\n")
        out.append(self.buildSeriesInstanceTypesTable(s))

        out.append("")

        return "\n".join(out)

    def buildSeriesInstanceTypesTable(self, s):
        hdr = ["Name", "Cores", "Memory"]

        # Fix natural sort for GiB
        rows = sorted([[i.name, i.cores, i.memory] for i in s.instanceTypes()], key=lambda e: (e[1], e[2]))

        colMaxLens = [-1 for _ in range(0, len(rows[0]))]
        for row in [hdr] + rows:
            for idx, val in enumerate(row):
                colMaxLens[idx] = max(colMaxLens[idx], len(str(row[idx])))

        def formatRow(row):
            return " | ".join(str(val).ljust(colMaxLens[idx]) for idx, val in enumerate(row))

        out = []

        out.append(formatRow(hdr))
        out.append(formatRow("-" * colMaxLens[idx] for idx,_ in enumerate(hdr)).replace(" ", "-"))
        for row in rows:
            out.append(formatRow(row))

        return "\n".join(out)

    def __str__(self):
        return self.build()

    def print(self):
        print(self)


def dumpAll(g):
    docs = list(g)

    ss = Seriess.from_list(docs)
    MarkdownifySeriess(ss).print()

if __name__ == "__main__":
    with open("instanceTypes.yaml", "r") as f:
        dumpAll(yaml.safe_load_all(f))
