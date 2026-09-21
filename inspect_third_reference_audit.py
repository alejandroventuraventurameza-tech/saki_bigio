"""Print bounded slices of the third reference-audit packet for review."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "tmp" / "third_reference_audit_packet.json"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--only-suspicious", action="store_true")
    args = parser.parse_args()
    rows = json.loads(PACKET.read_text(encoding="utf-8"))["sample"]
    if args.only_suspicious:
        rows = [
            row for row in rows
            if row.get("quality_flags")
            or not all(row["automatic_evidence"].get(key) for key in (
                "title_literal_in_entry", "surname_literal_in_entry", "year_literal_or_forthcoming"
            ))
        ]
    selected = rows[args.start - 1:args.start - 1 + args.count]
    print(f"TOTAL={len(rows)} MOSTRADOS={args.start}-{args.start + len(selected) - 1}")
    for row in selected:
        print(
            f"\n[{row['sample_id']}] {row['document_id']}-R{row['reference_index']:03d} "
            f"p.{row['page_start']}-{row['page_end']} flags={row.get('quality_flags') or '-'}"
        )
        print(f"SURNAME/YEAR/TITLE: {row.get('surname')} | {row.get('year')} | {row.get('title')}")
        print(f"ENTRY: {' '.join((row.get('entry') or '').split())}")
        print(f"PDF CONTEXT:\n{row.get('pdf_context') or ''}")


if __name__ == "__main__":
    main()
