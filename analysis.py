"""Figures, tables and summary values from the model runs in results/.

Used by 3_figures_and_results.ipynb. Each fig_* function saves a figure to the output folder as PNG (300 dpi) and PDF;
write_tables() writes the tables and summary values.

Definitions:
- PUE input columns: HealthDemand = health, EducationDemand = crop farming (solar irrigation),
  CommercialDemand = water (boreholes, purification), AgriDemand = poultry. The column names follow the OnSSET
  template; the values are the solution demands from the Energy Demand Model.
- New capacity / investment = sum of the two model periods (2020-2025 and 2025-2030). Each period's
  NewCapacity/InvestmentCost is the increment for that period, so the sum is the 2020-2030 total.
- Technology in a period = FinalElecCode for that year. Grid = codes 1, 2. Off-grid = SA PV (3) + mini-grids (4-9).
  Mini-grids are PV mini-grids (code 5) at a single generation cost of USD 4,000/kW including battery storage.
- Rural / urban = IsUrban after calibration (0 = rural, 2 = urban).
- Demand = annual electricity demand of the settlements newly connected (EnergyPerSettlement), plus total 2030 demand of
  all settlements (TotalEnergyPerCell) for reference.
- Investment for settlements with InvestmentCost = NaN counts as 0, as in the model's own summary tables.
- Crop farming is taken out of the cluster load in the model (crop_farming_standalone) and added here as farm-level solar
  irrigation: capacity = demand / 1,500 kWh per kWp per year (1,500 kWh from 1 kWp; 900 kWh from 0.62 kWp),
  investment = capacity x the 101-200 W stand-alone PV price. It counts as rural off-grid, in 2030.
- Mini-grid viability: settlements not grid-connected in 2020 with PUE and at least 50 / 75 / 100 households in 2030.
  For the same settlements, without and with PUE: mini-grid LCOE (MG_PV2030), whether it is below the grid-extension LCOE
  (GridExtLCOE2030: direct MV extension from the nearest line), whether the least-cost run picks a mini-grid, and the gap
  to the small-commercial tariff (TARIFF).
"""
import json
import json
import os

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')

SCEN = {'noPUE': 'Scenario1_baseline_noPUE', 'PUE': 'Scenario2_enhanced_PUE'}
LABEL = {'noPUE': 'Without PUE', 'PUE': 'With PUE'}
YEARS = [2025, 2030]
GRID_CODES, SA_CODES, MG_CODES = [1, 2], [3], [4, 5, 6, 7, 8, 9]
SOLUTIONS = [  # (reporting column, solution name); CropFarmDemand is EducationDemand read from the input file
    ('HealthDemand', 'Health'),
    ('CommercialDemand', 'Water'),
    ('CropFarmDemand', 'Crop farming'),
    ('AgriDemand', 'Poultry'),
]
PUE_COLS = ['HealthDemand', 'EducationDemand', 'CommercialDemand', 'AgriDemand']  # PUE in the cluster load (model columns)
FARM_YIELD = 1500           # kWh per kWp per year of a farm solar irrigation system (EDM design)
TARIFF = 0.158              # USD/kWh, small-commercial electricity tariff in Meru (2026)
HH_MIN = [50, 75, 100]      # minimum households for a mini-grid site (KOSAP: 100; REREC sites from 75; 50 as a lower bound)

BLUE, ORANGE, AQUA, YELLOW = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'
TEXT, SUBTEXT, GRIDLINE, BOUNDARY = '#0b0b0b', '#52514e', '#e3e2dd', '#8a8985'
SCEN_COLOR = {'noPUE': BLUE, 'PUE': ORANGE}
SCEN_HATCH = {'noPUE': '', 'PUE': '//'}
TECH_STYLE = {  # name: (codes, colour, marker, size, zorder)
    'Grid': (GRID_CODES, BLUE, 'o', 3, 2),
    'Stand-alone PV': (SA_CODES, ORANGE, 'o', 3, 3),
    'Mini-grid (PV + battery)': (MG_CODES, AQUA, '*', 70, 4),
}

plt.rcParams.update({'font.size': 9, 'axes.titlesize': 10, 'axes.labelcolor': SUBTEXT,
                     'xtick.color': SUBTEXT, 'ytick.color': SUBTEXT, 'axes.edgecolor': SUBTEXT,
                     'hatch.color': 'white', 'hatch.linewidth': 0.8, 'savefig.dpi': 300})


def load(results_dir, scen=SCEN):
    d = {}
    for k, name in scen.items():
        df = pd.read_csv(results_file(results_dir, name), low_memory=False)
        df.attrs['missing_investment'] = int(sum(df['InvestmentCost%d' % y].isna().sum() for y in YEARS))
        add_crop_farming(df, os.path.join(results_dir, name, name + '_Variables.csv'))
        for y in YEARS:
            df['InvestmentCost%d' % y] = df['InvestmentCost%d' % y].fillna(0)
            df['NewCapacity%d' % y] = df['NewCapacity%d' % y].fillna(0)
        d[k] = df
    if {'noPUE', 'PUE'} <= set(d):
        assert (d['noPUE']['Pop2030'].values == d['PUE']['Pop2030'].values).all(), 'scenarios are not on the same settlements'
    return d


def add_crop_farming(df, variables_csv):
    """Add crop-farming demand (from the input file) and, if the run took it out of the cluster load, farm-level
    solar irrigation capacity and investment (2030)."""
    var = pd.read_csv(variables_csv).set_index('Variable')['Value']
    with_pue = df['HealthDemand'].sum() > 0
    crop = pd.Series(0.0, index=df.index)
    if with_pue:
        inp = pd.read_csv(os.path.join(DATA, 'onsset_with_pue.csv'), usecols=['id_left', 'EducationDemand'])
        assert (inp['id_left'].values == df['id_left'].values).all(), 'input and results rows differ'
        crop = inp['EducationDemand'].astype(float) * float(var.get('PUE scale', 1))
    df['CropFarmDemand'] = crop.values
    standalone = str(var.get('Crop farming standalone', 'False')) == 'True'
    df['FarmPVCapacity2030'] = crop.values / FARM_YIELD if standalone else 0.0
    df['FarmPVInvestment2030'] = df['FarmPVCapacity2030'] * float(var['sa_pv_capital_cost_4'])


def by_period(df, mask_fn, col):
    """Sum col over both periods, selecting each period's settlements with mask_fn(df, year)."""
    return sum(df.loc[mask_fn(df, y), col % y].sum() for y in YEARS)


def tech_mask(codes, rural_only=False):
    def f(df, y):
        m = df['FinalElecCode%d' % y].isin(codes)
        return m & (df['IsUrban'] == 0) if rural_only else m
    return f


