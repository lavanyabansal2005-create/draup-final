"""
Etter Value Model (EVM) -- reference implementation.

Where the money comes from, in three sentences:
  Etter says which hours of each role AI can do. We build AI only where it costs less than
  those hours, assume it takes over a stated share of them while people still check its
  work, and convert the freed hours into fewer positions only as fast as policy and natural
  attrition allow. What is left of the freed time is reported as capacity at cost, never as cash.

Pipeline:
  1 Work       Etter tasks: hours per person per month, by category.
  2 Potential  category ceilings -> AI-able hours (automate) and assistant time saving (augment).
  3 Scope      each workload is priced as a custom build and as a vendor purchase; the cheaper
               option is kept, and the workload passes only if the AI costs less than the work it
               takes over (cost-effectiveness test, policy independent). Passing workloads join the
               programme in rank order until five-year cash peaks (size_to_peak).
  4 Realised   takeover x (1 - review, rising with seniority), S-curve adoption from go-live, complexity drag
               (the work left behind is harder), phased go-live schedule.
  5 Routing    freed hours go to exactly one destination: fewer positions (policy, attrition
               paced), hires avoided (planned growth absorbed), released capacity, or stranded
               slivers (time per person too thin to redeploy, valued at zero).
  6 Money      cash vs today / cost avoidance vs plan / capacity at cost: computed and
               reported separately, never added together. Every dollar is in the ledger
               with the input row it came from.

Pure Python, no dependencies, deterministic (seeded PRNG identical to the browser engine).
"""
import math, json, copy

CAT_TYPE = {'Directive': 'automate', 'Feedback Loop': 'automate',
            'Task Iteration': 'augment', 'Learning': 'augment', 'Validation': 'augment',
            'Negligibility': 'human'}
COST_LINES = ['build', 'programme', 'training', 'licences', 'run', 'maintenance', 'severance']
CASH_LINES = ['hard', 'seats_reclaimed', 'recruit_avoided']
BAND_RANK = {'Para-professional': 0, 'Professional': 1, 'Management': 2, 'Executive': 3}


def review_of(S, band, pack):
    """Review load for a band: the measured review (Professional anchor) scaled up with seniority."""
    slope = S.get('review_slope', pack.get('review', {}).get('seniority_slope', 0.0))
    return min(0.95, S['review'] * (1 + slope * (BAND_RANK.get(band, 1) - 1)))


def norm(s):
    return ' '.join(s.strip().lower().replace(' & ', ' and ').split())


# ------------------------------------------------------------------ seeded PRNG (mulberry32)
class RNG:
    def __init__(self, seed):
        self.a = seed & 0xFFFFFFFF

    def u(self):
        self.a = (self.a + 0x6D2B79F5) & 0xFFFFFFFF
        t = self.a
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        t &= 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0

    def z(self):
        u1 = self.u() or 1e-12
        u2 = self.u()
        return math.sqrt(-2.0 * math.log(u1)) * math.cos(2 * math.pi * u2)


