# Etter Value Model — final list of assumptions

**Version:** final model, 23 October 2026, with the agent ceilings set by Chandan in the review meeting (Directive 90%, Feedback Loop 80%) · **Default case:** Etter FP&A data (11 roles, 1,523 people, 420 tasks), Moderate scenario, Attrition only policy, cross-industry defaults, assistant tools on.
**Where they live:** every number below is an input on the **Inputs** sheet of `Etter_Value_Model_FPA.xlsx` (blue text) and in the engine's parameter pack (`packs/base.json`). Change it there and the whole model follows.

**Grades** — **A** official statistic or list price · **B** industry benchmark with a stated method · **C** indirect evidence or estimate · **D** thin evidence, replace first · **Policy** the company's choice, not an estimate · **Design** a modelling choice.
**Pilot?** — ✔ = the six-month pilot is designed to measure it.

---

## 1. The four choices the client makes

| # | Choice | Default | Options | Notes |
|---|---|---|---|---|
| 1.1 | Scenario | **Moderate** | Conservative, Moderate, Aggressive | Switches the uncertain dials in section 2 together. |
| 1.2 | Policy for freed time | **Attrition only** | Capacity only, Attrition only, Active reduction | See section 3. Healthcare pack defaults to Capacity only. |
| 1.3 | Industry | **Cross-industry default** | 7 packs (section 6) | Changes discount rate, turnover and job growth only. |
| 1.4 | Assistant tools (Copilot-style seats) | **On** | On / Off | Off = agents only; no licences or assistant time. |
| 1.5 | Programme size (number of workloads) | **Peak-cash size** (45 at the default) | any number; 0 = all that pass | Optional override. Peak-cash sizes by case are in section 8. |

---

## 2. Scenario dials — the uncertain quantities

| # | Assumption | Conservative | **Moderate** | Aggressive | Range used for odds (P10–P90) | Grade | Pilot? | Basis |
|---|---|---|---|---|---|---|---|---|
| 2.1 | **AI takeover**: share of AI-able work the agent actually does | 25% | **40%** | 60% | 20–62% | C | ✔ | Indirect: finance AI deployments report low-to-moderate impact (Gartner, May 2026); accounts payable, the most automated finance process, averages ~33% touchless (Ardent Partners 2025). |
| 2.2 | **Human review**: hours people spend checking per 100 AI hours | 40% | **30%** | 20% | 15–45% | C | ✔ | Estimate; measured in the pilot as checking time per AI hour. |
| 2.3 | **Net realisation** = takeover × (1 − review) | 15% | **28%** | 48% | — | derived | ✔ | The single number the answer turns on. Break-even at the default: **14.3%**. Cross-check: agents followed AI recommendations ~35% of the time in a live deployment (Brynjolfsson, Li and Raymond, v2, PDF p. 23); an assistant-acceptance rate, so magnitude support only. |
| 2.4 | Months to full use after go-live (S-curve) | 18 | **12** | 6 | 6–24 | C | ✔ | MIT NANDA, State of AI in Business 2025. |
| 2.5 | Assistant active use (share of seat holders who save time) | 55% | **70%** | 85% | 50–85% | C | ✔ | Published weekly-active use of purchased assistant seats; estimate. |
| 2.6 | Assistant saving multiplier | 0.50 | **1.00** | 1.25 | 0.4–1.6 | C | ✔ | Scales the band rates in 4.4. |
| 2.7 | Cost multiplier (build, buy, running, maintenance, setup, deployment, licences) | 1.25 | **1.00** | 0.90 | 0.85–1.6 (skewed up) | C | ✔ | Projects overrun; training is priced per person and not scaled. |
| 2.8 | Complexity drag κ ("the work left behind is harder") | 0.30 | **0.30** | 0.30 | 0.10–0.55 | **D** | partly | Simple stand-in for the exception tail; needs Etter task volumes or handling times to replace. |
| 2.9 | Running-cost multiplier | 1.00 | **1.00** | 1.00 | 0.43–2.9 (≈ $1.50–$10/h custom) | D | ✔ | Held at 1 in scenarios; varied in the odds. |
| 2.10 | Turnover multiplier | 1.00 | **1.00** | 1.00 | 0.75–1.3 | B | — | Held at 1 in scenarios; varied in the odds. |

