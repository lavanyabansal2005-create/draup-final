import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'experiments')); os.chdir(ROOT)
import json, math, evm, archetype
data = json.load(open('data/etter_fpa.json')); pack = json.load(open('packs/base.json'))
A = json.load(open('packs/archetypes.json'))
OUT = {}
def be_net(prep, S0, pol, chosen):
    def f(net):
        S = dict(S0, takeover=min(0.999, net/(1-S0['review'])))
        return evm.simulate(prep, S, pol, dict(chosen=chosen))['npv_cash']
    lo, hi = 0.0, 0.69
    if f(hi) < 0: return None
    if f(lo) >= 0: return 0.0
    for _ in range(30):
        mid = (lo+hi)/2
        if f(mid) >= 0: hi = mid
        else: lo = mid
    return hi
for key, arch in A.items():
    d2, p2 = archetype.build(data, pack, arch)
    prep = evm.prepare(d2, p2)
    pol = evm.policy(p2, arch['default_policy'])
    N = sum(R['N'] for R in prep['roles'].values())
    print(f"\n== {arch['label']}  ({N} FP&A staff, policy: {arch['default_policy']}, WACC {p2['economics']['discount_rate']:.2%}, growth {p2['economics']['function_growth']:.0%})")
    sc = {}
    for sn in ['Conservative','Moderate','Aggressive']:
        r = evm.simulate(prep, evm.scenario(p2, sn), pol)
        sc[sn] = dict(npv=r['npv_cash'], avoid=r['pv_avoidance'], cap=r['pv_capacity'], pay=r['payback_month'],
                      pos=r['positions_end'], avoided=r['avoided_end'], built=r['n_built'], hurdle=r['capacity_hurdle'], peak=r['peak_funding'])
        print(f"  {sn:12s} built {r['n_built']:2d}  cash NPV {r['npv_cash']/1e6:7.2f}M  avoidance {r['pv_avoidance']/1e6:6.2f}M  capacity {r['pv_capacity']/1e6:6.2f}M  payback {r['payback_month']}  positions {r['positions_end']}  hires avoided {r['avoided_end']}  hurdle {r['capacity_hurdle']:.2f}")
    MOD = evm.scenario(p2, 'Moderate')
    chosen, _ = evm.scope(prep, MOD)
    b = be_net(prep, MOD, pol, chosen) if chosen else None
    mc = evm.montecarlo(prep, MOD, pol, n=600, keep=True)
    growth = p2['economics']['function_growth'] > 0
    npv = [x['npv_cash'] + (x['pv_avoidance'] if growth else 0) for x in mc]
    ppos = sum(1 for x in npv if x > 0)/len(npv)
    q = lambda p: evm.quantile(npv, p)
    basis = 'cash vs approved plan (incl. hires avoided)' if growth else 'cash vs today'
    if ppos >= 0.8: rec = 'Go: phased rollout, no pause needed.'
    elif ppos >= 0.4: rec = 'Pilot first: decide at the gate.'
    elif pol['harvest_automation'] == 0: rec = 'Capacity case only: fund if leadership commits to use the released time.'
    else: rec = 'Do not start on cash grounds.'
    rec += f'  [{basis}]'
    print(f"  Monte Carlo cash NPV P10 {q(.1)/1e6:.2f}M  P50 {q(.5)/1e6:.2f}M  P90 {q(.9)/1e6:.2f}M  P(cash>0) {ppos*100:.0f}%   break-even net realisation {b if b is None else round(b*100,1)}%")
    print(f"  -> {rec}")
    OUT[key] = dict(label=arch['label'], N=N, policy=arch['default_policy'], scenarios=sc, p10=q(.1), p50=q(.5), p90=q(.9), ppos=ppos, be=b, rec=rec)
json.dump(OUT, open('experiments/out/out_archetypes.json','w'), indent=1)
