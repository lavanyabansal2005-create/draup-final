# Etter Value Model — final list of assumptions

**Version:** final model, 23 October 2026, with the agent ceilings set by Chandan in the review meeting (Directive 90%, Feedback Loop 80%); updated 5 November 2026 with the finance-review fixes, wage growth and review by seniority (`Etter_Value_Model_spec_delta_review.md`) · **Default case:** Etter FP&A data (11 roles, 1,523 people, 420 tasks), Moderate scenario, Attrition only policy, cross-industry defaults, assistant tools on.
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
| 1.5 | Programme size (number of workloads) | **Peak-cash size** (35 at the default) | any number; 0 = all that pass | Optional override. Peak-cash sizes by case are in section 8. |

---

## 2. Scenario dials — the uncertain quantities

| # | Assumption | Conservative | **Moderate** | Aggressive | Range used for odds (P10–P90) | Grade | Pilot? | Basis |
|---|---|---|---|---|---|---|---|---|
| 2.1 | **AI takeover**: share of AI-able work the agent actually does | 25% | **40%** | 60% | 20–62% | C | ✔ | Indirect: finance AI deployments report low-to-moderate impact (Gartner, May 2026); accounts payable, the most automated finance process, averages ~33% touchless (Ardent Partners 2025). |
| 2.2 | **Human review**: hours people spend checking per 100 AI hours, at the Professional band | 40% | **30%** | 20% | 15–45% | C | ✔ | Estimate; measured in the pilot as checking time per AI hour. |
| 2.2a | **Review rise per band of seniority**: review × (1 + this × (band rank − 1)) | 20% | **20%** | 20% | 5–40% | **D** | ✔ | Judgment on magnitude; direction from Brynjolfsson et al. v2 (quality declines for the most skilled) and Dell'Acqua et al. (19 points less accurate outside the frontier). Gives 24 / 30 / 36 / 42% by band. Moves cash +$7.0M → +$5.5M across its range, mostly through which workloads pass the cost test. |
| 2.3 | **Net realisation** = takeover × (1 − review) | 15% | **28%** | 48% | — | derived | ✔ | The single number the answer turns on, measured at the Professional band. Break-even at the default: **19.2%**. |
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

Harvest share is the largest single driver: −$4.8M at 25% to +$18.4M at 75% (default case).

---

## 4. People, pay and time

