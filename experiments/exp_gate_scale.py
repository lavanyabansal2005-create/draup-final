"""K2. When is a pilot gate worth it?  Phased rollout with vs without a go/no-go gate, across scale."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'experiments')); os.chdir(ROOT)

import json, math, copy, evm
data = json.load(open('data/etter_fpa.json')); pack = json.load(open('packs/base.json'))
MOD = evm.scenario(pack, 'Moderate'); POL = evm.policy(pack, 'Attrition only')
N = 600
OUT = []
def be_net(prep, chosen):
    def f(net):
        S = dict(MOD, takeover=min(0.999, net/(1-MOD['review'])))
        return evm.simulate(prep, S, POL, dict(chosen=chosen))['npv_cash']
    lo, hi = 0.0, 0.69
    if f(hi) < 0: return None
    if f(lo) >= 0: return 0.0
    for _ in range(30):
        mid = (lo+hi)/2
        if f(mid) >= 0: hi = mid
        else: lo = mid
    return hi
for fct in [0.3, 0.45, 0.6, 1.0, 2.0]:
    d2 = copy.deepcopy(data)
    for rr in d2['roles']: rr['headcount'] = max(1, round(rr['headcount']*fct))
    prep = evm.prepare(d2, pack)
    chosen, _ = evm.scope(prep, MOD)
    pilot = chosen[:3]
    b = be_net(prep, chosen)
    rng = evm.RNG(20261019); mrng = evm.RNG(777)
    ph, gt = [], []
    for i in range(N):
        dd = evm.draw_scenario(pack, rng); S = dict(MOD); S.update(dd)
        net = S['takeover']*(1-S['review'])
        p = evm.simulate(prep, S, POL, {'chosen': chosen})['npv_cash']
        obs = net*math.exp(0.25*mrng.z())
        g = p if (b is not None and obs >= b) else evm.simulate(prep, S, POL, {'chosen': pilot})['npv_cash']
        ph.append(p); gt.append(g)
    hc = sum(R['N'] for R in prep['roles'].values())
    mean = lambda xs: sum(xs)/len(xs)
    pl = lambda xs: sum(1 for x in xs if x < 0)/len(xs)
    el = lambda xs: sum(min(0,x) for x in xs)/len(xs)
    row = dict(N=hc, be=b, phased_mean=mean(ph), gated_mean=mean(gt), phased_ploss=pl(ph), gated_ploss=pl(gt),
               phased_p10=evm.quantile(ph,.1), gated_p10=evm.quantile(gt,.1), phased_el=el(ph), gated_el=el(gt))
    OUT.append(row)
    print(f"N={hc:5d}  break-even net {b if b is None else round(b*100,1)}%  | no gate: mean {row['phased_mean']/1e6:6.2f}M P10 {row['phased_p10']/1e6:6.2f}M P(loss) {row['phased_ploss']*100:4.1f}%  | gate: mean {row['gated_mean']/1e6:6.2f}M P10 {row['gated_p10']/1e6:6.2f}M P(loss) {row['gated_ploss']*100:4.1f}%  | gate value {(row['gated_mean']-row['phased_mean'])/1e6:+.2f}M")
json.dump(OUT, open('experiments/out/out_gate_scale.json','w'), indent=1)
