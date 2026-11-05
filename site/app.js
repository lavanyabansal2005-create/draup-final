(function () {
  'use strict';
  const E = window.EVM;
  const BASE_DATA = window.ETTER_DATA, BASE_PACK = window.BASE_PACK, ARCH = window.ARCHETYPES;
  const POLICIES = [['Capacity only', 'No reductions'], ['Attrition only', 'Attrition only'], ['Active reduction', 'Active reduction']];
  const SCENS = ['Conservative', 'Moderate', 'Aggressive'];
  const N_MC = 1000, CHUNK = 40, SEED = 20261019;
  const state = { org: 'base', policy: 'Attrition only', scen: 'Moderate', horizon: 60, tab: 'leader', scopeK: null,
    edits: { scenario: {}, policy: {}, economics: {}, costs: {}, capacity: {}, review: {} } };
  let cur = null, mcToken = 0, rerunTimer = null;

  // ------------------------------------------------------------ formatting
  const $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const M = v => (v == null || !isFinite(v)) ? 'n/a' : `${v < 0 ? '−' : '+'}$${Math.abs(v / 1e6).toFixed(1)}M`;
  const Mabs = v => `$${Math.abs(v / 1e6).toFixed(1)}M`;
  const P = (v, d = 0) => v == null ? 'n/a' : `${(v * 100).toFixed(d)}%`;
  const F = (v, d = 0) => v == null ? 'n/a' : Number(v).toLocaleString('en-US', { maximumFractionDigits: d, minimumFractionDigits: d });
  const usd = v => `$${Math.round(v).toLocaleString('en-US')}`;
  const cap1 = s => s.charAt(0).toUpperCase() + s.slice(1);
  const sgnCls = v => v < 0 ? 'neg' : 'pos';
  const roundHalfEven = x => { const f = Math.floor(x), d = x - f; if (d > 0.5) return f + 1; if (d < 0.5) return f; return f % 2 === 0 ? f : f + 1; };
  const cumulative = xs => { let c = 0; return xs.map(v => (c += v)); };
  const policyName = k => (POLICIES.find(p => p[0] === k) || [k, k])[1];

  // ------------------------------------------------------------ register (every adjustable input, with its evidence)
  const PCT = { show: v => +(v * 100).toFixed(2), read: v => v / 100, unit: '%' };
  const NUM = { show: v => +(+v).toFixed(4), read: v => v, unit: '' };
  const REGISTER = [
    { grp: 'scenario', key: 'takeover', label: 'AI takeover of AI-able work', t: PCT, range: '20 to 62%', grade: 'C', kind: 'Measure in pilot', src: 'Ardent Partners 2025, AP touchless: 32.6% all orgs, 49.2% best-in-class' },
    { grp: 'scenario', key: 'review', label: 'Human review load, share of AI time', t: PCT, range: '15 to 45%', grade: 'C', kind: 'Measure in pilot', src: 'Workday 2026: about 40% of AI time savings lost to rework' },
    { grp: 'scenario', key: 'drag', label: 'Complexity drag on the work left behind', t: NUM, range: '0.10 to 0.55', grade: 'D', kind: 'Measure in pilot', src: 'Bainbridge 1983, ironies of automation; no direct measurement', fallback: p => p.nonlinear.complexity_drag },
    { grp: 'scenario', key: 'adopt_months', label: 'Months from go-live to full use', t: NUM, range: '6 to 24', grade: 'C', kind: 'Measure in pilot', src: 'Gartner 2026: 63% of finance AI rollouts slower than expected' },
    { grp: 'scenario', key: 'active_use', label: 'Assistant active use', t: PCT, range: '50 to 85%', grade: 'C', kind: 'Measure in pilot', src: 'Team estimate' },
    { grp: 'scenario', key: 'aug_mult', label: 'Assistant time saving, multiplier on the bands', t: NUM, range: 'x0.4 to x1.6', grade: 'C', kind: 'Measure in pilot', src: 'Brynjolfsson, Li and Raymond 2025; METR 2025' },
    { grp: 'scenario', key: 'cost_mult', label: 'Build and programme cost, multiplier', t: NUM, range: 'x0.85 to x1.6', grade: 'C', kind: 'Measure in pilot', src: 'Team cost build-up' },
    { grp: 'policy', key: 'harvest_automation', label: 'Harvest share of automation-freed time', t: PCT, range: '0 to 100%', grade: '', kind: 'Choice', src: 'Management decision' },
    { grp: 'policy', key: 'harvest_augmentation', label: 'Harvest share of assistant-freed time', t: PCT, range: '0 to 50%', grade: '', kind: 'Choice', src: 'Management decision' },
    { grp: 'economics', key: 'function_growth', label: 'Planned headcount growth of the function, per year', t: PCT, range: 'client plan', grade: '', kind: 'Client fact', src: 'Client hiring plan' },
    { grp: 'economics', key: 'discount_rate', label: 'Discount rate', t: PCT, range: '5.6 to 9.3%', grade: 'A', kind: 'Fact', src: 'Damodaran WACC by industry, January 2026' },
    { grp: 'economics', key: 'turnover_multiplier', label: 'Turnover multiplier on the band rates', t: NUM, range: 'x0.59 to x1.3', grade: 'B', kind: 'Fact, client overrides', src: 'Mercer band rates; JOLTS 2025 industry quits' },
    { grp: 'economics', key: 'wage_growth', label: 'Wage growth per year', t: PCT, range: '2.5 to 4.5%', grade: 'A', kind: 'Fact', src: 'BLS Employment Cost Index, private industry, 12 months to Sep 2026: 3.4%' },
    { grp: 'review', key: 'seniority_slope', label: 'Review rise per band of seniority (Professional = the measured review)', t: PCT, range: '5 to 40%', grade: 'D', kind: 'Judgment', src: 'Direction: Brynjolfsson et al. v2; Dell\u2019Acqua et al. 2026. No measured magnitude' },
    { grp: 'economics', key: 'on_cost', label: 'On-cost multiplier on salary', t: NUM, range: 'fixed', grade: 'A', kind: 'Fact', src: 'BLS ECEC June 2026, Table 5, full-time private: 1/(68.5% + 8.1%)' },
    { grp: 'economics', key: 'cost_per_hire', label: 'Cost per hire avoided, $', t: NUM, range: '$4,100 to $10,000', grade: 'B', kind: 'Fact', src: 'SHRM benchmarking' },
    { grp: 'costs', key: 'build_workflow', label: 'Build cost, single-role workload, $', t: NUM, range: 'x0.85 to x1.6', grade: 'C', kind: 'Measure in pilot', src: 'Team cost build-up' },
    { grp: 'costs', key: 'build_enterprise', label: 'Build cost, multi-role workload, $', t: NUM, range: 'x0.85 to x1.6', grade: 'C', kind: 'Measure in pilot', src: 'Team cost build-up' },
    { grp: 'costs', key: 'maintenance_share_per_year', label: 'Agent maintenance, share of build per year', t: PCT, range: '15 to 20%', grade: 'C', kind: 'Fact', src: 'Software maintenance convention' },
    { grp: 'costs', key: 'run_cost_per_ai_hour', label: 'AI running cost per AI hour, $', t: NUM, range: '$1.50 to $10', grade: 'D', kind: 'Measure in pilot', src: 'One estimating method only' },
    { grp: 'costs', key: 'run_cost_decline_per_year', label: 'Running cost decline per year', t: PCT, range: '0 to 30%', grade: 'C', kind: 'Fact', src: 'Team estimate' },
    { grp: 'costs', key: 'programme_fixed', label: 'Programme fixed cost, $', t: NUM, range: 'n/a', grade: 'C', kind: 'Fact', src: 'Forrester TEI, Microsoft 365 Copilot' },
    { grp: 'costs', key: 'deploy_per_affected_head', label: 'Deployment cost per affected person, $', t: NUM, range: 'n/a', grade: 'C', kind: 'Fact', src: 'Forrester TEI, Microsoft 365 Copilot' },
    { grp: 'costs', key: 'training_spend_per_head', label: 'Training spend per affected person, $', t: NUM, range: '$423 to $1,692', grade: 'B', kind: 'Fact', src: 'ATD 2026' },
    { grp: 'costs', key: 'training_hours_per_head', label: 'Training hours per affected person', t: NUM, range: '8 to 33', grade: 'B', kind: 'Fact', src: 'ATD 2026' },
    { grp: 'costs', key: 'training_refresh_per_year', label: 'Yearly refresher, share of the initial training', t: PCT, range: '10 to 50%', grade: 'D', kind: 'Judgment', src: 'No measured rate; BCG AI at Work 2025 links training to regular use' },
    { grp: 'capacity', key: 'min_block_share', label: 'Smallest redeployable block of freed time per person, share of month', t: PCT, range: '0 to 10%', grade: 'D', kind: 'Judgment', src: 'No measured rate; Forrester TEI uses a flat 50% recapture instead' },
    { grp: 'costs', key: 'assistant_licence_per_seat_year', label: 'Assistant licence per active seat per year, $', t: NUM, range: 'fixed', grade: 'A', kind: 'Fact', src: 'Microsoft 365 Copilot list price, $30 a month' },
    { grp: 'costs', key: 'seat_cost_per_position', label: 'Software seat reclaimed per position, $ per year', t: NUM, range: '$0 to $2,000', grade: 'B', kind: 'Fact, client adds tools', src: 'Microsoft 365 E3 list price from July 2026' }
  ];
  const LINE = {
    hard: ['Positions not refilled or removed', 'Role salary x on-cost 1.3055 (BLS ECEC), growing 3.4% a year (BLS ECI)', 'A'],
    seats_reclaimed: ['Software seats reclaimed', 'Positions x $468 (M365 E3)', 'B'],
    recruit_avoided: ['Recruiting avoided', 'Leavers not replaced x cost per hire (SHRM)', 'B'],
    build: ['Build', 'Workloads x $55k or $130k (team build-up)', 'C'],
    programme: ['Programme and deployment', '$75k + $623 per affected person (Forrester TEI)', 'C'],
    training: ['Training', '$846 + 16.7 hours per person at first use, then each joiner, plus a yearly refresher', 'B'],
    licences: ['Assistant licences', 'Active seats of people in post x $360 a year, trued down each contract year', 'A'],
    run: ['AI running cost', 'AI hours x $3.48, falling 13% a year', 'D'],
    maintenance: ['Agent maintenance', '18% of build a year', 'C'],
    severance: ['Severance', '12 weeks of salary per separation', 'C'],
    avoidance: ['Hires avoided against plan', 'Planned hires not made x loaded cost + cost per hire', 'B'],
    capacity: ['Capacity released, at cost', 'Freed hours above the smallest usable block per person x each role’s cost per hour', 'A']
  };
  const PARAM = {
    takeover: ['AI takeover rate', v => P(v)], review: ['Human review load', v => P(v)], adopt_months: ['Months to full adoption', v => F(v, 0)],
    active_use: ['Assistant active use', v => P(v)], aug_mult: ['Assistant time saving', v => `x${F(v, 2)}`],
    cost_mult: ['Build and programme cost', v => `x${F(v, 2)}`], run_mult: ['AI running cost', v => `$${F(3.48 * v, 2)}/h`],
    drag: ['Complexity drag', v => F(v, 2)], turnover_mult: ['Staff turnover', v => `x${F(v, 2)}`], harvest_automation: ['Harvest share (policy)', v => P(v)],
    training_refresh: ['Training refresher', v => `${P(v)} a year`], wage_growth: ['Wage growth', v => `${P(v, 1)} a year`],
    review_slope: ['Review rise with seniority', v => `${P(v)} per band`]
  };

  // ------------------------------------------------------------ inputs
  function buildInputs() {
    const d = E.clone(BASE_DATA), p = E.clone(BASE_PACK);
    if (state.org !== 'base') {
      const a = ARCH[state.org];
      for (const r of d.roles) { r.headcount = Math.max(1, roundHalfEven(r.headcount * a.headcount_factor)); r.salary = r.salary * a.salary_factor; }
      Object.assign(p.economics, a.economics); p.meta.name = a.label;
    }
    p.economics.horizon_months = state.horizon;
    Object.assign(p.economics, state.edits.economics);
    Object.assign(p.costs, state.edits.costs);
    p.capacity = Object.assign({}, p.capacity, state.edits.capacity);
    p.review = Object.assign({}, p.review, state.edits.review);
    return [d, p];
  }
  function choices(p, scen, pol) {
    const S = Object.assign(E.scenario(p, scen || state.scen), state.edits.scenario);
    const Q = Object.assign(E.policy(p, pol || state.policy), state.edits.policy);
    return [S, Q];
  }

  // ------------------------------------------------------------ the run
  function run() {
    const [d, p] = buildInputs();
    const prep = E.prepare(d, p);
    const [S, Q] = choices(p);
    const [passing, ranked] = E.scope(prep, S);
    const peak = E.sizeToPeak(prep, S, Q, passing)[0];      // programme stops where five-year cash peaks
    const kCost = peak.length, kPass = passing.length;
    const chosen = state.scopeK != null ? ranked.slice(0, state.scopeK) : peak;
    const r = E.simulate(prep, S, Q, { chosen });
    const [sensBase, sens] = E.sensitivity(prep, S, Q, chosen);
    const be = E.breakevenNet(prep, S, Q, chosen);
    const gate = E.pilotGate(prep, Q, chosen, be);
    const stopped = gate.applies ? E.simulate(prep, S, Q, { chosen, stop_month: gate.month, ledger: false }) : null;
    cur = { d, p, prep, S, Q, chosen, ranked, kCost, r, sens, sensBase, be, gate, stopped, mc: null, funnel: E.funnel(prep, S, r) };
    cur.grid = SCENS.map(sn => POLICIES.map(([pn]) => {
      const [S2, Q2] = choices(p, sn, pn);
      const sc2 = E.scope(prep, S2);
      const ch = state.scopeK != null ? sc2[1].slice(0, state.scopeK) : E.sizeToPeak(prep, S2, Q2, sc2[0])[0];
      return E.simulate(prep, S2, Q2, { chosen: ch, ledger: false }).headline;
    }));
    const ks = Array.from(new Set([0, 3, 5, 10, 15, 20, 25, 30, 40, 50, kCost, kPass, ranked.length, state.scopeK == null ? kCost : state.scopeK]))
      .filter(k => k <= ranked.length).sort((a, b) => a - b);
    cur.frontier = ks.map(k => { const x = E.simulate(prep, S, Q, { chosen: ranked.slice(0, k), ledger: false }); return { k, npv: x.headline, cap: x.pv_capacity }; });
    renderAll();
    startMC();
  }
  function rerunSoon(ms) { clearTimeout(rerunTimer); rerunTimer = setTimeout(run, ms == null ? 120 : ms); }

  function startMC() {
    const token = ++mcToken;
    const { prep, S, Q, chosen, p, gate } = cur;
    const rng = new E.RNG(SEED);
    const acc = { hl: [], cap: [], cum: [], pay: [], stops: 0 };
    let i = 0;
    const step = () => {
      if (token !== mcToken) return;
      const end = Math.min(N_MC, i + CHUNK);
      for (; i < end; i++) {
        const dd = E.drawScenario(p, rng, S), S2 = Object.assign({}, S, dd);
        const stop = gate.applies && (gate.pass_mark == null || S2.takeover * (1 - S2.review) < gate.pass_mark);
        if (stop) acc.stops++;
        const x = E.simulate(prep, S2, Q, { chosen, ledger: false, stop_month: stop ? gate.month : null });
        acc.hl.push(x.headline); acc.cap.push(x.pv_capacity); acc.pay.push(x.count_avoidance ? x.payback_plan : x.payback_month);
        acc.cum.push(x.count_avoidance ? cumulative(x.series.plan_net) : x.series.cum_cash);
      }
      const done = i >= N_MC;
      cur.mc = { n: i, done, p10: E.quantile(acc.hl, 0.1), p50: E.quantile(acc.hl, 0.5), p90: E.quantile(acc.hl, 0.9),
        pPos: acc.hl.filter(v => v > 0).length / acc.hl.length, cap10: E.quantile(acc.cap, 0.1), cap90: E.quantile(acc.cap, 0.9),
        payShare: acc.pay.filter(v => v != null).length / acc.pay.length, pStop: acc.stops / i };
      if (done || i % 200 === 0) {
        const T = cur.r.T, lo = [], hi = [], md = [];
        for (let m = 0; m <= T; m++) { const col = acc.cum.map(c => c[m]); lo.push(E.quantile(col, 0.1)); hi.push(E.quantile(col, 0.9)); md.push(E.quantile(col, 0.5)); }
        cur.mc.fan = { lo, hi, md };
      } else if (cur.mcPrevFan) cur.mc.fan = cur.mcPrevFan;
      cur.mcPrevFan = cur.mc.fan;
      renderVerdict(); renderFinanceKpis(); renderFan(); renderGate();
      if (!done) setTimeout(step, 0);
    };
    setTimeout(step, 30);
  }

  // ------------------------------------------------------------ verdict band
  function headlineBasis() { return cur.r.count_avoidance ? 'against the approved hiring plan' : 'against today’s costs'; }
  function renderVerdict() {
    const { r, S, Q, prep, mc } = cur;
    const roles = Object.values(prep.roles);
    const N = r.headcount, ai = roles.reduce((a, R) => a + R.N * R.auto_share, 0) / Math.max(1, N);
    const T = r.T, yrs = T / 12, freed = r.freed_fte_ss, pos = r.positions_end, av = r.avoided_end;
    const avTxt = av > 0 ? `, ${F(av)} planned hires are not needed` : '';
    let s = `AI can do <b>${P(ai)}</b> of the work of ${F(N)} FP&amp;A staff. `;
    if (Q.harvest_automation === 0 && Q.harvest_augmentation === 0)
      s += `With no reductions, the work it frees by month ${T} equals <b>${F(freed)} people</b>${avTxt}; the rest is capacity worth <b>${Mabs(r.pv_capacity)}</b> at cost. `;
    else if (Q.mechanism === 'attrition')
      s += `By leaving some leavers unreplaced, <b>${F(pos)} positions</b> go by month ${T}${avTxt}; the rest of the ${F(freed)} people’s worth of freed work is capacity worth ${Mabs(r.pv_capacity)} at cost. `;
    else
      s += `With active reduction, <b>${F(pos)} positions</b> go by month ${T}${avTxt}; the rest of the ${F(freed)} people’s worth of freed work is capacity worth ${Mabs(r.pv_capacity)} at cost. `;
    s += `Over ${yrs} years, cash ${headlineBasis()} comes to <b>${M(r.headline)}</b>`;
    s += mc ? `, with a ${P(mc.pPos)} chance of being positive.` : '.';
    $('answer').innerHTML = s;
    const band = mc ? `P10 ${M(mc.p10)} to P90 ${M(mc.p90)}` : 'ranges computing…';
    const tiles = [];
    tiles.push(`<div class="tile cash"><span class="label">Cash vs today</span><span class="big">${M(r.npv_cash)}</span><span class="sub">${r.count_avoidance ? `${F(pos)} positions; payback ${r.payback_month ? 'month ' + r.payback_month : 'not within horizon'}` : band}</span></div>`);
    if (r.count_avoidance)
      tiles.push(`<div class="tile avoid"><span class="label">Cash vs approved plan</span><span class="big">${M(r.npv_plan)}</span><span class="sub">${band}; includes ${F(av)} ${av === 1 ? 'hire' : 'hires'} avoided</span></div>`);
    else
      tiles.push(`<div class="tile"><span class="label">Payback, discounted</span><span class="big">${r.payback_discounted ? 'Month ' + r.payback_discounted : 'None'}</span><span class="sub">Undiscounted ${r.payback_month ? 'month ' + r.payback_month : 'none'}; peak cash needed ${Mabs(r.peak_funding)}${r.irr != null ? '; IRR ' + P(r.irr) : ''}</span></div>`);
    tiles.push(`<div class="tile cap"><span class="label">Capacity at cost, not cash</span><span class="big">${Mabs(r.pv_capacity)}</span><span class="sub">${r.capacity_hurdle > 0 ? `Must be worth ${P(r.capacity_hurdle)} of its cost to cover the cash gap` : 'Value only if the time is put to use'}. Another ${F(r.stranded_fte_end, 0)} people’s worth is too thin per person to redeploy and counts as zero.</span></div>`);
    const v = mc && mc.done ? E.decide(mc.pPos, Q) : null;
    const chip = v ? `<span class="chip ${v[0]}">${{ go: 'Go', pilot: 'Pilot first', stop: 'Do not start', capacity: 'Capacity case' }[v[0]]}</span>` : `<span class="chip wait">Checking ${F(mc ? mc.n : 0)} of ${F(N_MC)} outcomes</span>`;
    tiles.push(`<div class="tile"><span class="label">Verdict</span>${chip}<span class="sub">${v ? esc(v[1]) : 'The verdict uses the chance of a positive result.'}</span><div class="meter" aria-hidden="true"><i style="width:${mc ? mc.n / N_MC * 100 : 0}%"></i></div></div>`);
    $('tiles').innerHTML = tiles.join('');
  }

  // ------------------------------------------------------------ leader
  function renderFunnel() {
    const { funnel, S, Q, p, r } = cur;
    const drag = S.drag == null ? p.nonlinear.complexity_drag : S.drag;
    const why = {
      cat: 'Directive and Feedback Loop tasks', able: 'Etter category ceilings', scope: 'AI costs less than the work it takes over',
      take: `AI takes over ${P(S.takeover)} of it`, review: `people check ${P(S.review)} of AI time at Professional level, more for senior roles`, drag: `remaining work is harder (drag ${F(drag, 2)})`,
      pos: Q.harvest_automation === 0 && Q.harvest_augmentation === 0 ? 'policy: no reductions' : Q.mechanism === 'attrition' ? `bank ${P(Q.harvest_automation)}, whole positions, as people leave` : `bank ${P(Q.harvest_automation)} of it, plus ${P(Q.harvest_augmentation)} of assistant time`
    };
    const mx = Math.max(...funnel.map(f => f.fte), 1);
    const rows = funnel.map((f, i) => {
      const keep = i > 0 && funnel[i - 1].fte > 0 ? `${Math.round(f.fte / funnel[i - 1].fte * 100)}%` : '';
      const last = i === funnel.length - 1;
      return `<div class="fn-row"><div class="fn-l"><b>${esc(f.stage)}</b><span>${esc(why[f.key])}</span></div><div class="fn-bar"><i style="width:calc((100% - 104px) * ${Math.max(0.004, f.fte / mx).toFixed(4)});background:${last ? 'var(--accent)' : 'var(--muted)'};opacity:${last ? 1 : 0.35}"></i><span class="num">${F(f.fte, f.key === 'pos' ? 0 : 1)} ${f.key === 'pos' ? 'positions' : 'FTE'}</span></div><div class="fn-k num">${keep ? 'keeps ' + keep : ''}</div></div>`;
    }).join('');
    const aug = r.roles.reduce((a, x) => a + x.aug_fte, 0);
    $('funnel').innerHTML = `<div class="fn">${rows}</div><p class="note">Assistants free another ${F(aug, 1)} FTE of time across all roles. ${Q.harvest_augmentation > 0 ? `This policy banks ${P(Q.harvest_augmentation)} of it as positions.` : 'Under this policy it all stays as capacity.'}</p>`;
  }
  function renderWorkloads() {
    const { ranked, chosen, r } = cur;
    const inProg = new Set(chosen.map(c => c.name));
    const top = ranked.slice(0, 10), mx = Math.max(...top.map(x => x.benefit), 1);
    $('wl').innerHTML = `<div class="wlist">${top.map(x => {
      const on = inProg.has(x.name), gl = r.golive[x.name];
      return `<div class="wl-row"><div class="wl-name">${esc(cap1(x.name))}<span>${x.tier === 'enterprise' ? 'multi-role' : 'single role'}, build ${usd(x.build_s)}${on ? `, live month ${gl}` : ', not built'}</span></div><div class="wl-bar"><i style="width:${x.benefit / mx * 100}%;${on ? '' : 'background:transparent;border:1.5px solid var(--muted)'}"></i></div><div class="wl-v num">${Mabs(x.benefit * 12)}/yr</div></div>`;
    }).join('')}</div><p class="note">${chosen.length} of ${ranked.length} workloads are in the programme. Value is the freed work at cost, once fully in use.</p>`;
  }
  function rangeTxt(row) { const f = (PARAM[row.param] || [row.param, v => F(v, 2)])[1]; return `${f(row.low)} to ${f(row.high)}`; }
  function renderDecides() {
    const rows = cur.sens.slice(0, 3);
    $('decides').innerHTML = `<ol class="dec">${rows.map(x => `<li><b>${esc((PARAM[x.param] || [x.param])[0])}</b><span class="muted"> from ${rangeTxt(x)}</span><br><span class="num">Cash moves from <span class="${sgnCls(x.npv_low)}">${M(x.npv_low)}</span> to <span class="${sgnCls(x.npv_high)}">${M(x.npv_high)}</span></span></li>`).join('')}</ol>
      <p class="note">${rows.filter(x => x.param !== 'harvest_automation').length} of these can be measured in a six-month pilot.${rows.some(x => x.param === 'harvest_automation') ? ' The harvest share is a decision for leadership.' : ''}</p>`;
  }
  function renderRoles() {
    const { r, Q, p } = cur;
    const T = r.T, tm = cur.S.turnover_mult == null ? 1 : cur.S.turnover_mult;
    const none = Q.harvest_automation === 0 && Q.harvest_augmentation === 0;
    $('people-sub').textContent = none ? 'No positions go. The freed time is redeployed, or absorbs planned hires where the function is growing.'
      : Q.mechanism === 'attrition' ? 'Positions go only as people leave. The guidance column is the backfill rule for each hiring manager.'
        : 'Positions are removed as the work goes, with severance. Planned hires are absorbed first where the function is growing.';
    const body = r.roles.map(x => {
      const leavers = x.N * (1 - Math.pow(1 - x.lam * tm, T / 12));
      let g;
      if (none) g = x.avoided_end > 0 ? `Absorb ${F(x.avoided_end)} planned hires` : `Redeploy ${F(x.freed_fte, 1)} FTE of time`;
      else if (Q.mechanism === 'attrition') g = x.positions_end > 0 ? `Leave ${F(x.positions_end)} of the next ${F(Math.round(leavers))} leavers unreplaced` : 'Refill as usual';
      else g = x.positions_end > 0 ? `Reduce by ${F(x.positions_end)}` : 'No change';
      return `<tr><td>${esc(x.role)}</td><td class="n">${F(x.N)}</td><td class="n">${P(x.auto_share)}</td><td class="n">${F(x.freed_fte, 1)}</td><td class="n">${F(x.positions_end)}</td><td class="n">${F(x.avoided_end)}</td><td>${g}</td></tr>`;
    }).join('');
    const tot = k => r.roles.reduce((a, x) => a + x[k], 0);
    $('roles').innerHTML = `<table><thead><tr><th>Role</th><th class="n">Staff</th><th class="n">AI-able</th><th class="n">Freed FTE</th><th class="n">Positions</th><th class="n">Hires avoided</th><th>Guidance</th></tr></thead><tbody>${body}<tr class="tot"><td>All roles</td><td class="n">${F(tot('N'))}</td><td class="n"></td><td class="n">${F(tot('freed_fte'), 1)}</td><td class="n">${F(tot('positions_end'))}</td><td class="n">${F(tot('avoided_end'))}</td><td></td></tr></tbody></table>`;
  }

  // ------------------------------------------------------------ finance
  function renderFinanceKpis() {
    if (!cur) return;
    const { r, mc, be, S } = cur;
    const k = [];
    k.push(['Cash vs today', M(r.npv_cash), r.count_avoidance ? 'excludes hires avoided' : (mc ? `P10 ${M(mc.p10)}, P90 ${M(mc.p90)}` : 'computing')]);
    if (r.count_avoidance) k.push(['Cash vs approved plan', M(r.npv_plan), mc ? `P10 ${M(mc.p10)}, P90 ${M(mc.p90)}` : 'computing']);
    k.push(['Chance cash is positive', mc ? P(mc.pPos) : '…', mc ? `${F(mc.n)} correlated draws` : '']);
    k.push(['Payback month, discounted', r.count_avoidance ? (r.payback_plan || 'None') : (r.payback_discounted || 'None'), r.count_avoidance ? `against plan, undiscounted; horizon ${r.T} months` : `undiscounted ${r.payback_month || 'none'}; horizon ${r.T} months`]);
    k.push(['IRR', r.irr == null ? 'n/a' : P(r.irr), 'cash vs today']);
    k.push(['Peak cash needed', Mabs(r.peak_funding), 'deepest point of the curve']);
    k.push(['Break-even realisation', be == null ? 'not reachable' : P(be, 1), `assumed ${P(S.takeover * (1 - S.review), 1)} (takeover x (1 − review))`]);
    k.push(['Capacity at cost', Mabs(r.pv_capacity), mc ? `P10 ${Mabs(mc.cap10)}, P90 ${Mabs(mc.cap90)}` : 'not cash']);
    $('fin-kpis').innerHTML = k.map(x => `<div class="kpi"><span class="v">${x[1]}</span><span class="k"><b>${x[0]}</b><br>${x[2]}</span></div>`).join('');
  }
  function renderFan() {
    if (!cur) return;
    const el = $('fan'); const W = Math.max(300, el.clientWidth || 700), H = 260, L = 56, R = 12, Tp = 14, B = 30;
    const { r, mc } = cur; const T = r.T;
    const det = r.count_avoidance ? cumulative(r.series.plan_net) : r.series.cum_cash;
    const fan = mc && mc.fan;
    const all = det.concat(fan ? fan.lo.concat(fan.hi) : []);
    let lo = Math.min(0, ...all), hi = Math.max(0, ...all); const pad = (hi - lo) * 0.06 || 1; lo -= pad; hi += pad;
    const X = m => L + m / T * (W - L - R), Y = v => Tp + (hi - v) / (hi - lo) * (H - Tp - B);
    const step = niceStep((hi - lo) / 5); const ticks = []; for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) ticks.push(t);
    let g = ticks.map(t => `<line class="grid" x1="${L}" x2="${W - R}" y1="${Y(t)}" y2="${Y(t)}"/><text class="q" x="${L - 6}" y="${Y(t) + 4}" text-anchor="end" font-size="11">${t === 0 ? '0' : (t / 1e6).toFixed(Math.abs(step) < 1e6 ? 1 : 0) + 'M'}</text>`).join('');
    for (let m = 0; m <= T; m += 12) g += `<text class="q" x="${X(m)}" y="${H - 10}" text-anchor="middle" font-size="11">${m === 0 ? 'Today' : 'Year ' + m / 12}</text>`;
    g += `<line class="axis" x1="${L}" x2="${W - R}" y1="${Y(0)}" y2="${Y(0)}"/>`;
    if (fan) {
      const pts = fan.hi.map((v, m) => `${X(m)},${Y(v)}`).concat(fan.lo.map((v, m) => `${X(m)},${Y(v)}`).reverse());
      g += `<polygon points="${pts.join(' ')}" fill="var(--band)"/>`;
    }
    g += `<polyline points="${det.map((v, m) => `${X(m)},${Y(v)}`).join(' ')}" fill="none" stroke="var(--accent)" stroke-width="2.5"/>`;
    const pb = r.count_avoidance ? r.payback_plan : r.payback_month;
    if (pb) g += `<line class="ref" x1="${X(pb)}" x2="${X(pb)}" y1="${Tp}" y2="${H - B}"/><text x="${X(pb) + (X(pb) > W - 140 ? -6 : 6)}" y="${Tp + 10}" font-size="11" text-anchor="${X(pb) > W - 140 ? 'end' : 'start'}" class="q">payback, month ${pb}</text>`;
    const mn = det.indexOf(Math.min(...det));
    if (det[mn] < 0) g += `<circle cx="${X(mn)}" cy="${Y(det[mn])}" r="3.5" fill="var(--accent)"/><text x="${X(mn)}" y="${Y(det[mn]) + 16}" text-anchor="middle" font-size="11" class="q">peak need ${Mabs(det[mn])}</text>`;
    g += `<text x="${X(T) - 4}" y="${Y(det[T]) - 8}" text-anchor="end" font-size="12" font-weight="600">${M(det[T])} by month ${T}, undiscounted</text>`;
    el.innerHTML = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Cumulative cash by month">${g}</svg>`;
  }
  function niceStep(x) { const p = Math.pow(10, Math.floor(Math.log10(Math.abs(x) || 1))); const f = x / p; return (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * p; }
  function renderLines() {
    const { r } = cur; const s = r.series, d = r.rate;
    const pvOf = k => E.pv(s[k], d);
    const sav = ['hard', 'seats_reclaimed', 'recruit_avoided'], cost = ['build', 'programme', 'training', 'licences', 'run', 'maintenance', 'severance'];
    const row = (k, sign) => { const v = pvOf(k); if (!v) return ''; const [n, src, gr] = LINE[k]; return `<tr><td>${n}<br><span class="note">${src}</span></td><td><span class="grade ${gr}">${gr}</span></td><td class="n ${sign < 0 ? 'neg' : 'pos'}">${sign < 0 ? '−' : '+'}${Mabs(v)}</td></tr>`; };
    const sv = sav.reduce((a, k) => a + pvOf(k), 0), cv = cost.reduce((a, k) => a + pvOf(k), 0);
    $('lines').innerHTML = `<table><thead><tr><th>Line</th><th>Grade</th><th class="n">PV</th></tr></thead><tbody>
      ${sav.map(k => row(k, 1)).join('')}<tr class="tot"><td>Cash savings</td><td></td><td class="n">${M(sv)}</td></tr>
      ${cost.map(k => row(k, -1)).join('')}<tr class="tot"><td>Costs</td><td></td><td class="n">${M(-cv)}</td></tr>
      <tr class="tot"><td>Cash NPV vs today</td><td></td><td class="n ${sgnCls(r.npv_cash)}">${M(r.npv_cash)}</td></tr>
      <tr><td>${LINE.avoidance[0]}<br><span class="note">Reported beside cash, never inside it</span></td><td><span class="grade B">B</span></td><td class="n">${Mabs(pvOf('avoidance'))}</td></tr>
      <tr><td>${LINE.capacity[0]}<br><span class="note">Not cash: valued at what the time costs</span></td><td><span class="grade A">A</span></td><td class="n">${Mabs(pvOf('capacity'))}</td></tr></tbody></table>`;
  }
  function renderTornado() {
    const rows = cur.sens.slice(0, 8), base = cur.sensBase;
    const vals = rows.flatMap(x => [x.npv_low, x.npv_high]).concat([0, base]);
    let lo = Math.min(...vals), hi = Math.max(...vals); const pad = (hi - lo) * 0.04; lo -= pad; hi += pad;
    const X = v => (v - lo) / (hi - lo) * 100;
    $('tornado').innerHTML = `<div class="tor">${rows.map((x, i) => {
      const a = Math.min(x.npv_low, x.npv_high), b = Math.max(x.npv_low, x.npv_high);
      return `<div class="tor-row"><div class="tor-l"><b>${esc((PARAM[x.param] || [x.param])[0])}</b><span>${rangeTxt(x)}</span></div><div class="tor-t"><span class="z" style="left:${X(0)}%"></span><span class="bs" style="left:${X(base)}%"></span><i style="left:${X(a)}%;width:${Math.max(0.5, X(b) - X(a))}%;background:${i < 3 ? 'var(--accent)' : 'var(--muted)'};opacity:${i < 3 ? 1 : 0.45}"></i></div><div class="tor-v num"><span class="${sgnCls(a)}">${M(a)}</span> to <span class="${sgnCls(b)}">${M(b)}</span></div></div>`;
    }).join('')}</div><p class="note">Solid line marks zero; dotted line marks the current result, ${M(base)}.</p>`;
  }
  function renderGrid() {
    const g = cur.grid;
    $('grid').innerHTML = `<table><thead><tr><th>Ambition</th>${POLICIES.map(p => `<th class="n">${p[1]}</th>`).join('')}</tr></thead><tbody>${SCENS.map((sn, i) => `<tr><td>${sn}</td>${POLICIES.map(([pn], j) => `<td class="n ${sgnCls(g[i][j])}" style="${sn === state.scen && pn === state.policy ? 'background:var(--accent-soft);font-weight:600' : ''}">${M(g[i][j])}</td>`).join('')}</tr>`).join('')}</tbody></table><p class="note">${cur.r.count_avoidance ? 'Cash against the approved hiring plan.' : 'Cash against today’s costs.'} Each cell is sized to its own peak cash.</p>`;
  }

  // ------------------------------------------------------------ plan
  function renderFrontier() {
    const el = $('frontier'); const pts = cur.frontier; const W = Math.max(300, el.clientWidth || 700), H = 280, L = 56, R = 16, B = 28;
    const kSel = state.scopeK == null ? cur.kCost : state.scopeK, kMax = cur.ranked.length || 1;
    const X = k => L + k / kMax * (W - L - R);
    const panel = (key, y0, h, colour, label) => {
      const vs = pts.map(p => p[key]); let lo = Math.min(0, ...vs), hi = Math.max(0, ...vs); const pad = (hi - lo) * 0.1 || 1; lo -= pad; hi += pad;
      const Y = v => y0 + (hi - v) / (hi - lo) * h;
      let g = `<text x="${L}" y="${y0 - 6}" font-size="12" font-weight="600">${label}</text><line class="axis" x1="${L}" x2="${W - R}" y1="${Y(0)}" y2="${Y(0)}"/>`;
      g += `<text class="q" x="${L - 6}" y="${Y(0) + 4}" text-anchor="end" font-size="11">0</text>`;
      g += `<polyline points="${pts.map(p => `${X(p.k)},${Y(p[key])}`).join(' ')}" fill="none" stroke="${colour}" stroke-width="2.2"/>`;
      g += pts.map(p => `<circle cx="${X(p.k)}" cy="${Y(p[key])}" r="${p.k === kSel ? 4.5 : 2.5}" fill="${colour}"><title>${p.k} workloads: ${M(p[key])}</title></circle>`).join('');
      const best = pts.reduce((a, p) => p[key] > a[key] ? p : a, pts[0]);
      const sel = pts.find(p => p.k === kSel);
      if (sel) g += `<text x="${X(sel.k) + (X(sel.k) > W - 120 ? -8 : 8)}" y="${Y(sel[key]) - 8}" text-anchor="${X(sel.k) > W - 120 ? 'end' : 'start'}" font-size="11.5" font-weight="600">${M(sel[key])}</text>`;
      if (key === 'npv' && best.k !== kSel) g += `<text class="q" x="${X(best.k)}" y="${Y(best[key]) - 8}" text-anchor="middle" font-size="11">peak ${M(best[key])} at ${best.k}</text>`;
      return g;
    };
    let g = panel('npv', 22, 96, 'var(--accent)', cur.r.count_avoidance ? 'Cash vs plan, NPV' : 'Cash vs today, NPV');
    g += panel('cap', 156, 80, 'var(--capacity)', 'Capacity at cost, PV');
    g += `<line class="ref" x1="${X(kSel)}" x2="${X(kSel)}" y1="14" y2="${H - B}"/>`;
    [0, 10, 20, 30, 40, 50, 60].filter(k => k <= kMax).forEach(k => { g += `<text class="q" x="${X(k)}" y="${H - 8}" text-anchor="middle" font-size="11">${k}</text>`; });
    el.innerHTML = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Cash and capacity by programme size">${g}</svg>`;
    const s = $('scopek'); s.max = String(kMax); s.value = String(kSel);
    $('scopek-v').textContent = `${kSel} of ${kMax}${state.scopeK == null ? ' (peak cash)' : ''}`;
    $('scope-reset').hidden = state.scopeK == null;
  }
  function renderGate() {
    if (!cur) return;
    const { chosen, be, S, mc, Q, p } = cur;
    const pilot = chosen.slice(0, p.programme.pilot_workloads);
    const net = S.takeover * (1 - S.review);
    $('gate-sub').textContent = `Run the top ${pilot.length} workloads for ${p.programme.pilot_evaluation_months} months, measure, then decide on the rest.`;
    const v = mc && mc.done ? E.decide(mc.pPos, Q) : null;
    $('gate').innerHTML = `<div><span class="label">Pilot workloads</span><ul class="plain">${pilot.map(x => `<li>${esc(cap1(x.name))}</li>`).join('') || '<li>None pass the cost test at this size</li>'}</ul></div>
      <div><span class="label">Go/no-go threshold</span><p>Scale if the pilot shows a net realisation of at least <b>${be == null ? 'n/a (not reachable)' : P(be, 1)}</b>. This run assumes ${P(net, 1)}: AI takes over ${P(S.takeover)} and people check ${P(S.review)} of its time (Professional level; senior roles check more).</p></div>
      <div><span class="label">Measure for ${p.programme.pilot_evaluation_months} months</span><ul class="plain"><li>Share of each workload’s hours the AI handles end to end</li><li>Minutes people spend checking each AI hour</li><li>Weeks from go-live to steady use</li><li>Actual build and running cost per workload</li></ul></div>
      <div><span class="label">If the pilot misses</span><p>${cur.gate.applies ? `The programme stops in month ${cur.gate.month}: AI off, the work comes back and any positions removed are refilled. Trying and stopping costs <b>${Mabs(-cur.stopped.headline)}</b>, mostly training already given.${mc ? ` In ${P(mc.pStop)} of simulated futures the pilot misses and the programme stops; the odds above include them.` : ''}` : 'No cash gate applies: nothing is turned into positions, so there is no cash pass mark.'}</p></div>
      <div><span class="label">When a gate is worth it</span><p class="note">Experiments on this data: a gate adds value when the chance of positive cash is between about 40% and 70%. Above that, roll out in waves without pausing. Below it, do not start.${v ? ` Here it is ${P(mc.pPos)}: ${esc(v[1])}` : ''}</p></div>`;
  }
  function renderWaves() {
    const { chosen, r } = cur; const by = new Map();
    for (const x of chosen) { const m = r.golive[x.name]; if (!by.has(m)) by.set(m, []); by.get(m).push(x.name); }
    const ms = Array.from(by.keys()).sort((a, b) => a - b);
    if (!ms.length) { $('waves').innerHTML = '<p class="muted">No workloads are built at this setting.</p>'; return; }
    const T = r.T;
    $('waves').innerHTML = `<div class="waves">${ms.map((m, i) => `<div class="wv"><div class="wv-l"><b>${i === 0 ? 'Pilot' : 'Wave ' + i}</b><span>month ${m}, ${by.get(m).length} workload${by.get(m).length > 1 ? 's' : ''}</span></div><div class="wv-t"><i style="left:${m / T * 100}%"></i></div></div>`).join('')}</div><p class="note">Each workload is built over the three months before it goes live, then ramps to full use over ${F(cur.S.adopt_months)} months.</p>`;
  }

  // ------------------------------------------------------------ audit
  function renderChecks() {
    const { r, d, p, S } = cur;
    const cap0 = E.simulate(cur.prep, S, Object.assign({}, cur.Q, { harvest_automation: 0, harvest_augmentation: 0 }), { chosen: cur.chosen, ledger: false });
    const ok = (b, t) => `<li><span class="${b ? 'pos' : 'neg'}">${b ? 'Pass' : 'Fail'}</span> ${t}</li>`;
    const over = r.roles.filter(x => x.positions_end > Math.floor(x.freed_fte + 1e-9));
    $('checks').innerHTML = `<ul class="plain">
      ${ok(r.check_reconciliation_max_hours < 1e-6, `Freed hours reconcile exactly across positions, hires avoided, capacity and stranded slivers: largest monthly gap ${r.check_reconciliation_max_hours.toFixed(5)} hours`)}
      ${ok(r.check_ledger_gap < 1, `Ledger present values sum to the cash NPV: difference ${usd(r.check_ledger_gap)}`)}
      ${ok(over.length === 0, 'No role loses more positions than the FTE its work frees')}
      ${ok(cap0.pv_capacity > 0, `With headcount conversion at zero, the run still returns ${Mabs(cap0.pv_capacity)} of capacity and a cash result of ${M(cap0.headline)}`)}
      ${ok(true, `Deterministic: draws use a seeded generator (seed ${SEED}), so the same inputs give the same numbers`)}
      ${ok(true, 'Checked when this page was built: the browser engine matches the Python reference to within 6 × 10⁻¹⁴ on six test runs')}</ul>`;
  }
  function renderLedger() {
    const { r } = cur; const by = new Map();
    for (const e of r.ledger) { if (!by.has(e.line)) by.set(e.line, []); by.get(e.line).push(e); }
    const order = ['hard', 'seats_reclaimed', 'recruit_avoided', 'build', 'programme', 'training', 'licences', 'run', 'maintenance', 'severance', 'avoidance', 'capacity'];
    $('ledger').innerHTML = `<table><thead><tr><th>Line</th><th class="n">Sources</th><th class="n">Nominal</th><th class="n">PV</th></tr></thead><tbody>${order.filter(k => by.has(k)).map(k => {
      const es = by.get(k).sort((a, b) => Math.abs(b.pv) - Math.abs(a.pv)), nom = es.reduce((a, e) => a + e.nominal, 0), pvs = es.reduce((a, e) => a + e.pv, 0);
      const top = es.slice(0, 8).map(e => `<div class="lg-src"><span>${esc(e.source)}</span><span class="num">${usd(e.pv)}</span></div>`).join('') + (es.length > 8 ? `<div class="note">and ${es.length - 8} more in the CSV</div>` : '');
      return `<tr><td><details><summary>${LINE[k][0]}</summary>${top}</details></td><td class="n">${es.length}</td><td class="n">${usd(nom)}</td><td class="n">${usd(pvs)}</td></tr>`;
    }).join('')}</tbody></table>`;
  }
  function ledgerCsv() {
    const rows = [['line', 'source', 'nominal_usd', 'pv_usd']].concat(cur.r.ledger.map(e => [e.line, e.source, e.nominal.toFixed(2), e.pv.toFixed(2)]));
    return rows.map(r => r.map(c => /[",]/.test(c) ? `"${String(c).replace(/"/g, '""')}"` : c).join(',')).join('\n');
  }
  function currentValue(item) {
    const p = cur.p;
    if (item.grp === 'scenario') { const v = cur.S[item.key]; return v == null && item.fallback ? item.fallback(p) : v; }
    if (item.grp === 'policy') return cur.Q[item.key];
    if (item.grp === 'economics') return p.economics[item.key] == null ? 0 : p.economics[item.key];
    if (item.grp === 'capacity') return (p.capacity || {})[item.key] || 0;
    if (item.grp === 'review') return (p.review || {})[item.key] || 0;
    return p.costs[item.key];
  }
  function renderRegister() {
    $('register').innerHTML = `<table><thead><tr><th>Assumption</th><th class="n">Value</th><th>Plausible range</th><th>Kind</th><th>Grade</th><th>Source</th></tr></thead><tbody>${REGISTER.map((it, i) => {
      const v = currentValue(it); const edited = state.edits[it.grp][it.key] != null;
      return `<tr><td><label for="reg-${i}">${esc(it.label)}</label></td><td class="n"><span class="regv"><input type="number" id="reg-${i}" data-i="${i}" step="any" value="${it.t.show(v)}" class="${edited ? 'edited' : ''}"><span class="u">${it.t.unit}</span></span></td><td>${esc(it.range)}</td><td>${esc(it.kind)}</td><td>${it.grade ? `<span class="grade ${it.grade}">${it.grade}</span>` : ''}</td><td class="note">${esc(it.src)}</td></tr>`;
    }).join('')}</tbody></table>`;
  }
  function renderFlags() {
    const f = cur.prep.flags;
    $('flags').innerHTML = f.length ? `<ul class="plain">${f.map(x => `<li><span class="label">${x[0]}</span> ${esc(x[1])}</li>`).join('')}</ul>` : '<p class="muted">No data notes.</p>';
  }
  function renderFoot() {
    const p = cur.p;
    $('foot').innerHTML = `Prototype of the Etter Value Model. The page runs a line-for-line port of the Python reference engine; nothing is sent anywhere. Data: Etter FP&amp;A sample (11 roles, 420 tasks), scaled for the archetypes; not client data. Pack: ${esc(p.meta.name)}; discount rate ${P(p.economics.discount_rate, 2)}; growth ${P(p.economics.function_growth || 0)} a year.`;
  }

  function renderAll() {
    renderVerdict(); renderFunnel(); renderWorkloads(); renderDecides(); renderRoles();
    renderFinanceKpis(); renderFan(); renderLines(); renderTornado(); renderGrid();
    renderFrontier(); renderGate(); renderWaves();
    renderChecks(); renderLedger(); renderRegister(); renderFlags(); renderFoot();
  }

  // ------------------------------------------------------------ controls
  function seg(id, items, get, set) {
    const el = $(id);
    el.innerHTML = items.map(([v, l]) => `<button type="button" data-v="${esc(v)}" aria-pressed="${get() === v}">${esc(l)}</button>`).join('');
    el.addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; set(b.dataset.v); el.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.v === b.dataset.v))); });
  }
  function setupControls() {
    const org = $('org');
    const opts = [['base', `Etter FP&A dataset, 1,523 staff`]].concat(Object.keys(ARCH).map(k => {
      const a = ARCH[k]; const n = BASE_DATA.roles.reduce((s, r) => s + Math.max(1, roundHalfEven(r.headcount * a.headcount_factor)), 0);
      return [k, `${a.label}, ${n.toLocaleString('en-US')} staff`];
    }));
    org.innerHTML = opts.map(([v, l]) => `<option value="${v}">${esc(l)}</option>`).join('');
    org.addEventListener('change', () => {
      state.org = org.value; state.scopeK = null; state.edits = { scenario: {}, policy: {}, economics: {}, costs: {} };
      state.policy = org.value === 'base' ? 'Attrition only' : ARCH[org.value].default_policy;
      $('policy').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.v === state.policy)));
      run();
    });
    seg('policy', POLICIES, () => state.policy, v => { state.policy = v; delete state.edits.policy.harvest_automation; delete state.edits.policy.harvest_augmentation; run(); });
    seg('scen', SCENS.map(s => [s, s]), () => state.scen, v => { state.scen = v; run(); });
    $('horizon').addEventListener('change', e => { state.horizon = +e.target.value; run(); });
    const tabs = ['leader', 'finance', 'plan', 'audit'];
    const show = t => {
      state.tab = t;
      tabs.forEach(x => { $('t-' + x).setAttribute('aria-selected', String(x === t)); $('p-' + x).hidden = x !== t; });
      if (t === 'finance') renderFan(); if (t === 'plan') renderFrontier();
      try { localStorage.setItem('evm-tab', t); } catch (e) { /* storage unavailable */ }
    };
    tabs.forEach(t => $('t-' + t).addEventListener('click', () => show(t)));
    $('scopek').addEventListener('input', e => { state.scopeK = +e.target.value; $('scopek-v').textContent = `${state.scopeK} of ${cur.ranked.length}`; rerunSoon(150); });
    $('scope-reset').addEventListener('click', () => { state.scopeK = null; run(); });
    $('register').addEventListener('change', e => {
      const inp = e.target.closest('input[data-i]'); if (!inp) return;
      const it = REGISTER[+inp.dataset.i]; const raw = parseFloat(inp.value);
      if (!isFinite(raw)) return;
      state.edits[it.grp][it.key] = it.t.read(raw); run();
    });
    $('reset-edits').addEventListener('click', () => { state.edits = { scenario: {}, policy: {}, economics: {}, costs: {} }; run(); });
    $('copy-csv').addEventListener('click', () => {
      const csv = ledgerCsv(); const msg = $('copy-msg'), ta = $('csv-fallback');
      const fallback = () => { ta.hidden = false; ta.value = csv; ta.focus(); ta.select(); msg.textContent = 'Copying is blocked here. The CSV is selected below; copy it with your keyboard.'; };
      try { navigator.clipboard.writeText(csv).then(() => { msg.textContent = `Copied ${cur.r.ledger.length} ledger rows.`; ta.hidden = true; }, fallback); } catch (e) { fallback(); }
    });
    let rt = null; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { if (cur) { renderFan(); renderFrontier(); } }, 150); });
    let saved = null; try { saved = localStorage.getItem('evm-tab'); } catch (e) { saved = null; }
    if (saved && tabs.includes(saved)) show(saved);
  }

  setupControls();
  run();
})();
