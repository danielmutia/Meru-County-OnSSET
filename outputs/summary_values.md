# Summary values

| Quantity | Without PUE | With PUE |
|---|---|---|
| PUE + community-service demand (GWh/yr) | - | 10.11 |
| Demand of settlements connected by 2030, incl. farm irrigation (MWh/yr) | 31,759 | 41,867 |
| Demand of all settlements, 2030 (MWh/yr) | 166,155 | 176,263 |
| New capacity, rural (kW) | 15,869 | 21,813 |
| New capacity, urban (kW) | 21,400 | 21,471 |
| New capacity, total (kW) | 37,269 | 43,284 |
| Grid capacity (kW) | 32,468 | 35,495 |
| SA PV capacity (kW) | 4,800 | 4,828 |
| Mini-grids (count) | 0 | 46 |
| Mini-grid capacity (kW) | 0 | 594 |
| Farm solar irrigation capacity (kWp) | 0 | 2,366 |
| Farm solar irrigation investment (M USD) | 0.0 | 3.55 |
| Total investment 2020-2030 (M USD) | 306.29 | 321.23 |
| Rural investment 2020-2030 (M USD) | 241.71 | 256.54 |
| Rural grid, USD/kW | 20,849 | 16,988 |
| Rural off-grid, USD/kW | 2,280 | 2,217 |
| All technologies, USD/kW | 8,218 | 7,421 |

## PUE demand by solution

| Solution | GWh/yr | Share | Settlements | Mini-grid settlements with this load |
|---|---|---|---|---|
| Health | 0.50 | 4.9% | 149 | 10 |
| Water | 5.86 | 58.0% | 378 | 36 |
| Crop farming | 3.55 | 35.1% | 751 | 1 |
| Poultry | 0.20 | 2.0% | 4 | 0 |

## Table C.6: annual demand by sub-county (kWh/yr)

| Sub-county | Health | Crop farming | Water | Poultry | Total |
|---|---|---|---|---|---|
| Buuri | 40,068 | 306,000 | 780,583 | 50,000 | 1,176,651 |
| Igembe Central | 33,390 | 0 | 1,272,502 | 50,000 | 1,355,892 |
| Igembe North | 56,763 | 0 | 1,736,545 | 0 | 1,793,308 |
| Igembe South | 43,407 | 0 | 889,077 | 0 | 932,484 |
| Imenti Central | 63,441 | 1,037,400 | 15,340 | 0 | 1,116,182 |
| Imenti North | 40,068 | 997,500 | 23,522 | 50,000 | 1,111,090 |
| Imenti South | 100,170 | 532,800 | 0 | 0 | 632,970 |
| Tigania East | 53,424 | 358,800 | 1,062,731 | 0 | 1,474,955 |
| Tigania West | 66,780 | 316,200 | 81,874 | 50,000 | 514,854 |
| Total | 497,511 | 3,548,700 | 5,862,175 | 200,000 | 10,108,386 |

## All values

