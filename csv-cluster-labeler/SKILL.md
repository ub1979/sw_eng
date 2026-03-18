---
name: csv-cluster-labeler
description: Use when analyzing CSV datasets by embedding text columns, clustering semantically, and labeling clusters using LLM classification with a label vocabulary from the CSV
---

# CSV Cluster Labeler

Embeds a text column, auto-clusters rows semantically, then uses LLM reasoning to assign labels from the label vocabulary already present in the CSV.

---

## Step 1 — Collect Inputs

Ask the user (skip any already provided):

1. **Input path** — a single `.csv` file or a folder (processed recursively)
2. **Text column** — which column contains the text to embed
3. **Label column** — which column contains the label vocabulary (its unique values become valid labels)
4. **Conda environment** — run `conda env list` and show the list; ask which env to use

Accept arguments inline if provided: `--path`, `--text-col`, `--label-col`, `--conda-env`.

---

## Step 2 — Discover CSV Files

```python
import pathlib
p = pathlib.Path(input_path)
csv_files = sorted(p.rglob("*.csv")) if p.is_dir() else [p]
```

Tell the user how many files were found before proceeding.

---

## Step 3 — Install Dependencies

Run once in the chosen conda environment:

```bash
conda run -n <env> pip install sentence-transformers scikit-learn pandas numpy --quiet
```

Confirm success before proceeding.

---

## Step 4 — Per-File Pipeline

Repeat for **each CSV file** independently:

### 4a. Embed & Cluster

```bash
conda run -n <env> python /path/to/embed_cluster.py \
  --csv "<csv_path>" \
  --text-col "<text_col>" \
  --label-col "<label_col>" \
  --output "<csv_path_without_extension>"
```

This writes `<prefix>_clusters.json` and prints the path to stdout.

The script path is: `<SKILL_DIR>/embed_cluster.py`
(Same directory as this SKILL.md — resolve with `pathlib.Path(__file__).parent` or equivalent.)

### 4b. LLM Classification

Read the `_clusters.json` file. It contains:
- `label_vocabulary` — the valid labels (string list)
- `clusters[].samples[].text` — raw text samples per cluster

**For each cluster**, reason as follows:

```
Cluster <id> has <size> rows.
Sample texts:
  1. "<text>"
  2. "<text>"
  ...

Label vocabulary: [<labels>]

Task: Assign 1 or more labels from the vocabulary that best describe this cluster.
Multi-label is allowed. Choose only from the vocabulary.
Briefly justify your choice (1–2 sentences).
```

Collect results as a JSON map: `{"0": ["label_a"], "1": ["label_b", "label_c"], ...}`

### 4c. Merge Labels

```bash
conda run -n <env> python /path/to/merge_labels.py \
  --csv "<csv_path>" \
  --clusters-json "<prefix>_clusters.json" \
  --labels '<labels_json>' \
  --output-prefix "<csv_path_without_extension>"
```

This writes `<prefix>_labeled.csv` and `<prefix>_report.json`.

---

## Step 5 — Summary

After all files are processed, print a table:

| File | Rows | Clusters | Output |
|------|------|----------|--------|
| foo.csv | 500 | 6 | foo_labeled.csv |

List any errors encountered per file.

---

## LLM Classification Guidelines

- **Read all samples carefully** — look for themes, intent, topic, sentiment
- **Use only the provided label vocabulary** — do not invent new labels
- **Multi-label is fine** — a cluster can span multiple categories
- **Be decisive** — assign at least one label per cluster
- **Justify briefly** — one sentence explaining the choice

---

## Output Files (per CSV)

| File | Description |
|------|-------------|
| `<name>_clusters.json` | Embedding + clustering data with samples |
| `<name>_labeled.csv` | Original CSV + `cluster_id` + `cluster_labels` columns |
| `<name>_report.json` | Summary: cluster sizes, assigned labels, sample texts |

All outputs are written to the **same folder as the input CSV**.

---

## Script Locations

Both helper scripts live alongside this SKILL.md:

- `embed_cluster.py` — embedding + KMeans clustering
- `merge_labels.py` — label merging + report generation

Use `pathlib.Path` to resolve their absolute paths relative to this file when invoking them.
