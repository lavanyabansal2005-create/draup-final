"""FP&A AI financial model, v2. Research-backed cost build-up + decomposed delivery rate.
Every change from v1 is behind a flag so it can be ablated individually."""
import json, math
from collections import defaultdict

import os as _os
D = json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'data', 'etter_fpa.json')))
TASKS, ROLES = D['tasks'], D['roles']
norm = lambda s: s.strip().lower().replace(' & ', ' and ')

CEIL = {'Directive':0.85,'Feedback Loop':0.55,'Task Iteration':0.45,
        'Learning':0.25,'Validation':0.50,'Negligibility':0.0}
BUCKET = {'Directive':'ai','Feedback Loop':'ai','Task Iteration':'help',
          'Learning':'help','Validation':'help','Negligibility':'human'}
TURN = {'Para-professional':0.125,'Professional':0.091,'Management':0.063,'Executive':0.052}

# ---- scenario dials: delivery rate decomposed into three sourced components ----
SCEN = {
 'Conservative': dict(coverage=0.35, comeback=0.25, routing=0.60, adopt_months=18, reduce=0.25, active=0.55),
 'Base':         dict(coverage=0.50, comeback=0.20, routing=0.75, adopt_months=9,  reduce=0.50, active=0.70),
 'Aggressive':   dict(coverage=0.70, comeback=0.15, routing=0.90, adopt_months=6,  reduce=0.65, active=0.85),
}

P0 = dict(
  scenario='Base',
  # pay and time
  hours_year=1920, wage_share=0.700, leave_share=0.075,      # BLS ECEC Jun-2026 private industry T4
  disc=0.0703, window=60, useful=0.65,
  # AI help
  help_save=0.123, seat_share=0.60,
  # costs
  licence=360, licence_growth=0.0,
  action_cost=0.30, actions_per_hour=4.0,                    # bottom-up: Copilot Studio metering
  outcome_price=2.00, hours_per_outcome=0.575,               # top-down: Agentforce per conversation
  build_workflow=55000, build_enterprise=130000,             # sourced bands, upper end
  prog_setup=75000, deploy_per_seat=623,                     # Forrester TEI full study
  mgmt_per_seat_year=160.66,                                 # Forrester ongoing mgmt / avg seats
  reskill_spend=846, reskill_hours=16.7,                     # ATD 2026
  cost_decay=-0.13,
  cost_per_hire=4700,                                        # SHRM
  agent_maint_share=0.18,                                    # 15-20% custom-software maintenance convention
  # feature flags (all True = v2; all False = v1 behaviour)
  f_oncost=True, f_build_tier=True, f_running_buildup=True, f_impl_decomp=True,
  f_training_seats=True, f_mgmt_line=True, f_active_use=True, f_avoided_hire=True,
  f_agent_maint=True,
)
V1 = dict(wage_share=0.685, leave_share=0.081, f_oncost=False, f_build_tier=False,
          f_running_buildup=False, f_impl_decomp=False, f_training_seats=False,
          f_mgmt_line=False, f_active_use=False, f_avoided_hire=False, f_agent_maint=False)

def tier_of(w):
    """Build tier from the Etter data itself: integration surface, not hours."""
    if w['nai'] == 0: return 'none'
    return 'enterprise' if (len(w['roles']) >= 2 or w['nai'] >= 3) else 'workflow'

