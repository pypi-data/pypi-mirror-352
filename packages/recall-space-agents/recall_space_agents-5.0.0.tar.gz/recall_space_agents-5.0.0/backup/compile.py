import nbformat as nbf, os, textwrap, json, pandas as pd

# Define notebook content
nb = nbf.v4.new_notebook()

cells = []

# Title markdown
cells.append(nbf.v4.new_markdown_cell("# Material‑Planner Heuristic\n"
                                      "This notebook reproduces the human planner’s order‑proposal logic using:\n"
                                      "1. A **rule‑based heuristic** (freeze weeks, reorder point, two‑pass loop).\n"
                                      "2. A **learned MOQ table** derived automatically from the planner’s own proposals.\n"
                                      "\n"
                                      "It reads the three uploaded workbooks directly from the `/mnt/data` folder."))

# Imports & path vars
code_imports = textwrap.dedent("""\
    import pandas as pd, numpy as np, math, os, nbformat
    from IPython.display import display
    
    BASE = '/mnt/data'
    RAW_DEMAND = os.path.join(BASE, 'unbearbeitet_DispositionslisteHilfstoffe_raw.xlsx')
    RAW_OPEN   = os.path.join(BASE, 'Mawi_offene_Bestellungen.xlsx')
    RAW_FINAL  = os.path.join(BASE, '20250422DispositionslisteHilfstoffe_raw.xlsx')
    """)
cells.append(nbf.v4.new_code_cell(code_imports))

# Helper functions cell
code_helpers = textwrap.dedent("""\
    def to_int(x):
        try:
            return int(float(x))
        except:
            return np.nan
    """)
cells.append(nbf.v4.new_code_cell(code_helpers))

# Load raw demand cell
code_demand = textwrap.dedent("""\
    # ----------------- Load raw demand / packaging --------------------------
    raw = pd.read_excel(RAW_DEMAND, sheet_name='Dispositionsliste_ Hilfsstoffe')
    raw = raw.rename(columns={
        'Verpackungseinheit (VPE)': 'VPE',
        'Sofort (25/17)': '25/17',
        'Woche 1 (25/18)': '25/18',
        'Woche 2 (25/19)': '25/19',
        'Woche 3 (25/20)': '25/20',
        'Woche 4 (25/21)': '25/21'
    })
    
    demand_cols = ['MaterialNr','Bezeichnung','Bestand','VPE','25/17','25/18','25/19','25/20','25/21']
    demand_df = raw[demand_cols].copy()
    for c in ['Bestand','VPE','25/17','25/18','25/19','25/20','25/21']:
        demand_df[c] = pd.to_numeric(demand_df[c], errors='coerce').fillna(0)
    demand_df['MaterialNr'] = demand_df['MaterialNr'].apply(to_int)
    demand_df = demand_df[(demand_df['MaterialNr'].notna()) & (demand_df['VPE']>0)].copy()
    display(demand_df.head())
    """)
cells.append(nbf.v4.new_code_cell(code_demand))

# Load open orders cell
code_open = textwrap.dedent("""\
    # ----------------- Load open purchase orders ---------------------------
    open_df = pd.read_excel(RAW_OPEN, sheet_name='Tabelle1')
    open_df['MaterialNr'] = open_df['MaterialNr'].apply(to_int)
    kw_col = 'LieferterminKalenderwoche'
    open_df = open_df[open_df['MaterialNr'].notna()]
    # Keep only deliveries inside the five‑week horizon
    horizon_regex = r'25/1[7-9]|25/2[0-1]'
    open_df = open_df[open_df[kw_col].astype(str).str.match(horizon_regex)]
    
    receipts = (open_df.groupby(['MaterialNr', kw_col])['BestMenge']
                       .sum()
                       .reset_index()
                       .rename(columns={kw_col:'KW', 'BestMenge':'Receipt'}))
    display(receipts.head())
    """)
cells.append(nbf.v4.new_code_cell(code_open))

