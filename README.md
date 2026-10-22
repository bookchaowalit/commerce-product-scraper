# book-ecommerce-scraping

**Tier:** B (catalog label; Big Loop target L3)  
**Owner path:** `bookchaowalit/book-apps/tools/book-ecommerce-scraping`

> **Source terms (2026-10-15):** Kaidee was rejected by the owner; live collection and the cron below are not approved. Offline fixtures/tests only. See [Source terms decision](#source-terms-decision-2026-10-15).

## Purpose

Bounded collection of public Thai marketplace listings (currently Kaidee classifieds).

## Entry points

- `scripts/run_marketplace.py` -> `ecommerce/kaidee_scraper.py` (Kaidee collector; live use not approved since 2026-10-15)

The former `ecommerce/shopee_scraper.py` and `ecommerce/lazada_scraper.py` were
removed in the 2026-09 upgrade pass. Despite their names, the first was a
Notebookspec tech-news RSS reader (news belongs in `book-news-scraping`) and the
second an older Kaidee `__NEXT_DATA__` scraper superseded by
`ecommerce/kaidee_scraper.py`. Both imported the retired monorepo `adapters`
package and never ran from a standalone checkout; recover them from Git
history if needed.

## Stack

Python

## How to run (local)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Live Kaidee collection and cron are NOT approved (owner decision 2026-10-15):
# python3 scripts/run_marketplace.py
# bash setup_cron.sh install
```

Kaidee is the only collector. Category/price filters are applied once, while
parsing, so the 200-row cap counts matching listings only.
Output stays in this repository's `data/exported/`.

## Polite collection and privacy

`ecommerce/http.py` is the only network path: an identifying `User-Agent`
(`book-ecommerce-scraping/1.0`), a 30 s timeout, and at most three attempts
with exponential backoff that retry only timeouts, connection errors, HTTP 429
(honouring `Retry-After` as seconds or an HTTP-date, capped at 60 s) and
5xx; 403/404 fail at once. The helper is kept identical to
book-restaurant-scraping's `restaurants/http.py` apart from the User-Agent.
Kaidee pages (max 5 per run, 200 rows) are spaced 2 s apart. A malformed
listing card is skipped instead of failing the whole page. The raw JSON,
snapshot CSV and history CSV are written atomically (`ecommerce/atomic_io.py`:
temp file + fsync + `os.replace`), so a killed cron run never leaves a
truncated export or a torn history row.

Kaidee lists private sellers. Snapshot rows keep only `seller_role`, and the
raw capture keeps only the listing arrays of `__NEXT_DATA__`
(`listing_slices`) and passes them through `redact_personal_data` first:
seller/member/user objects keep only `role`, and phone, email, LINE ID, name,
address and session/token keys are dropped anywhere in the payload.
`scripts/run_marketplace.py` reports a failed job as `{"job": ...,
"error": "<ExceptionClass>"}` and exits 1.

## Checks (offline)

```bash
uv sync --frozen --all-extras          # runtime deps + dev extra (pytest, ruff, mypy) from uv.lock
uv run ruff check . && uv run ruff format --check .
uv run mypy                            # scope and strictness: [tool.mypy] in pyproject.toml
uv run python -m pytest -q --cov       # CI gate: total coverage >= 92%
uv run python scripts/run_marketplace.py --dry-run --json   # plan only, no network
```

Tests replay `tests/fixtures/` and mock the HTTP layer; a conftest guard fails any real
socket connection. CI (`.github/workflows/ci.yml`, shared platform-ci-workflows v1.1.1)
runs the same checks on Python 3.10 and 3.13. `requirements.txt` is kept because
`setup_cron.sh` installs the cron venv from it; keep it in sync with `pyproject.toml`.

## Error reporting (opt-in)

With `SENTRY_DSN` set (optionally `SENTRY_ENVIRONMENT`), `scripts/run_marketplace.py`
sends one Sentry `error` event per failed job, carrying the job name and exception class
only (`ecommerce/observability.py`; no page content, `send_default_pii=False`, tracing
off). Without a DSN nothing is initialised; `--dry-run` never initialises it.

## Boundaries

- Producer for `marketplace.v1` (draft, collection rejected); it does **not** land data in the lake. The Bronze `marketplace_listings` replay belongs to the parent pipeline and is not wired.
- **Not** coupled to Solo Empire monorepo runtime. Nested Git repo; commit only inside this tree.
- Never commit `.env`, cookies, session dumps, or scraped PII dumps to Git.

## Source terms decision (2026-10-15)

**Kaidee: rejected by the owner on 2026-10-15 (BOO-127).** Kaidee's Thai terms
(clauses 4.3–4.5) prohibit scraper/crawler-style access and require written
Kaidee permission to collect, record, reproduce or use listing and user/contact
data. The 5-page/200-row bounds and two-second pacing do not supply that
permission. Do not run `scripts/run_marketplace.py` (job `kaidee_classifieds`) live or install `setup_cron.sh`; this is policy, not enforced in code;
`marketplace.v1` stays non-approved and the coverage registry marks marketplace
permission `blocked`. Offline synthetic parser fixtures and tests are unaffected.
Reopening requires written Kaidee permission naming URLs, fields, retention,
reuse and volume. This is an owner decision based on the published terms, not
legal advice. Record: architecture-docs `systems/ai-data/source-terms-decisions-2026-10-15.md` (private repository).
Source: [Kaidee terms (TH)](https://support.kaidee.com/hc/th/articles/360000885847).

## Limitations (honest)

Marketplace ToS often forbid scraping. Treat as learning/prototype code only; no secrets; no mass commercial harvest claims.

## Related

- Active collection product: `book-job-scraping` (Tier A tool)
- Lake products: `book-crypto-data`, `book-fx-data`, `book-stock-data`, …
- Solo Empire catalog: `repository-catalog/BOOK-DEV-BACKLOG-BD.md` (BD-012)
