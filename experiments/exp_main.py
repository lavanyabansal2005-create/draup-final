import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'experiments')); os.chdir(ROOT)
import json, copy, evm
data = json.load(open('data/etter_fpa.json')); pack = json.load(open('packs/base.json'))
prep = evm.prepare(data, pack)
MOD = evm.scenario(pack, 'Moderate'); ATT = evm.policy(pack, 'Attrition only')
OUT = {}
def summ(r):
    return dict(npv=r['npv_cash'], cap=r['pv_capacity'], pay=r['payback_month'], pos=r['positions_end'],
                built=r['n_built'], peak=r['peak_funding'], irr=r['irr'], hurdle=r['capacity_hurdle'])
def line(lbl, r):
    print(f"  {lbl:38s} cash NPV {r['npv_cash']/1e6:7.2f}M  cap {r['pv_capacity']/1e6:6.1f}M  payback {str(r['payback_month']):>4s}  pos {r['positions_end']:4.0f}  built {r['n_built']:2d}  peak {r['peak_funding']/1e6:5.2f}M")

print("A. SCOPE RULE (Moderate, attrition only)")
OUT['scope'] = {}
for lbl, o in [('cost-effective test (default)', {}), ('build every workload', {'scope_rule':'all'}),
               ('top 10 by ratio', {'scope_rule':'top_k','top_k':10}), ('top 20 by ratio', {'scope_rule':'top_k','top_k':20})]:
    r = evm.simulate(prep, MOD, ATT, o); line(lbl, r); OUT['scope'][lbl] = summ(r)

print("\nB. ADOPTION SHAPE")
OUT['ramp'] = {}
for lbl, o in [('S-curve (default)', {}), ('linear ramp', {'ramp':'linear'}), ('all workloads at once (no staging)', {'schedule':'all_at_once'})]:
    r = evm.simulate(prep, MOD, ATT, o); line(lbl, r); OUT['ramp'][lbl] = summ(r)

print("\nC. AUGMENTATION: experience-graded vs flat 12.3%")
OUT['aug'] = {}
p2 = copy.deepcopy(pack); p2['augment']['time_saving_by_band'] = {k: 0.123 for k in p2['augment']['time_saving_by_band']}
pr2 = evm.prepare(data, p2)
for lbl, pr in [('graded by band (default)', prep), ('flat 12.3% (v1/v2)', pr2)]:
    r = evm.simulate(pr, MOD, ATT); line(lbl, r); OUT['aug'][lbl] = summ(r)
    aug = sum(x['aug_fte'] for x in r['roles']); print(f"      assistant-freed FTE {aug:.1f}")

print("\nD. BASIS: task build-up vs Etter role score")
OUT['basis'] = {}
pr3 = evm.prepare(data, pack, basis='role_score')
for lbl, pr in [('task build-up (default)', prep), ('anchored to Etter role scores', pr3)]:
    r = evm.simulate(pr, MOD, ATT); line(lbl, r); OUT['basis'][lbl] = summ(r)
    ai = sum(R['N']*R['H']*R['auto_share'] for R in pr['roles'].values())/sum(R['N']*R['H'] for R in pr['roles'].values())
    print(f"      AI-able share {ai*100:.1f}%")

print("\nE. COMPLEXITY DRAG")
OUT['drag'] = {}
for k in [0.0, 0.3, 0.6]:
    S = dict(MOD, drag=k); r = evm.simulate(prep, S, ATT); line(f'drag {k}', r); OUT['drag'][k] = summ(r)

print("\nF. SCALE: same function, scaled headcount (Moderate)")
OUT['scale'] = []
for f in [0.02, 0.04, 0.08, 0.15, 0.3, 0.6, 1.0, 2.0]:
    d2 = copy.deepcopy(data)
    for rr in d2['roles']: rr['headcount'] = max(1, round(rr['headcount']*f))
    pr = evm.prepare(d2, pack)
    N = sum(R['N'] for R in pr['roles'].values())
    ra = evm.simulate(pr, MOD, ATT); rb = evm.simulate(pr, MOD, evm.policy(pack,'Active reduction'))
    rc = evm.simulate(pr, MOD, evm.policy(pack,'Capacity only'))
    print(f"  N={N:5d}  built {ra['n_built']:2d}  attrition NPV {ra['npv_cash']/1e6:7.2f}M ({ra['npv_cash']/N:7,.0f}/head)  active {rb['npv_cash']/1e6:7.2f}M  cap-only cash {rc['npv_cash']/1e6:6.2f}M cap {rc['pv_capacity']/1e6:6.2f}M  hurdle {rc['capacity_hurdle']:.2f}")
    OUT['scale'].append(dict(N=N, built=ra['n_built'], att=ra['npv_cash'], act=rb['npv_cash'], cap=rc['pv_capacity'], capcash=rc['npv_cash']))

print("\nG. PORTFOLIO: value concentration (Moderate)")
chosen, ranked = evm.scope(prep, MOD)
tot = sum(max(0, x['npv_at_cost']) for x in ranked)
cum = 0; cb = 0; pts = []
for i, x in enumerate(ranked):
    cum += max(0, x['npv_at_cost']); cb += x['build_s']; pts.append((i+1, cb, cum))
for k in [3, 5, 10, 20, 30, 49]:
    print(f"  top {k:2d} workloads: {pts[k-1][2]/tot*100:5.1f}% of value at cost, build ${pts[k-1][1]/1e6:.2f}M")
print("  top 5:", [(x['name'][:40], round(x['ratio'],1), x['tier']) for x in ranked[:5]])
print("  failing:", sum(1 for x in ranked if x['npv_at_cost'] <= 0), "of", len(ranked))
OUT['portfolio'] = [dict(rank=i+1, name=x['name'], ratio=x['ratio'], npv=x['npv_at_cost'], build=x['build_s'], tier=x['tier'], roles=len(x['roles'])) for i, x in enumerate(ranked)]

print("\nH. BREAK-EVEN: net realisation (takeover x (1-review)) for cash NPV = 0")
def be(pol, opts=None):
    ch, _ = evm.scope(prep, MOD)   # plan fixed at Moderate
    def f(net):
        S = dict(MOD, takeover=min(0.999, net/(1-MOD['review'])))
        return evm.simulate(prep, S, pol, dict(opts or {}, chosen=ch))['npv_cash']
    lo, hi = 0.0, 0.69
    if f(hi) < 0: return None
    for _ in range(40):
        mid = (lo+hi)/2
        if f(mid) >= 0: hi = mid
        else: lo = mid
    return hi
OUT['breakeven'] = {}
for pn in ['Attrition only', 'Active reduction']:
    b = be(evm.policy(pack, pn)); OUT['breakeven'][pn] = b
    print(f"  {pn:18s} break-even net realisation {b*100:.1f}%  (Moderate assumes {MOD['takeover']*(1-MOD['review'])*100:.0f}%)")

print("\nI. HORIZON")
OUT['horizon'] = {}
for T in [24, 36, 48, 60]:
    r = evm.simulate(prep, MOD, ATT, {'horizon': T}); line(f'{T} months', r); OUT['horizon'][T] = summ(r)
json.dump(OUT, open('experiments/out/out_main.json','w'), indent=1, default=str)