# Learn MOQ cell
code_learn_moq = textwrap.dedent("""\
    # ----------------- Derive MOQ per material from planner proposals -------
    final_xl = pd.ExcelFile(RAW_FINAL)
    tab1 = final_xl.parse('Tabelle1')
    zubest = final_xl.parse('zu bestellen')
    
    tab1_prop = tab1[tab1['NameKurz'].isna()].copy()
    tab1_prop = tab1_prop.rename(columns={'MaterialNr':'MaterialNr','BestMenge':'Qty'})
    tab1_prop['MaterialNr'] = tab1_prop['MaterialNr'].apply(to_int)
    
    zubest = zubest.rename(columns={'Unnamed: 1':'MaterialNr', 'zu bestellen 13.05':'Qty'})
    zubest['MaterialNr'] = zubest['MaterialNr'].apply(to_int)
    zubest = zubest[['MaterialNr','Qty']]
    
    planner_prop = pd.concat([tab1_prop[['MaterialNr','Qty']], zubest], ignore_index=True)
    planner_prop = planner_prop.dropna(subset=['MaterialNr','Qty'])
    planner_prop['Qty'] = planner_prop['Qty'].astype(int)
    
    vpe_series = demand_df.set_index('MaterialNr')['VPE']
    # MOQ in pieces = smallest planned quantity rounded up to full VPE
    min_qty = planner_prop.groupby('MaterialNr')['Qty'].min()
    moq_map = ((np.ceil(min_qty / vpe_series).astype(int) * vpe_series).dropna()).to_dict()
    
    # For materials without proposals, default MOQ = 1 × VPE
    for mat, vpe in vpe_series.items():
        moq_map.setdefault(mat, vpe)
    
    print(f"Derived MOQ for {len(moq_map)} materials.")
    """)
cells.append(nbf.v4.new_code_cell(code_learn_moq))

# Algorithm function cell
code_algo = textwrap.dedent("""\
    # ----------------- Planning algorithm (two‑pass) ------------------------
    KW_ORDER   = ['25/17','25/18','25/19','25/20','25/21']
    FREEZE_SET = set(KW_ORDER[:3])
    
    def plan_proposals(demand_df, receipts_df, moq_map):
        stock = dict(zip(demand_df['MaterialNr'], demand_df['Bestand']))
        rec = {(r.MaterialNr, r.KW): r.Receipt for r in receipts_df.itertuples()}
        proposals = []
        
        # project through frozen weeks
        for kw in KW_ORDER[:3]:
            for mat, row in demand_df.set_index('MaterialNr').iterrows():
                stock[mat] -= row[kw]
                stock[mat] += rec.get((mat, kw), 0)
        
        snapshot = stock.copy()
        for target_kw in ['25/20','25/21']:
            pass_receipts = {}
            for mat, row in demand_df.set_index('MaterialNr').iterrows():
                vpe = row['VPE']
                running = snapshot[mat]
                for kw in KW_ORDER[KW_ORDER.index('25/20'): KW_ORDER.index(target_kw)+1]:
                    running -= row[kw]
                    running += rec.get((mat, kw), 0)
                    running += pass_receipts.get((mat, kw), 0)
                if running < 1 and row[['25/20','25/21']].sum() > 0:
                    shortage = 1 - running
                    qty = math.ceil(shortage / vpe) * vpe
                    qty = max(qty, moq_map.get(mat, vpe))
                    proposals.append({'MaterialNr': mat, 'Qty': int(qty), 'KW': target_kw})
                    pass_receipts[(mat, target_kw)] = qty
            # fold receipts into snapshot for next loop
            for (mat, kw), qty in pass_receipts.items():
                rec[(mat, kw)] = rec.get((mat, kw), 0) + qty
                snapshot[mat] += qty
        return pd.DataFrame(proposals)
    
    algo_prop = plan_proposals(demand_df, receipts, moq_map)
    display(algo_prop.head())
    """)
cells.append(nbf.v4.new_code_cell(code_algo))

# Comparison cell
code_compare = textwrap.dedent("""\
    # ----------------- Compare with planner proposals -----------------------
    planner_prop['KW'] = planner_prop['KW'].fillna('25/21')  # zubest has no KW
    planner_agg = planner_prop.groupby('MaterialNr')['Qty'].sum().rename('Planner_Qty')
    algo_agg    = algo_prop.groupby('MaterialNr')['Qty'].sum().rename('Algo_Qty')
    
    cmp = pd.concat([planner_agg, algo_agg], axis=1).fillna(0).astype(int)
    cmp['Diff'] = cmp['Algo_Qty'] - cmp['Planner_Qty']
    cmp['Match'] = cmp['Diff'] == 0
    cmp.reset_index(inplace=True)
    
    display(cmp)
    print(f"Exact matches: {cmp['Match'].sum()} of {len(cmp)} SKUs.")
    """)
cells.append(nbf.v4.new_code_cell(code_compare))

nb['cells'] = cells

# Save notebook
nb_path = 'material_planner_algorithm.ipynb'
with open(nb_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

nb_path
