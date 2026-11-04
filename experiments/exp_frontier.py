"""G2. Programme size: cash NPV and capacity as more workloads are built, in rank order."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'experiments')); os.chdir(ROOT)

import json, evm
data = json.load(open('data/etter_fpa.json')); pack = json.load(open('packs/base.json'))
prep = evm.prepare(data, pack)
MOD = evm.scenario(pack, 'Moderate')
_, ranked = evm.scope(prep, MOD)
rows = []
for k in [0, 3, 5, 10, 15, 20, 25, 30, 40, 49, 59]:
    ch = ranked[:k]
    a = evm.simulate(prep, MOD, evm.policy(pack, 'Attrition only'), {'chosen': ch})
    b = evm.simulate(prep, MOD, evm.policy(pack, 'Active reduction'), {'chosen': ch})
    c = evm.simulate(prep, MOD, evm.policy(pack, 'Capacity only'), {'chosen': ch})
    rows.append(dict(k=k, att=a['npv_cash'], act=b['npv_cash'], capcash=c['npv_cash'], cap=c['pv_capacity'],
                     build=a['build_total'], pay_att=a['payback_month']))
    print(f"  k={k:2d}  build ${a['build_total']/1e6:4.2f}M  attrition {a['npv_cash']/1e6:6.2f}M (payback {a['payback_month']})  active {b['npv_cash']/1e6:6.2f}M  capacity-only cash {c['npv_cash']/1e6:6.2f}M, capacity {c['pv_capacity']/1e6:5.1f}M")
json.dump(rows, open('experiments/out/out_frontier.json', 'w'), indent=1)