| # | Assumption | Value | Grade | Source / basis |
|---|---|---|---|---|
| 4.1 | On-cost multiplier (loaded cost = salary × this) | **1.3055** | A | BLS Employer Costs for Employee Compensation, **Table 5, full-time private industry**: wages 68.5%, paid leave 8.1% of compensation; 100 ÷ (68.5 + 8.1). Paid leave is added back because the hours below are working hours. |
| 4.1a | **Wage growth** (salaries, capacity, avoided hires, severance and training hours grow with it; the cost test stays at today's prices) | **3.4% a year** | A | BLS Employment Cost Index, private industry compensation, 12 months to September 2026. Range 2.5–4.5%: cash +$6.5M → +$7.6M. |
| 4.2 | Working hours | **160 a month (1,920 a year)** | A | Etter file convention. If a role's tasks sum to a different total (Senior Analyst: 136), shares are taken of the hours recorded. |
| 4.3 | Hourly rate | loaded cost ÷ (12 × task hours a month) | derived | Time-driven activity-based costing. Example: Analyst $54.17/h. |
| 4.4 | Assistant time saving by band | Para-professional **20%**, Professional **12%**, Management **6%**, Executive **3%** | B | Brynjolfsson, Li and Raymond, *Generative AI at Work*, QJE 2025 (largest gains for less experienced workers). Applied as the smaller of this and the category ceiling. |
| 4.5 | Yearly turnover by band | Para-professional **12.5%**, Professional **9.1%**, Management **6.3%**, Executive **5.2%** | B | Mercer 2025 US turnover survey; × industry multiplier (section 6). |
| 4.6 | Role level → turnover band | Etter level mapped to band (e.g. Individual Contributor → Professional; Clerk → Para-professional) | Design | Turnover band given per role in the data. |
| 4.7 | Cost per hire (saved when a leaver is not replaced, or a planned hire is avoided) | **$4,700** | B | SHRM cost-per-hire benchmark. |
| 4.8 | Equipment and software per position (saved when not refilled) | **$468 a year** | C | Estimate. |

---

## 5. What AI could do (Etter categories)

| # | Etter category | Most AI could do (ceiling) | Kind | Grade |
|---|---|---|---|---|
| 5.1 | Directive | **90%** | Agent (does the work; can become positions) | Chandan (Draup), 23 Oct 2026 |
| 5.2 | Feedback Loop | **80%** | Agent | Chandan (Draup), 23 Oct 2026 |
| 5.3 | Task Iteration | **45%** | Assistant (person goes faster; capacity by default) | Team / Etter |
| 5.4 | Learning | **25%** | Assistant | Team / Etter |
| 5.5 | Validation | **50%** | Assistant | Team / Etter |
| 5.6 | Negligibility | **0%** | Human only | Team / Etter |

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
| Negligibility | 0.10 | 0.10 | 0.00 | **0.00** |

The Tasks column is the data shipped on all 420 rows, and the How to use it sheet says it is the full resolution of that column. The Read me table appears nowhere else in the file.

#### Which reading we use, and where it came from

- **Agent categories (Directive, Feedback Loop): 0.90 / 0.80.** Set by Chandan on 23 Oct 2026, overriding the shipped 0.85 / 0.55 (recorded on the value-model workbook's Inputs sheet and in its Read me, item 10). `experiments/legacy/engine_v2.py` line 11 shows the earlier engine used the shipped column, which dates the change. 0.90 matches the Read me table. **0.80 matches no table in the source.**
- **Assistant categories: the lower of the bucket ceiling and the Tasks column.** That gives 0.45 / 0.25 / 0.50.
- **Negligibility: 0.00**, the bucket ceiling. Both Etter tables say 0.10. This is dead config: Negligibility maps to Human, so the value is never read.

#### Why only two of the six move the headline

Assistant savings are the smaller of the category ceiling and the band rate, and the highest band rate is 0.20. Every assistant ceiling in every reading is at least 0.25, so it never binds. Checked: putting the Read me or bucket values on the assistant categories leaves the headline at exactly $9,376,169.02. **The whole spread comes from Directive and Feedback Loop.**

#### Priced impact (5-year cash NPV, Moderate, attrition only)

| Reading | Directive / Feedback Loop | Cash NPV | vs pack | Workloads in programme | Positions at month 60 | Payback month |
|---|---|---|---|---|---|---|
| Tasks column (shipped data) | 0.85 / 0.55 | $3,438,343 | −$3.59M (−51%) | 48 | 47 | 43 |
| **Pack (in use)** | **0.90 / 0.80** | **$7,023,655** | — | **35** | **56** | **36** |
| Read me table | 0.90 / 0.85 | $7,228,907 | +$0.21M (+3%) | 35 | 57 | 36 |
| Bucket ceiling | 1.00 / 1.00 | $10,645,163 | +$3.62M (+52%) | 35 | 66 | 32 |

Repriced after the finance-review fixes, wage growth and review by seniority (payback undiscounted; before any of them the four readings were $5.80M / $9.38M / $9.75M / $11.48M). High to low is a 3.1x spread on the headline, from an input the brief puts out of scope. The ceilings are not among the uncertainty draws, so the P10–P90 band (−$4.8M to +$20.7M) assumes the pack reading is correct. It does not cover this question.

These four figures are locked in by `tests/test_ceiling_sets.py`. Changing the ceilings, or anything that moves their price, fails that test.

#### Reproducing this in the workbook

`docs/Etter_Value_Model_FPA.xlsx` reproduces the pack reading to the cent. Programme size (Inputs B9) is the peak-cash size for the **default** ceilings (35 workloads), copied from the engine. To match the engine on the other three readings, set the override (Inputs B8) to their peak sizes, 48, 35 and 35.

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
| 7.13 | Training per person in every touched role | **$846 + 16.7 hours** of the person's own time, for everyone at first use and for **every joiner** who replaces a leaver | — | B | — | ATD 2026 State of the Industry. Not scaled by the cost multiplier. Joiners = leavers − positions not refilled that month (all leavers under active reduction). |
| 7.14 | Assistant licence | **$360 per seat a year** | — | A | — | Microsoft list price (unchanged since 2023). |
| 7.15 | Assistant seats | **people in post** × active use, ramped in; trued down only at each contract anniversary (contract year k priced on positions at month 12k) | — | derived | ✔ | Annual seat commitments are reduced at renewal. Assistant time saved still uses the full headcount: the work does not shrink when positions go. |
| 7.16 | Training refresher | **25% of the initial package a year** (about 4 hours and $212 per person), for people in post, from 12 months after first use | 10–50% | **D** | ✔ | Judgment; no measured rate. BCG *AI at Work 2025*: 79% of people with 5+ hours of training are regular users vs 67% with less. Ranks 7th of 13 in the tornado (+$8.5M → +$4.5M). |

---

## 8. Programme design and timing

| # | Assumption | Value | Grade | Notes |
|---|---|---|---|---|
| 8.1 | One agent per Etter workload, shared by every role that does it | — | Design | 59 workloads contain agent tasks. |
| 8.2 | Build or buy | **the option with the higher 5-year NPV at cost** (buy only if strictly better) | Design | Default: 25 buy, 10 build. |
| 8.3 | Cost test | workload passes if (freed value − running − maintenance) × annuity − up front > 0, freed value = work value × net realisation | Design | Policy-independent: "is the AI cheaper than the work?" |
| 8.4 | Annuity factor (months of full value in five years) | **42.5** | derived | After 3-month build, S-curve ramp, 6.96% discounting. |
| 8.5 | Ranking | **return per $ up front** | Design | — |
| 8.6 | Programme size | **stop where 5-year cash NPV peaks** | Design | Moderate: Attrition 35 · Active 39 · Capacity all (59). Conservative: 42 · 28 · 56. Aggressive: 41 · 57 · 59. |
| 8.7 | Pilot | **top 3 workloads**, live in month 3 | Design | — |
| 8.8 | Pilot evaluation before further builds | **6 months** | Design | — |
| 8.9 | Waves after the pilot | **10 workloads every 3 months** (go-live months 12, 15, 18 and 21 at the default) | Design | — |
| 8.10 | Adoption curve | **S-curve** from each go-live; the same curve in the cost test, running cost and savings | Design | — |
| 8.11 | Assistant rollout | starts **month 2**, full after **6 months** (S-curve) | Design | — |
| 8.12 | Horizon | **60 months** (5 years), month 0 = today | Design | Fixed; the cost test uses the same window. |

---

## 9. Turning freed time into money (structural assumptions)

| # | Assumption | Grade |
|---|---|---|
| 9.1 | **Every freed hour goes to exactly one place**: positions not refilled, hires avoided, capacity, or stranded slivers. Checked every month: largest gap 0.00000 hours, exact. | Design |
| 9.2 | **Positions are whole numbers, rounded down per role.** (Pooling across a level is described in the deck's engine as an option, off by default; not in this package yet.) | Design |
| 9.3 | Under attrition only, **a position goes only when someone leaves on their own**: positions ≤ people who have left so far = headcount × (1 − (1 − yearly rate)^(months ÷ 12)). | Design |
| 9.4 | Positions follow programme progress (target × share of steady-state freed time reached), do not bounce back while the AI runs, and **never exceed the time actually freed**. If the AI is switched off (a stopped programme), the work comes back and the positions are refilled at the cost per hire. | Design |
| 9.5 | Assistant time is not turned into positions under attrition only (minutes scattered across many people). | Policy |
| 9.6 | **Cash, hires avoided and capacity are never added together.** | Design |
| 9.7 | Capacity is valued at the hourly rate (at cost) and is real only if used; when cash is negative the model reports a **capacity hurdle** (share that must become real value to break even) instead of adding it. | Design |
| 9.7a | **Smallest redeployable block: 5% of a person's month** (8 hours at 160, about 24 minutes a day). Leftover freed time per person in post below this is stranded and valued at zero; only time above it is capacity. Range 0–10%: capacity is $50.7M at 0, $14.5M at 5% and $0 at 10% on this data, because freed time is spread evenly across each role. Forrester TEI uses a flat 50% recapture instead, which is its house assumption. | **D** (judgment) |
| 9.8 | Hires avoided count only if the industry has job growth; reported against the hiring plan, separate from cash. Headline = plan NPV if the industry grows, else cash NPV. | Design |
| 9.9 | Discounting: monthly, at the annual discount rate, (1 + r)^(−month ÷ 12). | A |
| 9.10 | Payback = first month after the last month with negative cumulative cash. Reported twice: **discounted** (cumulative discounted cash, the NPV's convention; 38 at the default) and **undiscounted** (36). | Design |

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
| 10.8 | Pilot pass mark / break-even to watch | net realisation ≥ the break-even (**19.2%** at the default) | derived |
| 10.9 | **Pilot gate in the odds** | each simulated future stops at month 9 (build lead + evaluation) if its net realisation is below the pass mark: AI off, work back, positions refilled, recurring costs end, money spent stays spent. 28% of futures stop at the default, at −$4.4M each. Only when cash is the case (harvest > 0). Measurement at the gate taken as exact (optimistic). | Design |

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
| 1 | AI takeover 40% (C) | 2nd largest driver: −$3.5M to +$17.2M | Pilot |
| 2 | Human review 30% (C) | 3rd largest: +$11.6M to +$1.6M | Pilot |
| 3 | Custom running cost $3.48/h (D) | +$8.5M to +$2.0M across $1.50–$10 | Pilot invoices / vendor quotes |
| 3a | Training refresher 25% a year (D) | +$8.5M to +$4.5M across 10–50% | Training records from the pilot |
| 3b | Smallest redeployable block 5% (D) | Capacity $50.7M at 0 to $0 at 10%; never touches cash | Time studies in the pilot: where the freed time went |
| 3c | Review rise with seniority 20% a band (D) | +$7.0M to +$5.5M across 5–40% | Pilot: checking time per AI hour, by level |
| 4 | Vendor prices $15k / $35k and $6/h (D/C) | Build-or-buy adds about $2M; it depends on them | Vendor quotes |
| 5 | Complexity drag 0.30 (D) | Stand-in for "the remaining work is harder" | Etter task volumes or handling times |
| 6 | One takeover and review for every task and level (design) | Treats Coordinator and Director work alike | Vary by Etter category and role level |
| 7 | Tasks vs Workloads sheet (open) | Can flip the verdict | Etter to confirm |
| — | Harvest share 50% (Policy) | Largest driver | Leadership decision, not research |
| — | Agent ceilings 90% / 80% (set by Chandan) | Raise every result: at 85% / 55% the default is +$3.4M on this engine | Validate against Etter's own task evidence or the pilot |
