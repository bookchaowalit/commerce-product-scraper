# book-ecommerce-scraping — Product brief

**Slug:** `bookchaowalit/commerce-product-scraper`  
**Tier:** B (catalog label) · target Big Loop L3  
**Status (2026-10-22):** one bounded Kaidee collector with offline tests. Live collection
is **not approved**: the owner rejected Kaidee on 2026-10-15 (BOO-127). Nothing runs on a
schedule from this repository today.

## Purpose

Marketplace domain producer: capture a bounded set of public Thai marketplace listings
into contract-shaped CSVs (`marketplace.v1`) for research. While no marketplace source is
approved, the repo is kept as tested code and synthetic fixtures only.

## What exists

- `ecommerce/kaidee_scraper.py`: parses Kaidee's `__NEXT_DATA__` (≤ 5 pages, ≤ 200 rows,
  2 s between pages) and writes `data/exported/kaidee_classifieds.csv`,
  `kaidee_classifieds_history.csv` and a redacted `kaidee_classifieds_raw.json`.
- `ecommerce/http.py`: the only network path (identifying User-Agent, timeout, bounded
  retries).
- `scripts/run_marketplace.py`: the runner; `--dry-run` prints the plan without network or
  writes; a failed job is reported as `{"job", "error": "<ExceptionClass>"}` and exit 1.
- `ecommerce/observability.py`: opt-in Sentry (see below).

There are no Shopee or Lazada collectors; the files once named that were removed in
2026-09 (see README).

## Runtime status (verified 2026-10-22)

| What | Status |
|---|---|
| Entry point | `python scripts/run_marketplace.py [--json] [--dry-run] [--output-dir DIR]` |
| Who schedules it | Nobody verified. `setup_cron.sh install` would add a 6-hourly crontab line (minute 20), but this WSL host's crontab has no scraper entries on 2026-10-22, and installing it is not approved. Other hosts / Windows tasks not verified from WSL [ต้องยืนยัน] |
| Hosted deployment | None. No API, no port, no cloud job (scheduler host is owner decision D6) |
| Error reporting | Sentry, opt-in: with `SENTRY_DSN` set, each failed job sends one `error` event (job name + exception class; no page content, no PII; locals, request bodies, exception messages and breadcrumbs are stripped from any event, including uncaught crashes). No DSN is configured for this product yet [ต้องยืนยัน] |
| Contract | `marketplace.v1` (architecture-docs `systems/architecture/scraping-contracts/`): status `draft`, `collection_approval: rejected`. The snapshot header equals its record fields (checked offline by `tests/test_contract.py`) |
| Lake landing | Not wired: no Bronze `marketplace_listings` manifest is produced |
| Quality gates in CI | ruff, ruff format, mypy (gradual), offline pytest with coverage ≥ 92%, dry-run smoke, on Python 3.10 and 3.13; shared security scan (platform-ci-workflows v1.1.1) |

## Limits

- Not production: no approved source, no schedule, no lake landing.
- The Kaidee rejection is a policy; the code does not refuse a live run by itself.

## Docs

- `specs/001-l2-baseline/spec.md`: current spec (acceptance, red/green log, planned schedule).
- `docs/measurement/KPI-PLAN.md`: data-product KPIs (freshness, rows, skips, contract).
- `docs/UPGRADE-PLAN.md`: earlier upgrade notes.
