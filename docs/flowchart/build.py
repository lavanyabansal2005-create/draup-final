"""Build docs/Etter_Value_Model_flowchart.pdf from the engine, so the flowchart cannot go stale.

    python3 docs/flowchart/build.py           # fills template.html from the engine, prints the PDF
    python3 docs/flowchart/build.py --html    # also keeps the filled page as docs/flowchart/flowchart.html

Page 1 is the model on one page; page 2 is what changed since 23 October and what Chandan
is asked to decide. Every number comes from evm.py at the defaults (Etter FP&A data,
Moderate, Attrition only, cross-industry), except the 23 October odds and verdict, which
are quoted from that run and checked against the legacy engine where it can reproduce them.

Printing needs Node and Playwright with Chromium (the page size is set in the template's CSS).
Without them, use --html and print the page from Chrome: margins none, background graphics on.
"""
import copy, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import evm  # noqa: E402

DATE = '5 November 2026'
OUT_PDF = os.path.join(ROOT, 'docs', 'Etter_Value_Model_flowchart.pdf')
DATA = json.load(open(os.path.join(ROOT, 'data', 'etter_fpa.json')))
PACK = json.load(open(os.path.join(ROOT, 'packs', 'base.json')))
MINUS = '−'


# ------------------------------------------------------------------ formatting
def M(x, d=2, sign=False):
    """Dollars in millions: $7.02M, -$4.8M, +$20.7M."""
    s = f'${abs(x) / 1e6:,.{d}f}M'
    return MINUS + s if x < 0 else ('+' + s if sign else s)


def D(x, d=0):
    s = f'${abs(x):,.{d}f}'
    return MINUS + s if x < 0 else s


def P(x, d=0):
    return f'{x * 100:.{d}f}%'


def N(x, d=0):
    return f'{x:,.{d}f}'


def signed(x, d=2):
    return M(x, d, sign=True)


def Kd(x, sign=False):
    """Dollars in thousands, so a bridge adds up exactly on the page."""
    v = round(x / 1e3)
    s = f'{abs(v):,}'
    return MINUS + s if v < 0 else ('+' + s if sign else s)


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


# ------------------------------------------------------------------ the runs
def sized(pack, S, Q, opts=None):
    prep = evm.prepare(DATA, pack)
    passing, ranked = evm.scope(prep, S)
    chosen, _ = evm.size_to_peak(prep, S, Q, passing, opts)
    r = evm.simulate(prep, S, Q, dict(opts or {}, chosen=chosen))
    return prep, passing, ranked, chosen, r


def lines(r):
    out = {}
    for e in r['ledger']:
        out[e['line']] = out.get(e['line'], 0.0) + e['pv']
    return out


