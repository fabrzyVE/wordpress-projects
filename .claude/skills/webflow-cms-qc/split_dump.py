#!/usr/bin/env python3
"""
Split a Webflow MCP `list_collection_items` result into the per-collection
JSON files that qc_cms.py consumes.

`list_collection_items` for a full collection is usually too large to return
inline, so the MCP layer persists it to a file and prints the path. Pass that
file (or several) here. Each action's `label` decides the destination:
  label containing "nbhd" or "neighbor" -> qc/neighborhoods.json
  label containing "svc"  or "service"  -> qc/services.json

Usage:
  python3 split_dump.py <mcp-result-file> [<mcp-result-file> ...] [--outdir qc]
"""
import argparse
import json
import os
import sys


def decode_objects(text):
    """Yield each top-level JSON object from a stream of concatenated objects."""
    dec = json.JSONDecoder()
    i, n = 0, len(text)
    while i < n:
        while i < n and text[i] in " \n\r\t":
            i += 1
        if i >= n:
            break
        obj, end = dec.raw_decode(text, i)
        yield obj
        i = end


def load_text(path):
    raw = open(path).read()
    # MCP persisted results are wrapped as [{"type":"text","text":"<json>"}]
    try:
        w = json.loads(raw)
        if isinstance(w, list) and w and isinstance(w[0], dict) and "text" in w[0]:
            return "".join(p.get("text", "") for p in w)
    except json.JSONDecodeError:
        pass
    return raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--outdir", default="qc")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    wrote = {}
    for f in args.files:
        for obj in decode_objects(load_text(f)):
            label = (obj.get("label") or "").lower()
            items = obj.get("result", {}).get("items", obj.get("items", []))
            if "neighbor" in label or "nbhd" in label:
                dest = "neighborhoods.json"
            elif "service" in label or "svc" in label:
                dest = "services.json"
            else:
                print(f"  ! skipped object with label {label!r} (no match)")
                continue
            path = os.path.join(args.outdir, dest)
            json.dump(items, open(path, "w"))
            wrote[dest] = len(items)
            print(f"  {dest}: {len(items)} items")

    if not wrote:
        print("No collection items found in inputs.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
