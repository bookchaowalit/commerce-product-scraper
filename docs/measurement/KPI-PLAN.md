---
title: KPI and Instrumentation Plan — commerce-product-scraper
created: 2026-10-22
updated: 2026-10-22
status: approved
template: architecture-docs templates/sdlc/kpi-and-instrumentation-plan.md
---

# book-ecommerce-scraping — KPI and Instrumentation Plan

This is a data producer, not a user-facing product, so its KPIs are data-product KPIs:
freshness, volume, parse quality and contract conformance. **Live collection is not
approved** (Kaidee rejected by the owner on 2026-10-15, BOO-127; `marketplace.v1` has
`collection_approval: rejected`), so no production baseline can be measured. Every
production figure below is `baseline: not yet measured`, and the targets apply only if a
marketplace source is approved.

## Document control

| Field | Value |
|---|---|
| Project / product ID | book-ecommerce-scraping (`bookchaowalit/commerce-product-scraper`) |
| Version | 0.1 |
| Status | draft |
| Metric owner | bookchaowalit (owner) |
| AI maker | Claude session b-data (2026-10-22) |
| AI reviewer | independent Claude reviewer subagent (`solo:solo-reviewer`, Sonnet, read-only, no maker context), 2026-10-24: approved (see Approval) |
| Charter objectives | Roadmap `data-scrapers.yaml` eco-g1..eco-g4 (no charter) |
| Analytics / data source of truth | Run output (`--json` result rows, `data/exported/*.csv`), Sentry events from `ecommerce/observability.py`; Bronze `marketplace_listings` once wired |
| Dashboard | none yet [ต้องยืนยัน] |
| Next review | when marketplace.v1 leaves `rejected`, or 2026-12-31 (roadmap horizon) |

## KPI tree

```text
OBJ-01 A contract-valid, fresh marketplace listing feed (only if a source is approved)
  └─ KPI-O-01 Bronze freshness (hours since last successful capture)
       ├─ KPI-L-01 Rows per run
       ├─ KPI-L-02 Card skip rate (malformed / unpriced cards dropped by the parser)
       ├─ KPI-G-01 Contract violations per run
       ├─ KPI-G-02 Failed runs not reported
       └─ KPI-G-03 Personal-data fields in exports
```

## KPI definitions

| KPI ID | Type | Name | Objective | Formula (numerator / denominator) | Unit | Min volume for a rate | Segment / filter | Data source and event(s) | Baseline (value, period, evidence) | Target (value, by date) | Alert threshold | Cadence | Owner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KPI-O-01 | outcome | Bronze freshness | OBJ-01 | now − max(`captured_at`) of `marketplace_listings` | hours | N/A | source = kaidee_classifieds (or the approved successor) | Bronze manifest (not wired) | not yet measured (collection rejected) | ≤ 8 h, from the first approved schedule [ต้องยืนยัน] | > 8 h | per run | owner |
| KPI-L-01 | leading | Rows per run | OBJ-01 | `count` in the run's result row | rows | N/A | per job | `scripts/run_marketplace.py --json` | not yet measured | ≥ 20 per run [ต้องยืนยัน] (cap 200) | 0 rows (the run already fails then) | per run | owner |
| KPI-L-02 | leading | Card skip rate | OBJ-01 | cards skipped by `parse_html` / candidate cards | % | ≥ 50 candidate cards | per page | not instrumented (the parser does not count skips yet) | not yet measured | ≤ 10% [ต้องยืนยัน] | > 25% | per run | owner |
| KPI-G-01 | guardrail | Contract violations | OBJ-01 | rows missing a `marketplace.v1` required field, or a header that differs from the record fields | rows | N/A | snapshot CSV | `tests/test_contract.py` (offline, every CI run) | 0 on the saved fixture, 2026-10-22, CI | must stay 0 | ≥ 1 (CI fails) | every CI run | owner |
| KPI-G-02 | guardrail | Failed runs not reported | OBJ-01 | failed jobs without a Sentry event / failed jobs | % | N/A | runs with `SENTRY_DSN` set | `ecommerce/observability.py` → Sentry; `tests/test_observability.py` | 0 in tests; production not measured (no DSN configured) | must stay 0 | ≥ 1 | per run | owner |
| KPI-G-03 | guardrail | Personal-data fields in exports | OBJ-01 | contact fields (phone, email, LINE ID, names, address) present in snapshot or raw JSON | fields | N/A | all exports | `redact_personal_data` tests, `tests/test_contract.py` | 0 on fixtures, 2026-10-22 | must stay 0 | ≥ 1 | every CI run | owner |

