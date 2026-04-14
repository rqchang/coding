# Replication Code — Giroud & Mueller (2010)

**"Does Corporate Governance Matter in Competitive Industries?"**  
*Journal of Financial Economics* 95 (3) 312–331

---

## Overview

This repository replicates and extends Table 3 of Giroud & Mueller (2010), which examines the heterogeneous effect of business combination (BC) laws on firm profitability (ROA) across industries with different competitive intensity (HHI).

The pipeline runs in three stages:

1. **Import** — R scripts download raw data from WRDS via PostgreSQL
2. **Cleaning** — R and Stata scripts construct the analysis panel
3. **Analysis** — Stata scripts produce all tables and figures

R is used solely for data access and import. All sample construction, variable construction, and statistical analysis are performed in Stata (Steps 6–8). Where noted in the code, AI tools assisted with output formatting and code efficiency; all analytical decisions, variable definitions, sample filters, and econometric specifications reflect the authors' own implementation of Giroud & Mueller (2010).

---

## Pipeline

| Order | Script | Language | Stage | Key Output |
|------:|--------|----------|-------|------------|
| 1 | `utils/wrds_credentials.R` | R | Utility | WRDS credential helper |
| 2 | `utils/f_compustat_variables_calculations.R` | R | Utility | Variable calculation functions |
| 3 | `data_import/import_compustat.R` | R | Import | `compustat_funda.csv`, `compustat_names.csv`, `compustat_histnames.csv` |
| 4 | `data_import/import_crsp_auxiliaries.R` | R | Import | `crsp_ccmxpf_lnkhist.csv`, `crsp_stocknames.csv` |
| 5 | `data_setup/clean_compustat_annual.R` | R | Cleaning | `compustat_annual.csv` |
| 6 | `data_setup/clean_data.do` | Stata | Cleaning | `gm2010_panel.dta` |
| 7 | `analyses/replicate_gm_table3.do` | Stata | Analysis | `Table3_*_panelA.tex`, `Table3_*_panelB.tex`, `parallel_trends_{all,low,high}.pdf` |
| 8 | `analyses/extend_gm_table3.do` | Stata | Analysis | `Table3ext_stacked_panel{A,B}.tex`, `Table3ext_cs_panelA.tex`, `Table3ext_sa_panelA.tex`, `*_event_{all,low,high}.pdf` |

---

## Script Descriptions

### Step 1 — `utils/wrds_credentials.R`

Reads WRDS username and password from the `.Renviron` file and returns them as a named list. Called by all import scripts; credentials are never hard-coded.

### Step 2 — `utils/f_compustat_variables_calculations.R`

Defines helper functions for computing accounting variables (ROA, leverage, book equity, etc.) from Compustat line items. Sourced by `clean_compustat_annual.R`.

### Step 3 — `data_import/import_compustat.R`

Connects to the WRDS PostgreSQL server via `RPostgres` and downloads Compustat Fundamentals Annual (`comp.funda`), firm names (`comp.names`), and historical name/state-of-incorporation records (`comp.names_hist`). Saves raw CSVs to `data/raw/compustat/`.

### Step 4 — `data_import/import_crsp_auxiliaries.R`

Downloads the CRSP–Compustat link table (`crsp.ccmxpf_lnkhist`) and CRSP stock-name history (`crsp.stocknames`) used to identify state of incorporation. Saves raw CSVs to `data/raw/crsp/`.

### Step 5 — `data_setup/clean_compustat_annual.R`

Merges Compustat fundamentals with the CRSP link and computes firm-level accounting variables. Outputs a cleaned, firm-year panel (`compustat_annual.csv`) ready for Stata.

### Step 6 — `data_setup/clean_data.do`

Constructs the final analysis panel `gm2010_panel.dta` from `compustat_annual.csv` and `compustat_histnames.csv`. Key steps:

