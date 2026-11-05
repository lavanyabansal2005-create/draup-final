# Spec delta: wage growth (`economics.wage_growth`)

**Date:** 5 Nov 2026 · **Status:** implemented in `evm.py` and `evm.js`, and in `docs/Etter_Value_Model_FPA.xlsx`. **Moves the headline**; `tests/reference.json` is deliberately left for the owner to update.

## The problem

Salaries are held flat for 60 months, but the discount rate (Damodaran WACC, 6.96%) is nominal and the AI running cost falls 13% a year. Costs move with time; the savings they are set against don't. That asymmetry understates every salary-linked line, and it is the first thing a controller who checks the timeline will notice.

## The input

| Key | Value | P10 | P90 | Source |
|---|---|---|---|---|
| `economics.wage_growth` | **3.4%** a year | 2.5% | 4.5% | BLS Employment Cost Index, private industry workers, compensation, 12 months to September 2026 (not seasonally adjusted). `sources.json` → `economics.wage_growth`. |

It is nominal, to match the nominal discount rate. P10 and P90 are recorded in the source book. They are **not** in the uncertainty draws (`uncertainty.params`), so the odds and the sensitivity table don't vary it; see "Earning its place" below.

## The rule

One wage index per month, the same for every role:

```
w(m) = (1 + wage_growth) ^ (m / 12)        month 0 = today's pay, w(0) = 1
```

This is the same convention as the running-cost decline, `(1 − decline) ^ (m / 12)`: smooth monthly compounding, not an annual step.