---

## 3. Policy — what leadership does with freed time (a choice, not an estimate)

| # | Setting | Capacity only | **Attrition only** | Active reduction | Grade |
|---|---|---|---|---|---|
| 3.1 | Harvest share of **agent**-freed time turned into positions | 0% | **50%** | 75% | Policy |
| 3.2 | Harvest share of **assistant**-freed time | 0% | **0%** | 25% | Policy |
| 3.3 | Mechanism | nobody goes | **positions go only as people leave and are not replaced** | separation after notice | Policy |
| 3.4 | Notice period | — | — | 2 months | Policy |
| 3.5 | Severance | — | — | 12 weeks of base salary (outplacement not included) | Policy |
| 3.6 | Freed time absorbs planned hires first (if the industry grows) | yes | **yes** | yes | Policy |

Harvest share is the largest single driver: −$1.4M at 25% to +$20.5M at 75% (default case).

---

## 4. People, pay and time

| # | Assumption | Value | Grade | Source / basis |
|---|---|---|---|---|
| 4.1 | On-cost multiplier (loaded cost = salary × this) | **1.3055** | A | BLS Employer Costs for Employee Compensation, **Table 5, full-time private industry**: wages 68.5%, paid leave 8.1% of compensation; 100 ÷ (68.5 + 8.1). Paid leave is excluded from the on-cost because the salary already pays for it; see the convention note below. |
| 4.2 | Working hours | **160 a month (1,920 a year)** | A | Etter file convention. If a role's tasks sum to a different total (Senior Analyst: 136), shares are taken of the hours recorded. |
| 4.3 | Hourly rate | loaded cost ÷ (12 × task hours a month) | derived | Time-driven activity-based costing. Example: Analyst $54.17/h. |
| 4.4 | Assistant time saving by band | Para-professional **20%**, Professional **12%**, Management **6%**, Executive **3%** | B | Brynjolfsson, Li and Raymond, *Generative AI at Work*, QJE 2025 (largest gains for less experienced workers). Applied as the smaller of this and the category ceiling. |
| 4.5 | Yearly turnover by band | Para-professional **12.5%**, Professional **9.1%**, Management **6.3%**, Executive **5.2%** | B | Mercer 2025 US turnover survey; × industry multiplier (section 6). |
| 4.6 | Role level → turnover band | Etter level mapped to band (e.g. Individual Contributor → Professional; Clerk → Para-professional) | Design | Turnover band given per role in the data. |
| 4.7 | Cost per hire (saved when a leaver is not replaced, or a planned hire is avoided) | **$4,700** | B | SHRM cost-per-hire benchmark. |
| 4.8 | Equipment and software per position (saved when not refilled) | **$468 a year** | C | Estimate. |

**On-cost convention (4.1).** 1.3055 reconciles to BLS ECEC **only with paid leave excluded from the on-cost**. ECEC counts paid leave (holidays, vacation, sick leave) as a benefit, separate from "wages and salaries", but an annual salary already includes the pay for that leave. So the right multiplier on an annual salary is total compensation ÷ (wages + paid leave) = 100 ÷ (68.5 + 8.1) = **1.3055** (Table 5, full-time private industry). The hourly rate then spreads the full loaded cost over 1,920 working hours (row 4.3), so leave is paid for once, not twice.

The **headline ECEC multiplier is 1.4287** (June 2026, all private-industry workers: $46.89 total compensation ÷ $32.82 wages an hour). That is the right multiplier on pay for hours worked, which excludes leave. Applying it to an annual salary counts leave twice. It is also a different population (all workers, including part-time); the full-time equivalent is 100 ÷ 68.5 = 1.460. A reviewer who checks the headline figure will see 1.3055 as 9% low; this is why it isn't. Priced: at 1.4287 the default headline would be **$10.97M** instead of $9.38M.

