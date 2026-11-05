# Spec delta: five fixes from the finance review

**Status:** specified 5 November 2026, before any engine change (working agreement, rule 1).
**Scope:** five points raised in a finance review of the final model. Four change numbers; one (discounted payback) adds an output.
**Headline effect:** cash NPV at the default (FP&A, Moderate, Attrition only) moves from **$9,376,169.02** to **about $6.15M**. The two training fixes cause the whole fall. The capacity fix does not touch cash. The exact figure is fixed in `tests/reference.json` once the engine is built.

| # | Finding | Fix | Kind | Moves cash? |
|---|---|---|---|---|
| 1 | Positions are floored; capacity counts every leftover sliver at full rate | Per-person granularity floor on capacity | 1 new judgment parameter | No (capacity only) |
| 2 | Training booked once, for the starting headcount only | Train joiners as they arrive; annual refresher for people in post | Structural (joiners) + 1 new judgment parameter (refresher) | Yes, down |
| 3 | Licence seats priced on the starting headcount forever | Seats priced on people in post, trued down at each contract anniversary | Structural | Yes, slightly up |
| 4 | Payback undiscounted while NPV is discounted | Report both, labelled | Output | No |
| 5 | No shape for "we tried this and stopped" | Stop path (AI off, work returns, positions refilled) and a pilot gate in the odds | Structural | No (headline); odds yes |

---

## 1. Capacity granularity

**Finding.** Positions are floored per role (`math.floor`). Everything left over is booked to capacity at the full loaded rate. At the default that is about 114 people's worth of time at month 60, spread across about 1,460 people still in post: **7.6 to 14.8 hours a month per person** (2 to 3.5 hours a week) in every role. Time that thin is not redeployable unless someone reorganises the work. Under this policy, nobody does: the time that was consolidated became positions.

**Rule.** Each person still in post keeps the first block of freed time as slack. Only time above that block counts as capacity.

```
left_h      = freed_h − positions × H − hires_avoided × H        (as before)
block_h     = min_block_share × H × (N − positions)               (H = the role's task hours a month)
capacity_h  = max(0, left_h − block_h)                            valued at the hourly rate, as before
stranded_h  = left_h − capacity_h                                 valued at zero, reported in hours
```

Freed hours now go to four places, and the monthly check becomes **freed = positions + hires avoided + capacity + stranded**. The gap stays exactly zero.

**Default.** `capacity.min_block_share = 0.05`: 8 hours a month at 160, about 24 minutes a day. Status **judgment**. Range 0 (old behaviour) to 0.10 (half a day a week).

**Why a threshold and not a flat discount.** Forrester's TEI studies apply a flat 50% "productivity recapture" to time saved. Forrester's own tables label it a TEI standard, a house assumption, not a measured rate. A flat discount ignores the size of the slice, which is what the review is about. A threshold applies the floor's logic per person: fractions too small to use count as zero. The 50% convention is recorded as a cross-check only.

**What it does here, stated plainly.** The freed time is spread evenly across everyone in a role, so per-person slivers in this data sit in a narrow band. That makes capacity a cliff in this parameter:

| min_block_share | per person | Capacity PV (default case) |
|---|---|---|
| 0 (old) | — | $47.7M |
| **0.05** | **~24 min/day** | **~$13.2M** |
| 0.10 | half a day a week | $0 |

This is the finding, not a defect. Capacity in this function is almost entirely slivers, and its value depends on a judgment about how thin is too thin. The pages show stranded hours next to capacity so the reader sees both.

**Capacity hurdle.** Under Capacity only, the hurdle rises from about 15% to about 43% of remaining capacity. Less capacity counts, and training costs more (fix 2).

**Rule 6 (parameters must earn their place).** The cash tornado in `evm.sensitivity()` cannot show this parameter, because it never touches cash (brief section 6: cash and capacity never blend). On the output it governs, it is the largest single mover: $47.7M → $0 across its range. It stays on that ground, and this exception is declared here rather than hidden.

---

## 2. Training: joiners and refresher

**Finding.** `R['N'] × (spend + hours × rate)` fires once, at first exposure. At 9–12.5% yearly turnover a large share of the people in post by month 60 joined after that date and were never trained. No refresher exists, although tools change with every wave and every vendor release.

**Rule.** The unit cost per person is unchanged: `unit = training_spend_per_head + training_hours_per_head × hourly rate`, not scaled by the cost multiplier, as before.

```
month of first exposure:   N × unit                                         (as before)
each later month m:
  leavers_m   = (N − positions_{m−1}) × (1 − (1 − turnover × turnover_mult)^(1/12))
  joiners_m   = leavers_m − new positions not refilled this month          (attrition policy)
              = leavers_m                                                  (active reduction: leavers are all replaced)
  refresher_m = (N − positions_m) × training_refresh / 12                  from 12 months after first exposure
  training_m  = (joiners_m + refresher_m) × unit
```

Joiners are counted as expected values (fractions allowed). Training is a cost, not a headcount.

**Default.** `costs.training_refresh_per_year = 0.25`: a quarter of the initial package a year, about 4 hours and $212 per person. Status **judgment**. Spread in `uncertainty.params.training_refresh`: P10 0.10, P90 0.50 (logit-normal). It enters the odds and the tornado.

**Evidence, stated at its real strength.**
- BCG, *AI at Work 2025*: 79% of employees with more than five hours of training were regular users, against 67% of those with less. This supports training as a driver of use. It does not measure a refresher rate.
- The review cites a study showing that gains depend on continued tool use and do not persist when the tool is removed. The closest primary evidence found is Budzyń et al., *Lancet Gastroenterology & Hepatology* 10 (2025) 896–903. Endoscopists' unaided adenoma detection fell from 28.4% to 22.4% after AI exposure. The study was covered in a *Nature* news feature in June 2026. No copy is in the repository. This evidence supports fix 5, that the work comes back when the tool is withdrawn, more directly than it supports refresher training. The refresher rate itself is judgment.