def compute_values(d):
    v = {}
    p, n = d['PUE'], d['noPUE']

    # 3.1 demand profile
    pue = {name: p[col].sum() for col, name in SOLUTIONS}
    tot = sum(pue.values())
    v['pue_demand_GWh'] = {k: round(x / 1e6, 2) for k, x in pue.items()} | {'Total': round(tot / 1e6, 2)}
    v['pue_demand_share_pct'] = {k: round(100 * x / tot, 1) for k, x in pue.items()}
    v['pue_sites'] = {name: int((p[col] > 0).sum()) for col, name in SOLUTIONS}

    # 3.2 demand and capacity
    for k, df in d.items():
        farm_dem = df['CropFarmDemand'] * (df['FarmPVCapacity2030'] > 0)  # demand served outside the cluster load
        v.setdefault('demand_new_connections_2030_MWh', {})[k] = round((df['EnergyPerSettlement2030'].sum() + farm_dem.sum()) / 1e3)
        v.setdefault('demand_all_settlements_2030_MWh', {})[k] = round((df['TotalEnergyPerCell'].sum() + farm_dem.sum()) / 1e3)
        cap = {g: round(by_period(df, lambda x, y, u=u: x['IsUrban'] == u, 'NewCapacity%d')
                        + df.loc[df['IsUrban'] == u, 'FarmPVCapacity2030'].sum()) for g, u in [('Rural', 0), ('Urban', 2)]}
        cap['Total'] = cap['Rural'] + cap['Urban']
        v.setdefault('new_capacity_kW', {})[k] = cap
    for key in ['demand_new_connections_2030_MWh', 'demand_all_settlements_2030_MWh']:
        v[key]['increase_pct'] = round(100 * (v[key]['PUE'] / v[key]['noPUE'] - 1), 1)

    # 3.3 technology mix
    for k, df in d.items():
        mix = {}
        for tech, (codes, *_) in TECH_STYLE.items():
            mix[tech] = {'capacity_kW': round(by_period(df, tech_mask(codes), 'NewCapacity%d')),
                         'investment_MUSD': round(by_period(df, tech_mask(codes), 'InvestmentCost%d') / 1e6, 2),
                         'population_2030': round(df.loc[df['FinalElecCode2030'].isin(codes), 'Pop2030'].sum())}
        mix['Solar irrigation (farm-level)'] = {'capacity_kW': round(df['FarmPVCapacity2030'].sum()),
                                                'investment_MUSD': round(df['FarmPVInvestment2030'].sum() / 1e6, 2)}
        mg = df['FinalElecCode2030'].isin(MG_CODES)
        mix['Mini-grid (PV + battery)']['count'] = int(mg.sum())
        if mg.any():
            mix['Mini-grid (PV + battery)']['size_kW_min_median_max'] = [round(x, 1) for x in df.loc[mg, 'NewCapacity2030'].quantile([0, .5, 1])]
        v.setdefault('technology_mix', {})[k] = mix

    # mini-grid drivers (with PUE)
    mg = p['FinalElecCode2030'].isin(MG_CODES)
    v['minigrid_settlements_with_solution'] = {name: int((p.loc[mg, col] > 0).sum()) for col, name in SOLUTIONS}
    if mg.any():
        v['minigrid_pue_share_of_demand_pct_median'] = round(
            100 * (p.loc[mg, PUE_COLS].sum(axis=1) / p.loc[mg, 'EnergyPerSettlement2030']).median(), 1)

    # 3.4 investment and cost per kW
    for k, df in d.items():
        farm_i, farm_c = df['FarmPVInvestment2030'], df['FarmPVCapacity2030']
        is_rural = df['IsUrban'] == 0
        inv = sum(df['InvestmentCost%d' % y].sum() for y in YEARS) + farm_i.sum()
        cap = sum(df['NewCapacity%d' % y].sum() for y in YEARS) + farm_c.sum()
        r = {'total_investment_MUSD': round(inv / 1e6, 2), 'all_USD_per_kW': round(inv / cap)}
        for g, codes in [('grid', GRID_CODES), ('offgrid', SA_CODES + MG_CODES)]:
            for scope, rural in [('rural', True), ('all', False)]:
                i = by_period(df, tech_mask(codes, rural), 'InvestmentCost%d')
                c = by_period(df, tech_mask(codes, rural), 'NewCapacity%d')
                if g == 'offgrid':  # farm-level solar irrigation is off-grid
                    i += farm_i[df['IsUrban'] == 0].sum() if rural else farm_i.sum()
                    c += farm_c[df['IsUrban'] == 0].sum() if rural else farm_c.sum()
                r['%s_%s_investment_MUSD' % (scope, g)] = round(i / 1e6, 2)
                r['%s_%s_capacity_kW' % (scope, g)] = round(c)
                r['%s_%s_USD_per_kW' % (scope, g)] = round(i / c) if c else None
        r['rural_investment_MUSD'] = round((by_period(df, lambda x, y: x['IsUrban'] == 0, 'InvestmentCost%d')
                                            + farm_i[is_rural].sum()) / 1e6, 2)
        v.setdefault('investment', {})[k] = r
    i0, i1 = v['investment']['noPUE'], v['investment']['PUE']
    v['investment']['change'] = {
        'total_investment_MUSD': round(i1['total_investment_MUSD'] - i0['total_investment_MUSD'], 2),
        'rural_investment_MUSD': round(i1['rural_investment_MUSD'] - i0['rural_investment_MUSD'], 2),
        **{key + '_pct': round(100 * (i1[key] / i0[key] - 1), 1)
           for key in ['all_USD_per_kW', 'rural_grid_USD_per_kW', 'rural_offgrid_USD_per_kW', 'all_grid_USD_per_kW', 'all_offgrid_USD_per_kW']
           if i0[key] and i1[key]},
    }
    v['settlement_periods_with_missing_investment'] = {k: df.attrs['missing_investment'] for k, df in d.items()}
    if mg.any():
        v['minigrid_renewable_share_min'] = round(float(p.loc[mg, 'RenewableShare2030'].min()), 3)
    return v


SENSITIVITY = [  # (mini-grid cost case in USD/kW, run name)
    ('Low (2,500)', 'Sens_MGcostLow_PUE'),
    ('Central (4,000)', 'Scenario2_enhanced_PUE'),
    ('High (5,200)', 'Sens_MGcostHigh_PUE'),
]
PUE_UPTAKE = [('100% (as planned)', 'Scenario2_enhanced_PUE'), ('50% (mini-grid USD 4,000/kW)', 'Sens_PUE50')]
def results_file(results_dir, name):
    """Path of a run's results, as written by the model (.csv) or compressed (.csv.gz)."""
    path = os.path.join(results_dir, name, name + '_Results.csv')
    return path if os.path.exists(path) else path + '.gz'


def run_exists(results_dir, name):
    return os.path.exists(results_file(results_dir, name))


def headline(results_dir, name):
    """Key system-wide results of one enhanced-demand run against the baseline."""
    v = compute_values(load(results_dir, {'noPUE': SCEN['noPUE'], 'PUE': name}))
    mg = v['technology_mix']['PUE']['Mini-grid (PV + battery)']
    inv = v['investment']
    return {'Demand increase, new connections (%)': v['demand_new_connections_2030_MWh']['increase_pct'],
            'Mini-grids': mg['count'], 'Mini-grid capacity (kW)': mg['capacity_kW'],
            'Grid capacity (kW)': v['technology_mix']['PUE']['Grid']['capacity_kW'],
            'Total investment (M USD)': inv['PUE']['total_investment_MUSD'],
            'Change in investment (M USD)': inv['change']['total_investment_MUSD'],
            'Rural grid USD/kW': inv['PUE']['rural_grid_USD_per_kW'],
            'Rural off-grid USD/kW': inv['PUE']['rural_offgrid_USD_per_kW'],
            'All technologies USD/kW': inv['PUE']['all_USD_per_kW']}


