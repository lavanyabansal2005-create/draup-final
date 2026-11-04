# Etter Value Model — how it works

**Version:** final model, 23 October 2026, with the agent ceilings set by Chandan in the review meeting (**Directive 90%, Feedback Loop 80%**). **Default case:** Etter FP&A data (11 roles, 1,523 people, 420 tasks), Moderate scenario, Attrition only, cross-industry defaults, assistant tools on. Every number below is an exact output of the model at that default. The full list of inputs, sources and grades is in `Etter_Value_Model_assumptions.md`.

---

## 1. What it answers

> *"If we put AI on this function, what changes, what is it worth, and should we go ahead?"*

Etter breaks each role into workloads and tasks and labels every task with a category that says how AI relates to it. It stops at percentages. This model turns those percentages into money that **a business leader can follow and a CFO will accept**: real cash only when payroll actually shrinks, every dollar traced to a role, task or cost line, and freed time never passed off as cash.

**The model in three sentences**
1. Etter says which tasks AI can do; the model keeps only the workloads where an agent (built or bought, whichever is cheaper) costs less than the work, and only the share AI really takes over once people have checked it.
2. That freed time becomes whole positions as people leave, hires the plan no longer needs, or capacity for other work — every hour goes to exactly one place.
3. Cash, avoided hires and capacity are reported separately, with the odds, a break-even and a ledger that traces every dollar to an input.

