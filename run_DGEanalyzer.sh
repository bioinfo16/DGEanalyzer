#!/bin/bash
##### run_all.sh #####
# This script automates the full RNA expression analysis pipeline:
# 1. Merges COSMIC expression data with GDSC metadata to match the cancer type and loads into MySQL.
# 2. Generates a boxplot for the gene of interest across cancer types.
# 3. Optionally performs DEG analysis if "-deg" flag is entered.

EXP_MAT=$1
GENE=$2
DEG_OPTION=$3

##### Step 1: Merge and Load Data #####
# This step loads the merged COSMIC + GDSC RNA expression data into MySQL
echo "[Step 1] Loading expression data into MySQL..."
python3 01.Merge_cellInfo_ExpDat.py $EXP_MAT

##### Step 2: Generate boxplot #####
# This step generates a boxplot for the given gene across cancer types
echo "[Step 2] Generating boxplot for $GENE..."
python3 02.Compare_across_types.py $GENE

##### Step 3: Perform DEG analysis if requested #####
if [ "$DEG_OPTION" == "-deg" ]; then
  echo "[Step 3] Running DEG analysis for $GENE..."
  python3 03.Perform_DEGanalysis.py $GENE
else
  echo "[Skip Step 3] DEG analysis not requested."
fi

echo "[Pipeline Complete] All steps finished."