1. Extract state-of-incorporation identifiers from the historical names file
2. Compute HHI as the sum of squared revenue market shares within 3-digit SIC × year cells, using all Compustat firms before any sample filters
3. Construct ROA = `oibdp / at`, Size = log(total assets), Age = log(1 + years in Compustat)
4. Merge BC law adoption years (30 states, 1985–1991) by state of incorporation
5. Encode firm, year, state, and industry fixed-effect identifiers

The panel covers 1976–2005.

**Inputs:** `data/processed/compustat_annual.csv`, `data/raw/compustat_histnames.csv`  
**Outputs:** `data/processed/gm_states.dta`, `data/processed/gm_hhi.dta`, `data/final/gm2010_panel.dta`

### Step 7 — `analyses/replicate_gm_table3.do`

Replicates Table 3 of Giroud & Mueller (2010) across four sample periods: the original 1976–1995 window and three robustness windows (1980–1995, 1976–1990, 1976–2005). For each period it estimates the baseline DDD specification for:

- **Panel A** — average BC effect, continuous BC×HHI interaction, and HHI-tercile interactions
- **Panel B** — reverse-causality test with four time-relative BC dummies (t−1, t0, t+1, t+2+)

Also produces parallel-trends event-study figures for the all-firms, low-HHI, and high-HHI subsamples, including a never-treated control group reference line.

**Inputs:** `data/final/gm2010_panel.dta`  
**Outputs:** `output/Table3_*_panel{A,B}.tex`, `output/parallel_trends_{all,low,high}.pdf`

### Step 8 — `analyses/extend_gm_table3.do`

Extends Table 3 using three modern DiD estimators for staggered treatment adoption, all on the 1976–1995 baseline sample.

**Task 3A — Stacked regression** (Gormley & Matsa 2011): Seven cohort sub-experiments (one per BC adoption year 1985–1991), stacked with never-treated controls in a ±4-year event window, estimated with cohort×firm and cohort×year fixed effects.

**Task 3B — Callaway & Sant'Anna (2021)**: Estimated via `csdid`, reporting five aggregations of the cohort-time ATTs — simple weighted average, group-specific effects, event study, calendar time, and balanced event study — for the all-firms, low-HHI, and high-HHI subsamples.

**Task 3C — Sun & Abraham (2021)**: Interaction-weighted estimator via `eventstudyinteract`, with the average post-period IW-weighted ATT as the summary statistic.

All three tasks output Panel A LaTeX tables and event-study PDF plots.

**Inputs:** `data/final/gm2010_panel.dta`  
**Outputs:** `output/Table3ext_stacked_panel{A,B}.tex`, `output/Table3ext_cs_panelA.tex`, `output/Table3ext_sa_panelA.tex`, `output/*_event_{all,low,high}.pdf`

---

## Directory Structure

```
code/
├── utils/
│   ├── wrds_credentials.R
│   └── f_compustat_variables_calculations.R
├── data_import/
│   ├── import_compustat.R
│   └── import_crsp_auxiliaries.R
├── data_setup/
│   ├── clean_compustat_annual.R
│   └── clean_data.do
├── analyses/
│   ├── replicate_gm_table3.do
│   └── extend_gm_table3.do
└── README.md

data/
├── raw/
│   ├── compustat/
│   └── crsp/
├── processed/
├── final/
└── temp/

output/
```

---

## Requirements

**R packages:** `data.table`, `RPostgres`, `dplyr`, `haven`

**Stata packages:** `reghdfe`, `ftools`, `csdid`, `drdid`, `eventstudyinteract`, `avar`

Install Stata packages with:
```stata
ssc install reghdfe
ssc install ftools
ssc install csdid
ssc install drdid
net install eventstudyinteract, from("https://raw.githubusercontent.com/lsun20/EventStudyInteract/master/")
ssc install avar
```

---

## Reference

Giroud, X., & H. M. Mueller (2010). Does corporate governance matter in competitive industries? *Journal of Financial Economics*, 95(3), 312–331.