# ------------------------------------------------------------------ helpers
def smoothstep(x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return x * x * (3 - 2 * x)


def linear_ramp(x):
    return 0.0 if x <= 0 else (1.0 if x >= 1 else x)


def df(m, rate):
    return (1 + rate) ** (-m / 12)


def pv(series, rate):
    """series[m] is month m (m = 0 is today). Monthly discounting at an annual rate."""
    return sum(v * df(m, rate) for m, v in enumerate(series))


def irr_annual(series):
    """Annualised IRR of a monthly series via bisection; None if no sign change."""
    if not any(v < 0 for v in series) or not any(v > 0 for v in series):
        return None
    npv = lambda r: sum(v / (1 + r) ** m for m, v in enumerate(series))
    lo, hi = -0.99, 1.0
    if npv(lo) * npv(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(lo) * npv(mid) <= 0: hi = mid
        else: lo = mid
    return (1 + (lo + hi) / 2) ** 12 - 1


def quantile(xs, q):
    ys = sorted(xs); k = (len(ys) - 1) * q; f = math.floor(k); c = math.ceil(k)
    return ys[f] if f == c else ys[f] + (ys[c] - ys[f]) * (k - f)


# ------------------------------------------------------------------ 1-2 prepare
def prepare(data, pack, basis='tasks'):
    """Join Etter tasks to roles, compute potentials, flag data problems (never fail on them)."""
    P = pack; cats = P['categories']; E = P['economics']
    roles, flags = {}, []
    for r in data['roles']:
        band = r.get('turnover_level') or r.get('band')
        roles[r['role']] = dict(role=r['role'], level=r.get('level'), band=band,
                                N=r.get('headcount'), S=r.get('salary'),
                                etter_score=r.get('etter_score'), seat_cost=r.get('seat_cost'),
                                H=0.0, auto={}, aug=0.0, hours_by_cat={})
    for t in data['tasks']:
        R = roles.get(t['role'])
        if R is None:
            flags.append(('error', f"task for unknown role '{t['role']}' ignored")); continue
        h = float(t.get('hours_month') or 0.0); c = t['category']
        R['H'] += h
        R['hours_by_cat'][c] = R['hours_by_cat'].get(c, 0.0) + h
        typ = CAT_TYPE.get(c)
        if typ is None:
            flags.append(('warn', f"unknown category '{c}' treated as human")); continue
        w = norm(t['workload'])
        if typ == 'automate':
            R['auto'][w] = R['auto'].get(w, 0.0) + h * cats[c]['ceiling']
        elif typ == 'augment':
            R['aug'] += h * min(cats[c]['ceiling'], P['augment']['time_saving_by_band'][R['band']])
    std = E['standard_task_hours_month']
    for R in roles.values():
        if not R['N']:
            flags.append(('warn', f"{R['role']}: headcount missing, role carries no money")); R['N'] = 0
        if not R['S']:
            flags.append(('warn', f"{R['role']}: salary missing, role carries no money")); R['S'] = 0
        if R['seat_cost'] is None:
            R['seat_cost'] = P['costs']['seat_cost_per_position']
        if R['H'] <= 0:
            flags.append(('warn', f"{R['role']}: no task hours")); R['H'] = std
        elif abs(R['H'] - std) / std > 0.05:
            flags.append(('info', f"{R['role']}: tasks sum to {R['H']:.0f} h/month, not {std:.0f}; "
                                  f"shares are taken relative to the recorded {R['H']:.0f}"))
        R['C'] = R['S'] * E['on_cost']                 # loaded annual cost per person
        R['rate'] = R['C'] / (12 * R['H'])             # $ per recorded task-hour (TDABC capacity cost rate)
        R['lam'] = P['turnover_by_band'][R['band']] * E.get('turnover_multiplier', 1.0)
        R['auto_share'] = sum(R['auto'].values()) / R['H']
        R['aug_share'] = R['aug'] / R['H']
        R['score_gap'] = None
        if R['etter_score'] is not None:
            R['score_gap'] = R['auto_share'] - R['etter_score']
            if abs(R['score_gap']) > P['data_quality']['score_tolerance']:
                flags.append(('warn', f"{R['role']}: tasks give {R['auto_share']*100:.1f}% AI-able, "
                                      f"Etter role score is {R['etter_score']*100:.1f}%"))
    if basis == 'role_score':
        for R in roles.values():
            if R['etter_score'] is not None and R['auto_share'] > 0:
                k = R['etter_score'] / R['auto_share']
                R['auto'] = {w: v * k for w, v in R['auto'].items()}
                R['auto_share'] = R['etter_score']
    W = {}
    for R in roles.values():
        for w, a in R['auto'].items():
            X = W.setdefault(w, dict(name=w, roles=[], auto_hours=0.0, value=0.0, n_auto_tasks=0))
            X['roles'].append(R['role'])
            X['auto_hours'] += R['N'] * a              # AI-able hours per month
            X['value'] += R['N'] * a * R['rate']       # $ per month, at cost
    for t in data['tasks']:
        if CAT_TYPE.get(t['category']) == 'automate' and norm(t['workload']) in W:
            W[norm(t['workload'])]['n_auto_tasks'] += 1
    C = P['costs']
    for X in W.values():
        X['tier'] = ('enterprise' if (len(X['roles']) >= C['enterprise_if_roles_at_least']
                                      or X['n_auto_tasks'] >= C['enterprise_if_auto_tasks_at_least'])
                     else 'workflow')
        X['build'] = C['build_enterprise'] if X['tier'] == 'enterprise' else C['build_workflow']
    return dict(roles=roles, workloads=W, flags=flags, pack=P, basis=basis)


# ------------------------------------------------------------------ 3 scope
def scope(prep, S, rule='cost_effective', top_k=None, horizon=None):
    """Rank workloads by (PV of work taken over at cost - running costs) / build cost.
    Default rule builds every workload whose AI costs less than the work it takes over."""
    P = prep['pack']; E = P['economics']; C = P['costs']
    T = horizon or E['horizon_months']; d = E['discount_rate']
    lead = C['build_lead_months']
    ann = sum(smoothstep((m - lead) / S['adopt_months']) * df(m, d) for m in range(1, T + 1))
    ranked = []
    roles = prep['roles']
    for X in prep['workloads'].values():
        # work taken over, at cost, net of each role's own review load
        benefit = sum(roles[n]['N'] * roles[n]['auto'][X['name']] * roles[n]['rate'] * S['takeover']
                      * (1 - review_of(S, roles[n]['band'], P)) for n in X['roles'])
        opts = []
        # build custom
        rate_b = C['run_cost_per_ai_hour'] * S['cost_mult'] * S.get('run_mult', 1.0)
        up_b = X['build'] * S['cost_mult']
        m_b = up_b * C['maintenance_share_per_year'] / 12
        opts.append(('build', rate_b, up_b, m_b, C['maintenance_share_per_year']))
        if C.get('allow_buy', True):
            up_v = (C['buy_enterprise'] if X['tier'] == 'enterprise' else C['buy_workflow']) * S['cost_mult']
            rate_v = C['buy_run_per_ai_hour'] * S['cost_mult'] * S.get('run_mult', 1.0)
            opts.append(('buy', rate_v, up_v, 0.0, 0.0))
        best = None
        for name, rate, up, maint, ms in opts:
            run = X['auto_hours'] * S['takeover'] * rate
            npv = (benefit - run - maint) * ann - up
            if best is None or npv > best[0]:
                best = (npv, name, rate, up, maint, ms, run)
        npv, name, rate, up, maint, ms, run = best
        sc = S['cost_mult']; rm = S['cost_mult'] * S.get('run_mult', 1.0)
        ranked.append(dict(X, benefit=benefit, run=run, maint=maint, build_s=up, npv_at_cost=npv, option=name,
                           run_rate=rate, maint_share=ms, up_base=up / sc, rate_base=rate / rm,
                           ratio=(benefit - run - maint) * ann / up if up else 0.0))
    ranked.sort(key=lambda x: -x['ratio'])
    if rule == 'all':
        chosen = [x for x in ranked if x['auto_hours'] > 0]
    elif rule == 'top_k':
        chosen = ranked[:top_k]
    else:
        chosen = [x for x in ranked if x['npv_at_cost'] > 0]
    return chosen, ranked


def schedule(prep, chosen, kind='staged'):
    P = prep['pack']; lead = P['costs']['build_lead_months']; G = P['programme']
    golive = {}
    for i, x in enumerate(chosen):
        if kind == 'all_at_once' or i < G['pilot_workloads']:
            golive[x['name']] = lead
        else:
            wave = (i - G['pilot_workloads']) // G['wave_size']
            golive[x['name']] = lead + G['pilot_evaluation_months'] + lead + wave * G['wave_gap_months']
    return golive


def size_to_peak(prep, S, Q, chosen, opts=None, key='headline'):
    """Programme size: add workloads in rank order and stop where five-year cash (the headline) peaks.
    When nothing is harvested (capacity only) there is no cash to peak, so every passing workload is kept."""
    if not chosen or (Q['harvest_automation'] == 0 and Q['harvest_augmentation'] == 0):
        return list(chosen), None
    o = dict(opts or {}); o['ledger'] = False
    best_k, best_v, sweep = None, None, []
    for k in range(1, len(chosen) + 1):
        v = simulate(prep, S, Q, dict(o, chosen=chosen[:k]))[key]
        sweep.append(v)
        if best_v is None or v > best_v:
            best_k, best_v = k, v
    return list(chosen[:best_k]), sweep


# ------------------------------------------------------------------ 4-6 simulate
def simulate(prep, S, Q, opts=None):
    """S: scenario (uncertain quantities), Q: policy (choices). Month 0 = today."""
    o = dict(scope_rule='cost_effective', top_k=None, schedule='staged', ramp='s',
             golive=None, horizon=None, chosen=None, aug_on=True, auto_on=True, count_avoidance=None, ledger=True,
             stop_month=None, legacy=False)
    o.update(opts or {})
    P = prep['pack']; E = P['economics']; C = P['costs']; A = P['augment']
    T = o['horizon'] or E['horizon_months']; d = E['discount_rate']
    ramp = smoothstep if o['ramp'] == 's' else linear_ramp
    kap = S.get('drag', P['nonlinear']['complexity_drag'])
    g = E.get('function_growth', 0.0)
    count_avoid = (g > 0) if o['count_avoidance'] is None else o['count_avoidance']
    chosen = o['chosen']
    if chosen is None:
        chosen, _ = scope(prep, S, o['scope_rule'], o['top_k'], T)
    if not o['auto_on']:
        chosen = []
    golive = dict(o['golive']) if o['golive'] is not None else schedule(prep, chosen, o['schedule'])
    built = {x['name']: x for x in chosen}
    lead = C['build_lead_months']
    roles = list(prep['roles'].values())
    aug_start = A['rollout_start_month']
    run_rate0 = C['run_cost_per_ai_hour'] * S.get('run_mult', 1.0) * S['cost_mult']
    stop = o['stop_month'] if o['stop_month'] is not None else T + 1   # from this month the AI is off
    fix = not o['legacy']                      # legacy=True reproduces the earlier engine (no fixes 1-3)
    block = P.get('capacity', {}).get('min_block_share', 0.0) if fix else 0.0
    refresh = S.get('training_refresh', C.get('training_refresh_per_year', 0.0)) if fix else 0.0
    wage_g = S.get('wage_growth', E.get('wage_growth', 0.0))
    net_of = {R['role']: S['takeover'] * (1 - review_of(S, R['band'], P)) for R in prep['roles'].values()}

    # steady state (everything chosen live, fully adopted) -> position targets
    st = {}
    for R in roles:
        fa = R['N'] * sum(a for w, a in R['auto'].items() if w in built) * net_of[R['role']] / R['H']
        fg = (R['N'] * R['aug'] * S['active_use'] * S['aug_mult'] / R['H']) if o['aug_on'] else 0.0
        y = (fa + fg) / R['N'] if R['N'] else 0.0
        fa *= (1 - kap * y); fg *= (1 - kap * y)
        harvest = Q['harvest_automation'] * fa + Q['harvest_augmentation'] * fg
        exp_months = [golive[w] for w in R['auto'] if w in built]
        if o['aug_on'] and R['aug'] > 0: exp_months.append(aug_start)
        st[R['role']] = dict(fa=fa, fg=fg, harvest=harvest, target=math.floor(harvest + 1e-9),
                             exposed=min(exp_months) if exp_months else None)

    z = lambda: [0.0] * (T + 1)
    keys = CASH_LINES + COST_LINES + ['avoidance', 'capacity', 'freed_h', 'reduced_h', 'absorbed_h',
                                      'capacity_h', 'drag_h', 'positions', 'avoided_hires', 'ai_hours',
                                      'seats_active', 'stranded_h', 'capacity_fte', 'stranded_fte', 'trained']
    ser = {k: z() for k in keys}
    # ledger: line -> source -> [nominal, pv]
    led = {}
    def book(line, src, m, amt):
        if not o['ledger']:
            return
        e = led.setdefault(line, {}).setdefault(src, [0.0, 0.0])
        e[0] += amt; e[1] += amt * df(m, d)

    affected = sum(R['N'] for R in roles if st[R['role']]['exposed'] is not None)
    fixed = C['programme_fixed'] * S['cost_mult']
    ser['programme'][0] += fixed; book('programme', 'pack: costs.programme_fixed', 0, fixed)
    for R in roles:
        if st[R['role']]['exposed'] is not None:
            amt = C['deploy_per_affected_head'] * R['N'] * S['cost_mult']
            ser['programme'][0] += amt; book('programme', 'role: ' + R['role'], 0, amt)
    live_build = z()
    for x in chosen:
        gl = golive[x['name']]; b = x['up_base'] * S['cost_mult'] if 'up_base' in x else x['build'] * S['cost_mult']
        for m in range(max(0, gl - lead), gl):
            if m <= T and m < stop:
                ser['build'][m] += b / lead; book('build', 'workload: ' + x['name'], m, b / lead)
        for m in range(gl, min(T + 1, stop)):
            live_build[m] += b * x.get('maint_share', C['maintenance_share_per_year'])

    prevP = {R['role']: 0 for R in roles}; prevAv = {R['role']: 0 for R in roles}
    histP = {R['role']: [0] for R in roles}    # positions by month, for licence true-down
    for m in range(1, T + 1):
        decay = (1 - C['run_cost_decline_per_year']) ** (m / 12)
        wi = (1 + wage_g) ** (m / 12)              # wage index: everything priced off pay grows with it
        for R in roles:
            s = st[R['role']]; nm = R['role']; src = 'role: ' + nm
            fa_h = 0.0; ai_h_tot = 0.0
            for w, a in R['auto'].items():
                if w in built:
                    ad = ramp((m - golive[w]) / S['adopt_months']) if m < stop else 0.0
                    fa_h += R['N'] * a * net_of[nm] * ad
                    ai_h = R['N'] * a * S['takeover'] * ad
                    ai_h_tot += ai_h
                    if ai_h:
                        cost = ai_h * (built[w]['rate_base'] * S.get('run_mult', 1.0) * S['cost_mult'] if 'rate_base' in built[w] else run_rate0) * decay
                        ser['run'][m] += cost; book('run', 'workload: ' + w, m, cost)
            cover = (S['active_use'] * ramp((m - aug_start) / A['rollout_months'])
                     if (o['aug_on'] and R['aug'] > 0 and m < stop) else 0.0)
            fg_h = R['N'] * cover * R['aug'] * S['aug_mult']       # the work does not shrink when positions go
            # licences are bought per person in post and trued down only at each contract anniversary
            seats = (R['N'] - (histP[nm][12 * ((m - 1) // 12)] if fix else 0)) * cover
            F_raw = fa_h + fg_h
            y = F_raw / (R['N'] * R['H']) if R['N'] else 0.0
            dr = 1 - kap * y
            ser['drag_h'][m] += F_raw * (1 - dr)
            fa_h *= dr; fg_h *= dr
            F_h = fa_h + fg_h; fte = F_h / R['H']
            # policy: positions follow progress; attrition-only waits for leavers
            cur = (Q['harvest_automation'] * fa_h + Q['harvest_augmentation'] * fg_h) / R['H']
            allowed = math.floor(s['target'] * (cur / s['harvest'] if s['harvest'] > 0 else 0) + 1e-9)
            if Q['mechanism'] == 'attrition':
                leavers = R['N'] * (1 - (1 - R['lam'] * S.get('turnover_mult', 1.0)) ** (m / 12))
                Pm = min(allowed, math.floor(leavers + 1e-9))
            else:
                Pm = allowed if m > Q.get('notice_months', 0) else 0
            Pm = max(Pm, prevP[nm])                    # a removed position does not come back
            Pm = min(Pm, math.floor(fte + 1e-9))       # never remove more than was freed
            spare = fte - Pm
            heads = R['N'] - Pm
            planned = R['N'] * ((1 + g) ** (m / 12) - 1) if g > 0 else 0.0
            Av = (max(0, min(math.floor(spare + 1e-9), math.floor(planned + 1e-9)))
                  if (g > 0 and Q.get('absorb_growth', True)) else 0)
            left_h = F_h - Pm * R['H'] - Av * R['H']
            # granularity: the first block of freed time per person in post is too thin to redeploy
            cap_h = max(0.0, left_h - block * R['H'] * heads)
            str_h = left_h - cap_h
            # money, booked to the role it comes from
            newP = Pm - prevP[nm]; newAv = max(0, Av - prevAv[nm])
            items = [('hard', Pm * R['C'] * wi / 12), ('seats_reclaimed', Pm * R['seat_cost'] / 12),
                     ('avoidance', Av * R['C'] * wi / 12 + newAv * E['cost_per_hire']),
                     ('capacity', cap_h * R['rate'] * wi),
                     ('licences', seats * C['assistant_licence_per_seat_year'] / 12 * S['cost_mult'])]
            if Q['mechanism'] == 'attrition' or newP < 0:     # a position that comes back is a hire
                items.append(('recruit_avoided', newP * E['cost_per_hire']))
            else:
                items.append(('severance', newP * Q['severance_weeks'] * R['S'] * wi / 52))
            # training: everyone at first exposure; then joiners as they arrive and a yearly refresher
            ex = s['exposed']; trained = 0.0
            if ex is not None and ex < stop:
                t0 = max(1, ex)
                if m == t0:
                    trained = R['N']
                elif fix and t0 < m < stop:
                    leavers = (R['N'] - prevP[nm]) * (1 - (1 - R['lam'] * S.get('turnover_mult', 1.0)) ** (1 / 12))
                    joiners = max(0.0, leavers - (max(0, newP) if Q['mechanism'] == 'attrition' else 0))
                    trained = joiners + (heads * refresh / 12 if m > t0 + 12 else 0.0)
            if trained:
                items.append(('training', trained * (C['training_spend_per_head']
                                                     + C['training_hours_per_head'] * R['rate'] * wi)))
            for line, amt in items:
                if amt:
                    ser[line][m] += amt; book(line, src, m, amt)
            ser['freed_h'][m] += F_h; ser['reduced_h'][m] += Pm * R['H']
            ser['absorbed_h'][m] += Av * R['H']; ser['capacity_h'][m] += cap_h; ser['stranded_h'][m] += str_h
            ser['capacity_fte'][m] += cap_h / R['H']; ser['stranded_fte'][m] += str_h / R['H']
            ser['trained'][m] += trained
            ser['positions'][m] += Pm; ser['avoided_hires'][m] += Av
            ser['seats_active'][m] += seats; ser['ai_hours'][m] += ai_h_tot
            prevP[nm] = Pm; prevAv[nm] = Av; histP[nm].append(Pm)
        mt = live_build[m] / 12
        if mt:
            ser['maintenance'][m] = mt
            for x in chosen:
                if golive[x['name']] <= m:
                    book('maintenance', 'workload: ' + x['name'], m,
                         (x['up_base'] * S['cost_mult'] if 'up_base' in x else x['build'] * S['cost_mult']) * x.get('maint_share', C['maintenance_share_per_year']) / 12)

    M = range(T + 1)
    ser['costs'] = [sum(ser[k][m] for k in COST_LINES) for m in M]
    ser['cash_net'] = [sum(ser[k][m] for k in CASH_LINES) - ser['costs'][m] for m in M]
    ser['plan_net'] = [ser['cash_net'][m] + ser['avoidance'][m] for m in M]
    def payback(series, disc=False):
        cum, pb = 0.0, None
        for m in M:
            cum += series[m] * (df(m, d) if disc else 1.0)
            if cum >= 0 and m > 0 and pb is None: pb = m
            if cum < 0: pb = None
        return pb
    cum = 0.0; ser['cum_cash'] = []
    for m in M:
        cum += ser['cash_net'][m]; ser['cum_cash'].append(cum)
    out = dict(T=T, rate=d, series=ser, chosen=chosen, golive=golive, n_built=len(chosen),
               build_total=sum((x['up_base'] * S['cost_mult'] if 'up_base' in x else x['build'] * S['cost_mult']) for x in chosen),
               scenario=S, policy=Q, count_avoidance=count_avoid)
    out['npv_cash'] = pv(ser['cash_net'], d)
    out['npv_plan'] = pv(ser['plan_net'], d)
    out['pv_avoidance'] = pv(ser['avoidance'], d)
    out['pv_capacity'] = pv(ser['capacity'], d)
    out['pv_costs'] = pv(ser['costs'], d)
    out['pv_savings'] = pv([sum(ser[k][m] for k in CASH_LINES) for m in M], d)
    out['payback_month'] = payback(ser['cash_net'])
    out['payback_plan'] = payback(ser['plan_net'])
    out['payback_discounted'] = payback(ser['cash_net'], True)
    out['irr'] = irr_annual(ser['cash_net'])
    out['peak_funding'] = -min(ser['cum_cash'])
    out['positions_end'] = ser['positions'][T]
    out['avoided_end'] = ser['avoided_hires'][T]
    out['capacity_fte_end'] = ser['capacity_fte'][T]
    out['stranded_fte_end'] = ser['stranded_fte'][T]
    out['stop_month'] = o['stop_month']
    out['headcount'] = sum(R['N'] for R in roles)
    out['payroll_loaded'] = sum(R['N'] * R['C'] for R in roles)
    out['freed_fte_ss'] = sum(s['fa'] + s['fg'] for s in st.values())
    headline = out['npv_plan'] if count_avoid else out['npv_cash']
    out['headline'] = headline
    out['capacity_hurdle'] = (-headline / out['pv_capacity']) if (headline < 0 and out['pv_capacity'] > 0) else 0.0
    out['roles'] = [dict(role=R['role'], N=R['N'], salary=R['S'], loaded=R['C'], band=R['band'],
                         auto_share=R['auto_share'], aug_share=R['aug_share'], etter_score=R['etter_score'],
                         freed_fte=st[R['role']]['fa'] + st[R['role']]['fg'], auto_fte=st[R['role']]['fa'],
                         aug_fte=st[R['role']]['fg'], target=st[R['role']]['target'],
                         positions_end=prevP[R['role']], avoided_end=prevAv[R['role']]) for R in roles]
    out['ledger'] = [dict(line=line, source=src, nominal=v[0], pv=v[1])
                     for line, srcs in led.items() for src, v in srcs.items()]
    # checks
    gap_h = [abs(ser['freed_h'][m] - ser['reduced_h'][m] - ser['absorbed_h'][m] - ser['capacity_h'][m]
                 - ser['stranded_h'][m]) for m in M]
    gaps = [gap_h[m] / ser['freed_h'][m] for m in M if ser['freed_h'][m] > 0]
    out['check_reconciliation_max_gap'] = max(gaps) if gaps else 0.0
    out['check_reconciliation_max_hours'] = max(gap_h)
    out['check_min_capacity_h'] = min(ser['capacity_h'])
    led_pv = lambda lines: sum(e['pv'] for e in out['ledger'] if e['line'] in lines)
    out['check_ledger_gap'] = abs(led_pv(CASH_LINES) - led_pv(COST_LINES) - out['npv_cash']) if o['ledger'] else 0.0
    return out


# ------------------------------------------------------------------ uncertainty
def _logit(p): return math.log(p / (1 - p))
def _sig(x): return 1 / (1 + math.exp(-x))
Z90 = 1.2815515655446004


def draw_scenario(pack, rng, center=None):
    """One correlated draw. A shared 'execution quality' factor makes good programmes take over
    more, need less review, adopt faster and see more active use, all at once.
    With `center`, each draw is centred on the scenario's own value, keeping the pack's spread."""
    U = pack['uncertainty']; rho = U['execution_correlation']
    q = rng.z(); out = {}
    for name, spec in U['params'].items():
        e = rng.z(); load = spec.get('quality_sign', 0)
        zz = (rho * q * load + math.sqrt(1 - rho * rho) * e) if load else e
        med = center[name] if (center is not None and center.get(name) is not None) else spec['median']
        if spec['dist'] == 'logitnormal':
            med = min(0.999, max(0.001, med))
            mu = _logit(med); sd = (_logit(spec['p90']) - _logit(spec['p10'])) / (2 * Z90)
            out[name] = _sig(mu + sd * zz)
        else:
            med = max(1e-9, med)
            mu = math.log(med); sd = (math.log(spec['p90']) - math.log(spec['p10'])) / (2 * Z90)
            out[name] = math.exp(mu + sd * zz)
    return out


def pilot_gate(prep, Q, chosen, breakeven, opts=None):
    """The go / no-go decision at the end of the pilot evaluation. Pass mark = the plan's break-even
    net realisation; None means no realisation breaks even, so every future stops. No gate when nothing
    is harvested (no cash case), when nothing is built, or when the schedule is not staged."""
    o = opts or {}; P = prep['pack']
    month = P['costs']['build_lead_months'] + P['programme']['pilot_evaluation_months']
    T = o.get('horizon') or P['economics']['horizon_months']
    applies = (bool(chosen) and o.get('schedule', 'staged') == 'staged' and month <= T
               and (Q['harvest_automation'] > 0 or Q['harvest_augmentation'] > 0))
    return dict(month=month, pass_mark=breakeven, applies=applies)


def montecarlo(prep, S0, Q, n=1000, seed=20261019, opts=None, keep=False, gate=None):
    """Plan is fixed up front (scope chosen at S0); reality is drawn n times.
    With `gate` (from pilot_gate), a future whose net realisation misses the pass mark stops at the gate."""
    rng = RNG(seed); o = dict(opts or {}); o.setdefault('ledger', keep)
    if o.get('chosen') is None:
        o['chosen'], _ = scope(prep, S0, 'cost_effective')
    res = []
    for _ in range(n):
        dd = draw_scenario(prep['pack'], rng, S0)
        S = dict(S0); S.update(dd)
        stopped = bool(gate and gate['applies'] and (gate['pass_mark'] is None
                                                     or S['takeover'] * (1 - S['review']) < gate['pass_mark']))
        r = simulate(prep, S, Q, dict(o, stop_month=gate['month'] if stopped else None))
        res.append(r if keep else dict(npv=r['npv_cash'], plan=r['npv_plan'], cap=r['pv_capacity'],
                                       pay=r['payback_month'], pos=r['positions_end'], draw=dd,
                                       headline=r['headline'], stopped=stopped))
    return res


def breakeven_net(prep, S0, Q, chosen=None, opts=None, key='headline'):
    """Net realisation (takeover x (1 - review)) at which the headline NPV is zero, plan fixed."""
    if chosen is None:
        chosen, _ = scope(prep, S0)
    def f(nr):
        S = dict(S0, takeover=min(0.999, nr / (1 - S0['review'])))
        return simulate(prep, S, Q, dict(opts or {}, chosen=chosen))[key]
    lo, hi = 0.0, min(0.95, 0.999 * (1 - S0['review']))
    if f(hi) < 0: return None
    if f(lo) >= 0: return 0.0
    for _ in range(32):
        mid = (lo + hi) / 2
        if f(mid) >= 0: hi = mid
        else: lo = mid
    return hi


def decide(p_positive, policy):
    """Decision rule taken from the experiments (exp_gate_scale.py): a pilot gate pays when the call is
    close. Gated mean NPV is about zero near a 36% chance of success and the gate stops paying near 70%."""
    if p_positive >= 0.7: return 'go', 'Go: phased rollout, no pause needed.'
    if p_positive >= 0.4: return 'pilot', 'Pilot first and decide at the gate.'
    if policy['harvest_automation'] == 0:
        return 'capacity', 'Capacity case only: fund it if leadership commits to using the released time.'
    return 'stop', 'Do not start on cash grounds.'


def sensitivity(prep, S0, Q, chosen=None):
    """One at a time across each uncertain parameter's P10..P90 plus the policy harvest share."""
    if chosen is None:
        chosen, _ = scope(prep, S0)
    U = prep['pack']['uncertainty']['params']
    base = simulate(prep, S0, Q, dict(chosen=chosen))['headline']
    rows = []
    for k, spec in U.items():
        lo = simulate(prep, dict(S0, **{k: spec['p10']}), Q, dict(chosen=chosen))['headline']
        hi = simulate(prep, dict(S0, **{k: spec['p90']}), Q, dict(chosen=chosen))['headline']
        rows.append(dict(param=k, low=spec['p10'], high=spec['p90'], npv_low=lo, npv_high=hi))
    if Q['harvest_automation'] > 0:
        a, b = max(0.0, Q['harvest_automation'] - 0.25), min(1.0, Q['harvest_automation'] + 0.25)
        rows.append(dict(param='harvest_automation', low=a, high=b,
                         npv_low=simulate(prep, S0, dict(Q, harvest_automation=a), dict(chosen=chosen))['headline'],
                         npv_high=simulate(prep, S0, dict(Q, harvest_automation=b), dict(chosen=chosen))['headline']))
    rows.sort(key=lambda r: -abs(r['npv_high'] - r['npv_low']))
    return base, rows


def scenario(pack, name):
    return dict(pack['scenarios'][name])


def policy(pack, name):
    return dict(pack['policies'][name])


# ------------------------------------------------------------------ one call for the pages
def funnel(prep, S, r):
    """FTE-equivalent funnel for the leader page (automation path) at steady state."""
    roles = list(prep['roles'].values())
    built = {x['name'] for x in r['chosen']}
    per_fte = lambda R: R['H']
    cat_h = sum(R['N'] * (R['hours_by_cat'].get('Directive', 0) + R['hours_by_cat'].get('Feedback Loop', 0)) / R['H'] for R in roles)
    able = sum(R['N'] * R['auto_share'] for R in roles)
    scope_ = sum(R['N'] * sum(a for w, a in R['auto'].items() if w in built) / R['H'] for R in roles)
    take = scope_ * S['takeover']
    rev = sum(R['N'] * sum(a for w, a in R['auto'].items() if w in built) / R['H'] * S['takeover']
              * (1 - review_of(S, R['band'], prep['pack'])) for R in roles)
    drag = sum(x['auto_fte'] for x in r['roles'])
    return [dict(key='cat', stage='Hours in AI categories', fte=cat_h),
            dict(key='able', stage='AI-able (Etter ceilings)', fte=able),
            dict(key='scope', stage='In workloads worth building', fte=scope_),
            dict(key='take', stage='AI takes over', fte=take),
            dict(key='review', stage='After human review', fte=rev),
            dict(key='drag', stage='After complexity drag', fte=drag),
            dict(key='pos', stage='Positions removed', fte=r['positions_end'])]


def report(data, pack, scen_name='Moderate', pol_name='Attrition only', n_mc=500, seed=20261019,
           overrides=None, scope_k=None):
    """Everything both pages need, from one deterministic run plus seeded draws."""
    prep = prepare(data, pack)
    S = scenario(pack, scen_name); S.update((overrides or {}).get('scenario', {}))
    Q = policy(pack, pol_name); Q.update((overrides or {}).get('policy', {}))
    passing, ranked = scope(prep, S)
    if scope_k is not None:
        chosen = ranked[:scope_k]
    else:
        chosen, _ = size_to_peak(prep, S, Q, passing)
    r = simulate(prep, S, Q, dict(chosen=chosen))
    be = breakeven_net(prep, S, Q, chosen)
    gate = pilot_gate(prep, Q, chosen, be)
    mc = montecarlo(prep, S, Q, n=n_mc, seed=seed, opts=dict(chosen=chosen), gate=gate)
    hl = [x['headline'] for x in mc]
    p_pos = sum(1 for x in hl if x > 0) / len(hl)
    if gate['applies']:
        st = simulate(prep, S, Q, dict(chosen=chosen, stop_month=gate['month']))
        gate.update(p_stop=sum(1 for x in mc if x['stopped']) / len(mc), headline_if_stopped=st['headline'],
                    positions_refilled=max(st['series']['positions']))
    base, sens = sensitivity(prep, S, Q, chosen)
    verdict, verdict_text = decide(p_pos, Q)
    T = r['T']; s = r['series']
    led = {}
    for e in r['ledger']:
        led[e['line']] = led.get(e['line'], 0.0) + e['pv']
    return dict(
        meta=dict(pack=pack['meta']['name'], scenario=scen_name, policy=pol_name, horizon=T,
                  discount_rate=r['rate'], basis='tasks', n_mc=n_mc, seed=seed),
        headline=dict(npv_cash=r['npv_cash'], npv_plan=r['npv_plan'], pv_avoidance=r['pv_avoidance'],
                      pv_capacity=r['pv_capacity'], pv_costs=r['pv_costs'], pv_savings=r['pv_savings'],
                      payback=r['payback_month'], payback_plan=r['payback_plan'],
                      payback_discounted=r['payback_discounted'], irr=r['irr'],
                      peak_funding=r['peak_funding'], positions=r['positions_end'], hires_avoided=r['avoided_end'],
                      freed_fte=r['freed_fte_ss'], headcount=r['headcount'], payroll=r['payroll_loaded'],
                      n_built=r['n_built'], build_total=r['build_total'], hurdle=r['capacity_hurdle'],
                      count_avoidance=r['count_avoidance'], headline=r['headline'],
                      capacity_fte=r['capacity_fte_end'], stranded_fte=r['stranded_fte_end']),
        bands=dict(p10=quantile(hl, .1), p50=quantile(hl, .5), p90=quantile(hl, .9), p_positive=p_pos,
                   cap_p10=quantile([x['cap'] for x in mc], .1), cap_p90=quantile([x['cap'] for x in mc], .9)),
        breakeven_net=be, realisation=S['takeover'] * (1 - S['review']), gate=gate,
        verdict=verdict, verdict_text=verdict_text,
        sensitivity=dict(base=base, rows=sens),
        funnel=funnel(prep, S, r),
        roles=r['roles'],
        programme=dict(n_passing=len(passing), n_built=len(chosen),
                       n_buy=sum(1 for x in chosen if x.get('option') == 'buy'),
                       n_build=sum(1 for x in chosen if x.get('option', 'build') == 'build')),
        workloads=[dict(rank=i + 1, name=x['name'], tier=x['tier'], roles=len(x['roles']), option=x.get('option', 'build'), build=x['build_s'],
                        value_month=x['benefit'], npv_at_cost=x['npv_at_cost'], ratio=x['ratio'],
                        built=any(c['name'] == x['name'] for c in chosen),
                        golive=r['golive'].get(x['name'])) for i, x in enumerate(ranked)],
        series={k: s[k] for k in ['cash_net', 'cum_cash', 'hard', 'avoidance', 'capacity', 'costs', 'positions',
                                  'avoided_hires', 'freed_h', 'capacity_h', 'stranded_h']},
        lines=led,
        ledger=r['ledger'],
        flags=prep['flags'],
        checks=dict(reconciliation_max_gap=r['check_reconciliation_max_gap'],
                    reconciliation_max_hours=r['check_reconciliation_max_hours'],
                    ledger_gap=r['check_ledger_gap'], min_capacity_h=r['check_min_capacity_h']))