def sensitivity_tables(results_dir):
    cost = pd.DataFrame([{'Mini-grid cost case': lab, **headline(results_dir, n)} for lab, n in SENSITIVITY if run_exists(results_dir, n)])
    uptake = pd.DataFrame([{'PUE realised': lab, **headline(results_dir, n)} for lab, n in PUE_UPTAKE if run_exists(results_dir, n)])
    return cost, uptake


# One-at-a-time capital-cost sensitivity: runs OAT_<parameter>_80 / _120 of the enhanced-demand scenario.
# (parameter, label, group, central value, unit). 'farm' is costed outside OnSSET, so it needs no model run.
OAT = [
    ('grid_connection', 'Grid connection', 'Grid', '1,300', 'USD/household'),
    ('mv_line', 'Medium-voltage line', 'Grid', '30,000', 'USD/km'),
    ('lv_line', 'Low-voltage line', 'Grid', '13,700', 'USD/km'),
    ('hv_line', 'High-voltage line', 'Grid', '90,000', 'USD/km'),
    ('transformers', 'Transformers and substations', 'Grid', '3,800–338,800', 'USD/unit'),
    ('grid_capacity', 'Grid generation capacity', 'Grid', '1,363', 'USD/kW'),
    ('sa_pv_1', 'Stand-alone PV, up to 20 W', 'Off-grid', '9,000', 'USD/kW'),
    ('sa_pv_2', 'Stand-alone PV, 21–50 W', 'Off-grid', '4,800', 'USD/kW'),
    ('sa_pv_3', 'Stand-alone PV, 51–100 W', 'Off-grid', '1,900', 'USD/kW'),
    ('sa_pv_4', 'Stand-alone PV, 101–200 W', 'Off-grid', '1,500', 'USD/kW'),
    ('farm', 'Farm solar irrigation', 'Off-grid', '1,500', 'USD/kWp'),
    ('mg_pv', 'Minigrid PV with battery', 'Off-grid', '4,000', 'USD/kW'),
    ('mg_connection', 'Minigrid connection', 'Off-grid', '140', 'USD/household'),
    ('mg_diesel', 'Minigrid diesel*', 'Off-grid', '721', 'USD/kW'),
    ('mg_wind', 'Minigrid wind*', 'Off-grid', '3,902', 'USD/kW'),
    ('sa_diesel', 'Stand-alone diesel*', 'Off-grid', '938', 'USD/kW'),
]
FARM_COST = 1500  # USD/kWp, central farm solar irrigation cost (the 101-200 W stand-alone PV price)


def oat_run(results_dir, name, farm_factor=1.0):
    """Investment by period (M USD, farm solar in 2030 at FARM_COST x farm_factor), 2030 technology group per settlement and
    mini-grid capacity of one run."""
    df = load(results_dir, {'x': name})['x']
    farm = df['FarmPVCapacity2030'].sum() * FARM_COST * farm_factor
    i25, i30 = df['InvestmentCost2025'].sum(), df['InvestmentCost2030'].sum() + farm
    code = df['FinalElecCode2030']
    tech = np.select([code.isin(GRID_CODES), code.isin(SA_CODES), code.isin(MG_CODES)], ['grid', 'SA', 'MG'], 'none')
    mg_kw = sum(df.loc[df['FinalElecCode%d' % y].isin(MG_CODES), 'NewCapacity%d' % y].sum() for y in YEARS)
    return {'2025': i25 / 1e6, '2030': i30 / 1e6, 'total': (i25 + i30) / 1e6, 'mg': int((tech == 'MG').sum()),
            'mg_kw': mg_kw}, tech


def capital_cost_sensitivity(results_dir):
    """Technology mix (mini-grids, settlements switching technology in 2030 compared with the central run) and cumulative
    investment to 2030 at 80% / 100% / 120% of each capital cost."""
    if not run_exists(results_dir, 'OAT_mv_line_80'):
        return None
    base, base_tech = oat_run(results_dir, SCEN['PUE'])
    rows = []
    for key, label, group, value, unit in OAT:
        r = {'Parameter': label, 'Group': group, 'Central value': value, 'Unit': unit}
        for pct in (80, 120):
            if key == 'farm':
                res, tech = oat_run(results_dir, SCEN['PUE'], pct / 100)
            else:
                name = 'OAT_%s_%d' % (key, pct)
                if not run_exists(results_dir, name):
                    break
                res, tech = oat_run(results_dir, name)
            moved = base_tech != tech
            sw = pd.Series([a + ' to ' + b for a, b in zip(base_tech[moved], tech[moved])]).value_counts()
            r['Mini-grids at %d%%' % pct] = res['mg']
            r['Mini-grid kW at %d%%' % pct] = round(res['mg_kw'])
            r['Settlements switching at %d%%' % pct] = int(moved.sum())
            r['Switches at %d%%' % pct] = ', '.join('%d %s' % (n, k) for k, n in sw.items())
            r['%d%% (M USD)' % pct] = round(res['total'], 2)
            r['%d%%, 2025 (M USD)' % pct] = round(res['2025'], 2)
            r['%d%%, 2030 (M USD)' % pct] = round(res['2030'], 2)
            r['Change at %d%% (M USD)' % pct] = round(res['total'] - base['total'], 2)
        else:
            r['Mini-grids, central'] = base['mg']
            r['100% (M USD)'] = round(base['total'], 2)
            r['Swing 80-120% (M USD)'] = round(r['120% (M USD)'] - r['80% (M USD)'], 2)
            r['Swing (% of central)'] = round(100 * r['Swing 80-120% (M USD)'] / base['total'], 1)
            rows.append(r)
    t = pd.DataFrame(rows)
    t['_order'] = t['Settlements switching at 80%'] + t['Settlements switching at 120%'] + t['Swing 80-120% (M USD)'].abs() / 1e3
    t = t.sort_values('_order', ascending=False).drop(columns='_order')
    t.attrs['base'] = base
    return t


OAT_SHORT = {'Minigrid PV with battery': 'Minigrid cost', 'Medium-voltage line': 'MV line cost', 'High-voltage line': 'HV line cost',
             'Grid connection': 'Grid connection cost', 'Minigrid connection': 'Minigrid connection cost',
             'Grid generation capacity': 'Grid generation capacity cost', 'Stand-alone PV, up to 20 W': 'Standalone PV (0–20 W)',
             'Stand-alone PV, 21–50 W': 'Standalone PV (20–50 W)', 'Stand-alone PV, 51–100 W': 'Standalone PV (50–100 W)',
             'Stand-alone PV, 101–200 W': 'Standalone PV (100–200 W)'}
OAT_HIDE = ['Farm solar irrigation', 'Low-voltage line', 'Transformers and substations']  # not shown in the tornado figures


