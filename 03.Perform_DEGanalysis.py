#!/usr/bin/env python3
import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import MySQLdb

# Read gene symbol from user argument
gene = sys.argv[1]

# Connect to MySQL
conn = MySQLdb.connect(
    host="localhost",
    user="min-jeongbaek",
    passwd="Hellounmcmj23*",
    db="min-jeongbaek",
    unix_socket="/run/mysqld/mysqld.sock"
)

# Prompt for cancer type
print("Available cancer types: LUAD, BRCA, PAAD, PRAD, LIHC")
cancer = input("Enter cancer type: ").strip()

# Step 1: get expression of the gene of interest in this cancer type
query_gene = """
SELECT cell_line, expression FROM RNAexp
WHERE genes = '{}' AND cancer_type = '{}'
""".format(gene, cancer)
df_expr = pd.read_sql(query_gene, conn)

if df_expr.empty:
    print("No data found for gene '{}' in cancer type '{}'.".format(gene, cancer))
    conn.close()
    sys.exit(1)

# Step 2: assign High/Low group based on median expression
median_val = df_expr["expression"].median()
df_expr["condition"] = ["High" if x > median_val else "Low" for x in df_expr["expression"]]

# Step 3: get full gene expression matrix for this cancer type
query_all = """
SELECT genes, cell_line, expression FROM RNAexp
WHERE cancer_type = '{}'
""".format(cancer)
df_all = pd.read_sql(query_all, conn)

# Step 4: create gene × sample expression matrix
count_matrix = df_all.pivot(index="genes", columns="cell_line", values="expression").fillna(0)

# Step 5: metadata table for samples
sample_conditions = df_expr[["cell_line", "condition"]].rename(columns={"cell_line": "sample"})

# Step 6: prepare counts (positive integer matrix) and metadata
filtered_counts = count_matrix[sample_conditions["sample"]].T
filtered_counts.index.name = "sample"
filtered_counts = filtered_counts.clip(lower=0)  # remove any negative values
filtered_counts = filtered_counts.round().astype(int) # round to int

#### Set index of metadata to sample name to be matched filtered_counts
sample_conditions = sample_conditions.set_index("sample")

# Step 7: run DESeq2
dds = DeseqDataSet(
    counts=filtered_counts,
    metadata=sample_conditions,
    design="~ condition"
)
dds.deseq2()

#### Get the result
# Extract results
stat_res = DeseqStats(
        dds,
        contrast=["condition", "High", "Low"]
)
stat_res.summary()
res = stat_res.results_df

# Step 8: format volcano plot info
res["neg_log10_padj"] = -np.log10(res["padj"].replace(0, np.nan))
res["significant"] = (res["padj"] < 0.05) & (abs(res["log2FoldChange"]) > 1)

# Step 9: save results
os.makedirs("../output/figures", exist_ok=True)
tsv_path = "../output/{}_{}_DEG_results.tsv".format(cancer, gene)
png_path = "../output/figures/volcano_{}_{}.png".format(cancer, gene)
res.to_csv(tsv_path, sep="\t", index=False)

# Step 10: plot volcano
plt.figure(figsize=(10, 6))
plt.scatter(
    res["log2FoldChange"],
    res["neg_log10_padj"],
    c=res["significant"].map({True: "red", False: "gray"}),
    alpha=0.6,
    edgecolor="none"
)
plt.axhline(-np.log10(0.05), linestyle="--", color="blue")
plt.axvline(1, linestyle="--", color="blue")
plt.axvline(-1, linestyle="--", color="blue")
plt.xlabel("log2 Fold Change")
plt.ylabel("-log10(padj)")
plt.title("Volcano Plot: {} High vs Low ({})".format(gene, cancer))
plt.tight_layout()
plt.savefig(png_path)
plt.close()

# Step 11: print result summary
print("DEG results saved to " + tsv_path)
print("Volcano plot saved to " + png_path)
print("[Finished] DEG analysis is done.")

conn.close()

