# Etter Value Model: the model in detail

> **State of the model: 5 November 2026** (branch `nov5-batch`, with wage growth at 3.4% a year). Every number here is an exact output of the current engine at the default case unless it says otherwise. `tests/reference.json` still holds the earlier flat-pay headline ($9,376,169.02) until its owner updates it.

**Default case:** Etter FP&A data (11 roles, 1,523 people, 420 tasks), Moderate scenario, Attrition only policy, cross-industry economics, assistant tools on.

**Companion documents:** `Etter_Value_Model_how_it_works.md` (the short version; its figures are at flat pay) · `Etter_Value_Model_assumptions.md` (the parameter book: every input, range, grade and source) · `spec_delta_wage_growth.md` (the latest change, before and after) · `source_reconciliation.md` (site grades vs the source book).

**How to read this.** A business leader can read sections 1, 2, 10, 13 and 14. A finance reviewer should add 5, 7, 11, 12 and 16. Anyone checking the arithmetic needs sections 5–11, which give every formula as the code computes it.

## Contents

1. [What the model answers](#1-what-the-model-answers)
2. [The answer at the default](#2-the-answer-at-the-default)
3. [How the model is built](#3-how-the-model-is-built)
4. [Inputs](#4-inputs)
5. [Step 1: price an hour of work](#5-step-1-price-an-hour-of-work)
6. [Step 2: what AI could do](#6-step-2-what-ai-could-do)
7. [Step 3: workloads and the cost test](#7-step-3-workloads-and-the-cost-test)
8. [Step 4: programme size and schedule](#8-step-4-programme-size-and-schedule)
9. [Step 5: what AI actually frees, month by month](#9-step-5-what-ai-actually-frees-month-by-month)
10. [Step 6: where each freed hour goes](#10-step-6-where-each-freed-hour-goes)
11. [Step 7: money](#11-step-7-money)
12. [How sure we are](#12-how-sure-we-are)
13. [The decision](#13-the-decision)
14. [Scenarios, policies and other companies](#14-scenarios-policies-and-other-companies)
15. [Missing or odd data](#15-missing-or-odd-data)
16. [How we know it holds](#16-how-we-know-it-holds)
17. [How the model meets the brief](#17-how-the-model-meets-the-brief)
18. [Limits and open questions](#18-limits-and-open-questions)
19. [Where everything lives](#19-where-everything-lives)
20. [Glossary](#20-glossary)

---

## 1. What the model answers

> *If we put AI on this function, what changes, what is it worth, and should we go ahead?*

Etter breaks every role into workloads and tasks, and labels each task with a category that says how AI relates to it. It stops at percentages. This model turns those labels into money that a business leader can explain to a team and a finance function can reconcile to a cost centre.

**The model in three sentences** (the brief's test for "explainable"):

1. Etter says which tasks AI can do. The model keeps only the workloads where an agent, built or bought, costs less than the work it takes over, and counts only the share AI really takes over once people have checked its work.
2. That freed time becomes whole positions as people leave, hires a growth plan no longer needs, or capacity for other work. Every freed hour goes to exactly one of those places.
3. Cash, hires avoided and capacity are reported separately and never added together, along with the odds, a break-even and a ledger that traces every dollar to an input row.

**Three kinds of money, always kept apart:**

| | What it is | Why it is separate |
|---|---|---|
| **Cash vs today** | Salaries that stop being paid, seats reclaimed and recruiting avoided, minus every programme cost. | It leaves the cost base, and a budget owner can find it. |
| **Hires avoided vs plan** | Hires that a growth plan needed and no longer does. | It is a saving against a plan, not against today's payroll. Zero when the function isn't growing. |
| **Capacity at cost** | Freed time left over, valued at what that time costs. | Real value with no budget line. A controller discounts it heavily, and correctly, so it is never added to cash. |

---

## 2. The answer at the default

| Result | Default |
|---|---|
| **Cash vs today, 5-year NPV** | **+$11.55M** ($11,549,980.85), in today's money |
| Range: P10 / P50 / P90 of 1,000 draws | −$3.37M / +$6.86M / +$24.69M |
| Chance cash is positive | **79.2%** (about four in five) |
| Hires avoided vs plan | $0 (the FP&A default has no planned growth) |
| Capacity at cost, PV | **$52.29M**, never added to cash |
| Positions not refilled by month 60 | **59** (3.9% of 1,523), all reached by month 33 |
| Payback month | **31** |
| Peak funding needed | $4.41M |
| IRR | 63% a year (high because the outlay is small and early; NPV is the better guide) |
| Programme | 43 of 59 passing workloads: 33 bought, 10 built, $1.26M up front |
| Break-even net realisation | **13.0%**, against 28% assumed |
| Verdict | **GO: phased rollout** (it still starts with a pilot of 3 workloads) |

The middle of the 1,000 draws (P50, +$6.86M) is below the single run at the defaults. The model isn't linear in its inputs: positions round down, and costs and savings multiply, so the answer at the middle inputs isn't the middle answer.

---

## 3. How the model is built

The brief lists six approaches and asks which fits. The model uses four of them together, as the brief suggested, and borrows the activity-based-costing idea for one step.

| Approach (brief, section 3) | How the model uses it |
|---|---|
| Bottom-up task ledger | **The core.** Every dollar comes from a task's hours, a role's salary or a named cost line, and sits in a ledger with its source. |
| Policy scenario comparison | Three scenarios (how well AI works) × three policies (what leadership does with freed time). |
| Probabilistic simulation | 1,000 correlated draws for the range, odds and break-even. |
| Discounted cash flow | NPV, payback month, IRR and peak funding, monthly over 60 months. |
| Activity-based costing | The hourly rate is a time-driven activity-based-costing capacity cost rate (Kaplan & Anderson, *HBR*, 2004). Each saving is booked to the role, and so the cost centre, it comes from. |
| Top-down benchmark | Not used for the number. Etter's role-level score is kept only as a second opinion (section 15). |

**Properties.** Monthly, over 60 months, with month 0 = today. Deterministic: there's no AI call at run time, and the random draws use a fixed seed. Pure Python with no dependencies. The same equations are in `evm.py` (reference engine), `evm.js` (browser, line-for-line port) and `Etter_Value_Model_FPA.xlsx` (live formulas).

```
Etter tasks + roles
  → 1 price an hour of work
  → 2 AI-able hours per task (category ceilings)
  → 3 cost test per workload (build or buy)
  → 4 programme size (peak cash) and go-live schedule
  → 5 hours freed each month (takeover, review, ramp-up, drag)
  → 6 route each freed hour: positions / hires avoided / capacity
  → 7 money: three kinds, discounted, every dollar in the ledger
  → odds, break-even, sensitivity → verdict
```

---

## 4. Inputs

### Etter data (`data/etter_fpa.json`)

- **Tasks (420):** role, workload, task, category, and the hours one person in that role spends on it each month.
- **Roles (11):** headcount, average base salary, level (which sets the turnover band) and Etter's role-level automation score.

Base salary is a Draup estimate, which the Etter file calls indicative: not payroll and not fully loaded. Headcount is the client's own figure.

| Role | People | Base salary | Turnover band | Task hours / month | AI-able share of time | Etter role score |
|---|---|---|---|---|---|---|
| FP&A Senior Coordinator | 44 | $30,572 | Para-professional | 160 | 39.0% | 32.9% |
| FP&A Assistant Analyst | 185 | $51,532 | Professional | 160 | 38.0% | 41.0% |
| FP&A Associate Analyst | 371 | $58,896 | Professional | 160 | 34.0% | 33.4% |
| FP&A Analyst | 310 | $79,661 | Professional | 160 | 33.7% | 30.6% |
| FP&A Senior Analyst | 253 | $104,211 | Professional | **136** | 34.0% | 24.0% |
| FP&A Associate Manager | 140 | $138,408 | Management | 160 | 21.1% | 32.2% |
| FP&A Manager | 89 | $163,670 | Management | 160 | 18.5% | 26.1% |
| FP&A Senior Manager | 58 | $198,825 | Management | 160 | 27.0% | 13.0% |
| FP&A Director | 46 | $304,094 | Executive | 160 | 23.1% | 4.4% |
| FP&A Senior Director (Band B) | 17 | $381,174 | Executive | 160 | 20.1% | 9.7% |
| FP&A Senior Director (Band A) | 10 | $416,678 | Executive | 160 | 25.5% | 12.0% |
| **Total** | **1,523** | payroll $153.9M | | | | |

"AI-able share of time" is the model's own build-up from the tasks (section 6). The Etter role score is produced separately by Etter, which is why the two differ (section 15).

### The four choices a client makes

| Choice | Options | Default |
|---|---|---|
| Scenario: how well AI works | Conservative / Moderate / Aggressive | Moderate |
| Policy: what happens to freed time | Capacity only / Attrition only / Active reduction | Attrition only |
| Industry | Sets discount rate, staff turnover and job growth | Cross-industry |
| Assistant tools | On or off | On |

### The parameter pack (`packs/base.json`)

Every other number is in the pack. `packs/sources.json` says where each default comes from, using one of four statuses: `sourced` (public, citable), `client_supplied` (no credible public source; the client provides it), `judgment` (a modelling choice with a deliberately wide range) and `out_of_scope` (taken as given from Etter). A test fails if any pack key lacks a source entry. The parameter book (`Etter_Value_Model_assumptions.md`) lists every value with its range and grade.

---

## 5. Step 1: price an hour of work

```
loaded cost C      = base salary × on-cost (1.3055)
hourly rate        = C ÷ (12 × the role's task hours per month)
wage index w(m)    = (1 + 3.4%) ^ (m ÷ 12)          month 0 = today, so w(0) = 1
```

- **On-cost 1.3055** = 100 ÷ (68.5 + 8.1): wages and paid leave as shares of total compensation for full-time private-industry workers (BLS ECEC, Table 5). Paid leave is left out of the on-cost because an annual salary already pays for it. The headline ECEC multiplier, 1.4287 (June 2026, all private workers), applies to pay for hours worked; on a salary it would count leave twice.
- **Task hours.** Each role's tasks add up to 160 hours a month (1,920 a year), except the Senior Analyst at 136. The model divides by the hours actually recorded, so shares of time stay true. That's why a Senior Analyst hour costs $83.36.
- **Wage growth.** Pay grows 3.4% a year (BLS Employment Cost Index, 12 months to September 2026), compounded monthly. Salary and hourly rate are multiplied by the **same** index every month. If only one grew, an hour would be worth more when it becomes a position than when it stays as capacity, and the hour-for-hour reconciliation in step 6 would break.
- This rate is a time-driven activity-based-costing **capacity cost rate**: the cost of one hour of that role's working time.

*Example: FP&A Analyst.* $79,661 × 1.3055 = **$103,997** a year. ÷ (12 × 160) = **$54.17 an hour** today. By month 60 the same hour costs $54.17 × 1.182 = **$64.02**.

In the code: `prepare()` sets `R['C']` and `R['rate']` at today's pay; `simulate()` multiplies each salary-linked line by `w(m)` when it books it.

---

## 6. Step 2: what AI could do

Each task's Etter category sets the most AI could ever do with it (the ceiling) and what kind of help it is.

| Category | Ceiling | Kind | What happens |
|---|---|---|---|
| Directive | **90%** | Agent | An agent does the work instead of the person. |
| Feedback Loop | **80%** | Agent | An agent does the work, with feedback cycles. |
| Task Iteration | 45% | Assistant | The person does it; an assistant speeds them up. |
| Learning | 25% | Assistant | As above. |
| Validation | 50% | Assistant | The person checks and decides; an assistant prepares. |
| Negligibility | none | Human | Stays with people. No ceiling (removed from the pack on 5 Nov 2026; it was never used). |

```
AI-able hours per person (agent work)     = Σ over the role's Directive and Feedback Loop tasks:
                                              task hours × ceiling
assistant hours saved per person          = Σ over its Task Iteration, Learning and Validation tasks:
                                              task hours × min(ceiling, band saving)
```

**Band saving:** Para-professional 20%, Professional 12%, Management 6%, Executive 3% of the task's hours (Brynjolfsson, Li & Raymond: the biggest gains go to the least experienced). The highest band saving (20%) is below the lowest assistant ceiling (25%), so **the band rate always binds**, and the assistant ceilings don't move the answer.

**Where the ceilings come from.** The agent ceilings were set by Chandan (Draup) on 23 October 2026, raising Directive from 85% and Feedback Loop from 55%. The assistant ceilings are the lower of Etter's two ceilings for each category. They are inputs, not model choices: the brief puts the scoring engine out of scope.

**The ceiling conflict.** Etter's source workbook gives the per-category potential twice, and the two tables disagree on five of six categories (only Negligibility agrees). The pack matches neither. Only Directive and Feedback Loop move the answer: 90% matches Etter's Read me table, and **80% matches no table in the source**. Priced on the current engine, each reading sized to its own peak cash:

| Reading | Directive / Feedback Loop | Cash NPV | Workloads | Positions | Payback |
|---|---|---|---|---|---|
| Tasks column (shipped on all 420 rows) | 85% / 55% | $7.46M | 36 | 47 | 35 |
| **Pack, in use** | **90% / 80%** | **$11.55M** | **43** | **59** | **31** |
| Etter's Read me table | 90% / 85% | $11.94M | 41 | 60 | 31 |
| Bucket ceiling (AI 100%, Human + AI 50%) | 100% / 100% | $13.87M | 41 | 67 | 30 |

That is a 1.86x spread from an input the model doesn't control. It is open question 1 for Chandan (section 18). With the shipped 85% / 55%, the default comes out at 72% chance positive: still **go**, but only just over the 70% line.

*Example.* An Analyst's task "Extract and format financial data" is Directive, 8.64 hours a month per person. 8.64 × 310 Analysts × 90% = **2,410.6 AI-able hours a month** (28,927 a year). Across all their tasks, Analysts' AI-able share is 33.7% of their time.

Across the whole function, **563.7 people's worth** of work sits in agent categories, and **482.0** of it is AI-able once the ceilings apply.

---

## 7. Step 3: workloads and the cost test

Agents are set up **per workload**, one agent shared by every role that does that workload. The data has 60 workloads (after normalising names), and 59 of them contain agent tasks. Each workload has a tier: **enterprise** if two or more roles do it or it has three or more agent tasks, otherwise **workflow**.

Every workload is priced two ways, and the option with the higher five-year NPV is kept. Buy replaces build only if it is strictly better.

| | Build a custom agent | Buy a vendor agent |
|---|---|---|
| Up front | $55,000 (workflow) / $130,000 (enterprise) | $15,000 / $35,000 |
| Running | $3.48 per AI hour | $6.00 per AI hour |
| Upkeep | 18% of the build cost a year | included in the price |

```
work value / month     = Σ over roles: headcount × AI-able hours in this workload × hourly rate
freed value / month    = work value × net realisation          (takeover × (1 − review) = 40% × 70% = 28%)
AI hours / month       = AI-able hours (all roles) × takeover   (running cost is paid on these)
running / month        = AI hours × $ per AI hour
maintenance / month    = build cost × 18% ÷ 12                  (custom builds only)

NPV at cost            = freed value × 46.74 − (running + maintenance) × 42.55 − up-front cost
return per $ up front  = (freed value × 46.74 − (running + maintenance) × 42.55) ÷ up-front cost
```

- **42.55** is the sum over months 1–60 of the adoption ramp × the discount factor: the months of full value inside five years after a 3-month build lead and a 12-month S-curve ramp-up, discounted at 6.96%. **46.74** is the same sum weighted by the wage index, because the work taken over is paid at grown wages while running and maintenance are not.
- A workload **passes** if its best NPV at cost is above zero. At the default all 59 pass. Passing workloads are ranked by return per dollar up front.
- The test is deliberately simple. It ignores the 13% yearly fall in running cost, which makes it stricter. It also ignores the go-live waves, complexity drag and whole-position rounding, which make it looser. The sizing step deals with the second group.

*Examples:*

| Workload | Roles | AI-able hours / month | Work value / month | Build: NPV | Buy: NPV | Kept | Rank |
|---|---|---|---|---|---|---|---|
| Financial analysis and reporting | 5 (enterprise) | 19,722 | $1,016,529 | **$11.92M** ($130k up front, $27,454 running and $1,950 upkeep a month) | $11.26M ($35k up front, $47,334 running) | Build | 2 of 59 |
| Cost review planning and support | 1 (workflow) | 185 | $3,850 | −$50,687 | **+$16,473** | Buy | 59 of 59 |

The second one passes the test but doesn't make the programme (step 4).

In the code: `scope()`.

---

## 8. Step 4: programme size and schedule

**Size to peak cash.** Passing workloads join the programme in rank order. At each size the full 60-month model is run, and the programme stops at the size where five-year cash is highest. At the default that is **43 of 59** workloads (33 bought, 10 built; 5 enterprise and 38 workflow; $1.26M up front). Cash is $11.55M at 43 workloads, and $11.40M if all 59 went in.

**Why it stops before every passing workload is in.** The cost test values freed time at full cost, but cash counts only the time that becomes **whole positions** as people leave. Late, small workloads free fractions of people that never round up to a position. They also go live later, so they add cost but little cash. Under Capacity only, where nothing becomes a position, there is no cash to peak, so every passing workload is kept.

**Schedule:**

| | Go-live month | Workloads |
|---|---|---|
| Pilot: the top 3 | 3 | 3 |
| Evaluation | months 3–9 | — |
| Wave 1 | 12 | 10 |
| Wave 2 | 15 | 10 |
| Wave 3 | 18 | 10 |
| Wave 4 | 21 | 10 |

A wave goes live after the 6-month pilot evaluation plus another 3-month build lead, then every 3 months. Each workload's build or setup cost is spread evenly over the 3 months before it goes live. Custom-agent upkeep starts at go-live.

The Senior Coordinators have the highest AI-able share of any role (39%) but the lowest pay ($20.79 an hour). All eight of their agent workloads are theirs alone, and they rank 49–59, below the cut. So agents free none of their work, and only assistants help them. This answers a question the Etter file raises directly: what happens at the bottom of the ladder, where the automatable share is highest.

In the code: `size_to_peak()` and `schedule()`.

---

## 9. Step 5: what AI actually frees, month by month

For each role, each month m:

```
adoption a(m)            = S-curve from go-live: smoothstep((m − go-live) ÷ 12)     0 → 1 over 12 months
hours freed by agents    = Σ over built workloads: headcount × AI-able hours × takeover × (1 − review) × a(m)
AI hours                 = Σ over built workloads: headcount × AI-able hours × takeover × a(m)
running cost             = AI hours × $ per AI hour × (1 − 13%)^(m ÷ 12)

assistant seats          = headcount × active use (70%) × rollout(m)       S-curve from month 2 over 6 months
hours saved by assistants= seats × assistant hours saved per person × assistant multiplier (1.0)

drag factor              = 1 − 0.30 × (share of the role's total hours freed this month)
hours freed              = (agent hours + assistant hours) × drag factor
```

`smoothstep(x) = x² × (3 − 2x)`, clipped to 0 below 0 and 1 above 1.

- **Takeover (40%)** is the share of AI-able work the agent actually does. **Review (30%)** is the hours people spend checking per 100 AI hours. **Net realisation = 40% × (1 − 30%) = 28%** is the number the answer turns on, and the one a pilot measures. Running cost is paid on every AI hour, including the work people then check.
- **Cross-check on 28%.** In a live deployment to customer-support agents, agents followed the AI's recommendations about **35%** of the time on average (Brynjolfsson, Li & Raymond, *Generative AI at Work*, v2, PDF p. 23). That measures accepting an assistant's suggestions, not an agent taking over work, so it supports the size of 28%; it isn't a source for takeover.
- **Complexity drag (0.30)** stands in for "the work left behind is harder": the more of a role is freed, the more the freed time is trimmed. It is a single judgment parameter, graded D.

*Example (the Analyst task from step 2).* 28,927 AI-able hours a year × 40% = 11,571 AI hours → × 70% = 8,099 hours freed. At full adoption Analysts free 13.6% of their time in total, so the drag factor is 1 − 0.30 × 0.136 = 0.959. That leaves **7,769 hours a year, about 4.05 people's worth**, from this one task.

**Why AI-able hours are not headcount.** People's worth across the whole function at full adoption:

| Step | People's worth |
|---|---|
| Hours in agent categories | 563.7 |
| × ceilings: AI-able | 482.0 |
| In the 43 workloads in the programme | 462.9 |
| × 40% takeover | 185.2 |
| × 70% after review | 129.6 |
| After complexity drag | 124.6 |
| **Positions not refilled** (step 6) | **59** |

Assistants free another 52.3 people's worth, so **176.9 people's worth is freed in all**. 59 becomes positions and 117.9 stays as capacity.

In the code: the month loop in `simulate()`.

---

## 10. Step 6: where each freed hour goes

Freed time doesn't automatically become a smaller payroll. **Policy**, the company's choice, decides how much of it may become positions and how:

| | Capacity only | **Attrition only** (default) | Active reduction |
|---|---|---|---|
| Agent-freed time that may become positions | 0% | **50%** | 75% |
| Assistant-freed time that may become positions | 0% | **0%** | 25% |
| How positions go | nobody goes | as people leave, not refilled | separation after 2 months' notice, 12 weeks' severance |

Each role, each month:

```
freed people at full adoption   = agent people + assistant people, after drag
harvest                         = 50% × agent people + 0% × assistant people
target positions                = harvest, rounded down                      (whole positions, per role)
progress(m)                     = harvest this month ÷ harvest at full adoption
allowed(m)                      = target × progress(m), rounded down

leavers by month m              = headcount × (1 − (1 − yearly turnover)^(m ÷ 12))
positions(m), attrition only    = smaller of allowed(m) and leavers so far (rounded down)
positions(m), active reduction  = allowed(m), once the notice period has passed
then, both:                       never fewer than last month (a removed position doesn't come back)
                                  never more than the people actually freed this month

hires avoided(m)                = only if the function grows: smaller of spare freed people
                                  and planned new hires (headcount × ((1 + growth)^(m ÷ 12) − 1))
capacity hours(m)               = hours freed − positions × hours − hires avoided × hours
```

**Yearly turnover by band:** Para-professional 12.5%, Professional 9.1%, Management 6.3%, Executive 5.2%, times an industry multiplier (1.0 cross-industry).

**Every hour goes to exactly one place.** The model checks every month that hours freed = positions + hires avoided + capacity. The gap is zero, to machine precision.

**Role by role at the default:**

| Role | Freed people (agents + assistants) | Positions not refilled | Leavers over 5 years | Rule for hiring managers |
|---|---|---|---|---|
| Senior Coordinator | 0.0 + 2.5 | 0 | 21 | refill as usual |
| Assistant Analyst | 18.8 + 6.7 | 9 | 70 | leave 9 of the next 70 leavers unreplaced |
| Associate Analyst | 33.8 + 14.9 | 16 | 141 | leave 16 of the next 141 |
| Analyst | 28.1 + 12.4 | 14 | 118 | leave 14 of the next 118 |
| Senior Analyst | 23.1 + 9.8 | 11 | 96 | leave 11 of the next 96 |
| Associate Manager | 8.1 + 2.8 | 4 | 39 | leave 4 of the next 39 |
| Manager | 4.5 + 1.6 | 2 | 25 | leave 2 of the next 25 |
| Senior Manager | 4.3 + 1.0 | 2 | 16 | leave 2 of the next 16 |
| Director | 2.9 + 0.3 | 1 | 11 | leave 1 of the next 11 |
| Senior Director (Band B) | 0.8 + 0.1 | 0 | 4 | refill as usual |
| Senior Director (Band A) | 0.4 + 0.1 | 0 | 2 | refill as usual |
| **Total** | **124.6 + 52.3** | **59** | | |

*Example: Analysts.* Agents free 28.1 people's worth × 50% = 14.03, rounded down to **14 positions**. About 118 Analysts leave over five years anyway, so the rule is "leave 14 of the next 118 leavers unreplaced". Positions build up as the waves go live: 15 by month 12, 45 by month 24, and all **59 by month 33**.

Rounding down per role means a role needs roughly 20 to 40 people, depending on how much of it is AI-able, before agents free one whole position at 50% harvest. That is why small organisations struggle (section 14). At this scale attrition isn't the binding limit (leavers far outnumber targets), which is why staff turnover barely moves the answer.

In the code: the routing block in `simulate()`.

---

## 11. Step 7: money

Each line is booked every month to the role, workload or pack line it comes from. Cash lines are summed; capacity and hires avoided are kept separate.

| Line | Monthly formula | PV at default |
|---|---|---|
| **Cash savings** | | |
| Salaries no longer paid | positions × C × w(m) ÷ 12 | $21.07M |
| Recruiting avoided (attrition only) | each new position not refilled × $4,700 cost per hire | $0.25M |
| Software seats reclaimed | positions × $468 ÷ 12 | $0.08M |
| **Total savings** | | **$21.40M** |
| **Costs** | | |
| Training (once per person, in the month their role is first touched) | headcount × ($846 + 16.7 hours × hourly rate × w(m)) | $3.06M |
| AI running cost | AI hours × $3.48 (build) or $6 (buy) × (1 − 13%)^(m ÷ 12) | $2.69M |
| Assistant licences, at real adoption | active seats × $360 ÷ 12 | $1.48M |
| Build or buy, up front | spread over the 3 months before go-live | $1.17M |
| Programme | $75,000 fixed + $623 per affected person, in month 0 | $1.02M |
| Custom-agent upkeep | 18% of build cost a year, from go-live | $0.41M |
| Severance (active reduction only) | new separations × 12 weeks × salary × w(m) ÷ 52 | $0 |
| **Total costs** | | **$9.85M** |
| **Cash vs today** | savings − costs | **+$11.55M** |
| **Kept apart** | | |
| Hires avoided vs plan | hires avoided × C × w(m) ÷ 12 + each new hire avoided × $4,700 | $0 |
| Capacity at cost | capacity hours × hourly rate × w(m) | $52.29M |

The build, programme and running lines are multiplied by the scenario's cost multiplier (1.0 at Moderate), and so are licences and deployment. Assistant tools reach every role, so all 1,523 people are trained, in month 2 when the assistants arrive.

**Discounting.** Month m is multiplied by (1.0696)^(−m ÷ 12), the Damodaran January 2026 total-market WACC, nominal and after tax. Month 0 is not discounted. Cash flows are nominal (wages grow, running cost falls) and currently **pre-tax**; whether to tax them is open question 2.

**Other outputs:**
- **Payback month:** the first month cumulative cash turns non-negative and stays there. Month 31 at the default.
- **Peak funding:** the deepest point of cumulative cash, $4.41M.
- **Cash by year (nominal):** day 0 −$1.09M · year 1 −$3.32M · year 2 +$1.82M · year 3 +$5.14M · year 4 +$6.37M · year 5 +$6.74M.
- **Headline:** cash vs today. When the function is growing, it is cash plus hires avoided, measured against the hiring plan.
- **Capacity hurdle:** when the headline is negative, the share of capacity that must turn into real value for the programme to break even, = −headline ÷ capacity PV. Under Capacity only, with all 59 workloads, cash is −$10.15M against $74.35M of capacity: a hurdle of **13.7%**. The model states the hurdle instead of adding capacity to cash.
- **Assistant tools under attrition only** cost $1.85M of cash and add $23.79M of capacity, because none of the time they free becomes positions at the default.

**The ledger.** Every amount carries a source: `role: …`, `workload: …` or `pack: costs.programme_fixed`. PV of savings minus PV of costs equals the cash NPV, and the model checks the gap is zero.

---

## 12. How sure we are

### Scenarios

| Dial | Conservative | **Moderate** | Aggressive |
|---|---|---|---|
| AI takeover | 25% | **40%** | 60% |
| Human review | 40% | **30%** | 20% |
| Net realisation | 15% | **28%** | 48% |
| Months to full use | 18 | **12** | 6 |
| Assistant active use | 55% | **70%** | 85% |
| Assistant saving multiplier | 0.5 | **1.0** | 1.25 |
| Build and programme cost multiplier | 1.25 | **1.0** | 0.9 |

Complexity drag (0.30), the running-cost multiplier (1.0) and the turnover multiplier (1.0) are the same in all three scenarios; they vary only in the draws below.

### The draws

The plan is fixed first: which workloads, and when they go live. Reality is then drawn 1,000 times with a fixed seed (20261019), so the answer is identical on every run. Each uncertain input is drawn from a range fitted to its P10 and P90 and centred on the scenario's value: shares use a logit-normal distribution, everything else a log-normal.

| Input | P10 → P90 |
|---|---|
| AI takeover | 20% → 62% |
| Human review | 15% → 45% |
| Months to full use | 6 → 24 |
| Assistant active use | 50% → 85% |
| Assistant saving multiplier | ×0.4 → ×1.6 |
| Build and programme cost multiplier | ×0.85 → ×1.6 |
| Running-cost multiplier | ×0.43 → ×2.9 (about $1.50 → $10 an AI hour for custom agents) |
| Complexity drag | 0.10 → 0.55 |
| Turnover multiplier | ×0.75 → ×1.3 |

One shared **execution-quality** factor, with correlation 0.5, makes good programmes good at several things at once: higher takeover, lower review, faster adoption and more active use move together. The other inputs are drawn independently.

**Results at the default:** 79.2% of draws have positive cash. P10 −$3.37M, P50 +$6.86M, P90 +$24.69M. Capacity P10 $30.96M, P90 $83.57M.

**Break-even.** With the plan fixed and review held at 30%, the net realisation at which cash NPV is zero is **13.0%**, under half the 28% assumed. That is the pass mark for the pilot.

### What moves the answer most

One input at a time across its P10–P90 range, plan fixed:

| Input | Range | Cash NPV, low → high | Swing |
|---|---|---|---|
| Harvest share of agent time (a choice, not an estimate) | 25% → 75% | −$0.44M → +$24.09M | $24.52M |
| AI takeover | 20% → 62% | +$0.91M → +$22.67M | $21.76M |
| Human review | 15% → 45% | +$14.64M → +$6.27M | $8.37M |
| Running-cost multiplier | ×0.43 → ×2.9 | +$13.08M → +$6.44M | $6.65M |
| Months to full use | 6 → 24 | +$13.32M → +$8.17M | $5.15M |
| Build and programme cost multiplier | ×0.85 → ×1.6 | +$12.57M → +$7.48M | $5.09M |
| Complexity drag | 0.10 → 0.55 | +$11.78M → +$10.64M | $1.14M |
| Assistant active use | 50% → 85% | +$11.97M → +$10.90M | $1.07M |
| Assistant saving multiplier | ×0.4 → ×1.6 | +$11.80M → +$11.22M | $0.58M |
| Turnover multiplier | ×0.75 → ×1.3 | +$11.55M → +$11.55M | $0 |

**The three that matter** are harvest share, takeover and review, and a test enforces that they stay the top three. Wage growth isn't in the draws. Measured the same way (2.5% → 4.5%), it swings the answer by $1.31M, which would rank 7th.

In the code: `draw_scenario()`, `montecarlo()`, `breakeven_net()`, `sensitivity()`.

---

## 13. The decision

| Chance that cash is positive | Verdict |
|---|---|
| 70% or more | **Go:** phased rollout |
| 40% to 70% | **Pilot first**, and decide at the gate |
| Below 40%, and the policy turns no agent-freed time into positions | **Capacity case:** fund it only if leadership commits to using the released time |
| Below 40%, otherwise | **Stop** on cash grounds |

The thresholds come from the experiments (`experiments/exp_gate_scale.py`). A pilot gate pays when the call is close: the gated mean NPV is about zero near a 36% chance of success, and the gate stops paying near 70%.

**At the default:** 79.2% → **GO, phased rollout**. The rollout still starts with the top 3 workloads (live in month 3) and a 6-month evaluation before the waves. Takeover, checking time, adoption speed and real costs are measured first, and the number to watch is **13.0%** net realisation. Hiring managers get the per-role rule from section 10.

---

## 14. Scenarios, policies and other companies

### Same organisation, nine ways

Each combination is sized to its own peak cash. Each cell shows cash NPV · chance positive · verdict.

| | Capacity only | Attrition only | Active reduction |
|---|---|---|---|
| **Conservative** | −$9.80M · capacity case (hurdle 27.9%) | −$0.04M · 34.4% · **stop** | +$6.28M · 66.8% · pilot |
| **Moderate** | −$10.15M · capacity case (hurdle 13.7%) | **+$11.55M · 79.2% · go** | +$26.26M · 97.9% · go |
| **Aggressive** | −$11.41M · capacity case (hurdle 9.1%) | +$28.83M · 98.5% · go | +$55.65M · 100% · go |

Capacity only always loses cash, because it buys tools and keeps everyone. Its value is the capacity, and the hurdle says how much of that must be put to use for the programme to break even.

### Other companies (`packs/archetypes.json`)

The equations never change between companies, only the settings. An archetype scales the Etter FP&A data's headcount and salaries, and overrides the three industry settings: discount rate, staff turnover and job growth. Company size isn't a separate setting; it enters through headcount, and whole-position rounding does the rest.

| Archetype | People | Policy | Headline | Cash vs today | Chance positive | Verdict |
|---|---|---|---|---|---|---|
| Large software company (WACC 9.34%, growth 8%) | 1,523 | Attrition only | **+$56.28M** vs plan (116 hires avoided) | +$10.22M | 100% | go |
| Large insurer (6.34%, growth 2%) | 760 | Attrition only | +$18.90M vs plan | +$3.16M | 99.9% | go |
| Large hospital system, redeploy only (6.19%, growth 3%) | 305 | Capacity only | +$6.14M vs plan (32 hires avoided) | −$2.88M | 97.9% | go |
| **Mid-cap insurer** | **62** | Attrition only | **−$0.27M** | −$0.42M | **0%** | **stop** |
| Mid-cap software company, growing 15% | 123 | Attrition only | +$2.08M vs plan | −$0.54M | 94.2% | go |

- In growing industries the headline is measured **against the hiring plan**: freed time first fills planned hires, so the value is mostly hires not made. Cash vs today is still shown beside it.
- **The mid-cap insurer is the honest "do not start" case** the brief asks for. With about 6 people per role, agents free fractions of people that never round up to a position. Only 2 workloads make the cut, no position is ever removed, and the costs aren't recovered.
- Industry packs are settings applied to the FP&A data, not yet validated on other industries' own data. The Excel workbook carries seven industry packs (adding banking, retail and manufacturing).

---

## 15. Missing or odd data

Problems are flagged, never fatal; the brief asks for partial data to be a designed case.

| Situation | What the model does | Flag |
|---|---|---|
| Task for a role not in the roles list | Ignores the task | error |
| Unknown category | Treats the task as human | warning |
| Headcount or salary missing | The role carries no money | warning |
| A role has no task hours | Uses 160 hours | warning |
| A role's tasks don't sum to 160 (more than 5% off) | Takes shares of the hours recorded | info (Senior Analyst: 136) |
| Task build-up and Etter role score differ by more than 10 points | Builds on the tasks; keeps the score as a second opinion | info (5 roles) |

The score-gap notes are information, not warnings. Etter's own file says its role score and the task hours are produced independently and will not match, and advises building on task hours.

**Role-score mode.** `prepare(…, basis='role_score')` scales each role's AI-able hours to Etter's role score, for when task detail is missing. The default reports don't use it.

---

## 16. How we know it holds

**Automated tests** (`python3 -m unittest discover tests`), 27 in all:

| Group | Tests | What they prove |
|---|---|---|
| Brief acceptance criteria | 5 | Every currency line resolves to an input row; freed hours reconcile across the destinations (exactly, not just within 1%); zero headcount conversion still gives a meaningful answer (capacity and a hurdle); the three most sensitive parameters are named; one archetype says do not start. |
| Invariants | 13 | Deterministic; the random-number vector matches the browser's; positions never exceed freed time and never come back; more takeover never lowers cash; more harvest gives more positions; cash and capacity stay separate; missing data is flagged, not fatal; no build means no build cost; the peak-cash size beats every other size; Capacity only keeps every passing workload; build or buy keeps the cheaper option; the earlier engine is reproduced to the cent; the reference numbers. |
| Source book | 4 | Every pack key has a source entry; statuses are valid; "sourced" entries cite something; judgment parameters aren't dressed up as sourced. |
| Ceiling readings | 5 | The four readings of Etter's ceilings, each locked at its NPV, plus a guard that the pack row matches the pack. |

**Right now 22 pass and 5 fail by design.** The wage-growth change moved the golden numbers in `tests/reference.json` and the four ceiling-set locks, and their owner updates those deliberately.

**Other checks:**
- **Browser parity:** `evm.js` matches `evm.py` on six cases across scenarios, policies and archetypes, to a relative difference of about 4×10⁻¹⁶ (`tests/parity.py`).
- **Excel:** `Etter_Value_Model_FPA.xlsx` reproduces the headline to the cent with live formulas, and its 20 checks all pass. They tie to the Etter file (tasks, headcount, payroll, hours), reconcile every freed hour every month, keep positions whole and capacity non-negative, close the ledger, and match the reference engine. It also matches the engine to the cent in four other scenario/policy cases and for all four ceiling readings.
- **Determinism:** same inputs, same outputs, every time.

---

## 17. How the model meets the brief

### Functional requirements

| Brief | How the model does it | Status |
|---|---|---|
| FR1 Ingest and join | Joins Etter tasks to roles, headcount, salary, seat cost and licence cost; partial data is flagged, not fatal. | Met |
| FR2 Scores to hours | Category ceilings turn each task into AI-able hours (agents) or hours saved (assistants), per role. | Met |
| FR3 Hours to capacity | Divides by each role's recorded task hours (160, or 136 for Senior Analysts). | **Partly:** the brief asks for productive hours per level; the model uses one 160-hour convention. Known gap. |
| FR4 Apply policy | Routes every freed hour to positions not refilled, hires avoided, or capacity; policy sets the split. | Met. Capacity covers both redeployment and extra output; "review cadence" is the pilot gate and wave schedule, not a separate input. |
| FR5 Savings | Salaries of positions not refilled, seats reclaimed, recruiting avoided, and capacity at cost, reported separately. | Met |
| FR6 Investment | Licences at active use (70% of seats), training, programme and deployment, build or buy, running, upkeep, and severance where policy allows. | Met |
| FR7 Phasing | Month by month over 60 months: costs before savings, S-curve adoption, waves. | Met |
| FR8 Financial outputs | Net cash, payback month, IRR, NPV. | **Partly:** NPV comes as a range (P10/P50/P90); payback and IRR are single values at the default. |
| FR9 Compare scenarios | Three scenarios × three policies, side by side. | Met |
| FR10 Rank sensitivity | One-at-a-time P10–P90 swings, ranked. | Met |
| FR11 Two views | The site has Leader and Finance tabs from the same run (plus Plan and Audit). | Met |

### How the model must behave

| Brief | How |
|---|---|
| Deterministic | No AI call at run time; seeded random draws; a test checks it. |
| Reproducible | The Excel workbook reproduces the headline to the cent in live formulas. |
| Auditable | Every dollar sits in the ledger with its role, workload or pack-line source. Industry packs change only discount rate, turnover and job growth: the first two are sourced (Damodaran, BLS JOLTS), and growth is a client input. Cost inputs without a public source are declared `client_supplied` or `judgment`. |
| Explainable | The three sentences in section 1. |
| Portable | A new company is a new pack or archetype, not new code. |
| Adjustable | Every assumption is in the pack with a default and range; on the site, every register line is editable. |
| Honest | Bands, not points; and an archetype that says stop. |

### Acceptance criteria

All five are automated tests, and all five pass.

---

## 18. Limits and open questions

**Limits, stated plainly:**

1. **The ceilings are the biggest input the model doesn't control:** a 1.86x spread across Etter's own readings (section 6).
2. **One takeover and one review rate for every task and level.** Two studies (Dell'Acqua et al.; Brynjolfsson et al.) show unreviewed AI output costs more at senior levels. The fix is structural (review that rises with level), not a new parameter.
3. **Complexity drag is a single judgment parameter** (0.30, grade D). A real difficulty curve needs task volumes or handling times from Etter.
4. **Running cost and vendor prices have thin evidence**, and much of the build-or-buy gain depends on them.
5. **A flat 160-hour month** (FR3 asks for productive hours per level).
6. **The odds depend on the ranges chosen.** Quote them as "about four in five", not 79.2%.
7. **Etter's Tasks and Workloads sheets disagree on the category split.** The model uses Tasks; this could flip the verdict.
8. **Industry packs are settings on FP&A data**, not validated on other industries' own data.
9. **Wage growth isn't in the uncertainty draws**, and payback and IRR aren't reported as ranges.

**Open questions for Chandan:**

1. **Ceilings.** What do the 90% and 80% rest on, so they can go in the parameter book with a reason? (80% matches no table in Etter's workbook.)
2. **Tax.** Should cash flows be after tax, to match the after-tax discount rate? Taxing them at Damodaran's 8.3% effective rate would trim the headline by roughly that share.
3. **Residual value.** Should month 61 carry any value? Positions not refilled keep saving after month 60, and the model currently counts nothing then.

---

## 19. Where everything lives

| Step | Python (`evm.py`) | Excel (`docs/Etter_Value_Model_FPA.xlsx`) |
|---|---|---|
| 1–2 Price hours, potential | `prepare()` | Roles, Tasks |
| 3 Cost test, build or buy | `scope()` | Workloads |
| 4 Size and schedule | `size_to_peak()`, `schedule()` | Sizing (static engine sweep), Workloads go-live columns, Inputs row 9 |
| 5–7 Month by month, routing, money | `simulate()` | Timeline, Summary |
| Odds, break-even, sensitivity | `montecarlo()`, `breakeven_net()`, `sensitivity()` | Risk (static engine values) |
| Verdict | `decide()` | Risk |
| Checks | inside `simulate()`; `tests/` | Checks |
| Everything for the pages | `report()` | Summary |

- **Run it:** `python3 run.py` (FP&A, Moderate, Attrition only) or `python3 run.py insurance_mid`. It prints the headline and writes a report JSON and a ledger CSV to `out/`.
- **Other companies:** `archetype.py` and `packs/archetypes.json`.
- **Browser:** `evm.js` (the port), `site/app.js` (the pages), `python3 site/build.py` builds `site/etter_value_model.html`, with Leader, Finance, Plan and Audit tabs.
- **Inputs and sources:** `packs/base.json`, `packs/sources.json`, `data/etter_fpa.json`.
- **Working rules for anyone changing the model:** `CLAUDE.md`.

---

## 20. Glossary

| Term | Meaning |
|---|---|
| **Agent** | AI that does a task instead of the person (Directive, Feedback Loop). |
| **Assistant** | AI that makes a person faster at a task they still do (Task Iteration, Learning, Validation). |
| **Ceiling** | The most AI could ever do with a category of work. A limit, not a saving. |
| **AI-able hours** | Task hours × ceiling, for agent categories. |
| **Takeover** | The share of AI-able work an agent actually does (40%). |
| **Review** | Hours people spend checking per 100 AI hours (30%). |
| **Net realisation** | Takeover × (1 − review): the share of AI-able work that really comes off people's plates (28%). |
| **Complexity drag** | The trim on freed time because the work left behind is harder. |
| **People's worth (FTE)** | Hours divided by one person's monthly hours. |
| **Workload** | A group of tasks one agent covers, shared across the roles that do it. |
| **Cost test** | A workload passes if its agent costs less than the work it takes over, over five years. |
| **Peak-cash sizing** | Adding workloads in rank order and stopping where five-year cash is highest. |
| **Harvest share** | The share of freed time that policy allows to become positions. |
| **Position not refilled** | A leaver who isn't replaced (attrition) or a separation (active reduction). Always whole. |
| **Hires avoided** | Planned new hires no longer needed because freed time covers them. |
| **Capacity at cost** | Freed time left over, valued at its hourly cost. Never cash. |
| **Capacity hurdle** | When cash is negative: the share of capacity that must become real value to break even. |
| **Wage index** | (1 + 3.4%)^(m ÷ 12): how much more an hour costs in month m than today. |
| **P10 / P50 / P90** | The results that 10%, 50% and 90% of the 1,000 draws fall below. |
| **Break-even net realisation** | The net realisation at which cash NPV is zero, with the plan fixed. The pilot's pass mark. |
| **Headline** | Cash vs today, or against the hiring plan when the function is growing. |
| **Ledger** | Every amount, by line, with the role, workload or pack line it came from. |