def run(over=None, delivery=None):
    p = {**P0, **(over or {})}
    s = SCEN[p['scenario']]
    p = {**s, **p} if over and any(k in over for k in s) else {**p, **s, **(over or {})}
    # composite delivery rate
    d = delivery if delivery is not None else p['coverage']*(1-p['comeback'])*p['routing']
    on_cost = 1/(p['wage_share']+p['leave_share'])
    run_hr = (max(p['action_cost']*p['actions_per_hour'], p['outcome_price']/p['hours_per_outcome'])
              if p['f_running_buildup'] else 3.48)
    R = {}
    for r in ROLES:
        loaded = r['salary']*on_cost
        R[r['role']] = dict(**r, loaded=loaded, hourly=loaded/p['hours_year'],
                            lam=TURN[r['turnover_level']])
    ann = sum(min(1, m/p['adopt_months'])*(1+p['disc'])**(-m/12)
              for m in range(1, p['window']+1))/12
    T = []
    for t in TASKS:
        role = R[t['role']]; cat = t['category']; b = BUCKET[cat]
        hy = t['hours_month']*12*role['headcount']
        T.append(dict(t, wl=norm(t['workload']), bucket=b, ceil=CEIL[cat], hy=hy,
                      hourly=role['hourly'], M=hy*CEIL[cat] if b == 'ai' else 0.0))
    W = defaultdict(lambda: dict(M=0.0, val=0.0, n=0, nai=0, roles=set()))
    for t in T:
        w = W[t['wl']]; w['M'] += t['M']; w['val'] += t['M']*t['hourly']
        w['n'] += 1; w['nai'] += (t['bucket'] == 'ai'); w['roles'].add(t['role'])
    for k, w in W.items():
        w['tier'] = tier_of(w)
        w['build'] = ({'workflow': p['build_workflow'], 'enterprise': p['build_enterprise'],
                       'none': p['build_workflow']}[w['tier']] if p['f_build_tier'] else 85000)
        w['net'] = w['val']*p['useful'] - w['M']*run_hr
        w['be'] = 9.99 if w['net'] <= 0 else w['build']/(w['net']*ann)
        w['built'] = w['be'] <= d
    for t in T:
        t['built'] = W[t['wl']]['built']
        t['P'] = t['M']*d if (t['bucket'] == 'ai' and t['built']) else 0.0
        act = p['active'] if p['f_active_use'] else 1.0
        t['Q'] = (t['hy']*min(t['ceil'], p['help_save'])*p['seat_share']*act
                  if t['bucket'] == 'help' else 0.0)
        t['cap'] = (t['P']+t['Q'])*t['hourly']*p['useful']
        t['runcost'] = t['P']*run_hr
    for role in R.values():
        rt = [t for t in T if t['role'] == role['role']]
        role['L'] = sum(t['P'] for t in rt); role['Mh'] = sum(t['Q'] for t in rt)
        role['capval'] = sum(t['cap'] for t in rt); role['run'] = sum(t['runcost'] for t in rt)
        role['pe'] = role['L']/p['hours_year']
        role['pos'] = math.floor(role['pe']*p['reduce']+1e-6)
        role['seats'] = round(role['headcount']*p['seat_share'])
        role['lic'] = role['seats']*p['licence']
        role['mgmt'] = role['seats']*p['mgmt_per_seat_year'] if p['f_mgmt_line'] else 0.0
        role['reskill'] = (role['headcount']*p['reskill_spend']
                           + (role['seats'] if p['f_training_seats'] else role['headcount'])
                             * p['reskill_hours']*role['hourly'])
    tot = lambda k: sum(r[k] for r in R.values())
    builds = {t: sum(1 for w in W.values() if w['built'] and w['tier'] == t)
              for t in ('workflow','enterprise','none')}
    nb = sum(builds.values())
    build_cost = sum(w['build'] for w in W.values() if w['built'])
    decay = lambda start: (1+p['cost_decay'])**(start/12)
    def onetime(start):
        if p['f_impl_decomp']:
            impl = p['prog_setup'] + p['deploy_per_seat']*tot('seats')
        else:
            impl = 75000 + 765*tot('headcount')
        return (impl+build_cost)*decay(start) + tot('reskill')
    maint = build_cost*p['agent_maint_share'] if p['f_agent_maint'] else 0.0
    def go(start=0):
        ot = onetime(start)
        cash_m, cap_m, lic_m, run_m, mg_m, hire_m, mt_m = [], [], [], [], [], [], []
        cum, payback = 0.0, None
        prev_pos = 0.0
        for m in range(1, p['window']+1):
            ad = min(1, m/p['adopt_months'])
            pos = sum(min(r['pos']*ad, r['headcount']*(1-(1-r['lam']/12)**m)) for r in R.values())
            cash_m.append(sum(min(r['pos']*ad, r['headcount']*(1-(1-r['lam']/12)**m))*r['loaded']/12
                              for r in R.values()))
            cap_m.append(tot('capval')/12*ad)
            lic_m.append(tot('lic')/12*ad*(1+p['licence_growth'])**(m/12))
            run_m.append(tot('run')/12*ad); mg_m.append(tot('mgmt')/12*ad)
            mt_m.append(maint/12*ad)
            hire_m.append(max(0.0, pos-prev_pos)*p['cost_per_hire'] if p['f_avoided_hire'] else 0.0)
            prev_pos = pos
            cum += (cash_m[-1]+hire_m[-1]-lic_m[-1]-run_m[-1]-mg_m[-1]-mt_m[-1]
                    -(ot if m == 1 else 0))
            if cum < 0: payback = None
            elif payback is None: payback = m
        df = lambda m: (1+p['disc'])**(-(start+m)/12)
        pv = lambda xs: sum(x*df(i+1) for i, x in enumerate(xs) if i+1 <= p['window']-start)
        cost_pv = pv(lic_m)+pv(run_m)+pv(mg_m)+pv(mt_m)+ot*(1+p['disc'])**(-start/12)
        return dict(start=start, onetime=ot, cash_pv=pv(cash_m), cap_pv=pv(cap_m),
                    hire_pv=pv(hire_m), cost_pv=cost_pv,
                    cashnpv=pv(cash_m)-cost_pv, cashnpv_inc_hire=pv(cash_m)+pv(hire_m)-cost_pv,
                    capnpv=pv(cap_m)-cost_pv, payback=payback)
    starts = [go(s) for s in (0,6,12,18,24)] + [dict(start='never', cashnpv=0.0, capnpv=0.0,
                                                     cashnpv_inc_hire=0.0, payback=None, onetime=0,
                                                     cash_pv=0, cap_pv=0, hire_pv=0, cost_pv=0)]
    best_cash = max(starts, key=lambda x: x['cashnpv'])
    best_cap = max(starts, key=lambda x: x['capnpv'])
    n0 = starts[0]
    return dict(p=p, delivery=d, on_cost=on_cost, run_hr=run_hr, ann=ann, R=R, W=W, T=T,
                builds=builds, nbuilds=nb, build_cost=build_cost,
                positions=tot('pos'), share=tot('pos')/tot('headcount'),
                cash_yr=sum(r['pos']*r['loaded'] for r in R.values()),
                freed_ai=tot('L'), freed_help=tot('Mh'), capval=tot('capval'),
                lic_yr=tot('lic'), run_yr=tot('run'), mgmt_yr=tot('mgmt'),
                reskill=tot('reskill'), seats=tot('seats'), maint_yr=maint,
                onetime=n0['onetime'], cashnpv=n0['cashnpv'],
                cashnpv_inc_hire=n0['cashnpv_inc_hire'], capnpv=n0['capnpv'],
                hire_pv=n0['hire_pv'], payback=n0['payback'], starts=starts,
                best_cash=best_cash['start'], best_cap=best_cap['start'])