```json
{
 "pue_demand_GWh": {
  "Health": 0.5,
  "Water": 5.86,
  "Crop farming": 3.55,
  "Poultry": 0.2,
  "Total": 10.11
 },
 "pue_demand_share_pct": {
  "Health": 4.9,
  "Water": 58.0,
  "Crop farming": 35.1,
  "Poultry": 2.0
 },
 "pue_sites": {
  "Health": 149,
  "Water": 378,
  "Crop farming": 751,
  "Poultry": 4
 },
 "demand_new_connections_2030_MWh": {
  "noPUE": 31759,
  "PUE": 41867,
  "increase_pct": 31.8
 },
 "demand_all_settlements_2030_MWh": {
  "noPUE": 166155,
  "PUE": 176263,
  "increase_pct": 6.1
 },
 "new_capacity_kW": {
  "noPUE": {
   "Rural": 15869,
   "Urban": 21400,
   "Total": 37269
  },
  "PUE": {
   "Rural": 21813,
   "Urban": 21471,
   "Total": 43284
  }
 },
 "technology_mix": {
  "noPUE": {
   "Grid": {
    "capacity_kW": 32468,
    "investment_MUSD": 295.34,
    "population_2030": 1459054
   },
   "Stand-alone PV": {
    "capacity_kW": 4800,
    "investment_MUSD": 10.94,
    "population_2030": 322640
   },
   "Mini-grid (PV + battery)": {
    "capacity_kW": 0,
    "investment_MUSD": 0.0,
    "population_2030": 0,
    "count": 0
   },
   "Solar irrigation (farm-level)": {
    "capacity_kW": 0,
    "investment_MUSD": 0.0
   }
  },
  "PUE": {
   "Grid": {
    "capacity_kW": 35495,
    "investment_MUSD": 304.01,
    "population_2030": 1465136
   },
   "Stand-alone PV": {
    "capacity_kW": 4828,
    "investment_MUSD": 10.87,
    "population_2030": 314615
   },
   "Mini-grid (PV + battery)": {
    "capacity_kW": 594,
    "investment_MUSD": 2.8,
    "population_2030": 1942,
    "count": 46,
    "size_kW_min_median_max": [
     3.4,
     11.8,
     29.3
    ]
   },
   "Solar irrigation (farm-level)": {
    "capacity_kW": 2366,
    "investment_MUSD": 3.55
   }
  }
 },
 "minigrid_settlements_with_solution": {
  "Health": 10,
  "Water": 36,
  "Crop farming": 1,
  "Poultry": 0
 },
 "minigrid_pue_share_of_demand_pct_median": 94.0,
 "investment": {
  "noPUE": {
   "total_investment_MUSD": 306.29,
   "all_USD_per_kW": 8218,
   "rural_grid_investment_MUSD": 230.76,
   "rural_grid_capacity_kW": 11068,
   "rural_grid_USD_per_kW": 20849,
   "all_grid_investment_MUSD": 295.34,
   "all_grid_capacity_kW": 32468,
   "all_grid_USD_per_kW": 9096,
   "rural_offgrid_investment_MUSD": 10.94,
   "rural_offgrid_capacity_kW": 4800,
   "rural_offgrid_USD_per_kW": 2280,
   "all_offgrid_investment_MUSD": 10.94,
   "all_offgrid_capacity_kW": 4800,
   "all_offgrid_USD_per_kW": 2280,
   "rural_investment_MUSD": 241.71
  },
  "PUE": {
   "total_investment_MUSD": 321.23,
   "all_USD_per_kW": 7421,
   "rural_grid_investment_MUSD": 239.43,
   "rural_grid_capacity_kW": 14094,
   "rural_grid_USD_per_kW": 16988,
   "all_grid_investment_MUSD": 304.01,
   "all_grid_capacity_kW": 35495,
   "all_grid_USD_per_kW": 8565,
   "rural_offgrid_investment_MUSD": 17.11,
   "rural_offgrid_capacity_kW": 7719,
   "rural_offgrid_USD_per_kW": 2217,
   "all_offgrid_investment_MUSD": 17.22,
   "all_offgrid_capacity_kW": 7789,
   "all_offgrid_USD_per_kW": 2211,
   "rural_investment_MUSD": 256.54
  },
  "change": {
   "total_investment_MUSD": 14.94,
   "rural_investment_MUSD": 14.83,
   "all_USD_per_kW_pct": -9.7,
   "rural_grid_USD_per_kW_pct": -18.5,
   "rural_offgrid_USD_per_kW_pct": -2.8,
   "all_grid_USD_per_kW_pct": -5.8,
   "all_offgrid_USD_per_kW_pct": -3.0
  }
 },
 "settlement_periods_with_missing_investment": {
  "noPUE": 0,
  "PUE": 0
 },
 "minigrid_renewable_share_min": 1.0
}
```

## Sensitivity: PV mini-grid cost (enhanced-demand scenario)