---

## 5. What AI could do (Etter categories)

| # | Etter category | Most AI could do (ceiling) | Kind | Grade |
|---|---|---|---|---|
| 5.1 | Directive | **90%** | Agent (does the work; can become positions) | Chandan (Draup), 23 Oct 2026 |
| 5.2 | Feedback Loop | **80%** | Agent | Chandan (Draup), 23 Oct 2026 |
| 5.3 | Task Iteration | **45%** | Assistant (person goes faster; capacity by default) | Team / Etter |
| 5.4 | Learning | **25%** | Assistant | Team / Etter |
| 5.5 | Validation | **50%** | Assistant | Team / Etter |
| 5.6 | Negligibility | none (no ceiling in the pack) | Human only | Team / Etter |

The two agent ceilings were set by Chandan in the review meeting on 23 October 2026 (previously 85% and 55%, the lower of Etter's two ceilings). The assistant ceilings remain the lower of Etter's two ceilings per category (its potential and its bucket ceiling). A ceiling is the most AI could ever do, not a savings number on its own.

### 5.7 Category ceilings: the source workbook disagrees with itself

**Status: open question 1 for Chandan. The ceilings are not changed here; this records the conflict and what it costs.**

#### What the workbook says

The Etter source workbook (`Etter_FPandA_11roles_tasks_hours_automation.xlsx`, team-provided) gives the "Etter potential" per category in two places, and the two tables disagree on **five of six** categories (only Negligibility agrees). It also gives a coarse bucket ceiling (AI 100%, Human + AI 50%, Human 0%), which is a fourth possible reading.

| Category | Read me sheet | Tasks column / How to use it | Bucket ceiling | **Pack (in use)** |
|---|---|---|---|---|
| Directive | 0.90 | 0.85 | 1.00 | **0.90** |
| Feedback Loop | 0.85 | 0.55 | 1.00 | **0.80** |
| Task Iteration | 0.50 | 0.45 | 0.50 | **0.45** |
| Learning | 0.45 | 0.25 | 0.50 | **0.25** |
| Validation | 0.40 | 0.50 | 0.50 | **0.50** |
| Negligibility | 0.10 | 0.10 | 0.00 | **— (removed)** |

The Tasks column is the data shipped on all 420 rows, and the How to use it sheet says it is the full resolution of that column. The Read me table appears nowhere else in the file.

#### Which reading we use, and where it came from

- **Agent categories (Directive, Feedback Loop): 0.90 / 0.80.** Set by Chandan on 23 Oct 2026, overriding the shipped 0.85 / 0.55 (recorded on the value-model workbook's Inputs sheet and in its Read me, item 10). `experiments/legacy/engine_v2.py` line 11 shows the earlier engine used the shipped column, which dates the change. 0.90 matches the Read me table. **0.80 matches no table in the source.**
- **Assistant categories: the lower of the bucket ceiling and the Tasks column.** That gives 0.45 / 0.25 / 0.50.
- **Negligibility: no ceiling.** The pack used to carry 0.00 (the bucket ceiling) where both Etter tables say 0.10. Negligibility maps to Human, so the value was never read; the key was removed on 5 Nov 2026 with the headline unchanged to the cent.

#### Why only two of the six move the headline

Assistant savings are the smaller of the category ceiling and the band rate, and the highest band rate is 0.20. Every assistant ceiling in every reading is at least 0.25, so it never binds. Checked: putting the Read me or bucket values on the assistant categories leaves the headline at exactly $9,376,169.02. **The whole spread comes from Directive and Feedback Loop.**

#### Priced impact (5-year cash NPV, Moderate, attrition only)

| Reading | Directive / Feedback Loop | Cash NPV | vs pack | Workloads in programme | Positions at month 60 | Payback month |
|---|---|---|---|---|---|---|
| Tasks column (shipped data) | 0.85 / 0.55 | $5,800,227 | −$3.58M (−38%) | 36 | 47 | 36 |
| **Pack (in use)** | **0.90 / 0.80** | **$9,376,169** | — | **45** | **59** | **33** |
| Read me table | 0.90 / 0.85 | $9,754,377 | +$0.38M (+4%) | 41 | 60 | 32 |
| Bucket ceiling | 1.00 / 1.00 | $11,476,089 | +$2.10M (+22%) | 37 | 66 | 30 |

High to low is a 2.0x spread on the headline, from an input the brief puts out of scope. The ceilings are not among the uncertainty draws, so the P10–P90 band (−$4.2M to +$21.2M) assumes the pack reading is correct. It does not cover this question.

These four figures are locked in by `tests/test_ceiling_sets.py`. Changing the ceilings, or anything that moves their price, fails that test.

#### Reproducing this in the workbook

`docs/Etter_Value_Model_FPA.xlsx` reproduces all four figures to the dollar, with one catch. Programme size (Inputs B9) is the peak-cash size for the **default** ceilings (45 workloads), copied from the engine. Editing only the ceiling cells keeps 45 workloads and gives $5.49M / $9.56M / $11.27M for the other three readings. To match the engine, set the override (Inputs B8) to each size from 1 to 59 and take the highest cash NPV. The peaks are at 36, 41 and 37.

---

## 6. Industry packs (only these three settings change between industries)

| # | Industry | Discount rate | Turnover vs average | Job growth / yr | Default policy | Regulated |
|---|---|---|---|---|---|---|
| 6.1 | Healthcare providers | 6.19% | ×0.91 | 0.9% | Capacity only | Yes (CMS) |
| 6.2 | Insurance | 6.34% | ×0.59 | 0.2% | Attrition only | Yes (NAIC) |
| 6.3 | Technology and software | 9.34% | ×0.59 | 0.5% | Attrition only | No |
| 6.4 | Banking | 4.98% | ×0.59 | 0.2% | Attrition only | No |
| 6.5 | Retail | 7.27% | ×1.18 | 0.0% | Attrition only | No |
| 6.6 | Manufacturing | 7.70% | ×0.64 | 0.1% | Attrition only | No |
| 6.7 | **Cross-industry default** | **6.96%** | **×1.00** | **0.0%** | Attrition only | No |

Grades: discount rates **A** (Damodaran, cost of capital by industry, January 2026); turnover **B** (BLS JOLTS 2025 quits vs all private industry, 2.2%/month); growth **B** (BLS Employment Projections 2025–35); regulation (CMS FAQ, February 2024; NAIC model bulletin, December 2023). In regulated industries, decision tasks are treated as Validation (AI prepares, a person decides) — described in the deck's engine; not in this package or the Excel yet. Company size is **not** a setting; it enters through headcount.

---

## 7. Costs of the programme

| # | Assumption | Value | Range | Grade | Pilot? | Source / basis |
|---|---|---|---|---|---|---|
| 7.1 | Build a custom agent: workflow | **$55,000** | ×0.85–1.6 | C | ✔ | Two 2026 agent-development benchmarks: workflow builds $20–60k (upper end used). |
| 7.2 | Build a custom agent: enterprise | **$130,000** | ×0.85–1.6 | C | ✔ | Same benchmarks: enterprise builds $75–150k. |
| 7.3 | Enterprise tier rule | **2+ roles share the workload, or 3+ agent tasks** | — | Design | — | Integration surface read off the Etter data (54 single-role vs 5 cross-role workloads). |
| 7.4 | Custom agent running cost | **$3.48 per AI hour** | $1.50–$10 | **D** | ✔ | Weakest input. Paid on every hour the AI works, including hours people review. |
| 7.5 | Custom agent maintenance | **18% of build cost a year** after go-live | — | C | ✔ | 15–20% custom-software maintenance convention. |
| 7.6 | Buy a vendor agent: workflow | **$15,000** up front | $5k–$150k | **D** | ✔ | Vendor list prices. |
| 7.7 | Buy a vendor agent: enterprise | **$35,000** up front | $5k–$150k | **D** | ✔ | Vendor list prices. |
| 7.8 | Vendor agent price | **$6 per AI hour** (includes vendor upkeep) | $2.40–$12 | C | ✔ | Vendor usage and outcome pricing. |
| 7.9 | Running-cost price decline (custom and vendor) | **13% a year** | — | C | — | Observed AI price declines; estimate. |
| 7.10 | Build lead time (cost spread over these months before go-live) | **3 months** | — | C | ✔ | Estimate. |
| 7.11 | Programme setup, fixed (month 0) | **$75,000** | — | C | — | Forrester TEI of Microsoft 365 Copilot (full study). |
| 7.12 | Deployment per person in every touched role (month 0) | **$623** | — | C | — | Forrester TEI, setup cost per seat. |
| 7.13 | Training per person in every touched role (once) | **$846 + 16.7 hours** of the person's own time | — | B | — | ATD 2026 State of the Industry. Not scaled by the cost multiplier. |
| 7.14 | Assistant licence | **$360 per seat a year** | — | A | — | Microsoft list price (unchanged since 2023). |
| 7.15 | Assistant seats | headcount × active use, ramped in | — | derived | ✔ | — |

---

## 8. Programme design and timing

| # | Assumption | Value | Grade | Notes |
|---|---|---|---|---|
| 8.1 | One agent per Etter workload, shared by every role that does it | — | Design | 59 workloads contain agent tasks. |
| 8.2 | Build or buy | **the option with the higher 5-year NPV at cost** (buy only if strictly better) | Design | Default: 35 buy, 10 build. |
| 8.3 | Cost test | workload passes if (freed value − running − maintenance) × annuity − up front > 0, freed value = work value × net realisation | Design | Policy-independent: "is the AI cheaper than the work?" |
| 8.4 | Annuity factor (months of full value in five years) | **42.5** | derived | After 3-month build, S-curve ramp, 6.96% discounting. |
| 8.5 | Ranking | **return per $ up front** | Design | — |
| 8.6 | Programme size | **stop where 5-year cash NPV peaks** | Design | Moderate: Attrition 45 · Active 37 · Capacity all (59). Conservative: 35 · 32 · 53. Aggressive: 41 · 58 · 59. |
| 8.7 | Pilot | **top 3 workloads**, live in month 3 | Design | — |
| 8.8 | Pilot evaluation before further builds | **6 months** | Design | — |
| 8.9 | Waves after the pilot | **10 workloads every 3 months** (go-live months 12, 15, 18, 21 and 24 at the default) | Design | — |
| 8.10 | Adoption curve | **S-curve** from each go-live; the same curve in the cost test, running cost and savings | Design | — |
| 8.11 | Assistant rollout | starts **month 2**, full after **6 months** (S-curve) | Design | — |
| 8.12 | Horizon | **60 months** (5 years), month 0 = today | Design | Fixed; the cost test uses the same window. |

---

## 9. Turning freed time into money (structural assumptions)

| # | Assumption | Grade |
|---|---|---|
| 9.1 | **Every freed hour goes to exactly one place**: positions not refilled, hires avoided, or capacity. Checked every month (gap = 0). | Design |
| 9.2 | **Positions are whole numbers, rounded down per role.** (Pooling across a level is described in the deck's engine as an option, off by default; not in this package yet.) | Design |
| 9.3 | Under attrition only, **a position goes only when someone leaves on their own**: positions ≤ people who have left so far = headcount × (1 − (1 − yearly rate)^(months ÷ 12)). | Design |
| 9.4 | Positions follow programme progress (target × share of steady-state freed time reached), **never come back** once removed, and **never exceed the time actually freed**. | Design |
| 9.5 | Assistant time is not turned into positions under attrition only (minutes scattered across many people). | Policy |
| 9.6 | **Cash, hires avoided and capacity are never added together.** | Design |
| 9.7 | Capacity is valued at the hourly rate (at cost) and is real only if used; when cash is negative the model reports a **capacity hurdle** (share that must become real value to break even) instead of adding it. | Design |
| 9.8 | Hires avoided count only if the industry has job growth; reported against the hiring plan, separate from cash. Headline = plan NPV if the industry grows, else cash NPV. | Design |
| 9.9 | Discounting: monthly, at the annual discount rate, (1 + r)^(−month ÷ 12). | A |
| 9.10 | Payback = first month after the last month with negative cumulative cash. | Design |

---

## 10. Uncertainty and the decision

| # | Assumption | Value | Grade |
|---|---|---|---|
| 10.1 | Number of simulated futures | **1,000** | Design |
| 10.2 | Random seed (same answer every run) | **20261019** | Design |
| 10.3 | Distributions | percentages logit-normal, multipliers and months lognormal, centred on the scenario value with the P10–P90 ranges in section 2 | Design |
| 10.4 | Correlation | one shared "execution quality" factor, ρ = **0.5**: higher takeover, lower review, faster adoption and higher active use move together | Design |
| 10.5 | The plan (which workloads, when) is fixed before reality is drawn | — | Design |
| 10.6 | Break-even | net realisation at which cash NPV = 0, plan fixed (takeover varied, review held) | Design |
| 10.7 | Verdict thresholds | **Go** ≥ 70% chance of positive cash · **Pilot first** 40–70% · **Stop** < 40% · capacity case if nothing is harvested | experiment (value of a pilot gate) |
| 10.8 | Pilot pass mark / break-even to watch | net realisation ≥ the break-even (**14.3%** at the default) | derived |

---

## 11. Data assumptions

| # | Assumption | Grade |
|---|---|---|
| 11.1 | Hours come from Etter's **Tasks** sheet (420 tasks), not the Workloads sheet. The two split the same hours differently across categories; **which is authoritative is an open question for Etter** and the one structural item that could flip the verdict. | Design / open |
| 11.2 | Etter's role-level automation score is a second opinion only (flagged if it differs from the task build-up by more than 10 points); never mixed into the numbers. | Design |
| 11.3 | Senior Analysts' tasks cover 136 of 160 hours; the uncovered 24 hours are not counted. | Data |
| 11.4 | Workload names are matched after normalising (lower case, "&" → "and", extra spaces removed). | Design |
| 11.5 | If task hours are missing: fill from workload hours, else split 160 hours evenly, and flag (engine package). | Design |
| 11.6 | If only role scores exist: role-score mode = Etter automation/augmentation scores × category ceilings (engine package). | Design |
| 11.7 | Queue work (e.g. appointment desks): square-root staffing at 85% occupancy keeps a service buffer, so fewer positions free up (described in the deck's engine; not in this package or the Excel yet). | Design |

---

## 12. Weakest assumptions — replace first

| Rank | Assumption | Why it matters | How to fix |
|---|---|---|---|
| 1 | AI takeover 40% (C) | 2nd largest driver: −$0.1M to +$19.1M | Pilot |
| 2 | Human review 30% (C) | 3rd largest: +$12.0M to +$4.6M | Pilot |
| 3 | Custom running cost $3.48/h (D) | +$10.9M to +$4.3M across $1.50–$10 | Pilot invoices / vendor quotes |
| 4 | Vendor prices $15k / $35k and $6/h (D/C) | Build-or-buy adds about $2M; it depends on them | Vendor quotes |
| 5 | Complexity drag 0.30 (D) | Stand-in for "the remaining work is harder" | Etter task volumes or handling times |
| 6 | One takeover and review for every task and level (design) | Treats Coordinator and Director work alike | Vary by Etter category and role level |
| 7 | Tasks vs Workloads sheet (open) | Can flip the verdict | Etter to confirm |
| — | Harvest share 50% (Policy) | Largest driver | Leadership decision, not research |
| — | Agent ceilings 90% / 80% (set by Chandan) | Raise every result: at 85% / 55% the default was +$5.8M, 65%, pilot first | Validate against Etter's own task evidence or the pilot |