def breakeven(over=None, kind='cash'):
    grid = [i/100 for i in range(101)]
    vals = [run(over, delivery=x)[{'cash':'cashnpv','cash_hire':'cashnpv_inc_hire',
                                   'cap':'capnpv'}[kind]] for x in grid]
    if vals[0] >= 0: return 0.0
    for i in range(1, 101):
        if vals[i] >= 0:
            return grid[i-1]-vals[i-1]*(grid[i]-grid[i-1])/(vals[i]-vals[i-1])
    return None

if __name__ == '__main__':
    v1 = run(V1, delivery=0.30)
    print('--- sanity: v2 engine with v1 flags reproduces v1 ---')
    print(f"  cash NPV {v1['cashnpv']:,.0f}  (v1 workbook 9,653,145)   capacity {v1['capnpv']:,.0f}  (39,032,171)")
    print(f"  positions {v1['positions']}  builds {v1['nbuilds']}  one-time {v1['onetime']:,.0f}")
    r = run()
    print('\n--- v2, Base ---')
    print(f"  on-cost            {r['on_cost']:.4f}   (was 1.3055)")
    print(f"  delivery composite {r['delivery']*100:.1f}%  = coverage {r['p']['coverage']:.2f}"
          f" x (1-comeback {r['p']['comeback']:.2f}) x routing {r['p']['routing']:.2f}")
    print(f"  running cost       ${r['run_hr']:.2f}/AI-hour")
    print(f"  builds             {r['nbuilds']} of {len(r['W'])}  {r['builds']}   cost ${r['build_cost']:,.0f}")
    print(f"  positions          {r['positions']} ({r['share']*100:.2f}%)")
    print(f"  freed AI / help    {r['freed_ai']:,.0f} / {r['freed_help']:,.0f} h")
    print(f"  one-time           ${r['onetime']:,.0f}")
    print(f"  recurring          lic ${r['lic_yr']:,.0f}  run ${r['run_yr']:,.0f}  mgmt ${r['mgmt_yr']:,.0f}")
    print(f"  cash NPV           ${r['cashnpv']:,.0f}   (+avoided hire ${r['cashnpv_inc_hire']:,.0f})")
    print(f"  capacity NPV       ${r['capnpv']:,.0f}")
    print(f"  payback            {r['payback']}   best start cash {r['best_cash']} / cap {r['best_cap']}")
    print(f"  break-even cash    {breakeven()*100:.2f}%   (v1 16.41%)")
