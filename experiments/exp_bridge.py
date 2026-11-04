"""L. Bridge from the last model the team showed (v1 workbook) to the new engine, one change at a time.
   M. Conversion curve: Etter automation score -> share of positions, mechanism by mechanism (synthetic role)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'experiments')); os.chdir(ROOT)

import json, copy, math, sys, evm
sys.path.insert(0, os.path.join(ROOT, 'experiments', 'legacy'))
import engine_v2 as E2
v1 = E2.run(E2.V1, delivery=0.30)
print(f"v1 workbook (Base): cash NPV {v1['cashnpv']/1e6:.2f}M  positions {v1['positions']}  payback {v1['payback']}  capacity {v1['capnpv']/1e6:.1f}M")
data = json.load(open('data/etter_fpa.json')); pack = json.load(open('packs/base.json'))
MOD = evm.scenario(pack, 'Moderate'); ATT = evm.policy(pack, 'Attrition only')
# Step 0: new engine configured as close to v1 as the structure allows
p = copy.deepcopy(pack)
p['augment']['time_saving_by_band'] = {k: 0.123 for k in p['augment']['time_saving_by_band']}
p['economics']['discount_rate'] = 0.0703
p['costs'].update(dict(build_workflow=85000, build_enterprise=85000, maintenance_share_per_year=0.0,
                       programme_fixed=75000, deploy_per_affected_head=765, seat_cost_per_position=0,
                       run_cost_decline_per_year=0.13))
S = dict(MOD, takeover=0.30, review=0.0, adopt_months=9, active_use=0.6, aug_mult=1.0, cost_mult=1.0, drag=0.0)
pol = dict(ATT, harvest_automation=0.5)
steps = []
def run(label, pk, S_, pol_, opts):
    pr = evm.prepare(data, pk)
    r = evm.simulate(pr, S_, pol_, dict(ramp='linear', **opts))
    steps.append((label, r['npv_cash'], r['positions_end'], r['payback_month'], r['pv_capacity'], r['n_built']))
    print(f"  {label:58s} cash NPV {r['npv_cash']/1e6:7.2f}M  positions {r['positions_end']:4.0f}  payback {str(r['payback_month']):>4s}  capacity {r['pv_capacity']/1e6:5.1f}M  built {r['n_built']}")
    return pr
run('0  new engine, v1 settings (30% delivery, 50% reduce, all at once)', p, S, pol, {'schedule': 'all_at_once'})
p1 = copy.deepcopy(p); p1['costs'].update(build_workflow=55000, build_enterprise=130000)
run('1  + build cost tiered by integration surface', p1, S, pol, {'schedule': 'all_at_once'})
p2 = copy.deepcopy(p1); p2['costs'].update(maintenance_share_per_year=0.18, programme_fixed=75000, deploy_per_affected_head=623, seat_cost_per_position=468)
run('2  + maintenance 18%/yr, v5 deployment cost, seats reclaimed', p2, S, pol, {'schedule': 'all_at_once'})
p3 = copy.deepcopy(p2); p3['economics']['discount_rate'] = 0.0696
S3 = dict(S, takeover=0.40, review=0.30)
run('3  + delivery split: takeover 40% x (1 - review 30%) = 28%', p3, S3, pol, {'schedule': 'all_at_once'})
S4 = dict(S3, adopt_months=12)
run('4  + 12-month adoption S-curve', p3, S4, pol, {'schedule': 'all_at_once'})
p5 = copy.deepcopy(p3); p5['augment']['time_saving_by_band'] = pack['augment']['time_saving_by_band']
S5 = dict(S4, active_use=0.7)
run('5  + assistant saving graded by seniority, 70% active use', p5, S5, pol, {'schedule': 'all_at_once'})
S6 = dict(S5, drag=0.3)
run('6  + complexity drag 0.3', p5, S6, pol, {'schedule': 'all_at_once'})
run('7  + phased rollout: pilot, then waves of 10 per quarter', p5, S6, pol, {'schedule': 'staged'})
pol8 = dict(pol, harvest_automation=0.75)
run('   (policy variant: harvest 75% instead of 50%)', p5, S6, pol8, {'schedule': 'staged'})
pr = evm.prepare(data, pack)
r = evm.simulate(pr, MOD, ATT)
print(f"  {'=  new engine default (Moderate, attrition only)':58s} cash NPV {r['npv_cash']/1e6:7.2f}M  positions {r['positions_end']:4.0f}  payback {r['payback_month']}")
json.dump(dict(v1=dict(npv=v1['cashnpv'], pos=v1['positions'], pay=v1['payback'], cap=v1['capnpv']), steps=steps,
               final=dict(npv=r['npv_cash'], pos=r['positions_end'], pay=r['payback_month'])), open('experiments/out/out_bridge.json','w'), indent=1)

print("\nM. CONVERSION CURVE: one synthetic role of 1,000 people, $90k salary, Professional band")
curve = []
for score in [0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50,0.60,0.70,0.80]:
    # role whose AI-able share equals `score` after ceilings: put hours in Directive (ceiling .85)
    h_dir = 160*score/0.85
    tasks = [dict(role='X', workload='w%d'%i, task='t', category='Directive', hours_month=h_dir/4) for i in range(4)]
    tasks.append(dict(role='X', workload='human', task='h', category='Negligibility', hours_month=160-h_dir))
    d = dict(tasks=tasks, roles=[dict(role='X', level='IC', headcount=1000, salary=90000, turnover_level='Professional', etter_score=score)])
    pk = copy.deepcopy(pack); pk['programme']['pilot_workloads'] = 4
    pr = evm.prepare(d, pk)
    out = {}
    for lbl, S_, pol_ in [('takeover only', dict(MOD, review=0.0, drag=0.0), dict(ATT, mechanism='separation', harvest_automation=1.0, notice_months=0, severance_weeks=0)),
                          ('+ review', dict(MOD, drag=0.0), dict(ATT, mechanism='separation', harvest_automation=1.0, notice_months=0, severance_weeks=0)),
                          ('+ complexity drag', MOD, dict(ATT, mechanism='separation', harvest_automation=1.0, notice_months=0, severance_weeks=0)),
                          ('+ policy (attrition, 50% harvest)', MOD, ATT)]:
        rr = evm.simulate(pr, S_, pol_, {'scope_rule': 'all', 'aug_on': False, 'horizon': 120})
        out[lbl] = rr['positions_end']/1000
    curve.append(dict(score=score, **out))
    print(f"  score {score:4.0%}: " + '  '.join(f"{k} {v:5.1%}" for k, v in out.items()))
json.dump(curve, open('experiments/out/out_curve.json','w'), indent=1)