def fig_capital_cost_sensitivity(t, out):
    """Only the costs that change the technology mix or investment by at least USD 1 million, with
    short labels; all costs are in fig_capital_cost_sensitivity_all."""
    t = t[~t['Parameter'].str.endswith('*')].copy()
    t['dmg80'] = t['Mini-grids at 80%'] - t['Mini-grids, central']
    t['dmg120'] = t['Mini-grids at 120%'] - t['Mini-grids, central']
    keep = ((t['Settlements switching at 80%'] + t['Settlements switching at 120%']) > 0) | \
           (t[['Change at 80% (M USD)', 'Change at 120% (M USD)']].abs().max(axis=1) >= 1)
    g = t[keep].iloc[::-1].reset_index(drop=True)
    y = np.arange(len(g))
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    for ax, (c80, c120), title, fmt in ((axes[0], ('dmg80', 'dmg120'), '(a) Change in least-cost minigrids', '%+d'),
                                        (axes[1], ('Change at 80% (M USD)', 'Change at 120% (M USD)'),
                                         '(b) Change in investment (million USD)', '%+.1f')):
        lim = max(g[c80].abs().max(), g[c120].abs().max()) * 1.35
        for col, color, lab in ((c80, BLUE, '−20%'), (c120, ORANGE, '+20%')):
            ax.barh(y, g[col], 0.7, color=color, label=lab, zorder=2)
            for yi, val in zip(y, g[col]):
                if val != 0:
                    ax.text(val + (0.02 * lim if val > 0 else -0.02 * lim), yi,
                            (fmt if abs(val) >= 0.05 or fmt == '%+d' else '%+.2f') % val, va='center',
                            ha='left' if val > 0 else 'right', fontsize=10, color=TEXT)
        ax.axvline(0, color=TEXT, linewidth=0.8, zorder=3)
        ax.set_xlim(-lim, lim)
        ax.tick_params(axis='x', labelsize=10)
        ax.set_title(title, loc='left', color=TEXT, fontsize=12)
        ax.spines[['top', 'right']].set_visible(False)
        ax.xaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
    for ax in axes:
        ax.set_yticks(y)
        ax.set_yticklabels([OAT_SHORT.get(p_, p_) for p_ in g['Parameter']], fontsize=11, color=TEXT)
        ax.tick_params(axis='y', labelleft=True)
    axes[1].legend(frameon=False, fontsize=10, loc='lower right', title='Capital cost', title_fontsize=10)
    fig.tight_layout()
    save(fig, out, 'capital_cost_sensitivity')


def fig_capital_cost_sensitivity_all(t, out):
    """Two tornado panels for -20% / +20% in each capital cost: (a) change in the number of least-cost mini-grids,
    (b) change in cumulative investment to 2030."""
    t = t[~t['Parameter'].str.endswith('*')].copy()  # diesel and wind are outside the study's technology set
    t['dmg80'] = t['Mini-grids at 80%'] - t['Mini-grids, central']
    t['dmg120'] = t['Mini-grids at 120%'] - t['Mini-grids, central']
    t = t[~t['Parameter'].isin(OAT_HIDE)]
    labels = lambda g: [OAT_SHORT.get(p_, p_) for p_ in g['Parameter']]
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.6))
    panels = [(axes[0], ('dmg80', 'dmg120'), '(a) Change in least-cost minigrids', 'Change in number of minigrids', '%+d', 0.5),
              (axes[1], ('Change at 80% (M USD)', 'Change at 120% (M USD)'), '(b) Change in investment to 2030',
               'Change in investment (million USD)', '%+.1f', 0.005)]
    for ax, (c80, c120), title, xlab, fmt, tol in panels:
        g = t.iloc[::-1].reset_index(drop=True)  # same order in both panels (as in the table), first row at the top
        y = np.arange(len(g))
        lim = max(g[c80].abs().max(), g[c120].abs().max()) * 1.3
        for col, color, lab in ((c80, BLUE, '−20% cost'), (c120, ORANGE, '+20% cost')):
            ax.barh(y, g[col], 0.7, color=color, label=lab, zorder=2)
            for yi, val in zip(y, g[col]):
                if abs(val) >= tol:
                    ax.text(val + (0.015 * lim if val > 0 else -0.015 * lim), yi, (fmt if abs(val) >= 0.05 else '%+.2f') % val, va='center',
                            ha='left' if val > 0 else 'right', fontsize=9.5, color=TEXT)
        for yi, a_, b_ in zip(y, g[c80], g[c120]):
            if abs(a_) < tol and abs(b_) < tol:
                ax.text(0.015 * lim, yi, 'no effect', va='center', fontsize=9, color=SUBTEXT, style='italic')
        ax.set_yticks(y)
        ax.set_yticklabels(labels(g), fontsize=10.5, color=TEXT)
        ax.tick_params(axis='x', labelsize=10)
        ax.axvline(0, color=TEXT, linewidth=0.8, zorder=3)
        ax.set_xlim(-lim, lim)
        ax.set_title(title, loc='left', color=TEXT, fontsize=12)
        ax.set_xlabel(xlab, fontsize=10.5)
        ax.spines[['top', 'right']].set_visible(False)
        ax.xaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
    axes[0].legend(frameon=False, fontsize=10, loc='lower left')
    fig.tight_layout()
    save(fig, out, 'capital_cost_sensitivity_all')


def viability_frame(n, p):
    """Per settlement: mini-grid cost, grid-extension cost and least-cost choice, without and with PUE."""
    hh = p['Pop2030'] / p['NumPeoplePerHH']
    f = pd.DataFrame({'id_left': p['id_left'], 'subcounty': p['subcounty'].str.replace(' Sub County', '', regex=False),
                      'lon': p['X_deg'], 'lat': p['Y_deg'], 'households_2030': hh.round(1),
                      'off_grid_2020': p['ElecStart'] == 0, 'pue_kWh': p[PUE_COLS].sum(axis=1)})
    for tag, d in [('without_pue', n), ('with_pue', p)]:
        f['mg_lcoe_' + tag] = d['MG_PV2030']
        f['grid_ext_lcoe_' + tag] = d['GridExtLCOE2030']
        f['mg_cheaper_than_grid_' + tag] = d['MG_PV2030'] <= d['GridExtLCOE2030']
        f['least_cost_mg_' + tag] = d['FinalElecCode2030'].isin(MG_CODES)
        f['tariff_gap_' + tag] = (d['MG_PV2030'] - TARIFF).clip(lower=0)
    return f


def minigrid_viability(results_dir):
    """Mini-grid viability in off-grid settlements with PUE, by household threshold, without and with PUE."""
    rows, central = [], None
    for lab, name in SENSITIVITY + PUE_UPTAKE[1:]:
        if not run_exists(results_dir, name):
            continue
        d = load(results_dir, {'noPUE': SCEN['noPUE'], 'PUE': name})
        f = viability_frame(d['noPUE'], d['PUE'])
        if name == SCEN['PUE']:
            central = f
        run = lab if name != 'Sens_PUE50' else 'PUE 50% (4,000)'
        for hmin in HH_MIN:
            m = f['off_grid_2020'] & (f['pue_kWh'] > 0) & (f['households_2030'] >= hmin)
            e = f[m]
            # the without-PUE baseline is run at the central mini-grid cost only
            tags = ['without_pue', 'with_pue'] if name == SCEN['PUE'] else ['with_pue']
            for tag in tags:
                rows.append({'Run': run, 'Demand': 'Without PUE' if tag == 'without_pue' else 'With PUE',
                             'Min. households': hmin, 'Settlements': len(e), 'Households': round(e['households_2030'].sum()),
                             'Median MG LCOE': round(e['mg_lcoe_' + tag].median(), 2) if len(e) else None,
                             'Median grid-extension LCOE': round(e['grid_ext_lcoe_' + tag].median(), 2) if len(e) else None,
                             'MG cheaper than grid extension': int(e['mg_cheaper_than_grid_' + tag].sum()),
                             'Least-cost mini-grids': int(e['least_cost_mg_' + tag].sum()),
                             'At or below tariff': int((e['tariff_gap_' + tag] == 0).sum()),
                             'Median tariff gap': round(e['tariff_gap_' + tag].median(), 2) if len(e) else None})
    return pd.DataFrame(rows), central


