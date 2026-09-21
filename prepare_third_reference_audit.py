"""Prepare a third, non-overlapping reference audit sample.

The sample is drawn from the current 1,416-row candidate and excludes records
already reviewed in either the development or holdout controls.  PDF evidence
is extracted independently from the source pages; no external API is called.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import unicodedata
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "referencias_parseadas_candidate.json"
PRIOR_AUDITS = [
    ROOT / "data" / "auditoria_referencias_control.json",
    ROOT / "data" / "auditoria_referencias_holdout.json",
]
OUTPUT = ROOT / "tmp" / "third_reference_audit_packet.json"
SEED = 20260919
SAMPLE_SIZE = 100


def folded(text: str | None) -> str:
    value = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return "".join(char for char in value if char.isalnum())


def identity_key(row: dict) -> tuple:
    corrections = row.get("corrections") or {}
    return (
        row["document_id"],
        folded(corrections.get("surname", row.get("surname"))),
        corrections.get("year", row.get("year")),
        folded(corrections.get("title", row.get("title"))),
    )


def main() -> None:
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    prior_rows = [
        row
        for path in PRIOR_AUDITS
        for row in json.loads(path.read_text(encoding="utf-8"))["sample"]
    ]
    prior_keys = {identity_key(row) for row in prior_rows}
    prior_entries = {(row["document_id"], row.get("entry")) for row in prior_rows}

    full_population = [
        dict(reference, document_id=doc_id, source_pdf=document["source_pdf"], reference_index=index)
        for doc_id, document in sorted(data["documents"].items())
        for index, reference in enumerate(document["references"], start=1)
    ]
    eligible = [
        row for row in full_population
        if identity_key(row) not in prior_keys
        and (row["document_id"], row.get("entry")) not in prior_entries
    ]
    sample = random.Random(SEED).sample(eligible, SAMPLE_SIZE)
    sample.sort(key=lambda row: (row["document_id"], row["reference_index"]))

    by_pdf: dict[str, list[dict]] = {}
    for position, row in enumerate(sample, start=1):
        row["sample_id"] = f"T-{position:03d}"
        title = folded(row.get("title"))
        entry = folded(row.get("entry"))
        row["automatic_evidence"] = {
            "title_literal_in_entry": bool(title) and title in entry,
            "surname_literal_in_entry": bool(folded(row.get("surname"))) and folded(row.get("surname")) in entry,
            "year_literal_or_forthcoming": (
                str(row.get("year")) in row.get("entry", "")
                if row.get("year") is not None
                else bool(re.search(r"forthcoming|en prensa", row.get("entry", ""), re.I))
            ),
            "year_mentions": re.findall(r"(?<!\d)(?:18\d{2}|19\d{2}|20[0-2]\d)(?!\d)", row.get("entry", "")),
        }
        by_pdf.setdefault(row["source_pdf"], []).append(row)

    for relative_path, rows in by_pdf.items():
        with pdfplumber.open(ROOT / relative_path) as pdf:
            for row in rows:
                contexts: list[str] = []
                probe = folded(row.get("title") or row.get("entry"))[:80]
                for page_number in range(row["page_start"], row["page_end"] + 1):
                    lines = (pdf.pages[page_number - 1].extract_text() or "").splitlines()
                    scores: list[int] = []
                    for index in range(len(lines)):
                        text = folded(" ".join(lines[index:index + 5]))
                        scores.append(sum(
                            probe[offset:offset + 8] in text
                            for offset in range(0, max(1, len(probe) - 7), 4)
                        ))
                    best = max(range(len(scores)), key=lambda index: scores[index]) if scores else 0
                    contexts.append(
                        f"Página PDF {page_number}:\n"
                        + "\n".join(lines[max(0, best - 3):best + 10])
                    )
                row["pdf_context"] = "\n".join(contexts)

    packet = {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "parser_sha256": hashlib.sha256((ROOT / "parse_refs.py").read_bytes()).hexdigest(),
        "seed": SEED,
        "design": (
            "Tercera muestra aleatoria simple sin reemplazo de 100 filas sobre la candidata vigente. "
            "Se excluyeron por identidad corregida y cadena literal los 200 registros de los controles "
            "de desarrollo y reserva. La evidencia PDF se extrajo independientemente con pdfplumber."
        ),
        "full_population": data["meta"]["reference_entries"],
        "prior_reviewed_records": len(prior_rows),
        "eligible_population": len(eligible),
        "sample_size": SAMPLE_SIZE,
        "sample": sample,
    }
    OUTPUT.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in packet.items() if key != "sample"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
