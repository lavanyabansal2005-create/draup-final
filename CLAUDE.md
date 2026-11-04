# Etter Value Model — working agreement

## What this is
Turns Etter task-level scores into a month-by-month financial estimate: cash vs today,
cost avoided vs plan, and capacity at cost, reported separately and never added together.
Assignment brief from Chandan Kumar (Principal Architect, Draup). The brief is the spec of
record; `docs/` holds the model's own spec, assumptions and context.

## Read before changing anything
- `docs/Etter_Value_Model_how_it_works.md` — the pipeline
- `packs/base.json` — every parameter
- `packs/sources.json` — where every parameter's default comes from, and which have no source
- `tests/reference.json` — the golden headline numbers

## Hard rules

**1. Specification before code.** The brief says code written before the spec encodes
assumptions nobody chose. For any change that alters a number, write the change as a spec
delta in `docs/` first, in the same session, before touching `evm.py`.

**2. `reference.json` is golden.** Any change to the headline number is a deliberate act.
If a change moves it, say so explicitly, state the new number and why, and update
`reference.json` as its own commit. Never update it silently to make a test pass.

**3. The full suite stays green.** `python3 -m unittest discover tests` — currently 27 tests.
Includes the five acceptance criteria from the brief. A red suite is never "fixed" by
weakening an assertion.

**4. JS parity is a gate.** `evm.js` is a line-for-line port. Any change to `evm.py` means
the same change to `evm.js`, then `python3 tests/parity.py` must pass, then
`python3 site/build.py` to rebuild the page.

**5. Every pack key needs a source entry.** `tests/test_sources.py` enforces this. Adding a
parameter to `packs/base.json` without deciding where its default comes from fails the suite.
That is intentional — it is what keeps parameter growth self-policing.

**6. New parameters must earn their place.** A parameter that does not appear in the top ten
of `evm.sensitivity()` is decoration and should be deleted. The top three movers are
`harvest_automation`, `takeover` and `review`; anything whose P10–P90 swing is small against
theirs sits below the noise floor. Prefer a structural fix over a new parameter.

**7. The scoring engine is out of scope.** Consume Etter's scores as given. Do not rebuild or
reverse-engineer task decomposition or scoring (brief, section 7).

**8. Cash and capacity never blend.** Brief section 6. Cash savings leave the cost base and
someone owns them; capacity savings are real value with no budget line. Keep them apart in
every output, every time.

**9. No AI calls at run time.** Above the scores this is arithmetic over a table.
Deterministic, same inputs same outputs. Seeded PRNG only.

**10. Honest output.** The model must be capable of returning an unfavourable answer. At least
one archetype must conclude the payback does not justify the programme.

**11. The Excel workbook is the reproducibility artifact.** The brief requires that someone
with a spreadsheet and no access to this code can reproduce the headline number in under an
hour. `docs/Etter_Value_Model_FPA.xlsx` currently satisfies that — its Summary sheet carries
$9,376,169.02, matching the engine to the cent. Any change that moves the headline must
regenerate that workbook in the same session. A stale workbook fails the requirement silently,
which is worse than failing it loudly.

## Claims and citations
`packs/sources.json` distinguishes `sourced` / `client_supplied` / `judgment` / `out_of_scope`.
Do not promote an entry to `sourced` without a real, checkable citation. A declared judgment
parameter with a wide range is stronger than a decorative citation — three honest rows read as
rigour, forty dressed-up ones read as the opposite.

Primary PDFs are in `docs/sources/`. Read them from disk when a number is in question rather
than quoting from memory; the effect sizes in several of them differ from the commonly quoted
versions (e.g. Brynjolfsson v2 reports 5,172 agents and 15%, not the 2023 working paper's
5,179 and 14%).

## Stale artifacts — read before citing any number from them

`experiments/out/*.json` and `experiments/legacy/` were produced by an earlier engine
(build-only, no buy option, no peak-cash sizing, ceilings 85% / 55%). **Never cite their
numbers as current.** `out_bridge.json`, `out_curve.json` and `out_frontier.json` are
historical records of how we got here, not results. If a figure is needed, recompute it on
the current engine.

`experiments/legacy/engine_v2.py` is kept deliberately. Line 11 hardcodes
`CEIL = {'Directive': 0.85, 'Feedback Loop': 0.55, 'Task Iteration': 0.45, ...}`, which is
exactly the per-row Etter potential column shipped in the team's source workbook. That is
evidence, not a bug: the earlier engine followed the shipped data, and the move to 90 / 80 was
a later, deliberate override by Chandan. It dates the decision, which matters for open
question 1 below. Do not "correct" it.

## Open questions for Chandan — do not resolve unilaterally
1. **Ceilings.** The source workbook states the Etter potential ceilings twice and the two
   tables disagree on five of six categories (only Negligibility agrees, both 0.10). The pack matches neither. Priced on this engine
   the readings give $5.80M / $9.38M / $9.75M / $11.48M of 5-year cash NPV. See
   `packs/sources.json` → `categories.*.ceiling` → `CONFLICT`. The question is not "which table
   is right" — `engine_v2.py` shows we once used the shipped column, so the override to 90 / 80
   was intentional. The question is what it rests on, so it can go in the parameter book with a
   reason rather than as an unexplained number.
2. Whether the model reports pre-tax or after-tax cash flows.
3. Whether month 61 carries any residual value.

## Known gaps, already diagnosed
- `on_cost` 1.3055 reconciles to BLS ECEC only if paid leave is excluded. The convention is
  undocumented; the headline ECEC multiplier is 1.4287.
- No wage escalation: salaries are flat for 60 months while run cost declines 13%/yr, under a
  nominal discount rate. Asymmetric, and it understates savings.
- `review` is a flat 0.30 across all bands. Two studies (Dell'Acqua; Brynjolfsson v2) show the
  cost of unreviewed output rises with seniority. This is a structural change, not a parameter.
- `standard_task_hours_month` is a flat 160. FR3 asks for productive hours per level.
- The score-gap check raises warnings on 5 of 11 roles for a mismatch the source workbook
  states is expected. These are not defects and should not be presented as warnings.
- Three workbook sheets are unused: Workloads (per-workload category splits), Skills (545 rows,
  current/emerging/declining), Read me.

## Commands
    python3 run.py                                  # FP&A dataset, Moderate, attrition only
    python3 run.py insurance_mid                    # an archetype with its default policy
    python3 -m unittest discover tests              # full suite, must stay green
    python3 tests/parity.py                         # evm.js matches evm.py
    python3 site/build.py                           # rebuild the site after engine changes

## Style
Minimal dependencies — the engine is pure Python with none, keep it that way. Clean, tested,
readable. Prefer editing over adding. If a change makes the model harder to reproduce in a
spreadsheet in under an hour, or harder to explain in three sentences, it is the wrong change.