def fig_minigrid_viability(f, bounds, out, via=None):
    """(a) Map of off-grid clusters with PUE; those with at least 50 households coloured by whether a minigrid or grid extension
    has the lower LCoE (with PUE). (b) Median minigrid and grid-extension LCoE without and with PUE, by minimum number of
    households (central run). Without via, only the map is drawn."""
    m = f['off_grid_2020'] & (f['pue_kWh'] > 0)
    small = f[m & (f['households_2030'] < HH_MIN[0])]
    big = f[m & (f['households_2030'] >= HH_MIN[0])]
    if via is None:
        fig, ax = plt.subplots(figsize=(6.5, 5.2))
    else:
        fig, (ax, axb) = plt.subplots(1, 2, figsize=(12.5, 5.6), gridspec_kw={'width_ratios': [1.35, 1]})
    style_map(ax, bounds)
    ax.scatter(*inside_xy(small, bounds, 'lon', 'lat'), s=5, color=BOUNDARY, alpha=0.5, linewidths=0, zorder=2)
    handles = [Line2D([], [], marker='o', color=BOUNDARY, linestyle='', markersize=4,
                      label='< %d households (%d)' % (HH_MIN[0], len(small)))]
    for flag, color, label in [(True, AQUA, 'Minigrid cheaper than grid extension'), (False, BLUE, 'Grid extension cheaper')]:
        b = big[big['mg_cheaper_than_grid_with_pue'] == flag]
        ax.scatter(*inside_xy(b, bounds, 'lon', 'lat'), s=10 + b['households_2030'] / 4, color=color, edgecolors='white', linewidths=0.6, zorder=3)
        handles.append(Line2D([], [], marker='o', color=color, linestyle='', markersize=7,
                              label='%s, \u2265 %d households (%d)' % (label, HH_MIN[0], len(b))))
    leg = ax.legend(handles=handles, title='Off-grid clusters with PUE', frameon=False, fontsize=8,
                    title_fontsize=9, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1)
    leg.get_title().set_fontweight('bold')
    if via is not None:
        ax.set_title('(a) Clusters with productive or community loads', loc='left', color=TEXT)
        c = via[via['Run'] == 'Central (4,000)'].set_index(['Demand', 'Min. households'])
        y = np.arange(len(HH_MIN))[::-1]
        for col, color, lab, dy in (('Median MG LCOE', AQUA, 'Minigrid', 0.13), ('Median grid-extension LCOE', BLUE, 'Grid extension', -0.13)):
            for yi, h in zip(y, HH_MIN):
                a_, b_ = c.loc[('Without PUE', h), col], c.loc[('With PUE', h), col]
                axb.annotate('', xy=(b_, yi + dy), xytext=(a_, yi + dy),
                             arrowprops=dict(arrowstyle='-|>', color=color, linewidth=1.6, shrinkA=5, shrinkB=5), zorder=2)
                axb.scatter([a_], [yi + dy], s=60, facecolors='white', edgecolors=color, linewidths=1.8, zorder=3)
                axb.scatter([b_], [yi + dy], s=60, color=color, zorder=3)
                axb.annotate('%.2f' % a_, (a_, yi + dy), xytext=(8, 0), textcoords='offset points', ha='left', va='center',
                             fontsize=7.5, color=SUBTEXT)
                axb.annotate('%.2f' % b_, (b_, yi + dy), xytext=(-8, 0), textcoords='offset points', ha='right', va='center',
                             fontsize=7.5, color=TEXT)
        n = c.xs('With PUE')['Settlements']
        axb.set_yticks(y)
        axb.set_yticklabels(['\u2265 %d households\n(%d clusters)' % (h, n[h]) for h in HH_MIN], color=TEXT)
        axb.set_ylim(-0.6, len(HH_MIN) - 0.4)
        hi = max(c['Median MG LCOE'].max(), c['Median grid-extension LCOE'].max())
        axb.set_xlim(0.4, hi * 1.12)
        axb.set_xlabel('Median LCoE (USD/kWh)')
        axb.spines[['top', 'right']].set_visible(False)
        axb.xaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
        axb.set_title('(b) Minigrid and grid-extension LCoE', loc='left', color=TEXT)
        lh = [Line2D([], [], marker='o', color=AQUA, linestyle='', markersize=7, label='Minigrid'),
              Line2D([], [], marker='o', color=BLUE, linestyle='', markersize=7, label='Grid extension'),
              Line2D([], [], marker='o', markerfacecolor='white', markeredgecolor=SUBTEXT, linestyle='', markersize=7, label='Without PUE'),
              Line2D([], [], marker='o', color=SUBTEXT, linestyle='', markersize=7, label='With PUE')]
        axb.legend(handles=lh, frameon=False, fontsize=7.5, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=4)
    fig.tight_layout()
    save(fig, out, 'minigrid_viability')


def table_c6(p):
    t = p.assign(subcounty=p['subcounty'].str.replace(' Sub County', '', regex=False)).groupby('subcounty')[[c for c, _ in SOLUTIONS]].sum()
    t.columns = [name for _, name in SOLUTIONS]
    t = t[['Health', 'Crop farming', 'Water', 'Poultry']]
    t['Total'] = t.sum(axis=1)
    t.loc['Total'] = t.sum()
    return t.round(0).astype(int)


def inside_xy(df, bounds, xcol='X_deg', ycol='Y_deg'):
    """Map coordinates of df's settlements. Any centroid outside the county outline is moved to the nearest point just
    inside it (display only). With the Meru County shapefile used for the settlement data (data/meru_subcounties.geojson)
    no centroid lies outside, so the coordinates are unchanged; this matters only with another boundary file, e.g. GADM."""
    from shapely.geometry import Point
    from shapely.ops import nearest_points
    key = id(bounds)
    if _INSIDE.get('key') != key:
        county = bounds.union_all() if hasattr(bounds, 'union_all') else bounds.unary_union
        _INSIDE.update(key=key, county=county, inner=county.buffer(-0.003))
    county, inner = _INSIDE['county'], _INSIDE['inner']
    x, y = df[xcol].to_numpy(float).copy(), df[ycol].to_numpy(float).copy()
    for i in range(len(x)):
        pt = Point(x[i], y[i])
        if not county.contains(pt):
            q = nearest_points(inner, pt)[0]
            x[i], y[i] = q.x, q.y
    return x, y


_INSIDE = {}


def style_map(ax, bounds):
    bounds.boundary.plot(ax=ax, color=BOUNDARY, linewidth=0.6, zorder=1)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.tick_params(labelsize=7)
    ax.set_aspect('equal')


