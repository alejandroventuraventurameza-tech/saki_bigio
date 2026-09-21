"""Build a corpus-wide AI-assisted audit and isolate rows needing visual review."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "referencias_parseadas_candidate.json"
OUTPUT = ROOT / "tmp" / "exhaustive_ai_audit_packet.json"
PRIOR_AUDITS = [
    ROOT / "data" / "auditoria_referencias_control.json",
    ROOT / "data" / "auditoria_referencias_holdout.json",
    ROOT / "data" / "auditoria_referencias_tercera_muestra.json",
]


def norm(value: str | None) -> str:
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def identity_key(document_id: str, row: dict) -> tuple:
    corrections = row.get("corrections") or {}
    return (
        document_id,
        norm(corrections.get("surname", row.get("surname"))),
        corrections.get("year", row.get("year")),
        norm(corrections.get("title", row.get("title"))),
    )


def main() -> None:
    candidate = json.loads(SOURCE.read_text(encoding="utf-8"))
    prior_rows = [
        row
        for path in PRIOR_AUDITS
        for row in json.loads(path.read_text(encoding="utf-8"))["sample"]
    ]
    reviewed = {identity_key(row["document_id"], row) for row in prior_rows}
    reviewed_entries = {(row["document_id"], row.get("entry")) for row in prior_rows}
    all_rows: list[dict] = []
    suspicious: list[dict] = []
    for document_id, document in candidate["documents"].items():
        for reference_index, reference in enumerate(document["references"], start=1):
            entry = reference.get("entry") or ""
            title = reference.get("title")
            surname = reference.get("surname")
            flags = reference.get("quality_flags", [])
            years = re.findall(r"(?<!\d)(?:18\d{2}|19\d{2}|20[0-2]\d)(?!\d)", entry)
            checks = {
                "title_literal": not title or norm(title) in norm(entry),
                "surname_literal_or_inherited": norm(surname) in norm(entry) or "inherited_author_notation" in flags,
                "year_literal_or_forthcoming": (
                    str(reference.get("year")) in entry
                    if reference.get("year") is not None
                    else bool(re.search(r"forthcoming|en prensa", entry, re.I))
                ),
                "long_entry": len(entry) > 700,
                "four_or_more_distinct_years": len(set(years)) >= 4,
                "known_contamination_marker": any(
                    marker.lower() in entry.lower()
                    for marker in (
                        "references references", "papers & work in progress",
                        "the american economic review month year", "vol. volume no. issue",
                    )
                ),
            }
            prior_reviewed = (
                identity_key(document_id, reference) in reviewed
                or (document_id, reference.get("entry")) in reviewed_entries
            )
            needs_review = not prior_reviewed and (
                not checks["title_literal"]
                or not checks["surname_literal_or_inherited"]
                or not checks["year_literal_or_forthcoming"]
                or checks["long_entry"]
                or checks["four_or_more_distinct_years"]
                or checks["known_contamination_marker"]
            )
            row = {
                "ref_id": f"{document_id}-R{reference_index:03d}",
                "document_id": document_id,
                "reference_index": reference_index,
                "source_pdf": document["source_pdf"],
                **reference,
                "prior_manually_reviewed": prior_reviewed,
                "automatic_checks": checks,
                "needs_visual_review": needs_review,
            }
            all_rows.append(row)
            if needs_review:
                suspicious.append(row)

    by_pdf: dict[str, list[dict]] = {}
    for row in suspicious:
        by_pdf.setdefault(row["source_pdf"], []).append(row)
    for relative_pdf, rows in by_pdf.items():
        with pdfplumber.open(ROOT / relative_pdf) as pdf:
            for row in rows:
                page_texts = []
                for page_number in range(row["page_start"], row["page_end"] + 1):
                    text = pdf.pages[page_number - 1].extract_text() or ""
                    page_texts.append(f"Página PDF {page_number}:\n{text}")
                row["pdf_page_text"] = "\n".join(page_texts)

    packet = {
        "source": str(SOURCE.relative_to(ROOT)),
        "population": len(all_rows),
        "prior_manual_sample_rows": len(prior_rows),
        "prior_reviewed_rows_mapped_to_current_candidate": sum(row["prior_manually_reviewed"] for row in all_rows),
        "automatic_pass_without_prior_manual_review": sum(
            not row["prior_manually_reviewed"] and not row["needs_visual_review"] for row in all_rows
        ),
        "visual_review_queue": len(suspicious),
        "rows": all_rows,
        "visual_review_rows": suspicious,
    }
    OUTPUT.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in packet.items() if key not in {"rows", "visual_review_rows"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
