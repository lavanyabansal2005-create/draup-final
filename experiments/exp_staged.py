"""K. Commit everything now vs pilot-then-decide, under the same uncertainty (common random numbers)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'experiments')); os.chdir(ROOT)

import json, math, evm
data = json.load(open('data/etter_fpa.json')); pack = json.load(open('packs/base.json'))
prep = evm.prepare(data, pack)
MOD = evm.scenario(pack, 'Moderate')
N = 1000
OUT = {}
for pn, be_net in [('Attrition only', 0.230), ('Active reduction', 0.091)]:
    POL = evm.policy(pack, pn)
    chosen, _ = evm.scope(prep, MOD)
    pilot = chosen[:pack['programme']['pilot_workloads']]
    rng = evm.RNG(20261019); mrng = evm.RNG(777)
    rows = []
    for i in range(N):
        dd = evm.draw_scenario(pack, rng); S = dict(MOD); S.update(dd)
        net_true = S['takeover'] * (1 - S['review'])
        commit = evm.simulate(prep, S, POL, {'chosen': chosen, 'schedule': 'all_at_once'})['npv_cash']
        phased = evm.simulate(prep, S, POL, {'chosen': chosen, 'schedule': 'staged'})
        obs = net_true * math.exp(0.25 * mrng.z())
        go = obs >= be_net
        if go:
            staged = phased['npv_cash']
        else:
            staged = evm.simulate(prep, S, POL, {'chosen': pilot, 'schedule': 'staged'})['npv_cash']
        nothing = 0.0
        rows.append(dict(net=net_true, commit=commit, phased=phased['npv_cash'], staged=staged, go=go))
    def st(k):
        xs = [r[k] for r in rows]
        return dict(mean=sum(xs)/N, p10=evm.quantile(xs, .1), p50=evm.quantile(xs, .5), p90=evm.quantile(xs, .9),
                    ploss=sum(1 for x in xs if x < 0)/N, mean_loss=sum(min(0, x) for x in xs)/N)
    res = {k: st(k) for k in ['commit', 'phased', 'staged']}
    # EVPI: knowing the truth, choose best of commit / nothing
    evpi = sum(max(r['commit'], 0.0) for r in rows)/N - max(res['commit']['mean'], 0.0)
    gate_go = sum(r['go'] for r in rows)/N
    wrong_stop = sum(1 for r in rows if (not r['go']) and r['commit'] > 0)/N
    wrong_go = sum(1 for r in rows if r['go'] and r['phased'] < 0)/N
    print(f"\n{pn}  (gate: scale if pilot shows net realisation >= {be_net:.1%})")
    for k, lbl in [('commit','Commit all now'), ('phased','Phased, no gate'), ('staged','Pilot, then decide')]:
        x = res[k]
        print(f"  {lbl:20s} mean {x['mean']/1e6:6.2f}M  P10 {x['p10']/1e6:6.2f}M  P50 {x['p50']/1e6:6.2f}M  P90 {x['p90']/1e6:6.2f}M  P(loss) {x['ploss']*100:4.1f}%  expected loss {x['mean_loss']/1e6:5.2f}M")
    print(f"  gate says go in {gate_go*100:.0f}% of worlds; wrongly stops {wrong_stop*100:.1f}%, wrongly goes {wrong_go*100:.1f}%")
    print(f"  EVPI (value of knowing realisation before committing): {evpi/1e6:.2f}M")
    OUT[pn] = dict(res=res, evpi=evpi, gate_go=gate_go, wrong_stop=wrong_stop, wrong_go=wrong_go)
json.dump(OUT, open('experiments/out/out_staged.json', 'w'), indent=1)
