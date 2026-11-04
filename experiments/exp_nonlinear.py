"""E2/E3: is the automation -> headcount mapping non-linear, and where does the non-linearity come from?"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'experiments')); os.chdir(ROOT)

import json, copy, evm
data = json.load(open('data/etter_fpa.json')); pack = json.load(open('packs/base.json'))
prep = evm.prepare(data, pack)
roles = prep['roles']
N = sum(R['N'] for R in roles.values())
hours = sum(R['N']*R['H'] for R in roles.values())
pay = sum(R['N']*R['C'] for R in roles.values())
ai_h = sum(R['N']*R['H']*R['auto_share'] for R in roles.values())
ai_pay = sum(R['N']*R['C']*R['auto_share'] for R in roles.values())
aug_h = sum(R['N']*R['aug'] for R in roles.values())
raw_ai = sum(R['N']*(R['hours_by_cat'].get('Directive',0)+R['hours_by_cat'].get('Feedback Loop',0)) for R in roles.values())
print(f"headcount {N}, loaded payroll ${pay/1e6:.1f}M")
print(f"hours in AI categories (Directive+FB): {raw_ai/hours*100:.1f}% of hours")
print(f"AI-able after category ceilings:     {ai_h/hours*100:.1f}% of hours, {ai_pay/pay*100:.1f}% of payroll")
print(f"assist-able time saving (aug):       {aug_h/hours*100:.1f}% of hours")

# The funnel at Moderate / Attrition only
sc = evm.scenario(pack,'Moderate'); po = evm.policy(pack,'Attrition only')
r = evm.simulate(prep, sc, po)
built = {x['name'] for x in r['chosen']}
in_scope_h = sum(R['N']*sum(a for w,a in R['auto'].items() if w in built) for R in roles.values())
net = sc['takeover']*(1-sc['review'])
s = r['series']; T = r['T']
print("\nFUNNEL (Moderate, attrition only), FTE equivalents at month 60")
fte = lambda h: h/ (hours/N)
print(f"  1 hours in AI categories        {raw_ai/(hours/N):8.1f} FTE  ({raw_ai/hours*100:.1f}%)")
print(f"  2 AI-able (category ceilings)   {ai_h/(hours/N):8.1f}")
print(f"  3 in workloads worth building   {in_scope_h/(hours/N):8.1f}")
print(f"  4 AI takes over ({sc['takeover']:.0%})          {in_scope_h*sc['takeover']/(hours/N):8.1f}")
print(f"  5 net of human review ({sc['review']:.0%})   {in_scope_h*net/(hours/N):8.1f}")
print(f"  + assistants (augmentation)     {sum(rr['aug_fte'] for rr in r['roles']):8.1f}")
print(f"  6 positions removed (policy)    {r['positions_end']:8.0f}  ({r['positions_end']/N*100:.1f}% of headcount)")

# per-role scatter: potential vs positions share, three policies
print("\nROLE: AI-able share vs positions removed share (Moderate)")
res = {pn: evm.simulate(prep, sc, evm.policy(pack,pn)) for pn in ['Attrition only','Active reduction']}
for R in roles.values():
    a = {x['role']:x for x in res['Attrition only']['roles']}[R['role']]['positions_end']/R['N']
    b = {x['role']:x for x in res['Active reduction']['roles']}[R['role']]['positions_end']/R['N']
    print(f"  {R['role']:30s} AI-able {R['auto_share']*100:5.1f}%  attrition {a*100:5.1f}%  active {b*100:5.1f}%")

# Sweep: scale the Etter automation potential and watch headcount
print("\nSWEEP: scale Etter automation potential (all ceilings x k) -> positions removed")
rows=[]
for k in [0.25,0.5,0.75,1.0,1.25,1.5,1.75,2.0]:
    p2 = copy.deepcopy(pack)
    for c in ['Directive','Feedback Loop']:
        p2['categories'][c]['ceiling'] = min(1.0, pack['categories'][c]['ceiling']*k)
    pr2 = evm.prepare(data, p2)
    pot = sum(R['N']*R['H']*R['auto_share'] for R in pr2['roles'].values())/hours
    out=[]
    for pn in ['Attrition only','Active reduction']:
        rr = evm.simulate(pr2, sc, evm.policy(p2,pn))
        out.append(rr['positions_end']/N)
    rows.append((k,pot,out))
    print(f"  k={k:4.2f}  AI-able {pot*100:5.1f}%  -> positions: attrition {out[0]*100:5.2f}%  active {out[1]*100:5.2f}%   ratio(active/potential) {out[1]/pot:.3f}")
json.dump(dict(rows=rows), open('experiments/out/out_nonlinear.json','w'))
