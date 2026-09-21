"""Print compact page evidence for a slice of the exhaustive AI audit queue."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "tmp" / "exhaustive_ai_audit_packet.json"


def norm(value: str | None) -> str:
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def context(row: dict) -> str:
    lines = row["pdf_page_text"].splitlines()
    probe = norm(row.get("title") or row.get("entry"))
    grams = {probe[index:index + 8] for index in range(0, max(1, len(probe) - 7), 4)}
    scores = []
    for index in range(len(lines)):
        window = norm(" ".join(lines[index:index + 7]))
        scores.append(sum(gram in window for gram in grams))
    best = max(range(len(scores)), key=scores.__getitem__) if scores else 0
    return "\n".join(lines[max(0, best - 4):best + 14])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    args = parser.parse_args()
    rows = json.loads(PACKET.read_text(encoding="utf-8"))["visual_review_rows"]
    for position, row in enumerate(rows[args.start - 1:args.end], start=args.start):
        print("=" * 100)
        print(position, row["ref_id"], row.get("surname"), row.get("year"), row.get("title"))
        print("ENTRY:", row.get("entry"))
        print("CHECKS:", json.dumps(row["automatic_checks"], ensure_ascii=False))
        print(context(row))


if __name__ == "__main__":
    main()