def compute():
    V = {'date': DATE}
    raw = {}                       # unformatted values, checked against the Excel workbook
    S = evm.scenario(PACK, 'Moderate'); Q = evm.policy(PACK, 'Attrition only')
    C, E, A = PACK['costs'], PACK['economics'], PACK['augment']
    rep = evm.report(DATA, PACK, 'Moderate', 'Attrition only', n_mc=1000)
    prep, passing, ranked, chosen, r = sized(PACK, S, Q)
    assert abs(r['npv_cash'] - rep['headline']['npv_cash']) < 1e-6
    ref = json.load(open(os.path.join(ROOT, 'tests', 'reference.json')))
    assert abs(r['npv_cash'] - ref['npv']) < 0.5, 'engine and tests/reference.json disagree'
    h, b, g = rep['headline'], rep['bands'], rep['gate']
    L = lines(r)
    roles = list(prep['roles'].values())

    # inputs
    V.update(n_tasks=N(len(DATA['tasks'])), n_roles=N(len(DATA['roles'])), headcount=N(h['headcount']))
    for k in ('takeover', 'review', 'active_use'):
        for sn in ('Conservative', 'Moderate', 'Aggressive'):
            V[f'd_{k}_{sn[:3]}'] = P(PACK['scenarios'][sn][k])
    for sn in ('Conservative', 'Moderate', 'Aggressive'):
        V[f'd_adopt_{sn[:3]}'] = N(PACK['scenarios'][sn]['adopt_months'])
        V[f'd_cost_{sn[:3]}'] = f"{PACK['scenarios'][sn]['cost_mult']:.2f}"
    slope = PACK['review']['seniority_slope']
    V['slope'] = P(slope)

    # cost of an hour
    an = prep['roles']['FP&A Analyst']
    V.update(oncost=f"{E['on_cost']:.2f}", wage=P(E['wage_growth'], 1),
             a_sal=D(an['S']), a_loaded=D(an['C']), a_rate=D(an['rate'], 2), a_n=N(an['N']))
    cats = PACK['categories']
    for c in cats:
        V['c_' + c.split()[0].lower()] = P(cats[c]['ceiling'])
    band_rows = []
    for band in ('Para-professional', 'Professional', 'Management', 'Executive'):
        band_rows.append(f"<tr><td>{band}</td><td class='n'>{P(A['time_saving_by_band'][band])}</td>"
                         f"<td class='n'>{P(evm.review_of(S, band, PACK))}</td>"
                         f"<td class='n'>{P(PACK['turnover_by_band'][band], 1)}</td></tr>")
    V['band_rows'] = '\n'.join(band_rows)
    V['rev_ladder'] = ' / '.join(P(evm.review_of(S, bd, PACK)) for bd in
                                 ('Para-professional', 'Professional', 'Management', 'Executive'))

    # what AI could do: worked examples on the Analyst role
    t_ex = next(t for t in DATA['tasks'] if t['role'] == 'FP&A Analyst' and t['task'] == 'Extract And Format Financial Data')
    able_m = t_ex['hours_month'] * an['N'] * cats[t_ex['category']]['ceiling']
    V.update(ex_h=f"{t_ex['hours_month']:.2f}", ex_ceil=P(cats[t_ex['category']]['ceiling']),
             ex_able_m=N(able_m), ex_able_y=N(able_m * 12))
    ai_y = able_m * 12 * S['takeover']
    rv = evm.review_of(S, an['band'], PACK)
    freed_y = ai_y * (1 - rv)
    V.update(ex_ai_y=N(ai_y), ex_keep=P(1 - rv), ex_freed_y=N(freed_y), takeover=P(S['takeover']),
             review=P(S['review']), net=P(S['takeover'] * (1 - S['review'])))
    built = {x['name'] for x in chosen}
    fa = an['N'] * sum(a for w, a in an['auto'].items() if w in built) * S['takeover'] * (1 - rv) / an['H']
    fg = an['N'] * an['aug'] * S['active_use'] * S['aug_mult'] / an['H']
    y = (fa + fg) / an['N']; dr = 1 - PACK['nonlinear']['complexity_drag'] * y
    V.update(ex_y=P(y), ex_dr=P(dr), ex_after=N(freed_y * dr), ex_people=f'{freed_y * dr / (12 * an["H"]):.1f}',
             drag=f"{PACK['nonlinear']['complexity_drag']:.2f}")
    t_as = next(t for t in DATA['tasks'] if t['role'] == 'FP&A Analyst' and t['task'] == 'Develop Custom Financial Analyses')
    sav = min(cats[t_as['category']]['ceiling'], A['time_saving_by_band'][an['band']])
    as_y = t_as['hours_month'] * an['N'] * 12
    V.update(as_y=N(as_y), as_sav=P(sav), active=P(S['active_use']), as_out=N(as_y * sav * S['active_use']),
             lic=D(C['assistant_licence_per_seat_year']))

    # the cost test
    T, d, lead = E['horizon_months'], E['discount_rate'], C['build_lead_months']
    ann = sum(evm.smoothstep((m - lead) / S['adopt_months']) * evm.df(m, d) for m in range(1, T + 1))
    V.update(ann=f'{ann:.1f}', disc=P(d, 2), n_wl=N(len(ranked)), adopt=N(S['adopt_months']))
    def both(x):
        run_b = x['auto_hours'] * S['takeover'] * C['run_cost_per_ai_hour'] * S['cost_mult']
        up_b = x['build'] * S['cost_mult']; mt = up_b * C['maintenance_share_per_year'] / 12
        up_v = (C['buy_enterprise'] if x['tier'] == 'enterprise' else C['buy_workflow']) * S['cost_mult']
        run_v = x['auto_hours'] * S['takeover'] * C['buy_run_per_ai_hour'] * S['cost_mult']
        return (x['benefit'] - run_b - mt) * ann - up_b, (x['benefit'] - run_v) * ann - up_v
    far = next(x for x in ranked if x['name'] == 'financial analysis and reporting')
    nb, nv = both(far)
    assert abs(max(nb, nv) - far['npv_at_cost']) < 1e-3, 'cost-test example does not match scope()'
    last = ranked[-1]
    V.update(far_roles=N(len(far['roles'])), far_value=D(far['value']), far_build=M(nb), far_buy=M(nv),
             far_opt='build' if far['option'] == 'build' else 'buy',
             last_name=last['name'].capitalize(), last_value=D(last['value']), last_opt=last['option'],
             last_npv=('+' if last['npv_at_cost'] >= 0 else '') + D(last['npv_at_cost']),
             last_passes='passes but ranks last' if last['npv_at_cost'] > 0 else 'fails')
    nbuy = sum(1 for x in chosen if x['option'] == 'buy')
    months = sorted(set(r['golive'].values()))
    waves = [str(m) for m in months[1:]]
    V.update(n_pass=N(len(passing)), n_built=N(len(chosen)), n_buy=N(nbuy), n_build=N(len(chosen) - nbuy),
             upfront=M(h['build_total']), pilot_m=N(months[0]),
             waves=', '.join(waves[:-1]) + ' and ' + waves[-1] if len(waves) > 1 else ''.join(waves),
             gate_m=N(g['month']), be=P(rep['breakeven_net'], 1))

    # funnel
    fn = {f['key']: f['fte'] for f in rep['funnel']}
    aug = sum(x['aug_fte'] for x in rep['roles'])
    V.update(fn_cat=N(fn['cat'], 1), fn_able=N(fn['able'], 1), fn_scope=N(fn['scope'], 1), fn_take=N(fn['take'], 1),
             fn_review=N(fn['review'], 1), fn_drag=N(fn['drag'], 1), fn_pos=N(fn['pos']),
             fn_aug=N(aug, 1), fn_all=N(h['freed_fte']))

    # where each freed hour goes
    pols = PACK['policies']
    for k, pn in (('cap', 'Capacity only'), ('att', 'Attrition only'), ('act', 'Active reduction')):
        V[f'p_{k}_auto'] = P(pols[pn]['harvest_automation']); V[f'p_{k}_aug'] = P(pols[pn]['harvest_augmentation'])
    V.update(notice=N(pols['Active reduction']['notice_months']), sev=N(pols['Active reduction']['severance_weeks']))
    sens = {x['param']: x for x in rep['sensitivity']['rows']}
    hv = sens['harvest_automation']
    V.update(h_lo=M(hv['npv_low'], 1, True), h_hi=M(hv['npv_high'], 1, True), h_lo_p=P(hv['low']), h_hi_p=P(hv['high']))
    ar = next(x for x in rep['roles'] if x['role'] == 'FP&A Analyst')
    pos = r['series']['positions']; end = pos[T]
    V.update(ar_auto=f"{ar['auto_fte']:.1f}", harvest=P(Q['harvest_automation']),
             ar_harv=f"{ar['auto_fte'] * Q['harvest_automation']:.1f}", ar_target=N(ar['target']),
             ar_leave=N(round(an['N'] * (1 - (1 - an['lam']) ** 5))),
             positions=N(end), pos_share=P(end / h['headcount'], 1),
             pos_month=N(next(m for m in range(T + 1) if pos[m] == end)), cph=D(E['cost_per_hire']))
    hc = copy.deepcopy(PACK); hc['economics'].update(discount_rate=0.0619, turnover_multiplier=0.91, function_growth=0.009)
    hp = evm.prepare(DATA, hc); hpass, _ = evm.scope(hp, S)
    rh = evm.simulate(hp, S, Q, dict(chosen=hpass[:len(chosen)]))
    V['health_hires'] = N(rh['avoided_end'])
    blk = PACK['capacity']['min_block_share']; std = E['standard_task_hours_month']
    per = [(x['freed_fte'] - x['positions_end']) * R['H'] / (R['N'] - x['positions_end'])
           for x, R in zip(rep['roles'], roles) if R['N'] > x['positions_end']]
    V.update(block_h=N(blk * std), block_min=N(blk * std / 20 * 60), cap_fte=N(h['capacity_fte']),
             str_fte=N(h['stranded_fte']), per_lo=f'{min(per):.1f}', per_hi=f'{max(per):.1f}')

    # money
    trained = r['series']['trained']; first = next(m for m, v in enumerate(trained) if v)
    r0 = evm.simulate(prep, dict(S, training_refresh=0.0), Q, dict(chosen=chosen))
    joiners = sum(r0['series']['trained'][first + 1:])
    costs = sum(L.get(k, 0.0) for k in evm.COST_LINES)
    assert abs(costs - r['pv_costs']) < 1e-3
    V.update(tr_spend=D(C['training_spend_per_head']), tr_hours=f"{C['training_hours_per_head']:g}",
             joiners=N(joiners), refresh=P(C['training_refresh_per_year']),
             l_training=M(L['training']), l_run=M(L['run']), l_lic=M(L['licences']), l_build=M(L['build']),
             l_prog=M(L['programme']), l_maint=M(L.get('maintenance', 0)), l_costs=M(costs),
             runrate=D(C['run_cost_per_ai_hour'], 2), buyrate=D(C['buy_run_per_ai_hour']),
             decline=P(C['run_cost_decline_per_year']),
             l_hard=M(L['hard']), l_recruit=M(L.get('recruit_avoided', 0) + L.get('seats_reclaimed', 0)),
             cash=M(r['npv_cash']), cash_exact=D(r['npv_cash'], 2), avoid=D(r['pv_avoidance']), capacity=M(r['pv_capacity'], 1),
             dfac=f'{1 + d:.4f}', pay_d=N(r['payback_discounted']), pay_u=N(r['payback_month']),
             peak=M(r['peak_funding'], 1))
    rc = sized(PACK, S, evm.policy(PACK, 'Capacity only'))[4]
    V.update(co_cash=M(rc['headline']), co_cap=M(rc['pv_capacity'], 1), co_hurdle=P(rc['capacity_hurdle']))

    # odds and the decision
    V.update(p_pos=P(b['p_positive']), p10=M(b['p10'], 1, True), p90=M(b['p90'], 1, True),
             p_stop=P(g['p_stop']), stop_cost=M(g['headline_if_stopped'], 1))
    chip = {'go': 'GO', 'pilot': 'PILOT FIRST', 'stop': 'DO NOT START', 'capacity': 'CAPACITY CASE'}[rep['verdict']]
    V['chip'] = chip
    alt = []
    for sn, pn, lab in (('Conservative', 'Attrition only', 'Conservative'), ('Aggressive', 'Attrition only', 'Aggressive'),
                        ('Moderate', 'Active reduction', 'Active reduction')):
        x = evm.report(DATA, PACK, sn, pn, n_mc=1000)
        word = {'go': '', 'pilot': ', pilot', 'stop': ', stop', 'capacity': ', capacity'}[x['verdict']]
        alt.append(f"{lab} {M(x['headline']['headline'], 1, True)} ({P(x['bands']['p_positive'])}{word})")
    V['alt'] = ' · '.join(alt)

    # ---------------------------------------------------------------- page 2: what changed
    S0 = dict(S, wage_growth=0.0, review_slope=0.0)
    _, _, _, lch, rl = sized(PACK, S0, Q, dict(legacy=True))
    assert abs(rl['npv_cash'] - 9376169.02) < 0.5 and rl['positions_end'] == 59 and rl['payback_month'] == 33, \
        'the legacy engine no longer reproduces the 23 October headline'
    lprep = evm.prepare(DATA, PACK)
    be_old = evm.breakeven_net(lprep, S0, Q, lch, dict(legacy=True))
    _, _, _, fch, rf = sized(PACK, S0, Q)                                    # finance-review fixes only
    _, _, _, f0ch, rf0 = sized(PACK, dict(S0, training_refresh=0.0), Q)       # ... without the refresher
    _, _, _, wch, rw = sized(PACK, dict(S, review_slope=0.0), Q)              # + wage growth
    # joiners vs licences inside the first step: same programme, so the ledger splits it exactly
    assert [x['name'] for x in f0ch] == [x['name'] for x in lch]
    Ll, Lf0 = lines(rl), lines(rf0)
    V.update(o_cash=M(rl['npv_cash']), o_pos=N(rl['positions_end']), o_k=N(len(lch)),
             o_buy=N(sum(1 for x in lch if x['option'] == 'buy')), o_cap=M(rl['pv_capacity'], 1),
             o_pay_u=N(rl['payback_month']), o_pay_d=N(rl['payback_discounted']), o_be=P(be_old, 1),
             o_odds='75%', o_verdict='Go',                                   # quoted from the 23 October run
             s_join=signed(-(Lf0['training'] - Ll['training'])), s_lic=signed(Ll['licences'] - Lf0['licences']),
             s_ref=signed(rf['npv_cash'] - rf0['npv_cash']), s_wage=signed(rw['npv_cash'] - rf['npv_cash']),
             s_slope=signed(r['npv_cash'] - rw['npv_cash']), wl_fix=N(len(fch)), wl_wage=N(len(wch)),
             n_buy_now=N(nbuy))
    # the bridge in $ thousands: each row is rounded from cumulative totals, so the column adds up exactly
    cum = [rl['npv_cash'], rl['npv_cash'] - (Lf0['training'] - Ll['training']), rf0['npv_cash'], rf['npv_cash'], rw['npv_cash'], r['npv_cash']]
    kk = [round(c / 1e3) for c in cum]
    V.update(k_o_cash=Kd(cum[0]), k_join=Kd((kk[1] - kk[0]) * 1e3, True), k_lic=Kd((kk[2] - kk[1]) * 1e3, True),
             k_ref=Kd((kk[3] - kk[2]) * 1e3, True), k_fix_cash=Kd(cum[3]), k_wage=Kd((kk[4] - kk[3]) * 1e3, True),
             k_wage_cash=Kd(cum[4]), k_slope=Kd((kk[5] - kk[4]) * 1e3, True), k_cash=Kd(cum[5]))
    assert abs((rf0['npv_cash'] - rl['npv_cash']) - ((Ll['training'] - Lf0['training']) + (Ll['licences'] - Lf0['licences']))) < 1.0
    sr, sw, st = sens['review_slope'], sens['wage_growth'], sens['training_refresh']
    order = [x['param'] for x in rep['sensitivity']['rows']]
    V.update(sl_lo=M(sr['npv_low'], 1, True), sl_hi=M(sr['npv_high'], 1, True), sl_rank=ordinal(order.index('review_slope') + 1),
             wg_lo=M(sw['npv_low'], 1, True), wg_hi=M(sw['npv_high'], 1, True), wg_rank=ordinal(order.index('wage_growth') + 1),
             tr_lo=M(st['npv_low'], 1, True), tr_hi=M(st['npv_high'], 1, True), n_sens=N(len(order)))
    caps = []
    for share in (0.0, 0.10):
        pk = copy.deepcopy(PACK); pk['capacity']['min_block_share'] = share
        caps.append(sized(pk, S, Q)[4]['pv_capacity'])
    V.update(cap0=M(caps[0], 1), cap10=M(caps[1], 1) if caps[1] >= 5e4 else '$0', block10_h=N(0.10 * std))
    cs = {'tasks': (0.85, 0.55, 0.45, 0.25, 0.50, 0.10), 'readme': (0.90, 0.85, 0.50, 0.45, 0.40, 0.10),
          'bucket': (1.00, 1.00, 0.50, 0.50, 0.50, 0.00)}
    for k, vals in cs.items():
        pk = copy.deepcopy(PACK)
        for c, v in zip(cats, vals):
            pk['categories'][c]['ceiling'] = v
        V['ceil_' + k] = M(sized(pk, S, Q)[4]['npv_cash'])
    raw.update(cash=r['npv_cash'], capacity=r['pv_capacity'], stranded=h['stranded_fte'], n_built=len(chosen),
               mix=f"{nbuy} buy / {len(chosen) - nbuy} build", upfront=h['build_total'], positions=end,
               pay_d=r['payback_discounted'], pay_u=r['payback_month'], peak=r['peak_funding'],
               p_pos=b['p_positive'], p10=b['p10'], p90=b['p90'], be=rep['breakeven_net'],
               p_stop=g['p_stop'], stopped=g['headline_if_stopped'],
               hard=L['hard'], seats=L.get('seats_reclaimed', 0.0), recruit=L.get('recruit_avoided', 0.0),
               training=L['training'], run=L['run'], licences=L['licences'], build=L['build'],
               programme=L['programme'], maintenance=L.get('maintenance', 0.0))
    V['_raw'] = raw
    return V


