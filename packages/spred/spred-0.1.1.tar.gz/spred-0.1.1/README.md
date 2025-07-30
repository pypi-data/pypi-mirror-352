# SpReD-GIT

**Splicing-regulatory Driver Genes Identification Tool**

SpReD-GIT is a computational tool for identifying splicing-regulatory driver genes (SDGs) based on isoform-level expression quantification, such as outputs from XAEM or RSEM.

---

## Prerequisites

```bash
Python >= 3.7 (Python 3.8 recommended)
```

---

## Installation

Recommended installation using Conda:

```bash
conda create -n SpReD python==3.8
conda activate SpReD
pip install spred
```

---

## Input Files

### 1. Count Matrix File (`matrix.count.input.tsv`)

| transcript\_id    | Case1 | Case2 | Case3 | Control1 | Control2 | Control3 |
| ----------------- | ----- | ----- | ----- | -------- | -------- | -------- |
| ENST00000513924.2 | 153   | 130   | 90    | 78       | 158      | 110      |
| ENST00000511178.1 | 12    | 36    | 12    | 17       | 12       | 10       |
| ENST00000524846.5 | 224   | 470   | 195   | 275      | 380      | 612      |
| ENST00000294428.8 | 4     | 61    | 1     | 28       | 23       | 35       |
| ENST00000371072.8 | 240   | 281   | 229   | 339      | 282      | 291      |
| ENST00000418058.1 | 7     | 17    | 0     | 19       | 13       | 4        |
| ENST00000367006.8 | 154   | 181   | 127   | 142      | 246      | 188      |
| ENST00000419091.7 | 67    | 125   | 61    | 11       | 12       | 67       |
| ENST00000452621.6 | 42    | 59    | 52    | 95       | 59       | 84       |

* Rows: Transcript-level identifiers (e.g., Ensembl IDs)
* Columns: Sample names (must match group file)

### 2. Group File (`group.tsv`)

| Sample   | Group   |
| -------- | ------- |
| Case1    | Case    |
| Case2    | Case    |
| Case3    | Case    |
| Control1 | Control |
| Control2 | Control |
| Control3 | Control |
* `Sample`: Must match column names in the count matrix
* `Group`: Define condition labels (e.g., Case vs Control)
---

## Quick Start

### 1. Run the full pipeline including analysis, enrichment, and visualization: 

```bash
spred run-all -m matrix.count.input.tsv -e group.tsv -g Group -c1 Case -c2 Control -o outdir --species human
```

### 2. Run the differential analysis module (`analyze`) 

This module performs the following comparisons between Case and Control groups:

* **DGE**: Differentially Expressed Genes
* **DTE**: Differential Transcript Expression
* **SDG**: Splicing-regulatory Driver Genes

```bash
spred analyze -m matrix.count.input.tsv -e group.tsv -g Group -c1 Case -c2 Control -o outdir --species human
```

### 3. Run functional enrichment analysis (`enrich`)

Performs GO/KEGG enrichment analysis on results from DGE, DTE, or SDG. Supports multiple correction methods

```bash
spred enrich -i outdir/results/tables/Case_vs_Control.gene.deg.results.tsv --protein-coding --multitest hs
spred enrich -i outdir/results/tables/Case_vs_Control.isoform.dte.results.tsv --protein-coding --multitest hs
spred enrich -i outdir/results/tables/Case_vs_Control.sdGenes.results.tsv --protein-coding --multitest fdr_bh
```

### 4. Generate volcano plots (for DGE and DTE results) `plot-volcano` 

```bash
spred plot-volcano -i outdir/results/tables/kogo/Case_vs_Control.gene.deg.results.for_kogo.table.tsv --filter-lfc 1
spred plot-volcano -i outdir/results/tables/kogo/Case_vs_Control.isoform.dte.results.for_kogo.table.tsv --filter-lfc 1
```

### 5. Generate Mahalanobis plots (for SDG results) `plot-manhan`