**Escalates by w(m)** (everything priced off a person's pay):

| Line | Before | After |
|---|---|---|
| Positions not refilled (`hard`) | positions × C / 12 | positions × C × w(m) / 12 |
| Hires avoided against plan (`avoidance`, salary part) | hires × C / 12 | hires × C × w(m) / 12 |
| Capacity at cost (`capacity`) | hours × rate | hours × rate × w(m) |
| Severance | separations × weeks × S / 52 | separations × weeks × S × w(m) / 52 |
| Training, time part | N × hours × rate | N × hours × rate × w(m) |
| Cost test, value of work taken over (`scope`) | benefit × annuity | benefit × wage-weighted annuity |

**Stays flat** (not pay): cost per hire, software seats, assistant licences, the training spend per person, build, buy, programme, deployment and maintenance costs. Running cost keeps its own decline. Cost per hire is largely recruiter time and arguably wage-linked; holding it flat understates savings slightly. That is deliberate, and conservative.

Reported `payroll` and each role's `loaded` cost stay at today's pay (month 0). They describe the function as it is now.

## Does `R['rate']` escalate alongside `R['C']`? Yes, by the same index, every month.

`R['rate']` is defined as `R['C'] / (12 × R['H'])`: the loaded cost of one task-hour. Task hours don't change over time, so if the salary grows, the cost of an hour grows by exactly the same factor. Escalating one and not the other breaks the model in a way a controller will find:

- **Rate escalates, C doesn't:** capacity at cost grows each year while the salary behind it stays flat. Capacity would be valued at a pay level nobody is paid.
- **C escalates, rate doesn't:** the cash from a position grows but the same person's hour, released as capacity, is still valued at today's pay. An hour would be worth more when it becomes a position than when it stays as capacity.

The second case breaks the model's core rule: every freed hour goes to exactly one place (a position, an avoided hire or capacity), and its value can't depend on where it lands. With one index on both, `rate = C / (12 H)` holds in every month, and so does the hour-for-hour reconciliation.

Implementation: `R['C']` and `R['rate']` stay as today's values in `prepare()`. `simulate()` multiplies each salary-linked line by `w(m)` when it books it, so no stored value changes meaning.

## Why the cost test changes too

The cost test asks whether an agent costs less than the work it takes over. If the simulation pays grown salaries but the test values the work at today's pay, a workload can fail the test even though the simulation would show it pays. So the value of work taken over is now discounted with a wage-weighted annuity, while running and maintenance keep the existing annuity:

```
annuity     = Σ ramp(m) × df(m)            (unchanged)
annuity_w   = Σ ramp(m) × df(m) × w(m)     (new)
NPV at cost = benefit × annuity_w − (running + maintenance) × annuity − up front
```

Workload ranking (return per dollar up front) uses the same split, so the order in which workloads join the programme can change.

## Earning its place (CLAUDE.md rule 6)

`sensitivity()` only swings the uncertainty draws and the harvest share, so `wage_growth` doesn't appear in it. Measured the same way (one at a time, plan fixed at the default), its P10–P90 swing is **$1.31M** (2.5% → $10.97M, 4.5% → $12.28M). That ranks **7th of 11**, just above complexity drag ($1.14M), so it is inside the top ten. The top three are unchanged: harvest share, takeover, review. It is not added to the uncertainty draws, which would change every seeded draw; that is a separate decision.

## Result at the default (Moderate, attrition only, cross-industry)

| | Before (flat pay) | After (3.4% a year) |
|---|---|---|
| Cash vs today, 5-year NPV | $9,376,169.02 | **$11,549,980.85** |
| Payback month | 33 | **31** |
| Workloads in the programme (peak cash) | 45 (35 buy / 10 build) | 43 (33 buy / 10 build) |
| Positions not refilled at month 60 | 59 | 59 |
| Capacity at cost, PV | $47.69M | $52.29M |
| Peak funding needed | $4.41M | $4.41M |
| Chance cash is positive (1,000 draws) | 75.1% | 79.2% |
| P10 / P50 / P90 | −$4.20M / $5.11M / $21.16M | −$3.37M / $6.86M / $24.69M |
| Break-even net realisation | 14.3% | 13.0% |
| Verdict | GO: phased rollout | GO: phased rollout |

With `wage_growth` set to 0 the engine reproduces $9,376,169.02 exactly, so every difference above comes from this change. The programme gets two workloads smaller (45 → 43): cash now peaks earlier, because the late, small workloads still add cost faster than they add positions.

### Every scenario × policy (each sized to its own peak cash)

| Scenario | Policy | Cash, flat pay | Cash, 3.4% | Payback |
|---|---|---|---|---|
| Conservative | Capacity only | −$9.72M | −$9.80M | none → none |
| Conservative | Attrition only | −$1.00M | −$0.04M | 60 → 55 |
| Conservative | Active reduction | $4.65M | $6.28M | 41 → 40 |
| Moderate | Capacity only | −$10.14M | −$10.15M | none → none |
| Moderate | Attrition only | $9.38M | $11.55M | 33 → 31 |
| Moderate | Active reduction | $22.65M | $26.26M | 25 → 25 |
| Aggressive | Capacity only | −$11.41M | −$11.41M | none → none |
| Aggressive | Attrition only | $24.98M | $28.83M | 21 → 20 |
| Aggressive | Active reduction | $49.09M | $55.65M | 18 → 17 |

### The four ceiling readings (see assumptions 5.7)

| Reading | Flat pay | 3.4% a year |
|---|---|---|
| Tasks column 0.85 / 0.55 | $5,800,227.08 | $7,455,038.68 |
| Pack 0.90 / 0.80 | $9,376,169.02 | $11,549,980.85 |
| Read me table 0.90 / 0.85 | $9,754,376.86 | $11,939,578.14 |
| Bucket ceiling 1.00 / 1.00 | $11,476,088.73 | $13,865,232.10 |

The high-to-low spread narrows from 1.98x to 1.86x.

## What was changed

- `packs/base.json`: `economics.wage_growth = 0.034`.
- `evm.py` and `evm.js`: `scope()` (wage-weighted annuity) and `simulate()` (wage index on the five salary-linked lines). Parity passes.
- `site/app.js`: the assumption register gains a "Pay growth per year" row; site rebuilt.
- `docs/Etter_Value_Model_FPA.xlsx`: new input `p_wage` (Inputs row 54), wage index in Timeline column FP, the five salary-linked Timeline columns escalated, cost test on `p_annw` (Workloads D4). Reference-engine values (Sizing, Risk, peak-cash sizes, Checks 16–20) recomputed. Matches the engine to the cent at the default and in four other scenario/policy cases; all 20 checks pass.
- `tests/test_evm.py`: `test_earlier_engine_is_reproduced` now sets `wage_growth = 0`, because the v0 engine it reproduces had flat pay. Its assertions are unchanged.

## Left for the owner

The golden numbers this change moves are **not** updated: `tests/reference.json` (`test_reference_numbers`) and the four locked values in `tests/test_ceiling_sets.py`. Those 5 tests fail until they are updated. The new values are in the tables above. Several documents still quote flat-pay numbers and carry a banner saying so.
