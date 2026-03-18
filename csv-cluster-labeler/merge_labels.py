#!/usr/bin/env python3
"""
merge_labels.py — Merge Claude's cluster labels back into the original CSV
"""

import argparse
import json
import sys

import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Merge cluster labels into CSV")
    parser.add_argument("--csv", required=True, help="Path to original CSV")
    parser.add_argument("--clusters-json", required=True, help="Path to _clusters.json produced by embed_cluster.py")
    parser.add_argument(
        "--labels",
        required=True,
        help='JSON mapping cluster_id (string) → list of label strings, e.g. \'{"0": ["billing"], "1": ["support"]}\'',
    )
    parser.add_argument("--output-prefix", required=True, help="Prefix for output files")
    args = parser.parse_args()

    print(f"[merge_labels] Loading {args.csv} ...", file=sys.stderr)
    df = pd.read_csv(args.csv)

    with open(args.clusters_json, encoding="utf-8") as f:
        cluster_data = json.load(f)

    try:
        labels_map: dict[str, list[str]] = json.loads(args.labels)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: --labels is not valid JSON: {e}")

    assignments = cluster_data["cluster_assignments"]
    if len(assignments) != len(df):
        sys.exit(
            f"ERROR: cluster_assignments length ({len(assignments)}) != CSV rows ({len(df)})"
        )

    df["cluster_id"] = assignments
    df["cluster_labels"] = df["cluster_id"].apply(
        lambda cid: ", ".join(labels_map.get(str(cid), []))
    )

    labeled_path = f"{args.output_prefix}_labeled.csv"
    df.to_csv(labeled_path, index=False)
    print(f"[merge_labels] Written → {labeled_path}", file=sys.stderr)

    # Build report
    report_clusters = []
    for cluster_info in cluster_data["clusters"]:
        cid = cluster_info["cluster_id"]
        sample_texts = [s["text"] for s in cluster_info["samples"]]
        report_clusters.append({
            "cluster_id": cid,
            "size": cluster_info["size"],
            "labels": labels_map.get(str(cid), []),
            "sample_texts": sample_texts,
        })

    report = {
        "csv_file": args.csv,
        "total_rows": cluster_data["total_rows"],
        "num_clusters": cluster_data["num_clusters"],
        "label_vocabulary": cluster_data["label_vocabulary"],
        "clusters": report_clusters,
    }

    report_path = f"{args.output_prefix}_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[merge_labels] Written → {report_path}", file=sys.stderr)

    print(f"{labeled_path}\n{report_path}")  # stdout for capture


if __name__ == "__main__":
    main()
