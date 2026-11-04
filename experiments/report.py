import evm
def costs_pv(r):
    s = r['series']; d = r['rate']
    keys = ['build','programme','training','licences','run','maintenance','severance','hard','seats_reclaimed','recruit_avoided','avoidance','capacity']
    return {k: evm.pv(s[k], d) for k in keys}
def show(r, label=''):
    c = costs_pv(r)
    print(f"--- {label}  built {r['n_built']} build ${r['build_total']/1e6:.2f}M")
    print('  savings PV: hard {hard:,.0f}  seats {seats_reclaimed:,.0f}  recruit {recruit_avoided:,.0f} | avoidance {avoidance:,.0f} | capacity {capacity:,.0f}'.format(**c))
    print('  costs PV:   build {build:,.0f}  programme {programme:,.0f}  training {training:,.0f}  licences {licences:,.0f}  run {run:,.0f}  maint {maintenance:,.0f}  sev {severance:,.0f}'.format(**c))
    print(f"  cash NPV {r['npv_cash']:,.0f}  payback {r['payback_month']}  peak {r['peak_funding']:,.0f}  positions {r['positions_end']}  freedFTE(ss) {r['freed_fte_end']:.1f}  hurdle {r['capacity_hurdle']:.3f}")
