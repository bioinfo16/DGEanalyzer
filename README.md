# DGEanalyzer: Differential Gene Expression Analysis for Cancer Cell Lines

## Purpose
This project provides a pipeline to explore RNA expression across cancer cell lines using COSMIC and GDSC data.
It allows:
- Read COSMIC expression data file format and loading data into MySQL to reduce the time of each analysis.
- Compare specific gene expression across cancer types
 : It works for 5 cancer types: LUAD, BRCA, PAAD, PRAD, and LIHC
- Differentially expressed genes (DEGs) can be identified by grouping cell lines into high and low expression groups based on a gene of interest.

## Background
To better understand the biological relevance of gene expression variability in cancer, we conducted differential gene expression analysis by dividing samples into high and low expression groups based on a gene of interest. This approach helps uncover downstream transcriptional changes that may reflect the gene’s functional role or involvement in key cellular pathways. Previous studies, including those from the GDSC and COSMIC databases, have shown that differences in gene expression can be closely linked to drug response and tumor behavior [1,2]. With the continued development of RNA-Seq technologies and robust analytical tools like DESeq2 and PyDESeq2, identifying expression-associated changes has become a powerful strategy for exploring tumor heterogeneity and discovering potential therapeutic targets [3,4].
## How to Use This Program

### Requirements
- Python 3.10+
- MySQL Server
- Required python libraries:
  1) pandas
  2) matplotlib
  3) MySQLdb
  4) pydeseq2
+ It is recommended to set up a Conda environment because of installation of pydeseq2, and the code for that is as follows.
```bash
# Make conda environment for DGEanalyzer
conda create --prefix /path/to/bigger/disk/pydeseq2_env python=3.10
conda init # Reaccess the server after this
conda activate pydeseq2_env

# Install pydeseq2 to new conda environment for DGEanalyzer
git clone https://github.com/owkin/PyDESeq2.git
cd PyDESeq2
pip install .
```
  
### Input
: Download the RNA cell line expression file from COSMIC (*.tsv)
[https://cancer.sanger.ac.uk/cosmic/download/cell-lines-project/v101/rawgeneexpression](https://cancer.sanger.ac.uk/cosmic/download/cell-lines-project/v101/rawgeneexpression)
: This data file is too big to load whole data to MySQL Server so, you can select specific gene expression data with modifying the command used for making toy dataset (toy_data_for_test.tsv) for code test. By example command, expression of 3 genes (KRAS, TP53, and MYC) could be selected for further analysis.
```bash
awk -F '\t' 'NR==1 || $4=="KRAS" || $4=="TP53" || $4=="MYC"' CellLinesProject_RawGeneExpression_v101_GRCh38.tsv > toy_data_for_test.tsv
```

### Run Example
- MySQL Setup
: Edit user/password in python files of "script" folder files to your information:
```python
user="your_username"
passwd="your_password"
db = "your_database"
unix_socket="/where/is/your_socket_file"
```

- Comparing gene expression across different cancer types
```bash
# For comparing RNA expression across different cell types only
bash run_DGEanalyzer.sh ../data/ KRAS

# For comparing RNA expression and DEG selection 
bash run_DGEanalyzer.sh ../data/toy_data_for_test.tsv KRAS -deg
```

## Output
+ All results are from the input expression matrix (toy_data_for_test.tsv) and it
has expression data of only 3 genes.
- Boxplot of selected gene across cancer types
![BoxPlot](http://odin.unomaha.edu/~min-jeongbaek/MYC_boxplot_across_cancers.png)

- Volcano plot and DEG lists from DEG analysis
![VolcanoPlot](http://odin.unomaha.edu/~min-jeongbaek/volcano_LIHC_KRAS.png)

## Reference papers
1. Yang, Wanjuan, et al. "Genomics of Drug Sensitivity in Cancer (GDSC): a resource for therapeutic biomarker discovery in cancer cells." Nucleic acids research 41.D1 (2012): D955-D961.
2. Forbes, Simon A., et al. "COSMIC: exploring the world's knowledge of somatic mutations in human cancer." Nucleic acids research 43.D1 (2015): D805-D811.
3. Costa-Silva, Juliana, Douglas Domingues, and Fabricio Martins Lopes. "RNA-Seq differential expression analysis: An extended review and a software tool." PloS one 12.12 (2017): e0190152.
4. Muzellec, Boris, et al. "PyDESeq2: a python package for bulk RNA-seq differential expression analysis." Bioinformatics 39.9 (2023): btad547.

## License
+ GPL 3.0 license