def fig_baseline_electrification(p, bounds, out):
    """Base-year (2020) electrification status after calibration: clusters marked (at least partly) electrified, and the
    calibrated electrification rate (electrified population in those clusters / 2020 population), total, urban, rural."""
    e = p['ElecStart'] == 1
    rate = lambda m: 100 * p.loc[m & e, 'ElecPopCalib'].sum() / p.loc[m, 'PopStartYear'].sum()
    allm, urb, rur = p.index == p.index, p['IsUrban'] == 2, p['IsUrban'] < 2
    fig, (ax, axb) = plt.subplots(1, 2, figsize=(15, 5.8))
    bounds.boundary.plot(ax=ax, color='black', linewidth=1, zorder=1)
    for m_, color, size, label in ((~e, '#b5b3ad', 5, 'Not electrified (%s)' % f'{(~e).sum():,}'),
                                   (e, BLUE, 6, 'Electrified (%s)' % f'{e.sum():,}')):
        x, y = inside_xy(p[m_], bounds)
        ax.scatter(x, y, s=size, color=color, linewidths=0, zorder=2 if color != BLUE else 3)
    handles = [Line2D([], [], marker='o', linestyle='', markersize=6, color=BLUE, label='Electrified (%s)' % f'{e.sum():,}'),
               Line2D([], [], marker='o', linestyle='', markersize=6, color='#b5b3ad',
                      label='Not electrified (%s)' % f'{(~e).sum():,}')]
    ax.legend(handles=handles, title='Clusters in 2020', loc='upper left', fontsize=8, title_fontsize=9, frameon=True)
    ax.text(0.98, 0.03, 'Electrification rate, 2020\nTotal %.0f%%\nUrban %.0f%% | Rural %.0f%%' % (rate(allm), rate(urb), rate(rur)),
            transform=ax.transAxes, ha='right', va='bottom', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'), zorder=4)
    # (b) solar resource: clusters coloured by annual global horizontal irradiation
    bounds.boundary.plot(ax=axb, color='black', linewidth=1, zorder=1)
    q = p.sort_values('GHI')
    x, y = inside_xy(q, bounds)
    sc = axb.scatter(x, y, s=6, c=q['GHI'], cmap='YlOrRd', vmin=1900, vmax=2400, linewidths=0, zorder=2)
    cax = axb.inset_axes([0.04, 0.80, 0.38, 0.035])
    cb = fig.colorbar(sc, cax=cax, orientation='horizontal', extend='min')
    cb.set_ticks([1900, 2100, 2300])
    cax.set_title('Global horizontal irradiation\n(kWh/m² per year)', fontsize=8.5, color=TEXT)
    cb.ax.tick_params(labelsize=8)
    axb.text(0.98, 0.03, 'Median irradiation (kWh/m² per year)\nin electrified clusters: %s\nin non-electrified clusters: %s'
             % (f"{p.loc[e, 'GHI'].median():,.0f}", f"{p.loc[~e, 'GHI'].median():,.0f}"),
             transform=axb.transAxes, ha='right', va='bottom', fontsize=9, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'), zorder=4)
    ax.set_title('(a) Electrification status, 2020', loc='left', fontsize=11, color=TEXT)
    axb.set_title('(b) Solar resource', loc='left', fontsize=11, color=TEXT)
    for a_ in (ax, axb):
        a_.set_xlabel('Longitude')
        a_.set_ylabel('Latitude')
        a_.tick_params(labelsize=8)
        a_.set_aspect('equal')
    fig.tight_layout()
    save(fig, out, 'baseline_electrification')


SUBCOUNTY_SHORT = {'Igembe North': 'Igembe N', 'Igembe South': 'Igembe S', 'Tigania East': 'Tigania E',
                   'Tigania West': 'Tigania W', 'Imenti North': 'Imenti N', 'Imenti South': 'Imenti S'}
FARMS_CSV = os.path.join(DATA, 'crop_farms.csv')  # the 3,150 EDM farm locations (900 or 1,500 kWh/yr each)


def fig_pue_demand_maps(p, bounds, out):
    """Demand locations by solution: one map per solution, points coloured by
    their demand value (each solution has only a few distinct values), total demand in the top-right box. Crop farming is
    shown per farm (data/crop_farms.csv), as designed in the EDM solution; the other solutions per cluster."""
    import matplotlib.patheffects as pe
    from shapely.ops import polylabel
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.6))
    for ax, (col, name) in zip(axes.flat, SOLUTIONS):
        bounds.boundary.plot(ax=ax, color='black', linewidth=1, zorder=1)
        s = p.loc[p[col] > 0]
        total = s[col].sum() / 1e6
        if col == 'CropFarmDemand' and os.path.exists(FARMS_CSV):
            pts = pd.read_csv(FARMS_CSV).rename(columns={'Energy': 'value'})
            x, y = inside_xy(pts, bounds, 'lon', 'lat')
            count = '{:,} farms'.format(len(pts))
        else:
            pts = s.assign(value=np.floor(s[col] + 0.5))  # round half up (15,340.5 -> 15,341)
            x, y = inside_xy(pts, bounds)
            count = '{:,} clusters'.format(len(pts))
        values = np.sort(pts['value'].unique())
        if col == 'CropFarmDemand':
            colors = dict(zip(values, ['#e8863a', '#5b80a8'][:len(values)]))
        else:
            colors = dict(zip(values, [plt.cm.plasma(f) for f in np.linspace(0, 0.85, len(values))]))
        if col == 'CropFarmDemand':
            # 900 and 1,500 kWh farms lie interleaved along the same rivers, so drawing one value after the other hides
            # it: draw all farms in a fixed random order, so both colours show in proportion
            order = np.random.default_rng(0).permutation(len(pts))
            ax.scatter(x[order], y[order], s=16, c=[colors[v_] for v_ in pts['value'].to_numpy()[order]],
                       edgecolors='white', linewidths=0.2, zorder=3)
            handles = [Line2D([], [], marker='o', linestyle='', markersize=6, color=colors[v_], label='%d' % v_)
                       for v_ in values]
        else:
            for val in values:
                m_ = (pts['value'] == val).to_numpy()
                ax.scatter(x[m_], y[m_], s=28, color=colors[val], linewidths=0, zorder=3)
            handles = [Line2D([], [], marker='o', linestyle='', markersize=6, color=colors[v_], label='%d' % v_)
                       for v_ in values]
        ax.legend(handles=handles, title='Demand (kWh)', loc='upper left', fontsize=8, title_fontsize=9, frameon=True)
        ax.text(0.98, 0.97, 'Total Demand\n%.2f GWh\n%s' % (total, count), transform=ax.transAxes, ha='right', va='top', fontsize=9,
                fontweight='bold', bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'), zorder=4)
        ax.set_title('%s Solutions Demand' % name.title(), fontsize=13, fontweight='bold')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.tick_params(labelsize=8)
        ax.set_aspect('equal')
        if name == 'Poultry':
            for _, row in bounds.iterrows():
                g = max(row.geometry.geoms, key=lambda q: q.area) if row.geometry.geom_type == 'MultiPolygon' else row.geometry
                c = polylabel(g, tolerance=0.001)
                # the white outline keeps names readable over boundary lines; long names on two lines; below the markers
                name_ = SUBCOUNTY_SHORT.get(row['subcounty'], row['subcounty'])
                ax.annotate(name_.replace(' ', '\n') if 'Central' in name_ else name_, (c.x, c.y),
                            fontsize=7.5, fontweight='bold', ha='center', va='center', linespacing=0.95, zorder=2,
                            path_effects=[pe.withStroke(linewidth=2.5, foreground='white')])
    fig.tight_layout()
    save(fig, out, 'pue_demand_maps')


def grouped_bars(ax, groups, series, fmt='{:,.0f}'):
    x = np.arange(len(groups))
    w = 0.36
    for i, k in enumerate(['noPUE', 'PUE']):
        vals = series[k]
        bars = ax.bar(x + (i - 0.5) * w, vals, w - 0.02, color=SCEN_COLOR[k], hatch=SCEN_HATCH[k], label=LABEL[k], zorder=2)
        for b, val in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(), fmt.format(val), ha='center', va='bottom', fontsize=8, color=TEXT)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, color=TEXT)
    ax.spines[['top', 'right']].set_visible(False)
    ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_ylim(0, max(max(series[k]) for k in series) * 1.22)  # headroom so the legend sits above the bars
    ax.legend(frameon=False, ncol=2, loc='upper center')


