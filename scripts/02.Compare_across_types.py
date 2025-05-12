#!/usr/bin/env python3
# 02.Compare_across_types.py
# Generates boxplots for selected gene across cancer types using MySQL data

import sys
import MySQLdb
import pandas as pd
import matplotlib.pyplot as plt
import os

# Read the gene symbol what user has an interest
gene = sys.argv[1]

conn = MySQLdb.connect(
    host="localhost",
    user="your_name",
    passwd="your_password",
    db="your_db"
)
cursor = conn.cursor()

cancer_types = ['LUAD', 'BRCA', 'PAAD', 'PRAD', 'LIHC']

data = []
labels = []

for cancer in cancer_types:
    query = "SELECT expression FROM RNAexp WHERE genes = '" + gene + "' AND cancer_type = '" + cancer + "'"
    cursor.execute(query)
    values = cursor.fetchall()
    values = [v[0] for v in values]
    if values:
        data.append(values)
        labels.append(cancer)

if data:
    os.makedirs("../output/figures", exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.boxplot(data, labels=labels)
    plt.title("Expression of " + gene + " Across Cancer Types")
    plt.ylabel("Expression Level")
    plt.tight_layout()
    outpath = "../output/figures/" + gene + "_boxplot_across_cancers.png"
    plt.savefig(outpath)
    plt.close()
    print("Boxplot saved to " + outpath)
else:
    print("No data found for gene: " + gene)

cursor.close()
conn.close()

print("[Finished] Gene expression comparison across cell lines is done.")
