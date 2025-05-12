#!/usr/bin/env python3
# 01.Merge_cellInfo_ExpDat.py
# Merge COSMIC RNA expression data with GDSC cell line metadata and generate the SQL database
# to use RNA expression data for analysis across different cell lines

import sys
import pandas as pd
import MySQLdb

##### File paths (adjust these to match your local files) #####
cosmic_RNA_expr = sys.argv[1]
gdsc_file = "../data/Cell_Lines_Details_fromGDSC.csv"

##### Load GDSC metadata and format COSMICnum #####
gdsc_df = pd.read_csv(gdsc_file)
gdsc_df['COSMIC_SAMPLE_ID'] = gdsc_df['COSMICnum'].apply(lambda x: "COSS{}".format(int(x)))
gdsc_df = gdsc_df[['COSMIC_SAMPLE_ID', 'Cell', 'TCGALabel']]
gdsc_df.columns = ['COSMIC_SAMPLE_ID', 'cellLine', 'cancer']

##### Load COSMIC RNA expression data #####
cosmic_df = pd.read_csv(cosmic_RNA_expr, sep="\t")

##### Merge GDSC metadata into COSMIC expression data #####
merged_df = pd.merge(cosmic_df, gdsc_df, on='COSMIC_SAMPLE_ID', how='inner')

##### Prepare final table #####
merged_df = merged_df[['GENE_SYMBOL', 'cellLine', 'cancer', 'GENE_EXPRESSION']]
merged_df.columns = ['genes', 'cell_line', 'cancer_type', 'expression']

##### Connect to MySQL database #####
conn = MySQLdb.connect(
    host="localhost",
    user="your_name",
    passwd="your_password",
    db="your_db",
    unix_socket="/run/mysqld/mysqld.sock"
)
cursor = conn.cursor()

##### Drop the RNA expression data table if it exists #####
cursor.execute("DROP TABLE IF EXISTS RNAexp")

##### Create the expressiont table to generate new dataset #####
cursor.execute("""
CREATE TABLE RNAexp (
    genes VARCHAR(100),
    cell_line VARCHAR(100),
    cancer_type VARCHAR(100),
    expression FLOAT
);
""")

##### Insert merged records into the MySQL table #####
# Loop over all rows in the merged DataFrame
for i in range(len(merged_df)):
    gene_name = merged_df.loc[i, 'genes']
    cell_line_name = merged_df.loc[i, 'cell_line']
    cancer_type_name = merged_df.loc[i, 'cancer_type']
    expression_value = merged_df.loc[i, 'expression']
    
    # Insert into the MySQL table "RNAexp"
    cursor.execute(
        "INSERT INTO RNAexp (genes, cell_line, cancer_type, expression) VALUES (%s, %s, %s, %s)",
        (gene_name, cell_line_name, cancer_type_name, expression_value)
    )

##### Finalize database transaction #####
conn.commit()
cursor.close()
conn.close()

print("[Finished - step 01] Cell line expression data successfully saved into the MySQL database.")

