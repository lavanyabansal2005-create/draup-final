import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'experiments')); os.chdir(ROOT)
import json, evm
data = json.load(open('data/etter_fpa.json')); pack = json.load(open('packs/base.json'))
prep = evm.prepare(data, pack)
for f in prep['flags']: print(f)
for sn in pack['scenarios']:
    for pn in pack['policies']:
        r = evm.simulate(prep, evm.scenario(pack, sn), evm.policy(pack, pn))
        print(f"{sn:12s} {pn:17s} built {r['n_built']:2d}  cashNPV {r['npv_cash']/1e6:7.2f}M  avoid {r['pv_avoidance']/1e6:6.2f}M  cap {r['pv_capacity']/1e6:6.2f}M  pay {r['payback_month']}  irr {r['irr'] if r['irr'] is None else round(r['irr']*100,1)}  peak {r['peak_funding']/1e6:5.2f}M  pos {r['positions_end']:.0f}  rec {r['check_reconciliation_max_gap']:.2e} mincap {r['check_min_capacity_h']:.1f}")