```bash
spred plot-manhan -i outdir/results/tables/kogo/Case_vs_Control.sdGenes.results.for_kogo.table.tsv
```

---

## Definitions

* **DGE (Differentially Expressed Genes)**: Genes that show statistically significant expression changes between groups.
* **DTE (Differential Transcript Expression)**: Transcript-level expression differences, potentially indicating alternative splicing events.
* **SDG (Splicing-regulatory Driver Genes)**: Genes that exhibit splicing regulatory alterations, potentially playing a key role in disease mechanisms.

---

## Output Structure

```text
outdir/
└── results/
    ├── kogo/
    │   ├── Case_vs_Control.gene.deg.for_kogo.genelist.tsv
    │   ├── Case_vs_Control.gene.deg.for_kogo.table.tsv
    │   ├── Case_vs_Control.gene.deg.kogo.barplot.pdf
    │   ├── Case_vs_Control.gene.deg.kogo.barplot.png
    │   ├── Case_vs_Control.gene.deg.kogo.results.tsv
    │   ├── Case_vs_Control.isoform.dtg.for_kogo.genelist.tsv
    │   ├── Case_vs_Control.isoform.dtg.for_kogo.table.tsv
    │   ├── Case_vs_Control.isoform.dtg.kogo.barplot.pdf
    │   ├── Case_vs_Control.isoform.dtg.kogo.barplot.png
    │   ├── Case_vs_Control.isoform.dtg.kogo.results.tsv
    │   ├── Case_vs_Control.sdGenes.deg.for_kogo.genelist.tsv
    │   ├── Case_vs_Control.sdGenes.deg.for_kogo.table.tsv
    │   ├── Case_vs_Control.sdGenes.deg.kogo.barplot.pdf
    │   ├── Case_vs_Control.sdGenes.deg.kogo.barplot.png
    │   ├── Case_vs_Control.sdGenes.deg.kogo.results.tsv
    │   └── tables/
    │       ├── Case_vs_Control.GO_BP.results.all.xls
    │       └── Case_vs_Control.KEGG.results.all.xls
    │
    └── tables/
        ├── Case_vs_Control.gene.deg.for_kogo.table.tsv
        ├── Case_vs_Control.gene.deg.for_kogo.volcano.pdf
        ├── Case_vs_Control.gene.deg.for_kogo.volcano.png
        ├── Case_vs_Control.gene.deg.results.tsv
        ├── Case_vs_Control.isoform.dtg.for_kogo.table.tsv
        ├── Case_vs_Control.isoform.dtg.for_kogo.volcano.pdf
        ├── Case_vs_Control.isoform.dtg.for_kogo.volcano.png
        ├── Case_vs_Control.isoform.dtg.results.tsv
        ├── Case_vs_Control.sdGenes.deg.for_kogo.manha.pdf
        ├── Case_vs_Control.sdGenes.deg.for_kogo.manha.png
        ├── Case_vs_Control.sdGenes.deg.for_kogo.table.tsv
        ├── Case_vs_Control.sdGenes.results.tsv
```

### Description

* **kogo/**: Contains all enrichment input and output related to KOGO (GO/KEGG) analysis.

  * `*.genelist.tsv`: Gene list used for enrichment.
  * `*.table.tsv`: Formatted input tables.
  * `*.kogo.barplot.*`: Bar plots of enrichment results (PDF and PNG).
  * `*.kogo.results.tsv`: Raw enrichment result tables.
  * `tables/`: Final GO/KEGG enrichment outputs.
* **tables/**: Differential expression and splicing results.

  * `*.results.tsv`: Full statistical test results.
  * `*.volcano.*`: Volcano plots for gene/isoform level results.
  * `*.manha.*`: Mahalanobis plots for SDG analysis.
  * `*.for_kogo.table.tsv`: Processed input tables for downstream enrichment.

## Contact

Maintained by \[Chenqing Zheng]. Contributions, issues, and pull requests are welcome via the GitHub repository.
