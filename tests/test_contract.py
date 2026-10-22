"""SPEC-001 AC-05: the snapshot CSV matches the marketplace.v1 contract, offline.

The contract lives in the private architecture-docs repository
(``systems/architecture/scraping-contracts/marketplace.v1.yaml``), which CI cannot
read, so the fields this producer must honour are copied here. If the contract
changes, update ``CONTRACT_*`` from that file in the same commit as the code.
Copied 2026-10-22 from contract status ``draft``, ``collection_approval: rejected``.
"""

import asyncio
import csv
import re
from pathlib import Path
from unittest.mock import patch

from ecommerce.kaidee_scraper import SNAPSHOT_FIELDS, KaideeScraper, parse_html

CONTRACT_RECORD_FIELDS = [
    "captured_at",
    "listing_id",
    "title",
    "price_thb",
    "currency",
    "purpose",
    "category",
    "condition",
    "location",
    "url",
    "image_url",
    "seller_role",
    "first_approved_at",
    "source_url",
]
CONTRACT_REQUIRED = ["captured_at", "listing_id", "title", "url", "source_url"]
# Fields the contract never lists: seller contact data must not reach the snapshot.
PERSONAL_FIELDS = {"phone", "email", "line_id", "seller_name", "contact_name", "address"}
UTC_SECONDS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

FIXTURE = Path(__file__).parent / "fixtures" / "kaidee_home.html"


class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        return None


def _snapshot_rows(tmp_path):
    scraper = KaideeScraper(urls=["https://www.kaidee.com/"], output_dir=tmp_path)
    with patch("ecommerce.http.httpx.get", return_value=FakeResponse(FIXTURE.read_text(encoding="utf-8"))):
        asyncio.run(scraper.run())
    with (tmp_path / "kaidee_classifieds.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def test_snapshot_fields_are_the_contract_record_fields_in_order():
    assert SNAPSHOT_FIELDS == CONTRACT_RECORD_FIELDS
    assert not PERSONAL_FIELDS & set(SNAPSHOT_FIELDS)


def test_written_snapshot_header_and_required_fields(tmp_path):
    header, rows = _snapshot_rows(tmp_path)

    assert header == CONTRACT_RECORD_FIELDS
    assert rows
    for row in rows:
        missing = [field for field in CONTRACT_REQUIRED if not row[field]]
        assert missing == [], f"listing {row['listing_id']} misses {missing}"
        assert UTC_SECONDS.match(row["captured_at"]), row["captured_at"]
        assert row["currency"] == "THB"
        assert row["url"].startswith("https://www.kaidee.com/")


def test_identity_is_unique_within_one_capture(tmp_path):
    # Identity is <source>|<listing_id>; one capture holds a single source, so
    # listing_id must not repeat (duplicate_policy picks the latest capture downstream).
    _header, rows = _snapshot_rows(tmp_path)
    ids = [row["listing_id"] for row in rows]
    assert len(ids) == len(set(ids))


def test_parser_never_emits_a_row_without_identity():
    _payload, rows = parse_html(FIXTURE.read_text(encoding="utf-8"))
    assert all(row["listing_id"].isdigit() and int(row["listing_id"]) > 0 for row in rows)