PUE_COLORS = {'Water': '#1baf7a', 'Crop farming': '#eda100', 'Health': '#d6457a', 'Poultry': '#7d5ba6'}


def demand_split(df):
    """2030 demand (MWh/yr) split into settlements already electrified in 2020, new household demand connected 2020-2030,
    and PUE by solution (crop farming = farm-level solar irrigation, costed outside the cluster load)."""
    tot = df['TotalEnergyPerCell'].sum()
    new = df['EnergyPerSettlement2025'].sum() + df['EnergyPerSettlement2030'].sum()
    pue = {'Water': df['CommercialDemand2030'].sum(), 'Crop farming': (df['CropFarmDemand'] * (df['FarmPVCapacity2030'] > 0)).sum(),
           'Health': df['HealthDemand2030'].sum(), 'Poultry': df['AgriDemand2030'].sum()}
    model_pue = pue['Water'] + pue['Health'] + pue['Poultry']
    return {'existing': (tot - new) / 1e3, 'households': (new - model_pue) / 1e3, 'pue': {k: v_ / 1e3 for k, v_ in pue.items()},
            'total': (tot + pue['Crop farming']) / 1e3}


def fig_demand_and_capacity(v, out, d=None):
    """(a) New electricity demand connected 2020-2030 (households and PUE by solution), with total 2030 demand above each
    bar; (b) required new capacity, rural and urban. Without d, only panel (b) is drawn."""
    cap = v['new_capacity_kW']
    if d is None:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        axb = ax
    else:
        fig, (axa, axb) = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw={'width_ratios': [1, 1.15]})
        x = np.arange(2)
        sp = {k: demand_split(d[k]) for k in ('noPUE', 'PUE')}
        hh = [sp[k]['households'] for k in ('noPUE', 'PUE')]
        axa.bar(x, hh, 0.55, color='#9a9892', label='Households', zorder=2)
        for xi, h in zip(x, hh):
            axa.text(xi, h / 2, f'{h:,.0f}', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')
        pue = np.array([sum(sp[k]['pue'].values()) for k in ('noPUE', 'PUE')])
        axa.bar(x, pue, 0.55, bottom=hh, color=ORANGE, label='PUE and community services', zorder=2)
        bottom = np.array(hh, dtype=float) + pue
        pue_tot = sum(sp['PUE']['pue'].values())
        new_tot = bottom
        for xi, nt, k in zip(x, new_tot, ('noPUE', 'PUE')):
            axa.text(xi, nt * 1.01, 'Total %s' % f'{nt:,.0f}', ha='center', va='bottom', fontsize=8.5, color=TEXT)
        axa.text(x[1], hh[1] + pue_tot / 2, f'{pue_tot:,.0f}', ha='center', va='center', fontsize=8.5, color='white',
                 fontweight='bold')
        axa.set_xticks(x)
        axa.set_xticklabels([LABEL['noPUE'], LABEL['PUE']], color=TEXT)
        axa.set_xlim(-0.6, 1.6)
        axa.set_ylim(0, new_tot.max() * 1.2)
        axa.set_ylabel('New demand connected 2020–2030 (MWh/year)')
        axa.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
        axa.spines[['top', 'right']].set_visible(False)
        axa.yaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
        axa.legend(frameon=False, fontsize=7.5, loc='upper left', ncol=2)
        axa.set_title('(a) Electricity demand (MWh/year)', loc='left', color=TEXT)
        axb.set_title('(b) Required new capacity (kW)', loc='left', color=TEXT)
    grouped_bars(axb, ['Rural', 'Urban'], {k: [cap[k]['Rural'], cap[k]['Urban']] for k in SCEN})
    axb.set_ylabel('New capacity 2020–2030 (kW)')
    fig.tight_layout()
    save(fig, out, 'demand_and_capacity')


def fig_technology_maps(d, bounds, out):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8))
    for ax, k in zip(axes, ['noPUE', 'PUE']):
        df = d[k]
        style_map(ax, bounds)
        handles = []
        for tech, (codes, color, marker, size, z) in TECH_STYLE.items():
            s = df[df['FinalElecCode2030'].isin(codes)]
            if s.empty:
                continue
            kw = dict(edgecolors='white', linewidths=0.5) if marker == '*' else dict(linewidths=0)
            x, y = inside_xy(s, bounds)
            ax.scatter(x, y, s=size, color=color, marker=marker, zorder=z, alpha=1 if marker == '*' else 0.6, **kw)
            handles.append(Line2D([], [], marker=marker, color=color, linestyle='', markersize=9 if marker == '*' else 5,
                                  label='%s (%d)' % (tech, len(s))))
        ax.set_title(LABEL[k], loc='left', color=TEXT)
        ax.legend(handles=handles, title='Technology (clusters)', frameon=False, fontsize=7, title_fontsize=7,
                  loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=3)
    fig.tight_layout()
    save(fig, out, 'technology_maps')


def fig_cost_per_kw(v, out):
    fig, ax = plt.subplots(figsize=(6, 4.2))
    inv = v['investment']
    grouped_bars(ax, ['Grid', 'Off-grid'], {k: [inv[k]['rural_grid_USD_per_kW'], inv[k]['rural_offgrid_USD_per_kW']] for k in SCEN})
    ax.set_ylabel('Investment per kW, rural 2020-2030 (USD/kW)')
    fig.tight_layout()
    save(fig, out, 'cost_per_kw_rural')


def fig_minigrid_sizes(p, out):
    """Least-cost minigrid capacities (with PUE), stacked by the anchor load in the cluster (water or health)."""
    mgm = p['FinalElecCode2030'].isin(MG_CODES)
    if not mgm.any():
        return
    cap = p.loc[mgm, 'NewCapacity2030']
    anchor = np.where(p.loc[mgm, 'CommercialDemand'] > 0, 'Water system', 'Health facility')
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    edges = np.arange(0, np.ceil(cap.max() / 5) * 5 + 5, 5)
    groups = [(cap[anchor == a], c, a) for a, c in (('Water system', BLUE), ('Health facility', ORANGE))]
    ax.hist([g[0] for g in groups], bins=edges, stacked=True, color=[g[1] for g in groups],
            label=['%s (%d)' % (g[2], len(g[0])) for g in groups], edgecolor='white', linewidth=1.5, zorder=2)
    ax.set_xticks(edges)
    ax.set_xlabel('Minigrid capacity (kW)')
    ax.set_ylabel('Number of minigrids')
    ax.legend(title='Anchor load in the cluster', frameon=False, fontsize=8, title_fontsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    save(fig, out, 'minigrid_sizes')


def save(fig, out, name):
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(out, '%s.%s' % (name, ext)), bbox_inches='tight')
    plt.close(fig)


