# Replication Code — Bernstein (2015)

**"Does Going Public Affect Innovation?"**  
*Journal of Finance* 70 (4) 1365–1403

---

## Overview

This repository replicates and extends Bernstein (2015), which uses an IV strategy to estimate the causal effect of IPO completion on post-listing innovation quality. The instrument is the 2-month cumulative CRSP value-weighted return (VWRETD) in the two months following the S-1 filing date, which predicts whether firms complete or withdraw their offering.

The pipeline runs in three stages:

1. **Import** — R scripts download raw data from WRDS via PostgreSQL
2. **Cleaning** — Stata script constructs the analysis dataset
3. **Analysis** — Stata scripts produce all tables and figures

R is used solely for data access and import. All sample construction, variable construction, and statistical analysis are performed in Stata (Steps 5–7). The KPSS patent dataset (`KPSS_2024.csv` and `Match_patent_permco_permno_2024.csv`) was downloaded manually from the KPSS project website and requires no import script. Where noted in the code, AI tools assisted with output formatting and code efficiency; all analytical decisions, variable definitions, sample filters, and econometric specifications reflect the authors' own implementation.

---

## Pipeline

| Order | Script | Language | Stage | Key Output |
|------:|--------|----------|-------|------------|
| 1 | `utils/wrds_credentials.R` | R | Utility | WRDS connection helper |
| 2 | `config.do` | Stata | Utility | Sets `$BASEDIR` and all derived path globals |
| 3 | `data_import/import_crsp_msi.R` | R | Import | `data/raw/crsp_msi.csv`, `data/temp/msi_monthly.dta` |
| 4 | `data_import/import_sdc.R` | R | Import | `data/raw/sdc_ni.csv` |
| 5 | `data_import/import_crsp_auxiliaries.R` | R | Import | `data/raw/crsp_stocknames.csv` |
| 6 | `data_setup/clean_data.do` | Stata | Cleaning | `data/processed/regression_panel.dta`, `data/processed/plot_data.dta` |
| 7 | `analyses/replicate_Bernstein.do` | Stata | Analysis | `output/figure2.pdf`, `output/table2_{full,event}.tex`, `output/table6_{full,event}.tex`, `data/final/reg_final.dta` |
| 8 | `analyses/extend_Bernstein.do` | Stata | Analysis | `output/task2_{full,event}.tex`, `output/task3_exclusion.tex` |

---

## Script Descriptions

### Step 1 — `utils/wrds_credentials.R`

Reads WRDS username and password from the `.Renviron` file and returns them as a named list. Called by all import scripts; credentials are never hard-coded.

### Step 2 — `config.do`

Defines the single base-path global and all derived directory globals used by every Stata script. To redirect the pipeline to a new machine, edit only the `BASEDIR` line in this file. Each Stata script sources `config.do` automatically at startup, so no manual path edits are needed in the analysis scripts themselves.

### Step 3 — `data_import/import_crsp_msi.R`

Connects to the WRDS PostgreSQL server via `RPostgres` and downloads the CRSP Monthly Stock Index file (`crsp.msi`), retaining the value-weighted return including distributions (`vwretd`) for the full sample period. Saves a raw CSV to `data/raw/crsp_msi.csv` and a Stata-ready `.dta` file to `data/temp/msi_monthly.dta` for use in the analysis scripts.

### Step 4 — `data_import/import_sdc.R`

Downloads SDC Platinum new-issues data (`tr_sdc_ni`) from WRDS, covering all U.S. IPO filings. Saves raw records to `data/raw/sdc_ni.csv`. The cleaning script (Step 6) applies all sample filters.

### Step 5 — `data_import/import_crsp_auxiliaries.R`

Downloads the CRSP historical stock-name file (`crsp.stocknames`) used to match SDC deals to CRSP permnos via 6-digit CUSIP. Saves to `data/raw/crsp_stocknames.csv`.

### Step 6 — `data_setup/clean_data.do`

Constructs the analysis dataset from the raw imports and KPSS patent files. Key steps:

