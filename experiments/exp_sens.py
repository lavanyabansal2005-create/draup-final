"""H2. Sensitivity (one at a time, plausible ranges) + Monte Carlo bands for each scenario x policy."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'experiments')); os.chdir(ROOT)

import json, copy, evm
data = json.load(open('data/etter_fpa.json')); pack = json.load(open('packs/base.json'))
prep = evm.prepare(data, pack)
MOD = evm.scenario(pack, 'Moderate'); ATT = evm.policy(pack, 'Attrition only')
chosen, _ = evm.scope(prep, MOD)
base = evm.simulate(prep, MOD, ATT, {'chosen': chosen})['npv_cash']
U = pack['uncertainty']['params']
labels = {'takeover':'AI takeover rate', 'review':'Human review load', 'adopt_months':'Months to full adoption',
          'active_use':'Assistant active use', 'aug_mult':'Assistant time saving', 'cost_mult':'Build & programme cost',
          'run_mult':'AI running cost per hour', 'drag':'Complexity drag', 'turnover_mult':'Staff turnover'}
rows = []
def run_with(S=None, pol=None, pk=None, pr=None):
    pr = pr or (evm.prepare(data, pk) if pk else prep)
    return evm.simulate(pr, S or MOD, pol or ATT, {'chosen': chosen if pr is prep else evm.scope(pr, S or MOD)[0]})['npv_cash']
for k, spec in U.items():
    lo = run_with(dict(MOD, **{k: spec['p10']})); hi = run_with(dict(MOD, **{k: spec['p90']}))
    rows.append((labels[k], spec['p10'], spec['p90'], lo, hi))
for lbl, key, lo_v, hi_v in [('Discount rate', 'discount_rate', 0.0560, 0.0934)]:
    out = []
    for v in (lo_v, hi_v):
        p2 = copy.deepcopy(pack); p2['economics'][key] = v; pr = evm.prepare(data, p2)
        out.append(evm.simulate(pr, MOD, ATT, {'chosen': chosen})['npv_cash'])
    rows.append((lbl, lo_v, hi_v, out[0], out[1]))
for lbl, key, lo_v, hi_v in [('Harvest share (policy)', 'harvest_automation', 0.25, 0.75)]:
    rows.append((lbl, lo_v, hi_v, run_with(pol=dict(ATT, **{key: lo_v})), run_with(pol=dict(ATT, **{key: hi_v}))))
for lbl, sect, key, lo_v, hi_v in [('Training cost per head', 'costs', 'training_spend_per_head', 423, 1692),
                                   ('Seat cost reclaimed', 'costs', 'seat_cost_per_position', 0, 2000),
                                   ('Cost per hire avoided', 'economics', 'cost_per_hire', 4100, 10000)]:
    out = []
    for v in (lo_v, hi_v):
        p2 = copy.deepcopy(pack); p2[sect][key] = v; pr = evm.prepare(data, p2)
        out.append(evm.simulate(pr, MOD, ATT, {'chosen': chosen})['npv_cash'])
    rows.append((lbl, lo_v, hi_v, out[0], out[1]))
pr_rs = evm.prepare(data, pack, basis='role_score')
rows.append(('Basis: tasks vs Etter role score', 'tasks', 'role score', base, evm.simulate(pr_rs, MOD, ATT)['npv_cash']))
rows.sort(key=lambda r: -abs(r[4]-r[3]))
print(f"base cash NPV (Moderate, attrition only) {base/1e6:.2f}M")
for lbl, a, b, lo, hi in rows:
    flip = ' FLIPS SIGN' if (lo < 0) != (hi < 0) or (lo < 0) != (base < 0) or (hi < 0) != (base < 0) else ''
    print(f"  {lbl:34s} {str(round(a,3) if isinstance(a,float) else a):>8s} .. {str(round(b,3) if isinstance(b,float) else b):<10s} NPV {lo/1e6:7.2f}M .. {hi/1e6:7.2f}M  swing {abs(hi-lo)/1e6:6.2f}M{flip}")
json.dump(dict(base=base, rows=rows), open('experiments/out/out_sens.json','w'), indent=1)

print("\nMONTE CARLO bands (1,000 correlated draws around Moderate), cash NPV $M")
mc = {}
for pn in ['Capacity only', 'Attrition only', 'Active reduction']:
    res = evm.montecarlo(prep, MOD, evm.policy(pack, pn), n=1000)
    npv = [x['npv'] for x in res]; cap = [x['cap'] for x in res]; pay = [x['pay'] for x in res]
    paid = sorted(p for p in pay if p is not None)
    mc[pn] = dict(p10=evm.quantile(npv,.1), p50=evm.quantile(npv,.5), p90=evm.quantile(npv,.9),
                  ppos=sum(1 for x in npv if x > 0)/len(npv),
                  cap_p10=evm.quantile(cap,.1), cap_p50=evm.quantile(cap,.5), cap_p90=evm.quantile(cap,.9),
                  pay_p50=evm.quantile(paid,.5) if paid else None, pay_share=len(paid)/len(pay))
    m = mc[pn]
    print(f"  {pn:17s} P10 {m['p10']/1e6:6.2f}  P50 {m['p50']/1e6:6.2f}  P90 {m['p90']/1e6:6.2f}  P(cash>0) {m['ppos']*100:4.1f}%  | capacity P10-P90 {m['cap_p10']/1e6:5.1f}-{m['cap_p90']/1e6:5.1f}  | pays back in horizon {m['pay_share']*100:.0f}%, median month {m['pay_p50']}")
json.dump(mc, open('experiments/out/out_mc.json','w'), indent=1)