| Mini-grid cost case | Demand increase, new connections (%) | Mini-grids | Mini-grid capacity (kW) | Grid capacity (kW) | Total investment (M USD) | Change in investment (M USD) | Rural grid USD/kW | Rural off-grid USD/kW | All technologies USD/kW |
|---|---|---|---|---|---|---|---|---|---|
| Low (2,500) | 31.8 | 111 | 1,688 | 34,927 | 319.49 | 13.2 | 17,390 | 2,224 | 7,293 |
| Central (4,000) | 31.8 | 46 | 594 | 35,495 | 321.23 | 14.94 | 16,988 | 2,217 | 7,421 |
| High (5,200) | 31.8 | 24 | 287 | 35,654 | 321.88 | 15.59 | 16,922 | 2,160 | 7,462 |

## Sensitivity: PUE uptake (central mini-grid cost)

| PUE realised | Demand increase, new connections (%) | Mini-grids | Mini-grid capacity (kW) | Grid capacity (kW) | Total investment (M USD) | Change in investment (M USD) | Rural grid USD/kW | Rural off-grid USD/kW | All technologies USD/kW |
|---|---|---|---|---|---|---|---|---|---|
| 100% (as planned) | 31.8 | 46 | 594 | 35,495 | 321.23 | 14.94 | 16,988 | 2,217 | 7,421 |
| 50% (mini-grid USD 4,000/kW) | 15.9 | 93 | 716 | 33,734 | 315.15 | 8.86 | 18,986 | 2,427 | 7,780 |

## Mini-grid viability in off-grid settlements with PUE

Settlements not grid-connected in 2020 that have PUE in the with-PUE scenario, by minimum number of households (2030); the same settlements are compared without and with PUE. Tariff = small-commercial, USD 0.158/kWh.

| Run | Demand | Min. households | Settlements | Households | Median MG LCOE | Median grid-extension LCOE | MG cheaper than grid extension | Least-cost mini-grids | At or below tariff | Median tariff gap |
|---|---|---|---|---|---|---|---|---|---|---|
| Low (2,500) | With PUE | 50 | 27 | 4,450 | 0.45 | 0.8 | 27 | 8 | 0 | 0.3 |
| Low (2,500) | With PUE | 75 | 16 | 3,796 | 0.46 | 1.12 | 16 | 0 | 0 | 0.31 |
| Low (2,500) | With PUE | 100 | 12 | 3,456 | 0.48 | 1.24 | 12 | 0 | 0 | 0.32 |
| Central (4,000) | Without PUE | 50 | 27 | 4,450 | 0.81 | 1.72 | 27 | 0 | 0 | 0.65 |
| Central (4,000) | With PUE | 50 | 27 | 4,450 | 0.66 | 0.8 | 21 | 3 | 0 | 0.5 |
| Central (4,000) | Without PUE | 75 | 16 | 3,796 | 0.75 | 1.63 | 16 | 0 | 0 | 0.59 |
| Central (4,000) | With PUE | 75 | 16 | 3,796 | 0.68 | 1.12 | 14 | 0 | 0 | 0.53 |
| Central (4,000) | Without PUE | 100 | 12 | 3,456 | 0.74 | 1.6 | 12 | 0 | 0 | 0.59 |
| Central (4,000) | With PUE | 100 | 12 | 3,456 | 0.69 | 1.24 | 12 | 0 | 0 | 0.53 |
| High (5,200) | With PUE | 50 | 27 | 4,450 | 0.81 | 0.8 | 15 | 0 | 0 | 0.65 |
| High (5,200) | With PUE | 75 | 16 | 3,796 | 0.86 | 1.12 | 12 | 0 | 0 | 0.7 |
| High (5,200) | With PUE | 100 | 12 | 3,456 | 0.86 | 1.24 | 12 | 0 | 0 | 0.7 |
| PUE 50% (4,000) | With PUE | 50 | 27 | 4,450 | 0.72 | 1.08 | 26 | 0 | 0 | 0.56 |
| PUE 50% (4,000) | With PUE | 75 | 16 | 3,796 | 0.72 | 1.32 | 16 | 0 | 0 | 0.56 |
| PUE 50% (4,000) | With PUE | 100 | 12 | 3,456 | 0.71 | 1.38 | 12 | 0 | 0 | 0.56 |