def check_workbook(raw):
    """The flowchart quotes the Excel as matching the engine: check it does, or say why not."""
    path = os.path.join(ROOT, 'docs', 'Etter_Value_Model_FPA.xlsx')
    try:
        import openpyxl
    except ImportError:
        print('openpyxl not installed: workbook not cross-checked'); return
    wb = openpyxl.load_workbook(path, data_only=True)
    Su, Ri, Tl = wb['Summary'], wb['Risk'], wb['Timeline']
    pairs = [('cash', Su['B8']), ('capacity', Su['B10']), ('stranded', Su['B12']), ('n_built', Su['B15']),
             ('mix', Su['B16']), ('upfront', Su['B17']), ('positions', Su['B18']), ('pay_d', Su['B21']),
             ('pay_u', Su['B22']), ('peak', Su['B23']), ('p_pos', Ri['C5']), ('p10', Ri['C6']), ('p90', Ri['C8']),
             ('be', Ri['C11']), ('p_stop', Ri['C45']), ('stopped', Ri['C46']), ('hard', Tl['G104']),
             ('seats', Tl['G105']), ('recruit', Tl['G106']), ('training', Tl['G107']), ('run', Tl['G108']),
             ('licences', Tl['G109']), ('build', Tl['G110']), ('programme', Tl['G111']), ('maintenance', Tl['G112'])]
    bad = []
    for k, cell in pairs:
        want, got = raw[k], cell.value
        tol = 0.01 if isinstance(want, float) and abs(want) >= 100 else 1e-9      # money to the cent, shares and counts exactly
        ok = (want == got) if isinstance(want, str) else (got is not None and abs(float(got) - want) <= tol)
        if not ok:
            bad.append(f'{k}: engine {want!r}, workbook {cell.parent.title}!{cell.coordinate} {got!r}')
    assert not bad, 'docs/Etter_Value_Model_FPA.xlsx is stale against the engine:\n  ' + '\n  '.join(bad)
    print(f'workbook agrees with the engine on {len(pairs)} figures')