**Answer at the default:** cash **+$9.38M** over five years (today's money) · **59** positions not refilled (3.9%) · capacity **$47.7M** (never added to cash) · payback **month 33** · **75%** chance cash is positive · break-even net realisation **14.3%** vs **28%** assumed · verdict **GO** (phased rollout).

---

## 2. Inputs

| From | What |
|---|---|
| **Etter Tasks sheet** | For each of 420 tasks: role, workload, category, hours one person spends on it a month. |
| **Etter Roles sheet + client** | For each role: headcount, average base salary, level (→ turnover band). Etter's role score is used only as a second opinion. |
| **Four client choices** | Scenario (Conservative / Moderate / Aggressive), policy for freed time (Capacity only / Attrition only / Active reduction), industry, assistant tools on or off. |
| **Assumption pack** | Category ceilings, takeover, review, costs, turnover, discount rate, programme design — each with a source and an A–D grade. |

---

## 3. The six steps

Worked example carried through: Analysts' task **"Extract and format financial data"** — Directive, 8.64 hours a month per person, 310 Analysts, salary $79,661.

### Step 1 — Price an hour of work
```
loaded cost  = salary × 1.3055
hourly rate  = loaded cost ÷ (12 × task hours a month)
```
1.3055 = 100 ÷ (68.5 + 8.1): wages and paid leave as shares of compensation for full-time private-industry workers (BLS ECEC, Table 5). Standard month = 160 hours.
*Example:* $79,661 × 1.3055 = $103,997 a year ÷ 1,920 = **$54.17 an hour**.

### Step 2 — Potential: what AI could do
Each task's category decides the most AI could ever do and what kind of help it is.

| Category | Most AI could do | Kind |
|---|---|---|
| Directive | **90%** | Agent — does the work instead of the person |
| Feedback Loop | **80%** | Agent |
| Task Iteration | 45% | Assistant — makes the person faster |
| Learning | 25% | Assistant |
| Validation | 50% | Assistant |
| Negligibility | 0% | Stays human |

Agent ceilings set by Chandan (Draup), 23 October 2026 (previously 85% and 55%).

```
AI-able hours (agent work)   = task hours × headcount × ceiling
assistant hours saved        = task hours × min(ceiling, band saving) × active use
```
Band saving: Para-professional 20%, Professional 12%, Management 6%, Executive 3%. Active use 70%.
*Example:* 8.64 × 310 × 90% = **2,411 AI-able hours a month** (28,927 a year).
Across the function, **563.7 people's worth** of work sits in agent categories; **482.0** is AI-able.

### Step 3 — Scope: what to build, how, and how much
Agents are set up **per workload** (59 contain agent tasks), shared by every role that does it.

**Cost test.** For each workload:
```
work value / month    = AI-able hours (all roles) × each role's hourly rate
freed value / month   = work value × net realisation (28%)
NPV at cost           = (freed value − running − maintenance) × 42.5 − up-front cost
```
Priced two ways, the higher NPV kept:

| | Build custom | Buy vendor |
|---|---|---|
| Up front | $55,000 (workflow) / $130,000 (enterprise: 2+ roles or 3+ agent tasks) | $15,000 / $35,000 |
| Running | $3.48 per AI hour | $6 per AI hour |
| Upkeep | 18% of build a year | included |

A workload passes if its best NPV is above zero. **42.5** = months of full value inside five years after a 3-month build, a 12-month S-curve ramp-up and 6.96% discounting.
*Example:* "Financial analysis and reporting" — 5 roles, **$1,016,529 of work a month**; build NPV $10.73M vs buy $10.06M → **build**. "Cost review planning and support" — $3,850 a month; buy, NPV +$11,953 → passes, ranks last.

**Sizing.** Passing workloads are ranked by return per dollar up front and added one at a time; the programme **stops where five-year cash peaks**: **45 of 59** (35 bought, 10 built, $1.29M up front). It stops early because the cost test values freed time at full cost, while cash only counts time that becomes whole positions; late, small workloads free fractions of people that never round up.

**Timing.** Pilot of the top 3 live in month 3 → 6-month evaluation → waves of 10 every 3 months (months 12, 15, 18, 21, then the last 2 in month 24). Build or setup cost is spread over the 3 months before each go-live.

### Step 4 — Realised: what AI actually frees
```
hours freed  = AI-able hours × takeover × (1 − review) × ramp-up × drag
AI hours     = AI-able hours × takeover × ramp-up          (running cost is paid on these)
drag         = 1 − 0.30 × (share of the role's time freed)
```
- **Takeover 40%**: share of AI-able work the agent actually does. **Review 30%**: hours people spend checking per 100 AI hours. **Net realisation = 40% × 70% = 28%** — the number the answer turns on, and the one a pilot measures.
- **Ramp-up**: each agent's use follows an S-curve from its go-live, full after 12 months; assistant seats roll out from month 2 over 6 months.
- **Complexity drag**: the work left behind is harder, so freed time is trimmed more the more of a role is automated (a simple stand-in, grade D).

*Example:* 28,927 × 40% = 11,571 AI hours → × 70% = 8,099 hours freed → Analysts free ~14% of their time, keep 96% → **7,769 hours a year ≈ 4.0 people's worth**.

**Why AI-able hours are not headcount (whole function, month 60, people's worth):**
| Step | |
|---|---|
| Hours in agent categories | 563.7 |
| × ceilings (AI-able) | 482.0 |
| In the 45 workloads | 460.9 |
| × 40% takeover | 184.4 |
| × 70% after review | 129.0 |
| After complexity drag | 124.1 |
| **Positions not refilled** | **59** |
Plus 52.3 people's worth from assistants: **176 freed in all**.

### Step 5 — Routing: where each freed hour goes
**Policy** (the company's choice):

| | Capacity only | **Attrition only** (default) | Active reduction |
|---|---|---|---|
| Agent time → positions | 0% | **50%** | 75% |
| Assistant time → positions | 0% | **0%** | 25% |
| How | nobody goes | as people leave | 2 months' notice, 12 weeks' severance |

**Positions not refilled (cash path):**
```
target positions (per role)   = floor(harvest share × freed people)
people who have left by m     = headcount × (1 − (1 − yearly turnover)^(m ÷ 12))
positions in month m          = smaller of (target × progress so far, people who have left),
                                never less than last month, never more than time freed
```
Turnover: Para-professional 12.5%, Professional 9.1%, Management 6.3%, Executive 5.2% (Mercer 2025) × industry factor.
*Example:* Analysts free 28.1 people's worth from agents × 50% = 14.0 → **14 positions**; 118 Analysts leave over five years anyway → hiring-manager rule: **"leave 14 of the next 118 leavers unreplaced."** All roles: **59 positions**, reached by about month 36. Rounding down per role means a role needs roughly 20–30 people before agents free a whole position.

**Hires avoided (against the plan):** only if the industry is growing — spare freed people fill planned hires before becoming capacity. FP&A default: 0% growth → 0.

**Capacity (time back):** freed hours − positions × hours − hires avoided × hours, valued at the hourly rate. ~117 people's worth at month 60.

Every month the model checks **freed = positions + hires avoided + capacity** (gap = 0).

### Step 6 — Money: three kinds, never added
Each month's money is discounted at 6.96% a year, (1.0696)^(−m ÷ 12), and summed over 60 months.

| Savings (PV) | | Costs (PV) | |
|---|---|---|---|
| Salaries no longer paid (× 1.31) | $18.89M | Training: $846 + 16.7 h, each of 1,523 people | $3.05M |
| Recruiting avoided ($4,700 per leaver not replaced) | $0.25M | Running: $3.48 / $6 per AI hour, 13% cheaper a year | $2.67M |
| Equipment per position ($468/yr) | $0.08M | Assistant licences: $360 a seat a year | $1.48M |
| | | Build or buy | $1.20M |
| | | Programme: $75,000 + $623 per person | $1.02M |
| | | Custom-agent upkeep: 18% a year | $0.41M |
| **Total** | **$19.22M** | **Total** | **$9.84M** |

| Three kinds of money | Default |
|---|---|
| **Cash vs today** (savings − costs) | **+$9.38M** |
| **Hires avoided vs plan** | $0 |
| **Capacity at cost** | **$47.7M** — never added to cash |

Payback **month 33**; peak funding needed **$4.4M**. Cash by year (nominal): day 0 −$1.09M, year 1 −$3.32M, year 2 +$1.61M, year 3 +$4.56M, year 4 +$5.51M, year 5 +$5.62M.

**Capacity hurdle.** If nobody leaves (Capacity only, all 59 workloads), cash is −$10.14M against $67.3M of capacity, so **about 15%** of the freed time must turn into real value for the programme to break even. The model states the hurdle instead of adding capacity to cash.

---

## 4. How sure we are

The plan (which workloads, when) is fixed, then reality is drawn **1,000 times** with a fixed seed (same answer every run). Each draw picks takeover, review, months to full use, active use, assistant saving, costs, running cost, drag and turnover from their ranges. One shared "execution quality" factor (correlation 0.5) makes good programmes good at everything at once.

| Result (default) | |
|---|---|
| Chance cash is positive | **75%** |
| Bad case (P10) / middle (P50) / good case (P90) | −$4.2M / +$5.1M / +$21.2M |
| Break-even net realisation | **14.3%** (assumed 28%) |

**What moves the answer most** (one input at a time):
| Input | Range | Cash NPV |
|---|---|---|
| Harvest share (leadership's choice) | 25% → 75% | −$1.4M → +$20.5M |
| AI takeover (pilot measures) | 20% → 62% | −$0.1M → +$19.1M |
| Human review (pilot measures) | 15% → 45% | +$12.0M → +$4.6M |
| Months to full use | 6 → 24 | +$11.0M → +$6.3M |
| Running cost | $1.50 → $10/h | +$10.9M → +$4.3M |
| Build and programme cost | ×0.85 → ×1.6 | +$10.4M → +$5.3M |

---

## 5. The decision

- **Go** if the chance of positive cash is 70% or more · **Pilot first** at 40–70% · **Stop** below 40% · **Capacity case** if nothing is turned into positions (fund only if leadership commits to using the time).
- FP&A: 75% → **GO, phased rollout**. The rollout still starts with the top 3 workloads (live in month 3) and a 6-month evaluation before the waves, so takeover, checking time, adoption speed and real costs are measured early; the break-even to watch is **14.3%** net realisation.
- A **backfill rule per role** for hiring managers (e.g. Associate Analyst: leave 16 of the next 141 leavers unreplaced; Analyst: 14 of the next 118; Senior Coordinator: refill as usual).

**Scenarios and policies (each sized to its own peak cash):**
| | Capacity only | Attrition only | Active reduction |
|---|---|---|---|
| Conservative | −$9.7M | −$1.0M · 30% · stop | +$4.7M · 60% · pilot |
| **Moderate** | −$10.1M (hurdle 15%) | **+$9.4M · 75% · go** | +$22.6M · 97% · go |
| Aggressive | −$11.4M | +$25.0M · 97% · go | +$49.1M · ~100% · go |

---

## 6. Making it work for any company

- **Same formulas everywhere; only settings change**: base defaults → industry pack → the client's own numbers.
- An industry pack changes the **discount rate, staff turnover and job growth** (and flags regulated industries). Packs: healthcare providers, insurance, technology (scoped with Chandan); banking, retail, manufacturing; cross-industry default.
- **Company size is not a setting**; it enters through headcount, and whole-position rounding does the rest. Organisations with about 6 people per role (mid-caps) come out as **stop**; large organisations work.
- Missing or odd data is flagged, not fatal (missing salary or headcount, unknown roles or categories, task hours that do not sum to 160), and a role-score mode uses Etter's role scores when tasks are missing — both in the engine package. Regulated decisions (AI prepares, a person decides), queue work (square-root staffing at 85% occupancy) and pooling positions across a level are described in the deck's engine but are not in this package or the Excel yet.

---

## 7. Outputs

| Output | For whom |
|---|---|
| Three kinds of money (cash, hires avoided, capacity) | CFO, CHRO |
| Funnel from AI-able hours to positions | Leaders: why AI % ≠ headcount |
| Odds, P10/P90, break-even, what moves it | CFO |
| Verdict, pilot design and break-even to watch | Programme sponsor |
| Backfill rule per role | Hiring managers |
| Workload list: build or buy, rank, go-live month | Programme team |
| Ledger: every dollar by line, role and workload | Finance / audit |

---

## 8. How we know it holds

- **20 checks** in the Excel, all pass: tasks, headcount, payroll and hours tie to the Etter file; every freed hour reconciles every month; capacity never negative; positions whole and within headcount; ledger sums to the cash NPV with a $0 gap; build charged equals workloads built; and the workbook matches the reference engine.
- The Excel matches the Python engine **to the cent** ($9,376,169.02 at the default) in six tested cases across scenarios, policies and an industry pack.
- The browser engine matches the Python engine to ~3×10⁻¹⁴ on six cases; **18 automated tests** pass, including reproducing the earlier engine to the cent when build-or-buy, sizing and the old ceilings are switched off.
- Deterministic: fixed seed, monthly arithmetic, no hidden steps.

---

## 9. Limits (stated plainly)

1. "The remaining work is harder" is a single drag parameter (0.30, grade D). A proper difficulty curve needs task volumes or handling times from Etter.
2. One takeover and review rate for every task and level. Next step: vary them by Etter category and role level.
3. Vendor prices and running cost have thin evidence; much of the gain from build-or-buy depends on vendor prices.
4. The odds depend on the ranges chosen; quote them as "about three in four".
5. Etter's Tasks and Workloads sheets disagree on the category split; the model uses Tasks. This is the one structural question that could flip the verdict.
6. Under attrition only, assistant tools are a cash cost (about $1.8M) justified only by capacity.
7. Industry packs are settings applied to the FP&A data, not validated on other industries' real data yet.
8. The higher agent ceilings (90% / 80%) raise every result; with the previous 85% / 55% the default was +$5.8M, 65%, pilot first.

---

## 10. Files

- `Etter_Value_Model_FPA.xlsx` — the model in live formulas (Read me, Summary, Inputs, Tasks, Workloads, Roles, Timeline, Sizing, Risk, Checks).
- `etter_value_model.zip` — the Python engine, browser engine, packs, data, tests, website prototype and these documents.
- `Etter_Value_Model_assumptions.md` — every assumption with value, range, grade and source.
- `Etter_Value_Model_context.md` — full background, version history and Q&A for anyone (or any agent) answering questions on the model.
- `Etter_Value_Model_flowchart.pdf` — the model on one page.
