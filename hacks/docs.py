#!/usr/bin/env python

import yaml

def printTable(rows):
    colMaxLens = [-1 for _ in range(0, len(rows[0]))]
    for row in rows:
        for idx, val in enumerate(row):
            colMaxLens[idx] = max(colMaxLens[idx], len(str(row[idx])))
    texts = ["\t".join(str(val).ljust(colMaxLens[idx]) for idx, val in enumerate(row)) for row in rows]
    return colMaxLens, texts

def buildOne(doc, cols):
    return [f(doc) for f in cols]
    

def dumpAll(g):
    cols = {
        "Class": lambda doc: doc["metadata"]["annotations"]["series.class"],
        "Name": lambda doc: doc["metadata"]["name"],
        "Series Description": lambda doc: doc["metadata"]["annotations"]["series.description"],
        "Cores": lambda doc: doc["spec"]["cpu"]["cores"],
        "Memory": lambda doc: doc["spec"]["memory"]["guest"],
        }

    rows = [buildOne(doc, cols.values()) for doc in g]
    maxs, texts = printTable(rows)
    print("\t".join(str(val).ljust(maxs[idx]) for idx, val in enumerate(cols.keys())))
    print("\n".join(texts))

if __name__ == "__main__":
    with open("instanceTypes.yaml", "r") as f:
        dumpAll(yaml.safe_load_all(f))
