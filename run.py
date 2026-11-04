"""Command line: python3 run.py [archetype|base] [scenario] [policy] -> prints the headline, writes report JSON and ledger CSV.
Example: python3 run.py insurance_large Moderate "Attrition only" """
import json, sys, csv, os, evm, archetype
ROOT = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(ROOT, 'data', 'etter_fpa.json')))
pack = json.load(open(os.path.join(ROOT, 'packs', 'base.json')))
arch = json.load(open(os.path.join(ROOT, 'packs', 'archetypes.json')))
key = sys.argv[1] if len(sys.argv) > 1 else 'base'
sn = sys.argv[2] if len(sys.argv) > 2 else 'Moderate'
pn = sys.argv[3] if len(sys.argv) > 3 else None
if key != 'base':
    data, pack = archetype.build(data, pack, arch[key]); pn = pn or arch[key]['default_policy']
pn = pn or 'Attrition only'
rep = evm.report(data, pack, sn, pn, n_mc=1000)
h, b = rep['headline'], rep['bands']
m = lambda v: f"{'+' if v >= 0 else '-'}${abs(v)/1e6:.1f}M"
print(f"{rep['meta']['pack']} | {sn} | {pn}")
print(f"  cash vs today {m(h['npv_cash'])}  (P10 {m(b['p10'])}, P50 {m(b['p50'])}, P90 {m(b['p90'])}, {b['p_positive']:.0%} positive)" if not h['count_avoidance']
      else f"  cash vs plan {m(h['npv_plan'])}; vs today {m(h['npv_cash'])}  (P10 {m(b['p10'])}, P90 {m(b['p90'])}, {b['p_positive']:.0%} positive)")
print(f"  capacity at cost {m(h['pv_capacity'])}, positions {h['positions']:.0f}, hires avoided {h['hires_avoided']:.0f}, payback month {h['payback']}")
print(f"  break-even realisation {rep['breakeven_net'] if rep['breakeven_net'] is None else format(rep['breakeven_net'], '.1%')} vs assumed {rep['realisation']:.1%}  ->  {rep['verdict_text']}")
os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
stem = os.path.join(ROOT, 'out', f"{key}_{sn}_{pn}".replace(' ', '_'))
json.dump(rep, open(stem + '.json', 'w'), indent=1, default=str)
with open(stem + '_ledger.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['line', 'source', 'nominal_usd', 'pv_usd'])
    for e in sorted(rep['ledger'], key=lambda e: (e['line'], -abs(e['pv']))):
        w.writerow([e['line'], e['source'], round(e['nominal'], 2), round(e['pv'], 2)])
print(f"  wrote {stem}.json and {stem}_ledger.csv")
