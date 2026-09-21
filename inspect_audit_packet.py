from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "tmp" / "pdfs" / "reference_audit" / "candidate_packet.json"
SOURCE = ROOT / "data" / "referencias_parseadas_candidate.json"


def is_ambiguous(row: dict) -> bool:
    entry_length = len(row.get("entry") or "")
    return bool(
        row.get("quality_flags")
        or row.get("page_match_score", 0) < 0.75
        or entry_length < 100
        or entry_length > 400
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--document")
    parser.add_argument("--source-document")
    parser.add_argument("--context", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()

    if args.source_document:
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        document = source["documents"][args.source_document]
        print(f"TOTAL={len(document['references'])}")
        for index, reference in enumerate(document["references"], 1):
            entry = " ".join((reference.get("entry") or "").split())
            flags = "; ".join(reference.get("quality_flags") or []) or "-"
            print(f"[{index:03d}] [{flags}] {entry}")
        return

    data = json.loads(PACKET.read_text(encoding="utf-8"))
    seen = set()
    rows = []
    for row in data["rows"]:
        key = (row["document_id"], row["candidate_index"])
        if key in seen:
            continue
        seen.add(key)
        if args.document and row["document_id"] != args.document:
            continue
        if not args.all:
            if args.clear and is_ambiguous(row):
                continue
            if not args.clear and not is_ambiguous(row):
                continue
        rows.append(row)
    rows.sort(key=lambda row: (row["document_id"], row["candidate_index"]))
    selected = rows[args.start : args.start + args.count]
    print(f"TOTAL={len(rows)} MOSTRADOS={args.start + 1}-{args.start + len(selected)}")
    for index, row in enumerate(selected, args.start + 1):
        entry = " ".join((row.get("entry") or "").split())
        print(
            f"\n[{index:03d}] {row['document_id']}:{row['candidate_index']} "
            f"p.{row['page_number']} score={row['page_match_score']} "
            f"flags={row['quality_flags'] or '-'}"
        )
        print(f"ENTRY: {entry}")
        if args.context:
            previous = " ".join((row.get("previous_entry") or "").split())
            following = " ".join((row.get("next_entry") or "").split())
            context = "\n".join(line.rstrip() for line in (row.get("page_context") or "").splitlines())
            print(f"PREV: {previous}")
            print(f"NEXT: {following}")
            print(f"PAGE CONTEXT:\n{context}")


if __name__ == "__main__":
    main()
