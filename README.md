# Integrating development-driven demand into energy planning: Meru County, Kenya

Code and data for the least-cost electrification analysis of Meru County, Kenya, to 2030, with and without
productive-use (PUE) and community-service demand. The model is
[OnSSET](https://github.com/OnSSET/onsset) (KTH dESA), run through an adapted version of the GEP Generator notebook.

## Contents

| File | Description |
|---|---|
| `1_run_model.ipynb` | Runs the OnSSET model for one scenario |
| `2_run_scenarios.ipynb` | Runs every scenario, each in a fresh kernel |
| `3_figures_and_results.ipynb` | Draws the figures and writes the tables and summary values |
| `analysis.py` | Functions used by `3_figures_and_results.ipynb` |
| `onsset.py`, `hybrids_pv.py`, `hybrids_wind.py` | OnSSET model code |
| `data/onsset_no_pue.csv` | Settlement data, household demand only |
| `data/onsset_with_pue.csv` | Settlement data, household plus PUE and community-service demand |
| `data/ke_solar.csv`, `data/me_wind.csv` | Hourly solar and wind profiles |
| `data/crop_farms.csv` | Crop-farm locations and annual demand (900 or 1,500 kWh/yr each) |
| `data/meru_subcounties.geojson` | Meru sub-county boundaries |
| `results/` | Model results for every scenario (settlement results compressed as `.csv.gz`) |
| `outputs/` | Figures (PNG and PDF), tables and summary values |

## How to run

```bash
python -m pip install -r requirements.txt
jupyter lab
```

The model results are included, so the figures and tables can be reproduced without running the model: open
`3_figures_and_results.ipynb` and use Run All (about a minute).

To rerun the model:

1. `2_run_scenarios.ipynb` runs all scenarios (about 2–4 minutes each; the 30 capital-cost sensitivity runs take about an
   hour). To run a single scenario, open `1_run_model.ipynb`, set the scenario name in the scenario cell and use Run All.
2. `3_figures_and_results.ipynb` reads `results/` and writes figures (PNG and PDF), tables and summary values to `outputs/`.

Each run writes to `results/<scenario>/`: `*_Results.csv` (one row per settlement), `*_Summaries.csv` and
`*_Variables.csv` (every setting used). `analysis.py` reads either the `.csv` or the compressed `.csv.gz` results.

## Scenarios

| Scenario | Description |
|---|---|
| `Scenario1_baseline_noPUE` | Household demand only |
| `Scenario2_enhanced_PUE` | Household plus PUE and community-service demand |
| `Sens_MGcostLow_PUE`, `Sens_MGcostHigh_PUE` | Scenario 2 with a mini-grid cost of USD 2,500/kW and USD 5,200/kW |
| `Sens_PUE50` | Scenario 2 with PUE demand at 50% of planned values |
| `OAT_<cost>_80`, `OAT_<cost>_120` | Scenario 2 with one capital cost at 80% or 120% of its central value |

## Main settings

| Setting | Value |
|---|---|
| Period | 2020–2030 (70% access by 2025, universal access by 2030) |
| Demand targets | Rural Tier 2, urban Tier 4 |
| Grid and transmission costs | Kenya Power and Lighting Company (KPLC) |
| Stand-alone PV | USD 9,000 / 4,800 / 1,900 / 1,500 per kW for ≤20 W / 21–50 W / 51–100 W / 101–200 W per household; larger systems excluded |
| Mini-grids | Solar PV with battery storage, USD 4,000/kW; USD 140 per connection |
| PUE | Health, water and poultry demand added to the settlement load in 2030; crop farming costed separately as farm-level solar irrigation (USD 1,500/kWp) |
| Excluded technologies | Diesel, wind and hybrid mini-grids |

PUE columns in the input files keep the OnSSET template names: `HealthDemand` = health, `EducationDemand` = crop farming,
`CommercialDemand` = water, `AgriDemand` = poultry.

## Licence

MIT (see `LICENSE`). The OnSSET model code is adapted from [OnSSET](https://github.com/OnSSET/onsset) (KTH dESA, MIT).
