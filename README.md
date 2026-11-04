# Etter Value Model: reference implementation (final model)

Turns Etter task data into a month-by-month financial estimate: cash vs today, cost avoided vs plan, and capacity at cost, never added together.

**Version:** final model, 23 October 2026. Agent ceilings set by Chandan (Draup): **Directive 90%, Feedback Loop 80%**.
**Default answer** (Etter FP&A data, Moderate, Attrition only, cross-industry): cash **+$9.38M** 5-yr NPV · **59** positions not refilled · capacity **$47.7M** (never added) · payback **month 33** · **75%** chance cash is positive · break-even net realisation **14.3%** vs 28% assumed · **45 of 59** workloads (35 buy, 10 build) · verdict **GO**.

## Run
    python3 run.py                                  # FP&A dataset, Moderate, attrition only
    python3 run.py insurance_mid                    # an archetype with its default policy
    python3 run.py base Aggressive "Active reduction"
    python3 -m unittest discover tests              # 18 acceptance and invariant tests
    python3 tests/parity.py                         # browser engine (evm.js) gives the same numbers
    python3 site/build.py                           # rebuild the website prototype after changes

## Files
- `evm.py`: the engine (no dependencies). `report()` returns everything the pages need.
- `evm.js`: line-for-line browser port; parity-checked against `evm.py` (worst relative difference ~3e-14).
- `packs/base.json`: every parameter, with scenarios, policies and uncertainty ranges.
- `packs/archetypes.json`: five archetypes (industry x size) as overrides of the base pack.
- `data/etter_fpa.json`: the Etter FP&A dataset (11 roles, 420 tasks).
- `tests/`: acceptance tests (`test_evm.py`), reference numbers (`reference.json`), JS parity (`parity.py`).
- `site/`: website prototype (`etter_value_model.html` is the built single page).
- `experiments/`: the experiments behind the strategy doc. They were run on the earlier engine (build only, ceilings 85% / 55%) and are kept for the record; their outputs in `experiments/out/` are not the current numbers.
- `docs/`: how the model works, the assumption list, the full context file, the flowchart and the Excel workbook.

## Model in three sentences
Etter says which tasks AI can do; the model keeps only the workloads where an agent (built or bought, whichever is cheaper) costs less than the work, and only the share AI really takes over once people have checked it.
That freed time becomes whole positions as people leave, hires the plan no longer needs, or capacity for other work: every hour goes to exactly one place.
Cash, avoided hires and capacity are reported separately, with the odds, a break-even and a ledger that traces every dollar to an input.

## What is new in the final model (vs the earlier engine)
- **Build or buy** per workload: custom build ($55k / $130k, $3.48 per AI hour, 18%/yr upkeep) vs vendor purchase ($15k / $35k, $6 per AI hour); the higher NPV at cost wins (`scope`).
- **Peak-cash sizing**: passing workloads join in rank order until five-year cash peaks (`size_to_peak`); capacity-only keeps every passing workload. `report()` sizes by default.
- **Agent ceilings** 90% (Directive) and 80% (Feedback Loop).
- With `allow_buy: false`, ceilings 85% / 55% and no sizing, the engine reproduces the earlier engine to the cent ($3,096,839.06, 47 positions, month 44); this is a test.

## Website prototype
- `site/etter_value_model.html`: the built page (open it in any browser; no server needed).
- Rebuild after changing the engine or packs: `python3 site/build.py` (inlines `evm.js`, the data and the packs into `site/template.html` + `site/app.js`).