Rules from the template apply: no KPI without a baseline is used to claim a benefit, and
rates below the minimum volume are reported as `not measurable`.

## Event and data specification

| Event / field | Trigger (exact user or system action) | Properties | Personal data (incl. IDs / IP)? | Emitted by | Requirement / story | Status |
|---|---|---|---|---|---|---|
| run result row | each job in `run_marketplace` finishes or fails | `job`/`source`, `count`, `output`, `history`, `raw` or `error` (exception class) | no | `scripts/run_marketplace.py` | SPEC-001 | implemented |
| Sentry `error` event | a job fails in a non-dry run with `SENTRY_DSN` set | message `job <name> failed: <ExceptionClass>`, tag `component=run_marketplace`, `environment` | no (`send_default_pii=False`) | `ecommerce/observability.py` | SPEC-001 AC-01 | implemented, not live (no DSN) |
| `captured_at` | snapshot write | UTC ISO-8601, seconds, `Z` | no | `ecommerce/kaidee_scraper.py` | marketplace.v1 | implemented |
| card skip counter | parser drops a card | page URL, reason | no | not implemented | KPI-L-02 | planned |

Privacy: snapshot rows keep `seller_role` only; raw captures keep only the listing arrays
after `redact_personal_data`. Sentry events carry no listing data. Retention of exports is
`pending_operator_approval` in the contract [ต้องยืนยัน].

## Dashboards and alerts

| Dashboard / alert | KPIs shown | Audience | Location | Refresh | Alert channel | Status |
|---|---|---|---|---|---|---|
| Sentry project for this collector | KPI-G-02 | owner | not created [ต้องยืนยัน] | per event | Sentry → owner | planned (owner action) |
| Lake freshness monitor | KPI-O-01, KPI-L-01 | owner | parent `task scraping:coverage` | per run | [ต้องยืนยัน] | planned (needs an approved source and lake landing) |

## Instrumentation verification (before G10)

| # | Check | Evidence | Result |
|---|---|---|---|
| 1 | Events fire once per real action | `tests/test_observability.py` (one event per failed job) | pass (offline) |
| 2 | Counts reconcile with the system of record | needs a live run | not run (collection rejected) |
| 3 | No PII in payloads | `tests/test_kaidee_scraper.py::test_raw_capture_drops_seller_personal_data`, `tests/test_contract.py` | pass (offline) |
| 4 | Dashboard renders each KPI | no dashboard | not run |
| 5 | Alerts reach the channel | no Sentry DSN configured | not run |
| 6 | Baselines captured | not yet measured | waived until a source is approved |
| 7 | Consent | not applicable (no end users) | N/A |

## Change history of definitions

| Date | KPI ID | Change | Reason | Baseline restated? | Approved by |
|---|---|---|---|---|---|
| 2026-10-22 | all | First draft | Big Loop L3 baseline | no | pending |

## Quality gate and approval

| Gate | Condition | Decision | Approver | Date | Evidence |
|---|---|---|---|---|---|
| G5 | KPI definitions accepted | pending | owner | — | this file |
| G10 | Instrumentation checks pass | blocked: no approved source, no DSN | owner | — | — |
| G11 | Dashboard live | blocked | owner | — | — |

## Approval (2026-10-24)

| Field | Value |
|---|---|
| Checker | independent Claude reviewer subagent (`solo:solo-reviewer`, Sonnet, read-only, no maker context) |
| Approver | AI approval under the owner's process (approvals by the owner or AI with evidence; maker and checker are different agents). Recorded by Claude session oa-remainder on the owner's instruction "ทำที่เหลือให้หน่อย" (2026-10-24) |
| Verdict | **approved** |
| Evidence | ecommerce/observability.py (off without DSN, no PII); run_marketplace.py --json + report_failures; kaidee_scraper.py redact_personal_data; named tests exist; Sentry marked not live. |