1. Apply SDC sample filters: filing-year window 1985–2003, U.S. Public or Withdrawn status, non-financial firms (SIC 6000–6999 dropped), common equity only, standard exchange listings, non-missing planned shares, first filing per CUSIP, non-negative book-building window
2. Match completed firms to CRSP permnos via CUSIP and offer date; match withdrawn-later-IPO firms via CUSIP and withdrawal date (requiring a subsequent listing within 10 years)
3. Merge KPSS patent data by permno; compute pre-filing patent counts, real patent values (`pre_xi_real`), and average citation-scaled quality (`pre_avg_sc`) over application years `filing_year − 3` to `filing_year − 1`
4. Compute post-event patent outcomes over application years `ref_year + 1` to `ref_year + 5`
5. Merge CRSP VWRETD returns; construct the 2-month filing-date instrument (`ret2m_vw`), 3-month pre-filing control (`ret3m_pre_vw`), Pioneer and Early Follower indicators

**Inputs:** `data/raw/sdc_ni.csv`, `data/raw/crsp_stocknames.csv`, `data/raw/crsp_msi.csv`, `KPSS_2024.csv`, `Match_patent_permco_permno_2024.csv`  
**Outputs:** `data/processed/regression_panel.dta`, `data/processed/plot_data.dta`

### Step 7 — `analyses/replicate_Bernstein.do`

Replicates Figure 2 and Tables II and VI of Bernstein (2015) in two sample cuts: the patent-active event-window sample (`pre_n_patents + post_n_patents > 0`) and the full permno-matched sample.

- **Figure 2**: plots the monthly 2-month cumulative VWRETD alongside the IPO withdrawal rate, 1985–2004
- **Table II (first stage)**: eight-column LPM of IPO completion on three instrument variants (2-month VW return, full book-building return, binary no-drop indicator), with and without controls, full sample and pre-2000 subsample
- **Table VI (second stage)**: OLS, reduced-form, and 2SLS regressions of post-IPO average citation-scaled quality (`post_avg_sc`) on IPO completion, instrumenting with the 2-month VWRETD

Also saves `data/final/reg_final.dta`, the fully merged and labeled regression dataset used by Step 8.

**Inputs:** `data/processed/regression_panel.dta`, `data/processed/plot_data.dta`  
**Outputs:** `output/figure2.pdf`, `output/table2_{full,event}.tex`, `output/table6_{full,event}.tex`, `data/final/reg_final.dta`

### Step 8 — `analyses/extend_Bernstein.do`

Extends the replication with two original tasks.

**Task 2 — Value of Innovation**: adds a second outcome, `ln(1 + post_xi_real)` (log KPSS real stock-market-imputed patent value), alongside the citation-quality measure from Table VI. Estimates OLS, reduced-form, and 2SLS for both outcomes in the event-window and full permno-matched samples. Reports diagnostic tests for pre-period covariate balance across treatment and control groups.

**Task 3 — Exclusion Restriction Timing Placebo**: tests the exclusion restriction following Bernstein Table IV. Constructs two placebo return measures — `ret2m_pre12` (months M−12, M−11) and `ret2m_post12` (months M+13, M+14) — and regresses `post_avg_sc` on each timing variant separately and jointly with the filing-date instrument. Supports the exclusion restriction if predictive power concentrates in the filing-date window and decays at off-window dates.

**Inputs:** `data/final/reg_final.dta`, `data/temp/msi_monthly.dta`  
**Outputs:** `output/task2_{full,event}.tex`, `output/task3_exclusion.tex`

---

## Directory Structure

```
code/
├── config.do
├── utils/
│   └── wrds_credentials.R
├── data_import/
│   ├── import_crsp_msi.R
│   ├── import_sdc.R
│   └── import_crsp_auxiliaries.R
├── data_setup/
│   └── clean_data.do
├── analyses/
│   ├── replicate_Bernstein.do
│   └── extend_Bernstein.do
└── README.md  (this file, located in write-up/)

data/
├── raw/          (crsp_msi.csv, sdc_ni.csv, crsp_stocknames.csv; KPSS files)
├── processed/    (regression_panel.dta, plot_data.dta)
├── final/        (reg_final.dta)
└── temp/         (msi_monthly.dta)

output/           (all .tex tables and .pdf figures)

write-up/         (rep3.tex, refs.bib, README.md)
```

---

## Requirements

**R packages:** `RPostgres`, `dplyr`, `data.table`, `haven`

**Stata packages:** `reghdfe`, `ivreghdfe`, `ftools`, `estout`

Install Stata packages with:
```stata
ssc install reghdfe
ssc install ivreghdfe
ssc install ftools
ssc install estout
```

---

## Reference

Bernstein, S. (2015). Does going public affect innovation? *Journal of Finance*, 70(4), 1365–1403.