def write_markdown(v, t, path):
    tm, inv = v['technology_mix'], v['investment']
    rows = [
        ('PUE + community-service demand (GWh/yr)', '-', v['pue_demand_GWh']['Total']),
        ('Demand of settlements connected by 2030, incl. farm irrigation (MWh/yr)', v['demand_new_connections_2030_MWh']['noPUE'], v['demand_new_connections_2030_MWh']['PUE']),
        ('Demand of all settlements, 2030 (MWh/yr)', v['demand_all_settlements_2030_MWh']['noPUE'], v['demand_all_settlements_2030_MWh']['PUE']),
        ('New capacity, rural (kW)', v['new_capacity_kW']['noPUE']['Rural'], v['new_capacity_kW']['PUE']['Rural']),
        ('New capacity, urban (kW)', v['new_capacity_kW']['noPUE']['Urban'], v['new_capacity_kW']['PUE']['Urban']),
        ('New capacity, total (kW)', v['new_capacity_kW']['noPUE']['Total'], v['new_capacity_kW']['PUE']['Total']),
        ('Grid capacity (kW)', tm['noPUE']['Grid']['capacity_kW'], tm['PUE']['Grid']['capacity_kW']),
        ('SA PV capacity (kW)', tm['noPUE']['Stand-alone PV']['capacity_kW'], tm['PUE']['Stand-alone PV']['capacity_kW']),
        ('Mini-grids (count)', tm['noPUE']['Mini-grid (PV + battery)']['count'], tm['PUE']['Mini-grid (PV + battery)']['count']),
        ('Mini-grid capacity (kW)', tm['noPUE']['Mini-grid (PV + battery)']['capacity_kW'], tm['PUE']['Mini-grid (PV + battery)']['capacity_kW']),
        ('Farm solar irrigation capacity (kWp)', tm['noPUE']['Solar irrigation (farm-level)']['capacity_kW'], tm['PUE']['Solar irrigation (farm-level)']['capacity_kW']),
        ('Farm solar irrigation investment (M USD)', tm['noPUE']['Solar irrigation (farm-level)']['investment_MUSD'], tm['PUE']['Solar irrigation (farm-level)']['investment_MUSD']),
        ('Total investment 2020-2030 (M USD)', inv['noPUE']['total_investment_MUSD'], inv['PUE']['total_investment_MUSD']),
        ('Rural investment 2020-2030 (M USD)', inv['noPUE']['rural_investment_MUSD'], inv['PUE']['rural_investment_MUSD']),
        ('Rural grid, USD/kW', inv['noPUE']['rural_grid_USD_per_kW'], inv['PUE']['rural_grid_USD_per_kW']),
        ('Rural off-grid, USD/kW', inv['noPUE']['rural_offgrid_USD_per_kW'], inv['PUE']['rural_offgrid_USD_per_kW']),
        ('All technologies, USD/kW', inv['noPUE']['all_USD_per_kW'], inv['PUE']['all_USD_per_kW']),
    ]
    lines = ['# Summary values', '',
             '| Quantity | Without PUE | With PUE |', '|---|---|---|']
    lines += ['| %s | %s | %s |' % (a, f'{b:,}' if isinstance(b, (int, float)) else b, f'{c:,}' if isinstance(c, (int, float)) else c) for a, b, c in rows]
    lines += ['', '## PUE demand by solution', '', '| Solution | GWh/yr | Share | Settlements | Mini-grid settlements with this load |', '|---|---|---|---|---|']
    lines += ['| %s | %.2f | %.1f%% | %d | %d |' % (name, v['pue_demand_GWh'][name], v['pue_demand_share_pct'][name], v['pue_sites'][name],
                                                 v['minigrid_settlements_with_solution'][name]) for _, name in SOLUTIONS]
    lines += ['', '## Table C.6: annual demand by sub-county (kWh/yr)', '',
              '| Sub-county | ' + ' | '.join(t.columns) + ' |', '|---' * (len(t.columns) + 1) + '|']
    lines += ['| %s | %s |' % (i, ' | '.join(f'{x:,}' for x in r)) for i, r in t.iterrows()]
    lines += ['',
              '## All values', '', '```json', json.dumps(v, indent=1), '```', '']
    open(path, 'w').write('\n'.join(lines))


def write_tables(results_dir, out):
    """Write the tables and summary values (CSV, JSON and Markdown) to out."""
    os.makedirs(out, exist_ok=True)
    d = load(results_dir)
    v = compute_values(d)
    t = table_c6(d['PUE'])
    t.to_csv(os.path.join(out, 'demand_by_subcounty.csv'))
    json.dump(v, open(os.path.join(out, 'summary_values.json'), 'w'), indent=1)
    write_markdown(v, t, os.path.join(out, 'summary_values.md'))
    md = lambda df: ('| ' + ' | '.join(df.columns) + ' |\n' + '|---' * len(df.columns) + '|\n' +
                     ''.join('| ' + ' | '.join('' if x is None or x != x else (f'{x:,}' if isinstance(x, (int, float)) else str(x))
                                               for x in r) + ' |\n' for r in df.itertuples(index=False)))
    cost, uptake = sensitivity_tables(results_dir)
    with open(os.path.join(out, 'summary_values.md'), 'a') as f:
        if len(cost) > 1:
            cost.to_csv(os.path.join(out, 'sensitivity_minigrid_cost.csv'), index=False)
            f.write('\n## Sensitivity: PV mini-grid cost (enhanced-demand scenario)\n\n' + md(cost))
        if len(uptake) > 1:
            uptake.to_csv(os.path.join(out, 'sensitivity_pue_uptake.csv'), index=False)
            f.write('\n## Sensitivity: PUE uptake (central mini-grid cost)\n\n' + md(uptake))
    via, central = minigrid_viability(results_dir)
    if central is not None:
        via.to_csv(os.path.join(out, 'minigrid_viability.csv'), index=False)
        central.to_csv(os.path.join(out, 'minigrid_viability_by_settlement.csv'), index=False)
        with open(os.path.join(out, 'summary_values.md'), 'a') as f:
            f.write('\n## Mini-grid viability in off-grid settlements with PUE\n\nSettlements not grid-connected in 2020 that have PUE '
                    'in the with-PUE scenario, by minimum number of households (2030); the same settlements are compared without '
                    'and with PUE. Tariff = small-commercial, USD %.3f/kWh.\n\n' % TARIFF + md(via))
    oat = capital_cost_sensitivity(results_dir)
    if oat is not None:
        oat.to_csv(os.path.join(out, 'sensitivity_capital_costs.csv'), index=False)
        b = oat.attrs['base']
        cols = ['Parameter', 'Central value', 'Unit', 'Mini-grids at 80%', 'Mini-grids at 120%', 'Mini-grid kW at 80%',
                'Mini-grid kW at 120%', 'Switches at 80%', 'Switches at 120%', '80% (M USD)', '120% (M USD)',
                'Swing (% of central)', '80%, 2025 (M USD)', '120%, 2025 (M USD)']
        with open(os.path.join(out, 'summary_values.md'), 'a') as f:
            f.write('\n## One-at-a-time capital-cost sensitivity (+/-20%%, enhanced-demand scenario)\n\nCumulative investment to '
                    '2030 including farm solar irrigation; central: %d mini-grids (%d kW), USD %.2fM (2025: %.2fM, 2030: %.2fM). '
                    'Switches = settlements whose 2030 technology differs from the central run.\n\n' % (b['mg'], b['mg_kw'], b['total'], b['2025'], b['2030']) +
                    md(oat[cols]))
    print('Wrote tables to', out)