## One-at-a-time capital-cost sensitivity (+/-20%, enhanced-demand scenario)

Cumulative investment to 2030 including farm solar irrigation; central: 46 mini-grids (594 kW), USD 321.23M (2025: 243.89M, 2030: 77.34M). Switches = settlements whose 2030 technology differs from the central run.

| Parameter | Central value | Unit | Mini-grids at 80% | Mini-grids at 120% | Mini-grid kW at 80% | Mini-grid kW at 120% | Switches at 80% | Switches at 120% | 80% (M USD) | 120% (M USD) | Swing (% of central) | 80%, 2025 (M USD) | 120%, 2025 (M USD) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Minigrid PV with battery | 4,000 | USD/kW | 74 | 29 | 1,056 | 367 | 28 grid to MG | 17 MG to grid | 320.51 | 321.75 | 0.4 | 243.89 | 243.89 |
| Medium-voltage line | 30,000 | USD/km | 30 | 55 | 377 | 723 | 16 MG to grid | 9 grid to MG | 320.69 | 321.76 | 0.3 | 243.89 | 243.89 |
| Grid connection | 1,300 | USD/household | 39 | 57 | 482 | 802 | 7 MG to grid | 11 grid to MG | 267.56 | 374.86 | 33.4 | 198.95 | 288.82 |
| Minigrid connection | 140 | USD/household | 46 | 45 | 594 | 572 |  | 1 MG to grid | 321.21 | 321.24 | 0.0 | 243.89 | 243.89 |
| Grid generation capacity | 1,363 | USD/kW | 46 | 46 | 594 | 594 |  |  | 315.42 | 327.03 | 3.6 | 240.44 | 247.33 |
| Stand-alone PV, 51–100 W | 1,900 | USD/kW | 46 | 46 | 594 | 594 |  |  | 319.68 | 322.77 | 1.0 | 243.89 | 243.89 |
| Transformers and substations | 3,800–338,800 | USD/unit | 46 | 46 | 594 | 594 |  |  | 320.42 | 322.04 | 0.5 | 243.49 | 244.28 |
| Farm solar irrigation | 1,500 | USD/kWp | 46 | 46 | 594 | 594 |  |  | 320.52 | 321.94 | 0.4 | 243.89 | 243.89 |
| Stand-alone PV, 21–50 W | 4,800 | USD/kW | 46 | 46 | 594 | 594 |  |  | 320.65 | 321.81 | 0.4 | 243.89 | 243.89 |
| Stand-alone PV, 101–200 W | 1,500 | USD/kW | 46 | 46 | 594 | 594 |  |  | 321.18 | 321.27 | 0.0 | 243.89 | 243.89 |
| Low-voltage line | 13,700 | USD/km | 46 | 46 | 594 | 594 |  |  | 321.23 | 321.23 | 0.0 | 243.89 | 243.89 |
| High-voltage line | 90,000 | USD/km | 46 | 46 | 594 | 594 |  |  | 321.23 | 321.23 | 0.0 | 243.89 | 243.89 |
| Stand-alone PV, up to 20 W | 9,000 | USD/kW | 46 | 46 | 594 | 594 |  |  | 321.23 | 321.23 | 0.0 | 243.89 | 243.89 |
| Minigrid diesel* | 721 | USD/kW | 46 | 46 | 594 | 594 |  |  | 321.23 | 321.23 | 0.0 | 243.89 | 243.89 |
| Minigrid wind* | 3,902 | USD/kW | 46 | 46 | 594 | 594 |  |  | 321.23 | 321.23 | 0.0 | 243.89 | 243.89 |
| Stand-alone diesel* | 938 | USD/kW | 46 | 46 | 594 | 594 |  |  | 321.23 | 321.23 | 0.0 | 243.89 | 243.89 |
