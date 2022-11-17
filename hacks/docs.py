#!/usr/bin/env python

import yaml
import textwrap


def buildOne(doc, cols):
    return [f(doc) for f in cols]

class InstanceType:
    name = None
    series = None
    cores = None
    memory = None

    def from_doc(doc):
        i = InstanceType()
        i.name = doc["metadata"]["name"]
        i.series = doc["metadata"]["annotations"]["series.name"]
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
        s.cls = doc["metadata"]["annotations"]["series.class"]
        s.description = doc["metadata"]["annotations"]["series.description"]
        return s

    def instanceTypes(self):
        series = self
        return list(filter(lambda i: i.series == series.name, (InstanceType.from_doc(doc) for doc in self._docs)))

    def printInstanceTypesTable(self):
        hdr = ["Name", "Cores", "Memory"]

        # Fix natural sort for GiB
        rows = sorted([[i.name, i.cores, i.memory] for i in self.instanceTypes()], key=lambda e: (e[1], e[2]))

        colMaxLens = [-1 for _ in range(0, len(rows[0]))]
        for row in [hdr] + rows:
            for idx, val in enumerate(row):
                colMaxLens[idx] = max(colMaxLens[idx], len(str(row[idx])))

        def formatRow(row):
            return "  ".join(str(val).ljust(colMaxLens[idx]) for idx, val in enumerate(row))

        print(formatRow(hdr))
        print("-".join("" for _ in range(-1, len(formatRow(hdr)))))
        for row in rows:
            print(formatRow(row))

    def print(self):
        print("# %s Series" % self.name.upper())
        print("\n".join(textwrap.wrap(self.description)))
        print("")
        print("The following instance types are available in this series:\n")
        self.printInstanceTypesTable()

        print("")

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, o):
        return hash(self) == hash(o)

class Seriess:
    def from_list(docs):
        return set(Series.from_doc(d, docs) for d in docs)

def dumpAll(g):
    docs = list(g)
    for s in Seriess.from_list(docs):
        s.print()
        print("")

if __name__ == "__main__":
    with open("instanceTypes.yaml", "r") as f:
        dumpAll(yaml.safe_load_all(f))
