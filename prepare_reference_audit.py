from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pdfplumber
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parent
WORKBOOK = ROOT / "data" / "auditoria_referencias.xlsx"
SOURCE_JSON = ROOT / "data" / "referencias_parseadas_candidate.json"
OUT_DIR = ROOT / "tmp" / "pdfs" / "reference_audit"
PACKET = OUT_DIR / "candidate_packet.json"


def fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", ascii_text.lower()))


def extract_rows() -> list[dict]:
    workbook = load_workbook(WORKBOOK, read_only=True, data_only=False)
    rows: list[dict] = []
    for sheet_name, first_row, last_row, sample_kind in [
        ("Auditoría aleatoria", 9, 158, "aleatoria"),
        ("Casos dirigidos", 6, 48, "dirigida"),
    ]:
        sheet = workbook[sheet_name]
        for excel_row in range(first_row, last_row + 1):
            values = [sheet.cell(excel_row, column).value for column in range(1, 18)]
            if sample_kind == "aleatoria":
                sample_id, document_id, source_pdf, candidate_index = values[:4]
                offset = 0
                reason = "muestra aleatoria"
            else:
                reason, document_id, source_pdf, candidate_index = values[:4]
                sample_id = f"D{excel_row - first_row + 1:03d}"
                offset = 0
            if not document_id:
                continue
            rows.append(
                {
                    "sheet": sheet_name,
                    "excel_row": excel_row,
                    "sample_kind": sample_kind,
                    "sample_id": sample_id,
                    "reason": reason,
                    "document_id": str(document_id),
                    "source_pdf": str(source_pdf),
                    "candidate_index": int(candidate_index),
                    "surname": values[4],
                    "year": values[5],
                    "title": values[6],
                    "entry": values[7],
                    "quality_flags": values[8] or "",
                }
            )
    return rows


def best_page(entry: str, pages: list[str]) -> tuple[int | None, float]:
    target_tokens = fold(entry).split()
    if not target_tokens:
        return None, 0.0
    focus = target_tokens[: min(24, len(target_tokens))]
    best_number = None
    best_score = -1.0
    phrase = " ".join(focus[: min(8, len(focus))])
    for page_number, page_text in enumerate(pages, 1):
        page_folded = fold(page_text)
        page_tokens = set(page_folded.split())
        coverage = sum(token in page_tokens for token in focus) / len(focus)
        phrase_bonus = 1.0 if phrase and phrase in page_folded else 0.0
        score = coverage + phrase_bonus
        if score > best_score:
            best_number = page_number
            best_score = score
    return best_number, best_score


def context_for(entry: str, page_text: str) -> str:
    lines = [line.rstrip() for line in page_text.splitlines() if line.strip()]
    target = fold(entry)
    target_words = target.split()
    probes = [" ".join(target_words[:count]) for count in (8, 6, 4) if len(target_words) >= count]
    target_index = None
    for index, line in enumerate(lines):
        line_folded = fold(line)
        if any(probe in line_folded for probe in probes):
            target_index = index
            break
    if target_index is None and target_words:
        first = target_words[0]
        for index, line in enumerate(lines):
            if first in fold(line).split():
                target_index = index
                break
    if target_index is None:
        return "\n".join(lines[-12:])
    start = max(0, target_index - 4)
    end = min(len(lines), target_index + 9)
    return "\n".join(lines[start:end])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = extract_rows()
    source = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    original_by_doc = {
        document_id: document["references"] for document_id, document in source["documents"].items()
    }

    unique_pdfs = sorted({row["source_pdf"] for row in rows})
    pdf_pages: dict[str, list[str]] = {}
    pdf_page_counts: dict[str, int] = {}
    for relative_pdf in unique_pdfs:
        pdf_path = ROOT / Path(relative_pdf.replace("/", str(Path("/").anchor or "/")))
        # Path conversion above is platform-neutral; on Windows the original slash form is accepted.
        pdf_path = ROOT / relative_pdf
        with pdfplumber.open(pdf_path) as pdf:
            pages = [page.extract_text(layout=True) or "" for page in pdf.pages]
        pdf_pages[relative_pdf] = pages
        pdf_page_counts[relative_pdf] = len(pages)

    packet_rows = []
    for row in rows:
        pages = pdf_pages[row["source_pdf"]]
        page_number, page_score = best_page(str(row["entry"] or ""), pages)
        original_entries = original_by_doc[row["document_id"]]
        source_index = row["candidate_index"] - 1
        previous_entry = original_entries[source_index - 1]["entry"] if source_index > 0 else None
        next_entry = (
            original_entries[source_index + 1]["entry"]
            if source_index + 1 < len(original_entries)
            else None
        )
        packet_rows.append(
            {
                **row,
                "page_number": page_number,
                "page_match_score": round(page_score, 3),
                "page_context": context_for(str(row["entry"] or ""), pages[page_number - 1])
                if page_number
                else "",
                "previous_entry": previous_entry,
                "next_entry": next_entry,
            }
        )

    packet_data = {
        "meta": {
            "workbook": str(WORKBOOK.relative_to(ROOT)),
            "rows": len(packet_rows),
            "unique_candidates": len(
                {(row["document_id"], row["candidate_index"]) for row in packet_rows}
            ),
            "unique_pdfs": len(unique_pdfs),
            "pdf_page_counts": pdf_page_counts,
        },
        "rows": packet_rows,
    }
    PACKET.write_text(json.dumps(packet_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "packet": str(PACKET),
                "rows": len(packet_rows),
                "unique_candidates": packet_data["meta"]["unique_candidates"],
                "unique_pdfs": len(unique_pdfs),
                "sample_kinds": Counter(row["sample_kind"] for row in rows),
                "low_page_matches": sum(row["page_match_score"] < 0.75 for row in packet_rows),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
