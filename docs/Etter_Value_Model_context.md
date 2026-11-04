# Etter Value Model — complete context for answering questions

> **Purpose of this file.** Everything an agent needs to answer questions about the Draup / Etter AI value model accurately: the problem, the history of versions, exactly how the final model works (formulas and parameters), the reference results, the deliverables, the known weaknesses and the likely questions. Numbers are exact outputs of the reference engine unless marked otherwise. When in doubt, prefer the numbers in Section 6 and the formulas in Section 5.
>
> As of: 23 October 2026 (after the review meeting in which Chandan set the agent ceilings to **Directive 90%, Feedback Loop 80%**). Currency: USD. Default case throughout: **Etter FP&A dataset, Moderate scenario, Attrition only policy, cross-industry defaults, assistants on.**

---

## 1. One-paragraph summary

Draup's product **Etter** breaks every job into roles → workloads → tasks and labels each task with a category describing how AI relates to it. Etter stops at percentages ("30% of this role is automatable"). The **Etter Value Model** turns that into dollars a business leader and a CFO will both accept. It keeps only AI that is cheaper than the work it replaces (built or bought, whichever is cheaper), counts only the share AI really takes over after people check it, turns freed time into **whole positions only as people leave** (by default), and reports **cash, hires avoided and capacity separately, never added together**. On the Etter FP&A data (11 roles, 1,523 people, 420 tasks) the default answer is **+$9.38M cash over five years (NPV), 59 positions not refilled, capacity $47.7M (never added), payback month 33, 75% chance cash is positive, break-even net realisation 14.3% vs 28% assumed, 45 of 59 workloads (35 buy, 10 build) → verdict: GO (phased rollout).** With the previous ceilings (85% / 55%) it was +$5.80M, 47 positions, 65%, pilot first.

The model in three sentences (official wording):
1. Etter says which tasks AI can do; the model keeps only the workloads where an agent costs less than the work, and only the share AI really takes over once people have checked it.
2. That freed time becomes whole positions as people leave, hires the plan no longer needs, or capacity for other work.
3. Cash, avoided hires and capacity are reported separately, with the odds, a break-even and a ledger that traces every dollar to an input.

---

## 2. People, products and the brief

- **Draup**: workforce-intelligence company. **Etter**: Draup's product that decomposes roles into workloads → tasks (→ skills) and scores each task.
- **Chandan (Chandan Kumar)**: Draup architect who set the assignment and reviews the work. He is the audience for presentations.
- **The team**: student/analyst team (BITS) building the valuation layer Etter is missing. The user is a team member; a colleague produced an intermediate version (v5, see history).
- **Etter's six task categories** and what the model does with them:

| Etter category | Meaning | Model treatment | Ceiling (most AI could do) |
|---|---|---|---|
| Directive | rule-following work AI can take over | **Agent** (automation) | **90%** (was 85%) |
| Feedback Loop | iterative back-and-forth work | **Agent** (automation) | **80%** (was 55%) |
| Task Iteration | person does it, AI speeds them up | **Assistant** (augmentation) | 45% |
| Learning | person does it, AI speeds them up | **Assistant** | 25% |
| Validation | person checks/decides, AI prepares | **Assistant** | 50% |
| Negligibility | human only | none | 0% |

