# Site grades vs source book: reconciliation

**As of 5 Nov 2026.** Compares the A–D grades the site shows (`site/app.js`: the assumption register and the per-line grades on "Every line, present value") against the `status` of the matching entry in `packs/sources.json`. **Neither file has been changed.** Each disagreement below needs a decision about which side is right.

**How the two scales line up.** The site's key: A = official statistic or list price, B = industry benchmark, C = indirect evidence or estimate, D = thin evidence. The source book's statuses: `sourced` = public, citable source; `client_supplied` = no credible public source; `judgment` = modelling choice. They agree when **A/B ↔ `sourced`** and **C/D ↔ `client_supplied` / `judgment`**. C with `sourced` counts as agreement when the source only supports the parameter indirectly (both files say so for takeover and review).

## 1. Grade and status disagree

The site grades these B. The source book says no credible public source exists, because the benchmark is gated and was never checked.

| Site item | Site grade | Site source | `sources.json` key | Status | What the source book says |
|---|---|---|---|---|---|
| Register: cost per hire avoided | **B**, "Fact" | SHRM benchmarking | `economics.cost_per_hire` | `client_supplied` | SHRM report is gated. "Mark client-supplied and move on." |
| Register: training spend per person | **B**, "Fact" | ATD 2026 | `costs.training_spend_per_head` | `client_supplied` | ATD is gated. |
| Register: training hours per person | **B**, "Fact" | ATD 2026 | `costs.training_hours_per_head` | `client_supplied` | ATD is gated. |
| Register: software seat per position | **B**, "Fact, client adds tools" | M365 E3 list price | `costs.seat_cost_per_position` | `client_supplied` | Client SaaS spend or gated Zylo/Productiv. The parameter book (row 4.8) grades it **C**, "Estimate". |
| Line: software seats reclaimed | **B** | Positions × $468 (M365 E3) | `costs.seat_cost_per_position` | `client_supplied` | As above. |
| Line: recruiting avoided | **B** | Cost per hire (SHRM) | `economics.cost_per_hire` | `client_supplied` | As above. |
| Line: training | **B** | ATD 2026 | `costs.training_*` | `client_supplied` | As above. |
| Line: hires avoided against plan | **B** | Planned hires × loaded cost + cost per hire | `economics.function_growth`, `economics.cost_per_hire` | `client_supplied` (both) | Both inputs are client-supplied; only the on-cost under it is sourced. |
| Line: severance | **C** | 12 weeks of salary | `policies.*.severance_weeks` | policy (`_policy_not_empirical`) | A policy choice, not evidence. The register shows policy items with no grade; this line should be the same. |

If the source book is right, the six B's become C. If the site is right, someone needs to get the SHRM and ATD figures, cite them with a date, and promote the entries to `sourced`.

## 2. Grade and status agree, but they cite different sources

The grades agree, but a reviewer comparing the site with the source book will find two different citations for the same number.

| Item | Grade / status | Site cites | `sources.json` cites |
|---|---|---|---|
| AI takeover | C / `sourced` | Ardent Partners 2025, AP touchless rates | Brynjolfsson et al. v2; Cui et al.; Noy & Zhang; ICLE review; Microsoft Research. None of these is Ardent. |
| Human review | C / `sourced` | Workday 2026, ~40% of AI time savings lost to rework | Dell'Acqua et al., Organization Science 2026. Workday is not mentioned. |
| Months to full use | C / `judgment` | Gartner 2026, 63% of finance AI rollouts slower than expected | Bass 1969 for the curve shape; Stanford HAI / McKinsey for context. |
| Running cost decline | C, "Fact" / `sourced` | "Team estimate" | Stanford HAI AI Index 2026 and Epoch AI. Both are marked `verify_before_use`, and Epoch has no URL. The site calls it an estimate; the source book calls it sourced on citations that haven't been checked. |
| Programme fixed cost; deployment per person | C, "Fact" / `client_supplied` | Forrester TEI, Microsoft 365 Copilot | Listed in `_unsourced_by_design`. "Candidate: Prosci (gated)." The site cites a source the source book says doesn't exist. |
| Turnover multiplier (and band rates) | B / `sourced` | Mercer band rates; JOLTS 2025 | BLS JOLTS by industry, with no URL and `verify_before_use`. Says the by-band split is interpolated. The parameter book (row 4.5) cites Mercer 2025. Mercer appears nowhere in the source book. |

## 3. Smaller mismatches

- **Kind says "Fact" on client-supplied items.** Maintenance share (C, "Fact", "software maintenance convention") is `client_supplied`, and the source book says the range "is conventional, not measured". The same applies to the programme, deployment, training and cost-per-hire rows in section 1.
- **Discount rate range.** The site shows 5.6–9.3%. `sources.json` gives P10 6.19%, P90 9.34% (Damodaran; the lowest reconciled industry is Hospitals at 6.19%), and the repo's archetypes span 6.19–9.34%. The Excel workbook's industry table goes lower, with Banking at 4.98%, which the source book doesn't reconcile. Nothing supports 5.6% as a bound.
- **Positions line graded A.** Salary × on-cost 1.3055. The on-cost is `sourced`, but the salary is the Draup estimate the Etter workbook calls "indicative … not payroll". Salary is data, so it has no `sources.json` entry, but an A grade overstates the line.

## 4. Agree

Drag (D / `judgment`), active use (C / `client_supplied`), assistant and cost multipliers (C / `judgment`), harvest shares (no grade / policy), function growth (no grade / `client_supplied`), discount rate (A / `sourced`), on-cost (A / `sourced`), assistant licence (A / `sourced`), build costs (C / `client_supplied`), AI running cost (D / `client_supplied`), the build, programme, licences, running cost and maintenance lines, and capacity at cost (A; on-cost and the TDABC method are both `sourced`).

## Not covered

`sources.json` entries the site doesn't grade: `augment.time_saving_by_band`, `turnover_by_band`, `uncertainty.execution_correlation`, `economics.standard_task_hours_month`, the schedule keys, and the proposed `economics.tax_rate` (which isn't in the pack). The Excel workbook's Inputs sheet carries its own grade column; it wasn't part of this check.