**Rule 6.** The refresher's P10–P90 swing on cash is about $3.7M, which ranks it above drag, active use and the assistant multiplier in the tornado.

---

## 3. Licences trued down

**Finding.** `seats = N × active_use × ramp` uses the starting headcount, so the model keeps paying for seats behind positions that are gone.

**Rule.** Assistant time saved is still `N × active_use × ramp × assistant hours × multiplier`. The work does not shrink when positions go; the people in post do it. Licences are bought per person in post. Seat contracts are annual and can be reduced only at the anniversary (Microsoft 365 Copilot is sold on annual commitments; reductions happen at renewal), so:

```
seats_m = (N − positions at the start of the current contract year) × active_use × ramp_m
          contract year k covers months 12k+1 … 12k+12, priced on positions at month 12k
```

No new parameter. Effect at the default: licences fall by about $0.03M PV, about 2%. The saving is small, but the model no longer contradicts itself.

---

## 4. Payback, discounted and undiscounted

**Finding.** NPV is discounted; payback is not. One output mixes two conventions.

**Rule.** Report both, labelled:
- **Payback (discounted)**: the first month after the last month in which cumulative *discounted* cash is negative. This is consistent with the NPV; a positive NPV implies a finite discounted payback.
- **Payback (undiscounted)**: the same rule on nominal cash, as before. Kept because finance teams quote it.

The discounted payback is never earlier than the undiscounted one. Both go to `reference.json`.

---

## 5. Trying and stopping

**Finding.** `Pm = max(Pm, prevP)` stops positions coming back, and nothing makes freed time fall. So the model cannot represent a programme that is switched off, and an unfavourable answer can only come from pessimistic inputs, never from the programme failing.

**Rule: stop path.** `simulate(..., stop_month=s)`. From month `s` onwards:
- AI is switched off: no agent hours, no assistant hours, no running cost, no maintenance, no licences, and no joiner or refresher training.
- Builds that would start at or after `s` are not spent. Money already spent stays spent: month-0 programme and deployment costs, initial training, and builds started before `s`.
- **The work comes back.** Freed hours fall to zero, so positions fall to zero through the existing cap ("never more positions than time freed"). Each returning position is refilled at the cost per hire, booked as negative recruiting avoided under both policies. This fixes a latent bug: under active reduction, a returning position would have been booked as negative severance, i.e. income.
- The ratchet stays, and now only does what it should: it stops positions bouncing while the AI runs. It never holds a position the freed time no longer covers.

**Rule: pilot gate in the odds.** The staged schedule already pauses for evaluation after the pilot, but nothing was ever decided there. Now, in every simulated future:

```
gate month   = build lead + pilot evaluation months          (9 at the default)
pass mark    = the plan's break-even net realisation          (computed already; ~19.7% after these fixes)
stop at gate if the future's takeover × (1 − review) < pass mark
```

- The gate applies only when cash is the case (harvest > 0) and the schedule is staged. Under Capacity only there is no cash pass mark.
- If no realisation can break even, every future stops at the gate.
- Measurement at the gate is taken as exact. This is optimistic; a noisy pilot would stop some good programmes and pass some bad ones.

No new parameter: the gate month and the pass mark come from inputs already in the pack. The deterministic headline does not stop, because Moderate passes the gate.

**What it shows at the default (prototype numbers, fixed after build):**
- About **30%** of futures stop at the gate. This is an output, not a calibration target. It sits on Gartner's forecast that at least 30% of GenAI projects would be abandoned after proof of concept by end-2025 (press release, 29 July 2024). S&P Global Market Intelligence reported that 42% of companies abandoned most AI initiatives in 2025.
- A programme stopped at the gate loses about **$4.4M**, mostly the training already given. The pages report it as "cost of trying and stopping".
- The gate trims the bad tail (P10 about −$7.6M without it, −$4.8M with it) and barely moves the chance of positive cash.

This gives the acceptance criterion its other route: an unfavourable answer can now come from the programme failing in a share of futures, and the report says how often and what it costs.

---

## Headline bridge (default case, programme re-sized to peak cash at each step)

| Step | Cash NPV | Payback (undisc. / disc.) |
|---|---|---|
| Before | $9,376,169 | 33 / 34 |
| + licences trued down | $9,411,809 | 33 / 34 |
| + joiners trained | $8,476,899 | 34 / 36 |
| + refresher 25% a year | $6,145,867 | 37 / 39 |
| + capacity floor, stop path, gate | $6,145,867 (cash unchanged) | 37 / 39 |

Workloads (45) and positions (59) do not change. The chance of positive cash falls from 75% to about 56%, so the verdict at the default moves from **Go** to **Pilot first**. Joiner training alone is enough to cross the 70% line, and that fix is structural, not a judgment.

## Kept reproducible

- The earlier engine is still reproduced to the cent: `simulate(..., legacy=True)` switches off fixes 1–3. Fixes 4 and 5 only add outputs and options. `tests/test_evm.test_earlier_engine_is_reproduced` keeps its meaning.
- Every fix is a monthly column in the workbook: remaining heads, joiners, refresher, seats on contract-year headcount, block and stranded hours, discounted cumulative cash. No new sheet.
- New pack keys: `capacity.min_block_share`, `costs.training_refresh_per_year`, `uncertainty.params.training_refresh`. Each has a `packs/sources.json` entry.

## Not changed

Ceilings (open question 1), tax (open question 2), terminal value (open question 3), wage escalation, review by band, and productive hours by level are untouched. They remain listed in the working agreement.