Ceilings: the two agent ceilings were set by Chandan in the review meeting on 23 Oct 2026 (Directive 90%, Feedback Loop 80%; previously 85% and 55%, the lower of Etter's two ceilings). Assistant ceilings remain the lower of Etter's two ceilings (potential and bucket ceiling).

### Chandan's brief (what "success" means)
A **generic** model turning Etter task-level data into a dollar estimate that passes three tests:
1. **A business leader understands it** (explainable in three sentences).
2. **Finance accepts it** (the hard one): no "savings" unless payroll shrinks; every figure traces to a task, salary or cost line; cash and capacity never share a total.
3. **Works for any company**: industries he named — **healthcare providers, insurance, technology**; sizes — **large and mid-cap**.

Non-negotiables / acceptance criteria: deterministic and reproducible; rebuildable in a spreadsheet in about an hour; auditable (ledger + graded sources); freed hours reconcile across destinations; cash and capacity never added; must still give a meaningful answer when the company will not reduce anyone ("reduce = 0"); must be able to say no (a failing case). Long-standing ask from August: model that **the remaining work is harder** (AI-able % does not map 1:1 to headcount). End goal: a **website** where a client uploads its Etter export plus headcount and salaries and gets the answer; the Excel and website run on the same engine.

---

## 3. The data (Etter FP&A export)

11 roles, 1,523 people, 420 tasks with hours per person per month. Total task hours per person across the 11 roles = 1,736/month. Base payroll = $153,899,959; loaded payroll ≈ $200.9M/yr.

| Role | Headcount | Base salary | Turnover band | Etter role score |
|---|---|---|---|---|
| FP&A Senior Coordinator | 44 | $30,572 | Para-professional | 32.9% |
| FP&A Assistant Analyst | 185 | $51,532 | Professional | 41.0% |
| FP&A Associate Analyst | 371 | $58,896 | Professional | 33.4% |
| FP&A Analyst | 310 | $79,661 | Professional | 30.6% |
| FP&A Senior Analyst | 253 | $104,211 | Professional | 24.0% |
| FP&A Associate Manager | 140 | $138,408 | Management | 32.2% |
| FP&A Manager | 89 | $163,670 | Management | 26.1% |
| FP&A Senior Manager | 58 | $198,825 | Management | 13.0% |
| FP&A Director | 46 | $304,094 | Executive | 4.4% |
| FP&A Senior Director (Band B) | 17 | $381,174 | Executive | 9.7% |
| FP&A Senior Director (Band A) | 10 | $416,678 | Executive | 12.0% |

Data facts worth knowing:
- Senior Analyst tasks sum to **136** h/month, not 160; the model takes shares relative to the recorded 136 (so its hourly rate is higher, $83.36).
- 59 distinct workloads contain agent (Directive/Feedback Loop) tasks: **54 single-role, 5 cross-role** (bimodal).
- **Tasks sheet vs Workloads sheet disagree** on the category split of the same hours (e.g. Analysts' Financial Analysis & Reporting: Directive tasks = 30% of hours on the Tasks sheet vs 6.8% on the Workloads sheet). The model uses the **Tasks sheet** (more detail; every number traces to a named task; Etter's notes say to build bottom-up on task hours). Using the Workloads split pushed the old model's break-even from ~16% to ~34%. **This is still an open question for Etter and the one structural issue that could flip the verdict.**
- Etter role scores differ from the task build-up by >10 points for several roles (e.g. Directors); used only as a second opinion/flag, never mixed into the numbers.

FTE by category across the function (people's worth): Directive 310.5, Feedback Loop 253.2, Task Iteration 300.5, Learning 225.9, Validation 193.9, Negligibility 239.1. **Agent-category total = 563.7.**

---

## 4. History: how we got here

### 4a. Phase 1 — before real data (v1–v9, constructed F&A data)
Built on a stand-in AP clerk scored at 68% automatable (above Etter's own sample max of 56.8%; Etter's 17-role sample averaged 17.2%). Versions grew sophisticated:
- v1 naive % × headcount × salary with a flat 0.70 consolidation factor and FLOOR rounding (staircase broke sensitivity).
- v2 task-level ledger, realisation chain (score × η × α × (1−v)), exception tail h(x)=NORMSDIST(NORMSINV(x)−σ), square-root staffing, attrition gate, five destinations (reinstatement / reduce / redeploy / output / slack) with conservation check, fat-tailed build risk, timing option → NPV −$168,645.
- v4 parallel role-level build, much better sourced (23 sources) → +$142,948; the sign flip traced to one unsourced automation score.
- v5 merge + ablation (killed level-specific productive hours, which cancelled algebraically); added rails (APQC 20% headcount reduction, Ardent $9.40/invoice, Deloitte 22-month payback). 64% of answer swing came from policy or grade-D assumptions.
- v6 process objects, three data tiers, rails as blocking checks; double-counting and self-generated "rail" problems.
- v7 simplification with a derived baseline; fatal: the client's labour cost cancelled out algebraically.
- v8 deleted the baseline construct (released = L × a × h(α)); discovered "difficulty effect beats density effect".
- v9 five fixes; α was double-discounting; verdict +$79k, payback month 23.
Loaded-cost convention then: 1.47 × salary on 1,800 available hours.
Key lessons carried forward: cash ≠ capacity; attrition gate; every hour to exactly one destination; A–D grading; rank sensitivity before researching; separate "money moved" from "verdict flipped"; say no when the numbers say no; the attack pass finds the real bugs.

### 4b. Phase 2 — real Etter FP&A data
1. **FP&A workbook v1 — the version last presented to Chandan.** Deliberately simple: one **delivery rate** (Conservative 15% / Base 30% / Aggressive 60%) absorbed every leak; build gate at $85,000 per workload (47 of 60 built at 30%); AI help = 12.3% × 60% seat share; capacity = every freed hour × 65% useful share; reduce share 25/50/65% by scenario; 9-month linear adoption; start-date option (now/6/12/18/24 months); break-even sweep over delivery rate 0–100%. **Result (Base): break-even ~16%, assumes 30%, cash +$9.7M (NPV $9,653,145), 51 positions (3.3%), capacity $39.0M, payback month 26, "build now".** Conservative −$6.3M (break-even 42%), Aggressive +$46.9M.
   - Meeting corrections (MoM): 2-year window cash −$1.2M, 2.5y +$0.8M, 3y +$2.7M, 5y +$9.7M; "target reached in 9 months" is adoption (MIT NANDA), not attrition; licence price change already in model; running cost $2.00 ÷ 0.575 h = $3.48.
   - **Chandan's action items:** add detail to weak cost inputs (build $85k; running $3.48/h; implementation $75k + $765 from a single Forrester study); add turnover costs (avoided cost per hire when not backfilling; severance for layoffs); make running cost intuitive (per task/action); email CFO the model, deck and flowcharts. Parked: existing company technology layer; layoff option (designed, not built).
2. **v2 re-sourcing (assistant-built).** Re-sourced costs; break-even 16.41% → 16.22%. An independent attack pass then found real errors: on-cost wrongly changed to 1.29 (used BLS ECEC Table 4 all-private incl. part-timers; v1's 1.3055 from **Table 5 full-time private industry** was correct); capacity overlapped cash by ~$14.2M (no reduce term); the delivery-rate decomposition double-discounted (coverage anchored on a touchless rate, then × (1 − comeback)); the $3.48 "top-down" method was circular (0.575 back-solved); Tasks-vs-Workloads missing from open items; claims written one notch stronger than evidence.
3. **Colleague's v5.** Good framing (Basis comparison sheet; reduce share held as a policy choice with odds per setting; decision surface; cost build-up sheet) but carried forward the on-cost, circular running cost and double-discounting, presented a "difficulty curve" the workbook didn't have, and quoted 99.8% odds conditional on the unresolved basis question.
4. **Rebuild from scratch → Etter Value Model v0** (Python engine `evm.py`, browser port `evm.js`, prototype website, strategy doc). Split the delivery rate into a choice (cost test) and two measurable unknowns (takeover, review); added review time, maintenance, phased go-live, complexity drag; capacity = leftover hours only; Monte Carlo + decision layer. **Result: +$3,096,839.06, 47 positions, payback month 44, ~51% chance positive, break-even 23.0%.** Same engine on v1's settings gives ≈ $9.2M (so the models agree; the drop is the added frictions).
5. **Final model (current).** Added **build-or-buy per workload** (+$2.04M) and **sizing the programme to peak cash** (+$0.65M), seven industry packs, six data situations, pooling option, decision layer (verdict, pilot gate, backfill rule). **Result: +$5.80M, 65% positive, break-even 17.1%, pilot first.** Presented in the deck "How the final model works" (14 slides, dated 20 Oct 2026, for Chandan).

6. **Ceiling update (23 Oct 2026, review meeting).** Chandan set Directive to 90% and Feedback Loop to 80%. Every result, the peak-cash sizes, the odds and the break-even were recomputed; the engine package, website, Excel and documents were all updated. **Result: +$9.38M, 59 positions, 45 workloads (35 buy, 10 build), 75% positive, break-even 14.3%, verdict GO.**

Bridge to quote (85% / 55% ceilings): **$9.7M (last time) ≈ $9.2M (new engine, old settings) → $3.1M (add review, maintenance, waves, drag) → +$2.04M build-or-buy → +$0.65M stop at peak cash → $5.8M.** Chance of positive cash 51% → 65%.
With the new ceilings (90% / 80%): build only, all cost-effective workloads (51) $7.20M → build-or-buy on all 59 $9.19M → stop at peak cash (45) **$9.38M**. The ceiling change alone adds about **+$3.6M** to the final answer and moves the verdict from pilot first to go.

---

## 5. How the final model works (exact mechanics)

Six steps plus two layers. Monthly simulation, months 0–60 (month 0 = today). Units: hours per person per month unless stated.

### Step 1 — Work and the price of an hour
- Loaded cost per person C = salary × **on-cost 1.3055** (BLS ECEC Table 5, full-time private industry: wages 68.5%, paid leave 8.1% of compensation; 100/(68.5+8.1)). Paid leave is added back because the hours are working hours.
- Task hours per role H = sum of the role's task hours (160 standard; Senior Analyst 136). Hourly rate = C / (12 × H). (TDABC capacity-cost rate.)
- Example: Analyst $79,661 × 1.3055 = $103,997/yr ÷ 1,920 = **$54.17/h**. Associate Analyst $76,889/yr, $40.05/h.

### Step 2 — Potential
- **Agent (AI-able) hours** per person, per task = task hours × category ceiling (Directive 90%, Feedback Loop 80%). Grouped by workload (normalised name: lower-case, " & " → " and ").
- **Assistant hours saved** per person, per task (Task Iteration / Learning / Validation) = task hours × min(category ceiling, band saving). Band saving: Para-professional 20%, Professional 12%, Management 6%, Executive 3% (Brynjolfsson, Li & Raymond, QJE 2025). Then × active use (70%) × aug multiplier (1.0) when seats are live.
- Example: Analysts' "Extract and format financial data" 8.64 h × 310 × 90% = **2,411 AI-able hours/month (28,927/yr)**. Associate Analyst per person: Directive 36.0 h × 90% + Feedback Loop 27.5 h × 80% → 54.3 AI-able h (34% of time); assistant hours 9.6.

### Step 3 — Scope (which workloads, build or buy, how many)
For each workload w (59 with agent tasks):
- AI-able hours/month (all roles) A_w = Σ roles headcount × AI-able h/person in w. Value/month V_w = Σ A × role hourly rate.
- Net realisation n = takeover × (1 − review) = 0.40 × 0.70 = **0.28**. Freed value/month = V_w × n.
- **Tier**: enterprise if the workload spans ≥2 roles or has ≥3 agent tasks, else workflow.
- **Build option**: up front $55,000 (workflow) / $130,000 (enterprise) × cost_mult; running = A_w × takeover × $3.48 × cost_mult × run_mult per month; maintenance = 18%/yr of up front.
- **Buy option**: up front $15,000 / $35,000 × cost_mult; vendor fees = A_w × takeover × $6.00 × cost_mult × run_mult per month; no separate maintenance.
- Annuity factor ann = Σ_{m=1..60} S((m − 3)/adopt) × (1+r)^(−m/12) = **42.549** (months of full value in five years, after 3-month build lead, 12-month S-curve, 6.96% discounting). S(x) = smoothstep: 0 below 0, 1 above 1, x²(3−2x) between.
- NPV at cost (each option) = (freed value − running − maintenance) × ann − up front. **Keep the higher-NPV option** (buy only if strictly better). Workload **passes** if best NPV > 0. Running cost is not declined inside this test.
- Rank passing workloads by **return per $ up front** = (freed value − running − maintenance) × ann / up front.
- **Sizing** (`size_to_peak`): add workloads in rank order; the programme stops where **five-year cash (headline) NPV peaks** (full re-simulation at each size). Default: **45 of 59** (35 buy, 10 build), $1.29M up front. Peak sizes by case: Conservative/Attrition 35, Moderate/Attrition 45, Aggressive/Attrition 41; Conservative/Active 32, Moderate/Active 37, Aggressive/Active 58; Capacity only builds every passing workload (0 = all; 53/59/59).
- Why cash peaks before all passing workloads are in: the cost test values freed time at full cost (policy-independent "is the AI cheaper than the work?"), but cash only counts time that becomes whole positions; late, small workloads free fractions of people that never round up, and go live later.
- Examples: "Financial analysis and reporting" — 5 roles, enterprise, 19,722 AI-able h/month, **$1,016,529 of work/month**, build NPV $10.73M vs buy $10.06M → build; ranked 2nd; pilot; live month 3. "Cost review planning and support" — $3,850/month, buy, NPV +$11,953, passes but ranks last (59th), not in programme.
- **Schedule**: rank 1–3 = pilot, go-live month 3 (build lead). Others: go-live = 3 + 6 (evaluation) + 3 + 3 × floor((rank − 4)/10) → months **12, 15, 18, 21, 24** (waves of 10, 10, 10, 10, 2 at the default). Build/setup cost is spread evenly over the 3 months before go-live.

### Step 4 — Realised
For each role r, month m:
- Agent hours freed (raw) = N_r × n × Σ_w∈programme AI-able h/person_rw × S((m − golive_w)/adopt). adopt = 12 months (Moderate).
- AI hours worked (for running cost) = same with **takeover** instead of n (running cost is paid on all AI hours, reviewed or not). Running $ = AI hours × rate_w × 0.87^(m/12) (13%/yr price decline, applied to build and buy).
- Assistant seats = N_r × active use × S((m − 2)/6) if the role has assistant hours and assistants are on. Assistant hours freed (raw) = seats × assistant h/person × aug_mult.
- **Complexity drag**: drag factor = 1 − κ × (raw agent + raw assistant hours)/(N_r × H_r), κ = 0.30. Both freed streams × drag factor. (Analysts free ~14% of their time → keep ~96%.)
- Example chain (Analyst task): 28,927 AI-able h/yr × 40% = 11,571 AI hours → × 70% = **8,099 h freed** → Analysts free ~14% of their time, drag keeps 96% → **7,769 h ≈ 4.0 people's worth**.
- Associate Analyst per person: 54.3 → 21.7 (takeover) → 15.2 (after review) → 14.6 (after drag) h/month; × 371 ÷ 160 = **33.8 people's worth**.

### Step 5 — Routing (every freed hour goes to exactly one place)
- **Policy** (a choice): harvest share of agent time / of assistant time / mechanism.

| Policy | Agent time → positions | Assistant time → positions | Mechanism |
|---|---|---|---|
| Capacity only | 0% | 0% | nobody goes |
| **Attrition only (default)** | **50%** | **0%** | positions go only as people leave |
| Active reduction | 75% | 25% | separation after 2 months' notice; severance 12 weeks of base salary |

- Steady state per role: agent FTE = N × (AI-able h in programme) × n / H; assistant FTE = N × assistant h × active × aug_mult / H; both × (1 − κ × (sum)/N). Harvest = h_auto × agent FTE + h_aug × assistant FTE. **Target = floor(harvest)** (whole positions, per role).
- Each month: allowed = floor(target × current harvestable FTE / steady-state harvest). Leavers so far = floor(N × (1 − (1 − λ)^(m/12))), λ = band turnover × industry multiplier × scenario turnover multiplier. Band turnover (Mercer 2025): Para-professional 12.5%, Professional 9.1%, Management 6.3%, Executive 5.2%.
- Positions P_m = min(max(attrition ? min(allowed, leavers) : (m > notice ? allowed : 0), P_{m−1}), floor(freed FTE)). Positions never come back and never exceed freed time.
- **Hires avoided** (only if industry job growth g > 0 and absorb = yes): planned hires = floor(N × ((1+g)^(m/12) − 1)); avoided = max(0, min(floor(freed FTE − P), planned)).
- **Capacity hours** = freed hours − P × H − avoided × H. Reconciliation (freed = positions + avoided + capacity) is checked every month; gap = 0.
- Rounding consequence: a role needs roughly **20–30 people** before agents free a whole position. Senior Coordinators free ~1.0 FTE from agents → 0.5 → **0**. Mid-caps (~6 people per role) lose almost everything to rounding. **Pooling** across a level (sum fractions before rounding) is an option in the reference engine, off by default.
- Backfill rule per role: "Leave P of the next L leavers unreplaced" (L = round(N × (1 − (1 − λ)^5))). Associate Analyst: **leave 16 of the next 141**; Analyst: **14 of the next 118**; Senior Coordinator: refill as usual.

### Step 6 — Money (three kinds, never added)
Monthly lines, discounted at (1 + r)^(−m/12), r = 6.96% (Damodaran cross-industry, Jan 2026), summed over months 0–60.
- **Costs**: build/setup (up front spread over 3 lead months); programme = $75,000 × cost_mult (month 0) + $623 × cost_mult per person in every touched role (month 0); training = N × ($846 + 16.7 h × hourly rate) once, at max(1, first-touched month) — **not** scaled by cost_mult; assistant licences = seats × $360/yr × cost_mult; running (above); maintenance = 18%/yr of build up front for custom agents live; severance (active reduction only) = new positions × 12 weeks × salary/52.
- **Cash savings**: salaries = P × C/12 per month; seats reclaimed = P × $468/yr; recruiting avoided (attrition only) = new positions × **$4,700** (SHRM cost per hire).
- **Cash vs today NPV** = PV(savings) − PV(costs). **Hires avoided vs plan** = PV(avoided × C/12 + new avoided × $4,700), reported separately. **Capacity at cost** = PV(capacity hours × hourly rate), never added to cash.
- Headline = plan NPV (cash + avoided) if the industry is growing, else cash NPV.
- **Capacity hurdle** = −headline / capacity PV when the headline is negative (share of capacity that must become real value to break even).
- Payback = first month after the last month with negative cumulative cash. Peak funding = −min cumulative cash.

### Uncertainty layer
- Plan (which workloads, when) is fixed at the scenario's values; reality drawn **1,000 times**, seed **20261019** (mulberry32 PRNG, identical in Python and JS).
- Draw distributions (P10–P90; median = scenario value): takeover logit-normal 0.20–0.62; review logit-normal 0.15–0.45; adopt months lognormal 6–24; active use logit-normal 0.50–0.85; aug_mult lognormal 0.4–1.6; cost_mult lognormal 0.85–1.6; run_mult lognormal 0.43–2.9 (≈ $1.50–$10/h custom); drag logit-normal 0.10–0.55; turnover_mult lognormal 0.75–1.3.
- Correlation: a shared "execution quality" factor (ρ = 0.5) loads +takeover, −review, −adopt months, +active use (good programmes are good at everything at once).
- Break-even: bisection on net realisation (takeover varied, review fixed) for headline NPV = 0, plan fixed.
- Sensitivity: one input at a time across P10–P90 (+ harvest share ±25 points), plan fixed.

### Decision layer
- **Go** if P(cash > 0) ≥ 70%; **Pilot first** if 40–70%; **Stop** below 40%; if harvest = 0 → **capacity case** ("fund it only if leadership commits to using the released time"). Thresholds come from an experiment on the value of a pilot gate (gated mean NPV ≈ 0 near 36% success; the gate stops paying near 70%; a pilot costs ~9 months of delay).
- Pilot design: top 3 workloads for 6 months; measure takeover, checking time per AI hour, weeks to steady use, real costs; scale if net realisation ≥ the break-even (**14.3%** at the default). At 75% the default verdict is **go**, so this becomes the phased rollout's first wave and the break-even is the number to watch.

### Universality
- Three layers: base defaults → industry pack → client's own numbers. Formulas never change. **Company size is not a setting** — it enters through headcount (rounding does the rest).

| Industry pack | Discount rate | Turnover vs average | Job growth/yr | Default policy | Regulated |
|---|---|---|---|---|---|
| Healthcare providers | 6.19% | ×0.91 | 0.9% | Capacity only | Yes, CMS |
| Insurance | 6.34% | ×0.59 | 0.2% | Attrition only | Yes, NAIC |
| Technology and software | 9.34% | ×0.59 | 0.5% | Attrition only | No |
| Banking | 4.98% | ×0.59 | 0.2% | Attrition only | No |
| Retail | 7.27% | ×1.18 | 0.0% | Attrition only | No |
| Manufacturing | 7.70% | ×0.64 | 0.1% | Attrition only | No |
| Cross-industry default | 6.96% | ×1.00 | 0.0% | Attrition only | No |

Sources: Damodaran WACC by industry (Jan 2026); BLS JOLTS 2025 quits vs all private (2.2%/month); BLS Employment Projections 2025–35; CMS FAQ Feb 2024; NAIC model bulletin Dec 2023.
- Six data situations (reference engine; flagged on an Audit page): task hours missing (fill from workload hours, else split 160 evenly); only role scores (role-score mode: Etter automation/augmentation scores × ceilings); **regulated decisions** (automate tasks become Validation: AI prepares, a person decides); **queue work** (square-root staffing at 85% occupancy keeps a service buffer, so fewer positions free up); small teams (whole positions per role; pooling optional); levels not bands (level names mapped to turnover bands).

---

## 6. Reference results (final model, ceilings 90% / 80%)

### 6a. Default case — Moderate, Attrition only, cross-industry
| Measure | Value |
|---|---|
| Cash vs today, 5-yr NPV | **$9,376,169.02** |
| Hires avoided vs plan | $0 |
| Capacity at cost, PV | **$47,694,309** |
| Positions not refilled (month 60) | **59** (3.9% of 1,523), all reached by ~month 36 (15 by month 12, 45 by month 24) |
| Payback month | **33** |
| Peak funding needed | $4.41M |
| IRR | ~55% a year |
| Workloads passing / in programme | 59 / **45** (35 buy, 10 build) |
| Up-front build + setup | $1.285M |
| Net realisation assumed | 28% |
| Break-even net realisation | **14.34%** |
| Chance cash positive (1,000 draws) | **75.1%** |
| P10 / P50 / P90 cash NPV | −$4.20M / +$5.11M / +$21.16M |
| Capacity P10 / P90 | $28.3M / $76.3M |
| Verdict | **GO** (phased rollout, no pause needed) |
| Freed FTE at steady state | 176.4 (124.1 agents + 52.3 assistants); 59 positions, ~117 capacity |

**Funnel (people's worth, agents, month 60):** hours in agent categories 563.7 → AI-able (ceilings) 482.0 → in the 45 workloads 460.9 → AI takes over (×40%) 184.4 → after review (×70%) 129.0 → after complexity drag 124.1 → **positions 59**.

**Ledger (PV, 5 years):**
| Savings | | Costs | |
|---|---|---|---|
| Salaries no longer paid | $18.89M | Training ($846 + 16.7 h, all 1,523) | **$3.05M** (largest) |
| Recruiting avoided ($4,700 each) | $0.25M | Running ($3.48 / $6 per AI h) | $2.67M |
| Seats reclaimed ($468/yr) | $0.08M | Assistant licences ($360/seat) | $1.48M |
| | | Build / setup | $1.20M |
| | | Programme ($75k + $623/person) | $1.02M |
| | | Custom-agent maintenance | $0.41M |
| **Total** | **$19.22M** | **Total** | **$9.84M** |

**Cash by year (nominal):** day 0 −$1.09M; year 1 −$3.32M; year 2 +$1.61M; year 3 +$4.56M; year 4 +$5.51M; year 5 +$5.62M.

**Positions by role (target = month-60):** Senior Coordinator 0; Assistant Analyst 9; Associate Analyst 16; Analyst 14; Senior Analyst 11; Associate Manager 4; Manager 2; Senior Manager 2; Director 1; Senior Director B 0; Senior Director A 0 (= 59). Leavers over 5 years: 21, 70, 141, 118, 96, 39, 25, 16, 11, 4, 2.

**Capacity-only hurdle:** builds all 59; cash −$10.14M, capacity $67.3M → **≈15%** of capacity must become real value to break even.

### 6b. Scenarios × policies (each sized to its own peak cash; capacity only builds all passing)
| Scenario | Policy | Workloads (buy) | Cash NPV | P(positive) | P10 | P90 | Positions | Capacity | Payback | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| Conservative | Capacity only | 53 (47) | −$9.72M | 0% | −$14.86M | −$7.50M | 0 | $31.6M | — | capacity |
| Conservative | Attrition only | 35 (29) | −$1.00M | 30% | −$8.01M | +$7.20M | 30 | $22.6M | 60 | stop |
| Conservative | Active reduction | 32 (26) | +$4.65M | 60% | −$5.06M | +$18.36M | 50 | $15.7M | 41 | pilot |
| Moderate | Capacity only | 59 (49) | −$10.14M | 0% | −$15.82M | −$7.62M | 0 | $67.3M | — | capacity |
| **Moderate** | **Attrition only** | **45 (35)** | **+$9.38M** | **75%** | **−$4.20M** | **+$21.16M** | **59** | **$47.7M** | **33** | **go** |
| Moderate | Active reduction | 37 (27) | +$22.65M | 97% | +$4.15M | +$42.27M | 100 | $31.6M | 25 | go |
| Aggressive | Capacity only | 59 (45) | −$11.41M | 0% | −$18.69M | −$8.22M | 0 | $114.8M | — | capacity |
| Aggressive | Attrition only | 41 (28) | +$24.98M | 97% | +$5.90M | +$36.92M | 98 | $77.2M | 21 | go |
| Aggressive | Active reduction | 58 (44) | +$49.09M | ~100% | +$22.77M | +$70.98M | 175 | $51.3M | 18 | go |

### 6c. Sensitivity (default case, one at a time, plan fixed; cash NPV at low → high)
| Input | Range | Cash NPV |
|---|---|---|
| Harvest share of agent time (policy) | 25% → 75% | −$1.43M → +$20.50M |
| AI takeover | 20% → 62% | −$0.10M → +$19.07M |
| Human review | 15% → 45% | +$11.99M → +$4.62M |
| Months to full use | 6 → 24 | +$11.02M → +$6.26M |
| Running-cost multiplier ($1.50 → $10/h custom) | 0.43 → 2.9 | +$10.90M → +$4.30M |
| Build/programme cost multiplier | 0.85 → 1.6 | +$10.39M → +$5.30M |
| Complexity drag | 0.10 → 0.55 | +$9.57M → +$8.35M |
| Assistant active use | 50% → 85% | +$9.80M → +$8.76M |
| Assistant saving multiplier | 0.4 → 1.6 | +$9.59M → +$8.87M (only through the drag factor) |
| Turnover multiplier | 0.75 → 1.3 | no cash effect (attrition not binding at this scale) |

Reading: the top lever is a **leadership choice**; the next two are **measurable in a pilot**; no cost input on its own takes cash below zero.

### 6d. Other reference points
- Previous ceilings (85% / 55%), same final engine: $5,800,227.08, 47 positions, 36 workloads (27 buy, 9 build), 65.1% positive, P10 −$4.68M, P90 +$15.89M, break-even 17.1%, payback 36, capacity $43.9M, pilot first. This is what the 20 Oct deck shows.
- Earlier engine v0 (build only, all cost-effective workloads, ceilings 85% / 55%): $3,096,839.06, 47 positions, payback 44 (reproduced as a test).
- New ceilings, build only, all cost-effective (51 workloads): $7.20M; build-or-buy on all 59: $9.19M; sized to 45: $9.38M.
- Without assistants (default, new ceilings): $11.21M → under attrition-only, assistants cost ≈ $1.83M of cash and are justified only by capacity.
- Healthcare pack (Moderate, Attrition only, FP&A data): 45 workloads, cash $9.71M, hires avoided PV $14.94M (65 hires), against-the-plan NPV $24.65M, 59 positions.
- Scenario library in the 20 Oct deck (ceilings 85% / 55%, archetypes; not recomputed with the new ceilings): any 62-person organisation → stop; multi-state health system (402) attrition +$2.2M* 88% go; large insurer (402) attrition −$0.3M 27% stop, active +$2.3M 74% go; large software (402) attrition +$0.5M* 45% pilot. Insight that still holds: people per role, not company size, decides; policy moves the answer most; industry acts through growth and turnover.

---

## 7. Parameters with sources and grades
Grades: **A** official statistic or list price · **B** industry benchmark · **C** indirect evidence or estimate · **D** thin evidence, replace first · **Policy** = the company's choice. The pilot measures the C and D rows.

| Parameter | Value (Moderate) | Range / alternatives | Grade | Source / basis |
|---|---|---|---|---|
| Category ceilings | **90/80**/45/25/50/0% | fixed | Chandan / Etter | Agent ceilings set by Chandan 23 Oct 2026 (were 85/55); assistant ceilings = Etter's lower of two |
| AI takeover | 40% (25/40/60) | 20–62% | C | indirect: finance AI impact low–moderate (Gartner May 2026); AP ~33% touchless avg (Ardent 2025) |
| Human review | 30% (40/30/20) | 15–45% | C | estimate; pilot measures checking time |
| Months to full use | 12 (18/12/6) | 6–24 | C | MIT NANDA 2025 |
| Assistant active use | 70% (55/70/85) | 50–85% | C | published weekly-active seat use |
| Assistant saving by band | 20/12/6/3% | ×0.4–1.6 | B | Brynjolfsson, Li & Raymond QJE 2025 |
| Cost multiplier | 1.00 (1.25/1.00/0.90) | 0.85–1.6 | C | overrun skew |
| Complexity drag κ | 0.30 | 0.10–0.55 | D | stand-in for exception tail |
| Harvest share agent / assistant | 50% / 0% | 0–100% | Policy | — |
| Turnover by band | 12.5/9.1/6.3/5.2% | ×0.75–1.3 | B | Mercer 2025 |
| On-cost | 1.3055 | — | A | BLS ECEC Table 5, full-time private industry |
| Hours | 160/month (1,920/yr) | — | A | Etter convention |
| Discount rate | 6.96% | 4.98–9.34% by industry | A | Damodaran Jan 2026 |
| Build workflow / enterprise | $55k / $130k | ×0.85–1.6 | C | 2026 agent-dev benchmarks ($20–60k / $75–150k) |
| Custom running cost | $3.48 per AI hour | $1.50–$10 | D | weakest input; pilot measures |
| Running-cost decline | 13%/yr | — | C | estimate |
| Maintenance (custom) | 18%/yr of build | — | C | 15–20% software convention |
| Buy workflow / enterprise | $15k / $35k | $5k–$150k | D | vendor list prices |
| Vendor price | $6 per AI hour | $2.40–$12 | C | vendor usage/outcome pricing |
| Build lead | 3 months | — | C | estimate |
| Programme fixed | $75,000 | — | C | Forrester TEI M365 Copilot (full study) |
| Deployment | $623 per affected person | — | C | Forrester TEI setup cost per seat |
| Training | $846 + 16.7 h per person | — | B | ATD 2026 |
| Assistant licence | $360/seat/yr | — | A | Microsoft list price (unchanged since 2023) |
| Seat cost per position | $468/yr | — | C | estimate |
| Cost per hire | $4,700 | — | B | SHRM |
| Pilot / evaluation / waves | 3 workloads / 6 months / 10 every 3 months | — | design | — |
| Assistant rollout | from month 2 over 6 months | — | design | — |
| Horizon | 60 months | — | design | — |
| Notice / severance (active) | 2 months / 12 weeks | — | Policy | outplacement not included |
| Verdict thresholds | go ≥70%, pilot ≥40% | — | experiment | pilot-gate value experiment |
| Uncertainty correlation | 0.5 | — | design | — |

---

## 8. What changed since the last presentation (v1 workbook → final)

| Topic | Last time (v1 workbook) | Now (final) |
|---|---|---|
| Headline | +$9.7M, break-even ~16%, assumes 30% | **+$9.38M, break-even 14.3%, assumes 28%, 75% chance positive, GO** (+$5.8M, 65%, pilot at the 20 Oct ceilings) |
| What AI delivers | one delivery rate 15/30/60% | cost test (choice) + takeover 40% × (1 − review 30%) |
| Getting the AI | build only, $85k flat; 47 of 60 built | build $55k/$130k **or buy** $15k/$35k; **45 of 59** sized to peak cash (35 buy, 10 build) |
| Implementation | $75k + $765 per person | $75k + $623 per affected person + training $846 + 16.7 h |
| Running cost | $3.48/h | $3.48/h custom (grade D, range $1.50–$10) + $6/h vendor |
| Turnover costs | missing | $4,700 recruiting saved per position not refilled; severance under active reduction |
| Layoff option | parked | **built** ("Active reduction") |
| Capacity | 65% of every freed hour, overlapping cash (~$14M) | leftover hours only, at full cost, plus a stated hurdle; never overlaps |
| Assistants | 12.3% × 60% seats | 20/12/6/3% by band × 70% active, capped by ceiling |
| Frictions | none | human review, maintenance, pilot + waves, S-curve, complexity drag |
| Adoption | 9 months, linear | 12 months, S-curve |
| Timing | start now vs 6–24 months | dropped; pilot gate and waves instead |
| Certainty | break-even sweep only | 1,000 correlated runs, P10/P90, sensitivity, break-even |
| Recommendation | build now / do not build | go / pilot / stop, pilot pass mark, backfill rule per role |
| Scope | FP&A only | 7 industry packs, size via headcount, 6 data situations |
| Positions / payback | 51 / month 26 | 59 / month 33 |
| Capacity | $39.0M | $47.7M |
| Conservative / Aggressive | −$6.3M / +$46.9M | −$1.0M / +$25.0M |
| Agent ceilings | 85% / 55% | **90% / 80%** (set by Chandan, 23 Oct) |
| Unchanged | | on-cost 1.31, 160 h/month, Tasks sheet, 5-year window, whole positions, attrition gate, cash ≠ capacity |

Chandan's action items → status: build cost detailed (tiers + buy) ✔; implementation decomposed ✔; running cost still D, per-task framing not implemented (open); cost per hire ✔; severance/layoff option ✔; CFO email (team task); existing company technology layer (parked, not built).

---

## 9. Relationship to the earlier constructed-data models (v1–v9)
- **Kept in simpler form**: realisation chain → takeover × (1 − review) (review = old v; takeover ≈ α × η combined); difficulty/exception tail → complexity drag (D); attrition gate (same formula, Mercer rates); five destinations → three (positions / hires avoided / capacity) with monthly reconciliation; cost-side-only overrun risk → skewed cost multiplier; P10/P50/P90 and chance of loss; industries differ via turnover/growth; square-root staffing kept only for queue work; "volume decides whether to build" → cost test on workload value (hours × headcount × rate).
- **Dropped deliberately**: exception-tail formula NORMSDIST(NORMSINV(x)−σ) (needs σ and volumes; Etter gives neither); per-transaction unit cost and the rails (APQC 20%, Ardent $9.40, Deloitte 22 months); reinstatement 15% and slack (review time and the capacity hurdle replace them); option to wait and materiality band (pilot gate and waves replace them); process objects and data tiers.
- **Different conventions**: on-cost 1.31 on 1,920 h (vs 1.47 on 1,800 h); real Etter data (vs stand-in scores); results in $ millions for a 1,523-person function (vs hundreds of thousands for one AP team).
- If asked "where are the rails?": not in the final model. Context: 47 positions = 3.1% vs APQC's 20% multi-year ceiling; payback month 36 vs Deloitte's 22 — both consistent with the model being conservative.

---

## 10. Known weaknesses (state them honestly)
1. **"The remaining work is harder"** (Chandan's August ask) is a single drag parameter (0.30, grade D); underneath, freed hours ≈ AI-able × 28%, close to linear. Proper difficulty curve needs task volumes or handling-time spread from Etter.
2. **One takeover/review for all tasks**: "upload data" and "executive presentation", Coordinator and Director work all get 40%/30%. Cheapest real upgrade: vary by Etter category and role level (no new data needed). The old chain varied by work type (transactional ~0.48 → expert judgement ~0.06).
3. **Part of the improvement since v0 rests on grade-D vendor prices** (build-or-buy adds about $2M).
4. **Odds are conditional on our ranges**; quote "about three in four", not 75.1%. They also assume the Tasks-sheet basis and the 90% / 80% ceilings.
4b. **The new agent ceilings are a direction from the review, not yet evidenced**; they add about $3.6M and move the verdict from pilot to go. Worth validating against Etter's own task evidence or the pilot.
5. **Tasks vs Workloads sheet** disagreement unresolved (only structural item that can flip the verdict).
6. **Running cost $3.48** still grade D; per-task/per-action framing requested by the reviewer not implemented.
7. **Assistants cost cash under attrition-only** (~$1.8M); justified by capacity only.
8. **Industry packs are parameter swaps on the FP&A data** (scaled headcount archetypes), not real datasets from other industries.
9. No external benchmark checks (rails) in the final model.
10. Not in the Excel: Monte Carlo, break-even, sizing sweep (static reference values), missing-data filling and role-score mode (in the engine package). Not in the engine package or the Excel: regulated-decision mode, square-root staffing, pooling (described in the 20 Oct deck's engine).

---

## 11. Deliverables and files
- **Deck "How the final model works"** (14 slides, PDF, 20 Oct 2026, for Chandan): question; six steps + two layers; assumptions & grades; funnel; three kinds of money; odds & sensitivity; decision; change since v0 (waterfall $3.10M → +$2.04M → +$0.65M → $5.79M); data situations; industry packs; scenario library; tests; asks.
  - Asks on the last slide: approve the structure (six steps, three kinds of money, go ≥70%, stop <40%); set defaults (attrition only; capacity only for healthcare; whole positions per role; pooling optional); confirm industries (healthcare, insurance, tech first; banking, retail, manufacturing ready); ask Etter for two fields (hours on every task, a level for every role); name a pilot partner. Then: Excel version and website v1 on the same engine.
  - Deck "tests" claims: 21 automated tests; website and Python engines agree to 2×10⁻¹³ on nine cases; ledger sums to cash NPV with $0 gap; build-only settings reproduce v0 to the cent.
- **Excel: `Etter_Value_Model_FPA.xlsx`** (live formulas, ~17,900 formulas, 0 errors; ceilings 90% / 80%). Sheets: Read me · Summary · Inputs (four yellow choices: scenario, policy, industry, assistants; override for programme size; all parameters with meaning/source/grade) · Tasks (420 rows) · Workloads (build vs buy, cost test, rank, programme, go-live, 8 go-live slots) · Roles (costs, freed FTE, target positions, backfill rule, leavers) · Timeline (months 0–60; costs, savings, hours; one block per quantity × 11 roles; 5-year results, by year, PV by line) · Sizing (static reference sweep) · Risk (static reference odds, break-even, sensitivity, scenario×policy grid, verdict) · Checks (20 checks incl. Etter tie-outs, reconciliation, ledger, and match to the engine at defaults). Matches the Python engine to the cent in six tested cases (Moderate/Attrition $9,376,169.02; Moderate/Active $22,646,490.45; Aggressive/Attrition $24,976,841.88; Conservative/Attrition −$1,003,243.82; Moderate/Capacity −$10,137,448.88; Healthcare pack $9,712,620.12). Peak-cash programme size comes from a lookup table by scenario × policy (computed at cross-industry defaults); the user can override. To change a ceiling: Inputs, "Etter categories" table.
- **Engine package: `etter_value_model.zip`** (same layout as the original zip): `evm.py` final engine (build-or-buy in `scope`, `size_to_peak`, `report()` sizes by default and returns a `programme` block and each workload's `option`); `evm.js` browser port (parity ~3×10⁻¹⁴ on six cases); `packs/base.json` (ceilings 0.90 / 0.80, `allow_buy`, `buy_workflow 15000`, `buy_enterprise 35000`, `buy_run_per_ai_hour 6.0`); `packs/archetypes.json` (5 archetypes); `data/etter_fpa.json`; `tests/` (18 tests incl. reference numbers in `reference.json`, cheaper-option and peak-size tests, and v0 reproduction with buy/sizing off and old ceilings); `site/etter_value_model.html` (website prototype, rebuilt; sizes to peak cash; shows +$9.4M, 59 positions, 75%, go); `experiments/` (strategy-doc experiments run on the earlier engine, kept for the record); `docs/` (these documents, the Excel and the flowchart). Run `python3 run.py`, `python3 -m unittest discover tests`, `python3 tests/parity.py`, `python3 site/build.py`. The deck's regulated mode, square-root staffing, pooling and 7-pack archetype code are not in the package.
- **Flowchart: `Etter_Value_Model_flowchart.pdf`** (one page, six columns: What goes in · Cost of an hour, kind of work · What AI could do, what to build · What AI really frees · Where each freed hour goes · Money, odds and the decision; rust = cash, green = capacity, blue = hires avoided; worked example = Analysts' "Extract and format financial data"); updated to the 90% / 80% ceilings.
- **`Etter_Value_Model_how_it_works.md`** and **`Etter_Value_Model_assumptions.md`**: team-facing documents, updated to the new ceilings.
- **Study-guide web page** (private artifact "Etter Value Model, Explained"): built before the ceiling change; its figures (v0 worked example; $5.8M headline) are out of date.
- Older artefacts: FP&A workbook v1 (`FPA_AI_model_1.xlsx`) and v2 (`FPA_AI_model_v2_1.xlsx`), their explainer PDFs, the old flowchart, the original v0 zip, and a 21-page explainer of the v1–v8 constructed-data line.

---

## 12. Likely questions and accurate answers
- **What changed after the review?** Chandan set the agent ceilings to Directive 90% and Feedback Loop 80% (from 85% and 55%). Everything was recomputed: cash +$5.8M → **+$9.38M**, positions 47 → **59**, workloads 36 → **45** (35 buy, 10 build), chance positive 65% → **75%**, break-even 17.1% → **14.3%**, payback 36 → **33**, verdict pilot first → **go**.
- **Why is it different from $9.7M last time?** At the old ceilings: the new engine on old settings gives ≈ $9.2M (the models agree); adding review time, agent maintenance, phased go-live and complexity drag takes it to $3.1M; build-or-buy (+$2.04M) and stopping at peak cash (+$0.65M) bring it to $5.8M. The higher ceilings then add about $3.6M → $9.38M. It also no longer double-counts capacity.
- **What is net realisation?** takeover × (1 − review) = 40% × 70% = 28%: of all the work AI could do in the programme, the share that really comes off people's plates. Break-even is 14.3%.
- **Why not count capacity as savings?** It is only money if leadership uses the time; it has no budget line. The model states a hurdle instead (≈15% under capacity only).
- **Why 50% harvest?** A leadership choice, not an estimate; it is the largest driver (−$1.4M at 25%, +$20.5M at 75%).
- **Is 40% takeover realistic?** Middle of a 20–62% range, grade C; finance AI evidence is modest. Even at 20% takeover cash is about break-even (−$0.1M).
- **Why go and not pilot?** 75% of 1,000 draws are positive, above the 70% go threshold. The rollout still starts with 3 workloads and a 6-month evaluation, so takeover and review are measured before the waves.
- **Why 45 workloads, not 59?** Cash peaks at 45; later small workloads free fractions of people that never become positions.
- **Why do mid-caps fail?** About 6 people per role; a role needs ~20–30 people before agents free a whole position, while setup and training costs remain.
- **Why does build vs buy matter?** Small workloads: buy (low up-front). Big high-volume workloads: build (lower per-hour cost). FP&A: 35 buy, 10 build.
- **What is the biggest cost?** Training ($3.05M PV), because it applies to all 1,523 people including their time.
- **Where does 1.31 come from?** BLS ECEC Table 5, full-time private industry: 100/(68.5 + 8.1) = 1.3055. (A 1.29 from Table 4 was an error in v2 and was reverted.)
- **What is the 42.5?** Months of full value in five years after build lead, ramp-up and discounting (annuity factor in the cost test).
- **How sure are we?** 75% of 1,000 correlated draws are positive; P10 −$4.2M, P50 +$5.1M, P90 +$21.2M.
- **What does the pilot measure?** Takeover, checking time per AI hour, weeks to steady use, real running and vendor costs. The break-even to watch is 14.3% net realisation.
- **What if layoffs are allowed?** Active reduction: +$22.6M, 97%, 100 positions, payback month 25 (sized to 37 workloads).
- **Do assistants pay?** Not in cash under attrition-only (their time is not harvested); they show up as capacity (about $1.8M of cash cost). Under active reduction 25% of their time is harvested.
- **Is the model too simple?** Simple where the evidence is thin, on purpose: earlier sophisticated versions failed because mechanisms sat on unmeasurable parameters. Roadmap: task volumes → exception tail; pilot results → takeover/review per workload; a second real dataset → validate industry packs; vary takeover by category and level now.
- **What does the backfill rule mean?** One line per role for hiring managers, e.g. Associate Analyst: leave 16 of the next 141 leavers unreplaced; Analyst: 14 of the next 118.

---

## 13. Glossary (plain language)
- **NPV** — five-year value in today's money (each month discounted at 6.96%/yr; a dollar in year 5 ≈ $0.71 today).
- **Loaded cost** — salary × 1.31 (benefits, payroll taxes, paid leave).
- **AI-able hours** — task hours × category ceiling (agent categories only).
- **Takeover** — share of AI-able work the agent actually does. **Review** — human checking time per AI hour. **Net realisation** — takeover × (1 − review).
- **Complexity drag** — trim for the leftover work being harder.
- **Harvest share** — share of freed time leadership turns into fewer positions.
- **Attrition only** — positions go only as people leave and are not replaced; no layoffs.
- **Capacity** — freed time not turned into positions or avoided hires, valued at cost, never added to cash.
- **Hires avoided** — planned hires no longer needed in a growing company; reported against the plan.
- **Capacity hurdle** — share of capacity that must become real value for a negative-cash programme to break even.
- **Workload** — Etter's group of related tasks; one agent is built or bought per workload.
- **Tier** — workflow (single role, ≤2 agent tasks) vs enterprise (≥2 roles or ≥3 agent tasks).
- **Peak-cash sizing** — adding workloads in rank order until five-year cash stops rising.
- **Break-even** — net realisation at which cash NPV = 0.
- **Pilot gate** — top 3 workloads for 6 months; scale if net realisation ≥ break-even.
- **Grades A–D** — source strength (A official/list price → D thin evidence).