# ------------------------------------------------------------------ render
PRINT_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const [src, out] = process.argv.slice(1);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + src); await p.waitForFunction(() => window.__drawn === true, null, { timeout: 60000 });
  const over = await p.evaluate(() => window.__overflow);
  if (over.length) { console.error('OVERFLOW ' + JSON.stringify(over)); process.exit(3); }
  await p.pdf({ path: out, printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
"""


def main():
    V = compute()
    check_workbook(V.pop('_raw'))
    tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
    missing = sorted(set(re.findall(r'\{\{(\w+)\}\}', tpl)) - set(V))
    assert not missing, f'template keys with no value: {missing}'
    html = re.sub(r'\{\{(\w+)\}\}', lambda m: V[m.group(1)], tpl)
    keep = '--html' in sys.argv
    path = os.path.join(HERE, 'flowchart.html') if keep else tempfile.mktemp(suffix='.html')
    open(path, 'w', encoding='utf-8').write(html)
    try:
        subprocess.run(['node', '-e', PRINT_JS, path, OUT_PDF], check=True, cwd=HERE)
        print('wrote', OUT_PDF)
    except (OSError, subprocess.CalledProcessError) as e:
        print(f'could not print the PDF ({e}); open {path} in Chrome and print it (no margins, backgrounds on)')
        if not keep:
            os.replace(path, os.path.join(HERE, 'flowchart.html'))
        sys.exit(1)
    finally:
        if not keep and os.path.exists(path):
            os.remove(path)


if __name__ == '__main__':
    main()
