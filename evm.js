/* Etter Value Model -- browser/Node port of evm.py (the Python file is the reference).
   Line-for-line equivalent; parity is checked by tests/parity.js. No dependencies. */
(function (root) {
  'use strict';
  const CAT_TYPE = { 'Directive': 'automate', 'Feedback Loop': 'automate', 'Task Iteration': 'augment',
    'Learning': 'augment', 'Validation': 'augment', 'Negligibility': 'human' };
  const COST_LINES = ['build', 'programme', 'training', 'licences', 'run', 'maintenance', 'severance'];
  const CASH_LINES = ['hard', 'seats_reclaimed', 'recruit_avoided'];

  const norm = s => s.trim().toLowerCase().split(' & ').join(' and ').split(/\s+/).filter(Boolean).join(' ');

  // ---------------------------------------------------------------- seeded PRNG (mulberry32)
  function RNG(seed) { this.a = seed >>> 0; }
  RNG.prototype.u = function () {
    this.a = (this.a + 0x6D2B79F5) >>> 0;
    let t = this.a;
    t = Math.imul(t ^ (t >>> 15), t | 1) >>> 0;
    t = (t ^ ((t + (Math.imul(t ^ (t >>> 7), t | 61) >>> 0)) >>> 0)) >>> 0;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  RNG.prototype.z = function () {
    const u1 = this.u() || 1e-12, u2 = this.u();
    return Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  };

  // ---------------------------------------------------------------- helpers
  const smoothstep = x => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
  const linearRamp = x => (x <= 0 ? 0 : x >= 1 ? 1 : x);
  const df = (m, rate) => Math.pow(1 + rate, -m / 12);
  const pv = (series, rate) => { let s = 0; for (let m = 0; m < series.length; m++) s += series[m] * df(m, rate); return s; };
  const floor = Math.floor;
  function irrAnnual(series) {
    if (!series.some(v => v < 0) || !series.some(v => v > 0)) return null;
    const npv = r => { let s = 0; for (let m = 0; m < series.length; m++) s += series[m] / Math.pow(1 + r, m); return s; };
    let lo = -0.99, hi = 1.0;
    if (npv(lo) * npv(hi) > 0) return null;
    for (let i = 0; i < 200; i++) { const mid = (lo + hi) / 2; if (npv(lo) * npv(mid) <= 0) hi = mid; else lo = mid; }
    return Math.pow(1 + (lo + hi) / 2, 12) - 1;
  }
  function quantile(xs, q) {
    const ys = xs.slice().sort((a, b) => a - b); const k = (ys.length - 1) * q; const f = floor(k), c = Math.ceil(k);
    return f === c ? ys[f] : ys[f] + (ys[c] - ys[f]) * (k - f);
  }
  const clone = o => JSON.parse(JSON.stringify(o));

  // ---------------------------------------------------------------- 1-2 prepare
  function prepare(data, pack, basis) {
    basis = basis || 'tasks';
    const P = pack, cats = P.categories, E = P.economics;
    const roles = {}, roleOrder = [], flags = [];
    for (const r of data.roles) {
      const band = r.turnover_level || r.band;
      roles[r.role] = { role: r.role, level: r.level, band, N: r.headcount, S: r.salary, etter_score: r.etter_score == null ? null : r.etter_score,
        seat_cost: r.seat_cost == null ? null : r.seat_cost, H: 0, auto: new Map(), aug: 0, hours_by_cat: {} };
      roleOrder.push(r.role);
    }
    for (const t of data.tasks) {
      const R = roles[t.role];
      if (!R) { flags.push(['error', `task for unknown role '${t.role}' ignored`]); continue; }
      const h = Number(t.hours_month || 0), c = t.category;
      R.H += h; R.hours_by_cat[c] = (R.hours_by_cat[c] || 0) + h;
      const typ = CAT_TYPE[c];
      if (!typ) { flags.push(['warn', `unknown category '${c}' treated as human`]); continue; }
      const w = norm(t.workload);
      if (typ === 'automate') R.auto.set(w, (R.auto.get(w) || 0) + h * cats[c].ceiling);
      else if (typ === 'augment') R.aug += h * Math.min(cats[c].ceiling, P.augment.time_saving_by_band[R.band]);
    }
    const std = E.standard_task_hours_month;
    for (const name of roleOrder) {
      const R = roles[name];
      if (!R.N) { flags.push(['warn', `${R.role}: headcount missing, role carries no money`]); R.N = 0; }
      if (!R.S) { flags.push(['warn', `${R.role}: salary missing, role carries no money`]); R.S = 0; }
      if (R.seat_cost == null) R.seat_cost = P.costs.seat_cost_per_position;
      if (R.H <= 0) { flags.push(['warn', `${R.role}: no task hours`]); R.H = std; }
      else if (Math.abs(R.H - std) / std > 0.05)
        flags.push(['info', `${R.role}: tasks sum to ${R.H.toFixed(0)} h/month, not ${std.toFixed(0)}; shares are taken relative to the recorded ${R.H.toFixed(0)}`]);
      R.C = R.S * E.on_cost; R.rate = R.C / (12 * R.H);
      R.lam = P.turnover_by_band[R.band] * (E.turnover_multiplier == null ? 1.0 : E.turnover_multiplier);
      let a = 0; for (const v of R.auto.values()) a += v;
      R.auto_share = a / R.H; R.aug_share = R.aug / R.H; R.score_gap = null;
      if (R.etter_score != null) {
        R.score_gap = R.auto_share - R.etter_score;
        if (Math.abs(R.score_gap) > P.data_quality.score_tolerance)
          flags.push(['info', `${R.role}: tasks give ${(R.auto_share * 100).toFixed(1)}% AI-able, Etter role score is ${(R.etter_score * 100).toFixed(1)}%. Expected, not an error: Etter produces the two independently. The model builds on task hours and keeps the role score as a second opinion`]);
      }
    }
    if (basis === 'role_score') {
      for (const name of roleOrder) {
        const R = roles[name];
        if (R.etter_score != null && R.auto_share > 0) {
          const k = R.etter_score / R.auto_share;
          for (const [w, v] of R.auto) R.auto.set(w, v * k);
          R.auto_share = R.etter_score;
        }
      }
    }
    const W = new Map();
    for (const name of roleOrder) {
      const R = roles[name];
      for (const [w, a] of R.auto) {
        if (!W.has(w)) W.set(w, { name: w, roles: [], auto_hours: 0, value: 0, n_auto_tasks: 0 });
        const X = W.get(w); X.roles.push(R.role); X.auto_hours += R.N * a; X.value += R.N * a * R.rate;
      }
    }
    for (const t of data.tasks) if (CAT_TYPE[t.category] === 'automate' && W.has(norm(t.workload))) W.get(norm(t.workload)).n_auto_tasks += 1;
    const C = P.costs;
    for (const X of W.values()) {
      X.tier = (X.roles.length >= C.enterprise_if_roles_at_least || X.n_auto_tasks >= C.enterprise_if_auto_tasks_at_least) ? 'enterprise' : 'workflow';
      X.build = X.tier === 'enterprise' ? C.build_enterprise : C.build_workflow;
    }
    return { roles, roleOrder, workloads: W, flags, pack: P, basis };
  }

  // ---------------------------------------------------------------- 3 scope
  function scope(prep, S, rule, topK, horizon) {
    rule = rule || 'cost_effective';
    const P = prep.pack, E = P.economics, C = P.costs;
    const T = horizon || E.horizon_months, d = E.discount_rate;
    const net = S.takeover * (1 - S.review), lead = C.build_lead_months;
    let ann = 0; for (let m = 1; m <= T; m++) ann += smoothstep((m - lead) / S.adopt_months) * df(m, d);
    const ranked = [];
    const rm = S.run_mult == null ? 1.0 : S.run_mult;
    for (const X of prep.workloads.values()) {
      const benefit = X.value * net;
      // build custom vs buy vendor: keep the option with the higher NPV at cost (buy only if strictly better)
      const opts = [];
      const upB = X.build * S.cost_mult;
      opts.push(['build', C.run_cost_per_ai_hour * S.cost_mult * rm, upB, upB * C.maintenance_share_per_year / 12, C.maintenance_share_per_year]);
      if (C.allow_buy == null ? true : C.allow_buy) {
        const upV = (X.tier === 'enterprise' ? C.buy_enterprise : C.buy_workflow) * S.cost_mult;
        opts.push(['buy', C.buy_run_per_ai_hour * S.cost_mult * rm, upV, 0.0, 0.0]);
      }
      let best = null;
      for (const [name, rate, up, maint, ms] of opts) {
        const run = X.auto_hours * S.takeover * rate;
        const npv = (benefit - run - maint) * ann - up;
        if (best == null || npv > best[0]) best = [npv, name, rate, up, maint, ms, run];
      }
      const [npv, name, rate, up, maint, ms, run] = best;
      const sc = S.cost_mult, rr = S.cost_mult * rm;
      ranked.push(Object.assign({}, X, { benefit, run, maint, build_s: up, npv_at_cost: npv, option: name,
        run_rate: rate, maint_share: ms, up_base: up / sc, rate_base: rate / rr,
        ratio: up ? (benefit - run - maint) * ann / up : 0 }));
    }
    ranked.sort((a, b) => b.ratio - a.ratio);
    let chosen;
    if (rule === 'all') chosen = ranked.filter(x => x.auto_hours > 0);
    else if (rule === 'top_k') chosen = ranked.slice(0, topK);
    else chosen = ranked.filter(x => x.npv_at_cost > 0);
    return [chosen, ranked];
  }

  function schedule(prep, chosen, kind) {
    const P = prep.pack, lead = P.costs.build_lead_months, G = P.programme, golive = {};
    chosen.forEach((x, i) => {
      if (kind === 'all_at_once' || i < G.pilot_workloads) golive[x.name] = lead;
      else { const wave = floor((i - G.pilot_workloads) / G.wave_size); golive[x.name] = lead + G.pilot_evaluation_months + lead + wave * G.wave_gap_months; }
    });
    return golive;
  }

  // ---------------------------------------------------------------- 4-6 simulate
  // Programme size: add workloads in rank order and stop where five-year cash (the headline) peaks.
  // When nothing is harvested (capacity only) there is no cash to peak, so every passing workload is kept.
  function sizeToPeak(prep, S, Q, chosen, opts, key) {
    key = key || 'headline';
    if (!chosen.length || (Q.harvest_automation === 0 && Q.harvest_augmentation === 0)) return [chosen.slice(), null];
    const o = Object.assign({}, opts || {}, { ledger: false });
    let bestK = null, bestV = null; const sweep = [];
    for (let k = 1; k <= chosen.length; k++) {
      const v = simulate(prep, S, Q, Object.assign({}, o, { chosen: chosen.slice(0, k) }))[key];
      sweep.push(v);
      if (bestV == null || v > bestV) { bestK = k; bestV = v; }
    }
    return [chosen.slice(0, bestK), sweep];
  }

  function simulate(prep, S, Q, opts) {
    const o = Object.assign({ scope_rule: 'cost_effective', top_k: null, schedule: 'staged', ramp: 's', golive: null,
      horizon: null, chosen: null, aug_on: true, auto_on: true, count_avoidance: null, ledger: true }, opts || {});
    const P = prep.pack, E = P.economics, C = P.costs, A = P.augment;
    const T = o.horizon || E.horizon_months, d = E.discount_rate;
    const ramp = o.ramp === 's' ? smoothstep : linearRamp;
    const kap = S.drag == null ? P.nonlinear.complexity_drag : S.drag;
    const g = E.function_growth || 0.0;
    const countAvoid = o.count_avoidance == null ? g > 0 : o.count_avoidance;
    let chosen = o.chosen;
    if (chosen == null) chosen = scope(prep, S, o.scope_rule, o.top_k, T)[0];
    if (!o.auto_on) chosen = [];
    const golive = o.golive != null ? Object.assign({}, o.golive) : schedule(prep, chosen, o.schedule);
    const built = new Set(chosen.map(x => x.name));
    const lead = C.build_lead_months, net = S.takeover * (1 - S.review);
    const roles = prep.roleOrder.map(n => prep.roles[n]);
    const augStart = A.rollout_start_month;
    const runRate0 = C.run_cost_per_ai_hour * (S.run_mult == null ? 1.0 : S.run_mult) * S.cost_mult;
    const turnMult = S.turnover_mult == null ? 1.0 : S.turnover_mult;
    const upFront = x => x.up_base != null ? x.up_base * S.cost_mult : x.build * S.cost_mult;
    const maintShare = x => x.maint_share != null ? x.maint_share : C.maintenance_share_per_year;
    const builtMap = new Map(chosen.map(x => [x.name, x]));
    const runRateOf = w => { const x = builtMap.get(w); return x && x.rate_base != null ? x.rate_base * (S.run_mult == null ? 1.0 : S.run_mult) * S.cost_mult : runRate0; };

    const st = {};
    for (const R of roles) {
      let sa = 0; for (const [w, a] of R.auto) if (built.has(w)) sa += a;
      let fa = R.N * sa * net / R.H;
      let fg = o.aug_on ? (R.N * R.aug * S.active_use * S.aug_mult / R.H) : 0.0;
      const y = R.N ? (fa + fg) / R.N : 0.0;
      fa *= (1 - kap * y); fg *= (1 - kap * y);
      const harvest = Q.harvest_automation * fa + Q.harvest_augmentation * fg;
      const exp = []; for (const w of R.auto.keys()) if (built.has(w)) exp.push(golive[w]);
      if (o.aug_on && R.aug > 0) exp.push(augStart);
      st[R.role] = { fa, fg, harvest, target: floor(harvest + 1e-9), exposed: exp.length ? Math.min(...exp) : null };
    }
    const z = () => new Array(T + 1).fill(0);
    const keys = CASH_LINES.concat(COST_LINES, ['avoidance', 'capacity', 'freed_h', 'reduced_h', 'absorbed_h', 'capacity_h',
      'drag_h', 'positions', 'avoided_hires', 'ai_hours', 'seats_active']);
    const ser = {}; for (const k of keys) ser[k] = z();
    const led = new Map();
    const book = (line, src, m, amt) => {
      if (!o.ledger) return;
      if (!led.has(line)) led.set(line, new Map());
      const L = led.get(line); if (!L.has(src)) L.set(src, [0, 0]);
      const e = L.get(src); e[0] += amt; e[1] += amt * df(m, d);
    };
    const fixed = C.programme_fixed * S.cost_mult;
    ser.programme[0] += fixed; book('programme', 'pack: costs.programme_fixed', 0, fixed);
    for (const R of roles) if (st[R.role].exposed != null) {
      const amt = C.deploy_per_affected_head * R.N * S.cost_mult; ser.programme[0] += amt; book('programme', 'role: ' + R.role, 0, amt);
    }
    const liveBuild = z();
    for (const x of chosen) {
      const gl = golive[x.name], b = upFront(x);
      for (let m = Math.max(0, gl - lead); m < gl; m++) if (m <= T) { ser.build[m] += b / lead; book('build', 'workload: ' + x.name, m, b / lead); }
      for (let m = gl; m <= T; m++) liveBuild[m] += b * maintShare(x);
    }
    const prevP = {}, prevAv = {}; for (const R of roles) { prevP[R.role] = 0; prevAv[R.role] = 0; }
    for (let m = 1; m <= T; m++) {
      const decay = Math.pow(1 - C.run_cost_decline_per_year, m / 12);
      for (const R of roles) {
        const s = st[R.role], nm = R.role, src = 'role: ' + nm;
        let faH = 0, aiTot = 0;
        for (const [w, a] of R.auto) {
          if (built.has(w)) {
            const ad = ramp((m - golive[w]) / S.adopt_months);
            faH += R.N * a * net * ad;
            const aiH = R.N * a * S.takeover * ad;
            aiTot += aiH;
            if (aiH) { const cost = aiH * runRateOf(w) * decay; ser.run[m] += cost; book('run', 'workload: ' + w, m, cost); }
          }
        }
        const seats = (o.aug_on && R.aug > 0) ? R.N * S.active_use * ramp((m - augStart) / A.rollout_months) : 0.0;
        let fgH = seats * R.aug * S.aug_mult;
        const Fraw = faH + fgH;
        const y = R.N ? Fraw / (R.N * R.H) : 0.0;
        const dr = 1 - kap * y;
        ser.drag_h[m] += Fraw * (1 - dr);
        faH *= dr; fgH *= dr;
        const Fh = faH + fgH, fte = Fh / R.H;
        const cur = (Q.harvest_automation * faH + Q.harvest_augmentation * fgH) / R.H;
        const allowed = floor(s.target * (s.harvest > 0 ? cur / s.harvest : 0) + 1e-9);
        let Pm;
        if (Q.mechanism === 'attrition') {
          const leavers = R.N * (1 - Math.pow(1 - R.lam * turnMult, m / 12));
          Pm = Math.min(allowed, floor(leavers + 1e-9));
        } else Pm = m > (Q.notice_months || 0) ? allowed : 0;
        Pm = Math.max(Pm, prevP[nm]);
        Pm = Math.min(Pm, floor(fte + 1e-9));
        const spare = fte - Pm;
        const planned = g > 0 ? R.N * (Math.pow(1 + g, m / 12) - 1) : 0.0;
        const Av = (g > 0 && (Q.absorb_growth == null ? true : Q.absorb_growth)) ? Math.max(0, Math.min(floor(spare + 1e-9), floor(planned + 1e-9))) : 0;
        const capH = Fh - Pm * R.H - Av * R.H;
        const newP = Pm - prevP[nm], newAv = Math.max(0, Av - prevAv[nm]);
        const items = [['hard', Pm * R.C / 12], ['seats_reclaimed', Pm * R.seat_cost / 12],
          ['avoidance', Av * R.C / 12 + newAv * E.cost_per_hire], ['capacity', capH * R.rate],
          ['licences', seats * C.assistant_licence_per_seat_year / 12 * S.cost_mult]];
        if (Q.mechanism === 'attrition') items.push(['recruit_avoided', newP * E.cost_per_hire]);
        else items.push(['severance', newP * Q.severance_weeks * R.S / 52]);
        if (s.exposed != null && m === Math.max(1, s.exposed))
          items.push(['training', R.N * (C.training_spend_per_head + C.training_hours_per_head * R.rate)]);
        for (const [line, amt] of items) if (amt) { ser[line][m] += amt; book(line, src, m, amt); }
        ser.freed_h[m] += Fh; ser.reduced_h[m] += Pm * R.H; ser.absorbed_h[m] += Av * R.H; ser.capacity_h[m] += capH;
        ser.positions[m] += Pm; ser.avoided_hires[m] += Av; ser.seats_active[m] += seats; ser.ai_hours[m] += aiTot;
        prevP[nm] = Pm; prevAv[nm] = Av;
      }
      const mt = liveBuild[m] / 12;
      if (mt) {
        ser.maintenance[m] = mt;
        for (const x of chosen) if (golive[x.name] <= m) book('maintenance', 'workload: ' + x.name, m, upFront(x) * maintShare(x) / 12);
      }
    }
    const M = T + 1;
    ser.costs = []; ser.cash_net = []; ser.plan_net = [];
    for (let m = 0; m < M; m++) {
      let c = 0; for (const k of COST_LINES) c += ser[k][m];
      let h = 0; for (const k of CASH_LINES) h += ser[k][m];
      ser.costs.push(c); ser.cash_net.push(h - c); ser.plan_net.push(h - c + ser.avoidance[m]);
    }
    const payback = series => { let cum = 0, pb = null; for (let m = 0; m < M; m++) { cum += series[m]; if (cum >= 0 && m > 0 && pb == null) pb = m; if (cum < 0) pb = null; } return pb; };
    let cum = 0; ser.cum_cash = []; for (let m = 0; m < M; m++) { cum += ser.cash_net[m]; ser.cum_cash.push(cum); }
    const out = { T, rate: d, series: ser, chosen, golive, n_built: chosen.length, scenario: S, policy: Q, count_avoidance: countAvoid };
    out.build_total = chosen.reduce((a, x) => a + upFront(x), 0);
    out.npv_cash = pv(ser.cash_net, d); out.npv_plan = pv(ser.plan_net, d);
    out.pv_avoidance = pv(ser.avoidance, d); out.pv_capacity = pv(ser.capacity, d); out.pv_costs = pv(ser.costs, d);
    const sav = []; for (let m = 0; m < M; m++) { let h = 0; for (const k of CASH_LINES) h += ser[k][m]; sav.push(h); }
    out.pv_savings = pv(sav, d);
    out.payback_month = payback(ser.cash_net); out.payback_plan = payback(ser.plan_net);
    out.irr = irrAnnual(ser.cash_net); out.peak_funding = -Math.min(...ser.cum_cash);
    out.positions_end = ser.positions[T]; out.avoided_end = ser.avoided_hires[T];
    out.headcount = roles.reduce((a, R) => a + R.N, 0); out.payroll_loaded = roles.reduce((a, R) => a + R.N * R.C, 0);
    out.freed_fte_ss = roles.reduce((a, R) => a + st[R.role].fa + st[R.role].fg, 0);
    const headline = countAvoid ? out.npv_plan : out.npv_cash;
    out.headline = headline;
    out.capacity_hurdle = (headline < 0 && out.pv_capacity > 0) ? -headline / out.pv_capacity : 0.0;
    out.roles = roles.map(R => ({ role: R.role, N: R.N, salary: R.S, loaded: R.C, band: R.band, auto_share: R.auto_share,
      aug_share: R.aug_share, etter_score: R.etter_score, freed_fte: st[R.role].fa + st[R.role].fg, auto_fte: st[R.role].fa,
      aug_fte: st[R.role].fg, target: st[R.role].target, positions_end: prevP[R.role], avoided_end: prevAv[R.role], lam: R.lam }));
    out.ledger = [];
    for (const [line, srcs] of led) for (const [src, v] of srcs) out.ledger.push({ line, source: src, nominal: v[0], pv: v[1] });
    let gap = 0; for (let m = 0; m < M; m++) if (ser.freed_h[m] > 0)
      gap = Math.max(gap, Math.abs(ser.freed_h[m] - ser.reduced_h[m] - ser.absorbed_h[m] - ser.capacity_h[m]) / ser.freed_h[m]);
    out.check_reconciliation_max_gap = gap;
    out.check_min_capacity_h = Math.min(...ser.capacity_h);
    const ledPv = lines => out.ledger.filter(e => lines.includes(e.line)).reduce((a, e) => a + e.pv, 0);
    out.check_ledger_gap = o.ledger ? Math.abs(ledPv(CASH_LINES) - ledPv(COST_LINES) - out.npv_cash) : 0.0;
    return out;
  }

  // ---------------------------------------------------------------- uncertainty
  const logit = p => Math.log(p / (1 - p)), sig = x => 1 / (1 + Math.exp(-x));
  const Z90 = 1.2815515655446004;
  function drawScenario(pack, rng, center) {
    const U = pack.uncertainty, rho = U.execution_correlation;
    const q = rng.z(), out = {};
    for (const name of Object.keys(U.params)) {
      const spec = U.params[name];
      const e = rng.z(), load = spec.quality_sign || 0;
      const zz = load ? (rho * q * load + Math.sqrt(1 - rho * rho) * e) : e;
      let med = (center != null && center[name] != null) ? center[name] : spec.median;
      if (spec.dist === 'logitnormal') {
        med = Math.min(0.999, Math.max(0.001, med));
        const mu = logit(med), sd = (logit(spec.p90) - logit(spec.p10)) / (2 * Z90);
        out[name] = sig(mu + sd * zz);
      } else {
        med = Math.max(1e-9, med);
        const mu = Math.log(med), sd = (Math.log(spec.p90) - Math.log(spec.p10)) / (2 * Z90);
        out[name] = Math.exp(mu + sd * zz);
      }
    }
    return out;
  }
  function montecarlo(prep, S0, Q, n, seed, opts) {
    const rng = new RNG(seed == null ? 20261019 : seed);
    const o = Object.assign({ ledger: false }, opts || {});
    if (o.chosen == null) o.chosen = scope(prep, S0, 'cost_effective')[0];
    const res = [];
    for (let i = 0; i < n; i++) {
      const dd = drawScenario(prep.pack, rng, S0);
      const S = Object.assign({}, S0, dd);
      const r = simulate(prep, S, Q, o);
      res.push({ npv: r.npv_cash, plan: r.npv_plan, cap: r.pv_capacity, pay: r.payback_month, pos: r.positions_end, draw: dd, headline: r.headline });
    }
    return res;
  }
  function breakevenNet(prep, S0, Q, chosen, opts, key) {
    key = key || 'headline';
    if (chosen == null) chosen = scope(prep, S0)[0];
    const f = nr => simulate(prep, Object.assign({}, S0, { takeover: Math.min(0.999, nr / (1 - S0.review)) }), Q, Object.assign({}, opts || {}, { chosen }))[key];
    let lo = 0.0, hi = Math.min(0.95, 0.999 * (1 - S0.review));
    if (f(hi) < 0) return null;
    if (f(lo) >= 0) return 0.0;
    for (let i = 0; i < 32; i++) { const mid = (lo + hi) / 2; if (f(mid) >= 0) hi = mid; else lo = mid; }
    return hi;
  }
  function decide(pPos, policy) {
    if (pPos >= 0.7) return ['go', 'Go: phased rollout, no pause needed.'];
    if (pPos >= 0.4) return ['pilot', 'Pilot first and decide at the gate.'];
    if (policy.harvest_automation === 0) return ['capacity', 'Capacity case only: fund it if leadership commits to using the released time.'];
    return ['stop', 'Do not start on cash grounds.'];
  }
  function sensitivity(prep, S0, Q, chosen) {
    if (chosen == null) chosen = scope(prep, S0)[0];
    const U = prep.pack.uncertainty.params;
    const base = simulate(prep, S0, Q, { chosen }).headline;
    const rows = [];
    for (const k of Object.keys(U)) {
      const spec = U[k];
      const lo = simulate(prep, Object.assign({}, S0, { [k]: spec.p10 }), Q, { chosen }).headline;
      const hi = simulate(prep, Object.assign({}, S0, { [k]: spec.p90 }), Q, { chosen }).headline;
      rows.push({ param: k, low: spec.p10, high: spec.p90, npv_low: lo, npv_high: hi });
    }
    if (Q.harvest_automation > 0) {
      const a = Math.max(0.0, Q.harvest_automation - 0.25), b = Math.min(1.0, Q.harvest_automation + 0.25);
      rows.push({ param: 'harvest_automation', low: a, high: b,
        npv_low: simulate(prep, S0, Object.assign({}, Q, { harvest_automation: a }), { chosen }).headline,
        npv_high: simulate(prep, S0, Object.assign({}, Q, { harvest_automation: b }), { chosen }).headline });
    }
    rows.sort((x, y) => Math.abs(y.npv_high - y.npv_low) - Math.abs(x.npv_high - x.npv_low));
    return [base, rows];
  }
  const scenario = (pack, name) => Object.assign({}, pack.scenarios[name]);
  const policy = (pack, name) => Object.assign({}, pack.policies[name]);

  function funnel(prep, S, r) {
    const roles = prep.roleOrder.map(n => prep.roles[n]);
    const built = new Set(r.chosen.map(x => x.name));
    let cat = 0, able = 0, sc = 0;
    for (const R of roles) {
      cat += R.N * ((R.hours_by_cat['Directive'] || 0) + (R.hours_by_cat['Feedback Loop'] || 0)) / R.H;
      able += R.N * R.auto_share;
      let s = 0; for (const [w, a] of R.auto) if (built.has(w)) s += a; sc += R.N * s / R.H;
    }
    const take = sc * S.takeover, rev = take * (1 - S.review);
    const drag = r.roles.reduce((a, x) => a + x.auto_fte, 0);
    return [{ key: 'cat', stage: 'Hours in AI categories', fte: cat }, { key: 'able', stage: 'AI-able (Etter ceilings)', fte: able },
      { key: 'scope', stage: 'In workloads worth building', fte: sc }, { key: 'take', stage: 'AI takes over', fte: take },
      { key: 'review', stage: 'After human review', fte: rev }, { key: 'drag', stage: 'After complexity drag', fte: drag },
      { key: 'pos', stage: 'Positions removed', fte: r.positions_end }];
  }

  function report(data, pack, scenName, polName, nMc, seed, overrides, scopeK) {
    scenName = scenName || 'Moderate'; polName = polName || 'Attrition only';
    nMc = nMc == null ? 500 : nMc; seed = seed == null ? 20261019 : seed;
    const prep = prepare(data, pack);
    const S = Object.assign(scenario(pack, scenName), (overrides || {}).scenario || {});
    const Q = Object.assign(policy(pack, polName), (overrides || {}).policy || {});
    const [passing, ranked] = scope(prep, S);
    let chosen;
    if (scopeK != null) chosen = ranked.slice(0, scopeK);
    else chosen = sizeToPeak(prep, S, Q, passing)[0];
    const r = simulate(prep, S, Q, { chosen });
    const mc = montecarlo(prep, S, Q, nMc, seed, { chosen });
    const hl = mc.map(x => x.headline);
    const pPos = hl.filter(x => x > 0).length / hl.length;
    const be = breakevenNet(prep, S, Q, chosen);
    const [base, sens] = sensitivity(prep, S, Q, chosen);
    const [verdict, verdictText] = decide(pPos, Q);
    const led = {}; for (const e of r.ledger) led[e.line] = (led[e.line] || 0) + e.pv;
    const chosenNames = new Set(chosen.map(c => c.name));
    const s = r.series;
    return {
      meta: { pack: pack.meta.name, scenario: scenName, policy: polName, horizon: r.T, discount_rate: r.rate, basis: 'tasks', n_mc: nMc, seed },
      headline: { npv_cash: r.npv_cash, npv_plan: r.npv_plan, pv_avoidance: r.pv_avoidance, pv_capacity: r.pv_capacity, pv_costs: r.pv_costs,
        pv_savings: r.pv_savings, payback: r.payback_month, payback_plan: r.payback_plan, irr: r.irr, peak_funding: r.peak_funding,
        positions: r.positions_end, hires_avoided: r.avoided_end, freed_fte: r.freed_fte_ss, headcount: r.headcount, payroll: r.payroll_loaded,
        n_built: r.n_built, build_total: r.build_total, hurdle: r.capacity_hurdle, count_avoidance: r.count_avoidance, headline: r.headline },
      bands: { p10: quantile(hl, 0.1), p50: quantile(hl, 0.5), p90: quantile(hl, 0.9), p_positive: pPos,
        cap_p10: quantile(mc.map(x => x.cap), 0.1), cap_p90: quantile(mc.map(x => x.cap), 0.9) },
      breakeven_net: be, realisation: S.takeover * (1 - S.review), verdict, verdict_text: verdictText,
      sensitivity: { base, rows: sens }, funnel: funnel(prep, S, r), roles: r.roles,
      programme: { n_passing: passing.length, n_built: chosen.length,
        n_buy: chosen.filter(x => x.option === 'buy').length, n_build: chosen.filter(x => (x.option || 'build') === 'build').length },
      workloads: ranked.map((x, i) => ({ rank: i + 1, name: x.name, tier: x.tier, roles: x.roles.length, option: x.option || 'build', build: x.build_s,
        value_month: x.benefit, npv_at_cost: x.npv_at_cost, ratio: x.ratio, built: chosenNames.has(x.name),
        golive: r.golive[x.name] == null ? null : r.golive[x.name] })),
      series: { cash_net: s.cash_net, cum_cash: s.cum_cash, hard: s.hard, avoidance: s.avoidance, capacity: s.capacity,
        costs: s.costs, positions: s.positions, avoided_hires: s.avoided_hires, freed_h: s.freed_h },
      lines: led, ledger: r.ledger, flags: prep.flags,
      checks: { reconciliation_max_gap: r.check_reconciliation_max_gap, ledger_gap: r.check_ledger_gap, min_capacity_h: r.check_min_capacity_h },
      scenario_used: S, policy_used: Q
    };
  }

  const EVM = { RNG, prepare, scope, schedule, sizeToPeak, simulate, drawScenario, montecarlo, breakevenNet, decide, sensitivity,
    scenario, policy, funnel, report, quantile, pv, clone, norm };
  if (typeof module !== 'undefined' && module.exports) module.exports = EVM; else root.EVM = EVM;
})(typeof window !== 'undefined' ? window : globalThis);
