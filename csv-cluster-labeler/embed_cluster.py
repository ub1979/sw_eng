#!/usr/bin/env python3
"""
embed_cluster.py — Embed text column, auto-cluster, extract samples → JSON
"""

import argparse
import json
import math
import random
import sys

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer


def auto_k(embeddings: np.ndarray, k_min: int = 2, k_max: int = 15) -> int:
    """Pick k that maximises silhouette score over [k_min, k_max]."""
    n = len(embeddings)
    k_max = min(k_max, int(math.sqrt(n)), n - 1)
    k_min = min(k_min, k_max)

    if k_min >= k_max:
        return k_min

    best_k, best_score = k_min, -1.0
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init="auto")
        labels = km.fit_predict(embeddings)
        try:
            score = silhouette_score(embeddings, labels, sample_size=min(2000, n))
        except Exception:
            continue
        if score > best_score:
            best_score, best_k = score, k
    return best_k


def main():
    parser = argparse.ArgumentParser(description="Embed + cluster a CSV text column")
    parser.add_argument("--csv", required=True, help="Path to input CSV")
    parser.add_argument("--text-col", required=True, help="Column with text to embed")
    parser.add_argument("--label-col", required=True, help="Column whose unique values = label vocabulary")
    parser.add_argument("--output", required=True, help="Output prefix (prefix_clusters.json will be written)")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="SentenceTransformer model name")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    print(f"[embed_cluster] Loading {args.csv} ...", file=sys.stderr)
    try:
        df = pd.read_csv(args.csv)
    except Exception:
        # Fallback: use Python engine which is more lenient with quoting
        df = pd.read_csv(args.csv, engine="python", on_bad_lines="warn")

    if args.text_col not in df.columns:
        sys.exit(f"ERROR: text column '{args.text_col}' not found. Available: {list(df.columns)}")
    if args.label_col not in df.columns:
        sys.exit(f"ERROR: label column '{args.label_col}' not found. Available: {list(df.columns)}")

    label_vocabulary = sorted(df[args.label_col].dropna().unique().tolist())
    texts = df[args.text_col].fillna("").astype(str).tolist()
    n = len(texts)
    print(f"[embed_cluster] {n} rows, {len(label_vocabulary)} unique labels.", file=sys.stderr)

    print(f"[embed_cluster] Embedding with '{args.model}' ...", file=sys.stderr)
    model = SentenceTransformer(args.model)
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    print("[embed_cluster] Selecting optimal k ...", file=sys.stderr)
    k = auto_k(embeddings)
    print(f"[embed_cluster] Clustering into k={k} clusters ...", file=sys.stderr)

    km = KMeans(n_clusters=k, random_state=args.seed, n_init="auto")
    assignments = km.fit_predict(embeddings).tolist()

    # Build cluster sample list
    clusters = []
    for cid in range(k):
        indices = [i for i, a in enumerate(assignments) if a == cid]
        sample_size = min(10, len(indices))
        sampled = random.sample(indices, sample_size)
        samples = []
        for idx in sampled:
            row_dict = df.iloc[idx].to_dict()
            # Convert non-serialisable types
            row_dict = {k: (v if isinstance(v, (str, int, float, bool)) or v is None else str(v))
                        for k, v in row_dict.items()}
            samples.append({
                "row_idx": idx,
                "text": texts[idx],
                "all_columns": row_dict,
            })
        clusters.append({
            "cluster_id": cid,
            "size": len(indices),
            "samples": samples,
        })

    output = {
        "csv_file": args.csv,
        "total_rows": n,
        "num_clusters": k,
        "label_vocabulary": label_vocabulary,
        "cluster_assignments": assignments,
        "clusters": clusters,
    }

    out_path = f"{args.output}_clusters.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"[embed_cluster] Written → {out_path}", file=sys.stderr)
    print(out_path)  # stdout: the output path for easy capture


if __name__ == "__main__":
    main()
