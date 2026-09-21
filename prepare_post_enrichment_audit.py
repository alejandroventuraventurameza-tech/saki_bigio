"""Prepare a holdout audit after local reference enrichment.

The sample excludes the 100 development-control entries whenever their literal
entry survives unchanged.  PDF contexts are extracted independently and no
external service is contacted.
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
PRIOR = ROOT / "data" / "auditoria_referencias_control.json"
OUTPUT = ROOT / "tmp" / "post_enrichment_control.json"
SEED = 20260918


def folded(text: str | None) -> str:
    value = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return "".join(char for char in value if char.isalnum())


def main() -> None:
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    development_entries = {(row["document_id"], row["entry"]) for row in prior["sample"]}
    population = [
        dict(reference, document_id=doc_id, source_pdf=document["source_pdf"], reference_index=index)
        for doc_id, document in sorted(data["documents"].items())
        for index, reference in enumerate(document["references"], start=1)
        if (doc_id, reference["entry"]) not in development_entries
    ]
    sample = random.Random(SEED).sample(population, 100)
    sample.sort(key=lambda row: (row["document_id"], row["reference_index"]))
    by_pdf: dict[str, list[dict]] = {}
    for position, row in enumerate(sample, start=1):
        row["sample_id"] = f"H-{position:03d}"
        title = folded(row.get("title"))
        entry = folded(row.get("entry"))
        row["automatic_evidence"] = {
            "title_literal_in_entry": bool(title) and title in entry,
            "surname_literal_in_entry": folded(row.get("surname")) in entry,
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
                probe = folded(row.get("title") or row.get("entry"))[:60]
                for page_number in range(row["page_start"], row["page_end"] + 1):
                    lines = (pdf.pages[page_number - 1].extract_text() or "").splitlines()
                    scores: list[int] = []
                    for index in range(len(lines)):
                        text = folded(" ".join(lines[index:index + 4]))
                        scores.append(sum(probe[offset:offset + 8] in text for offset in range(0, max(1, len(probe) - 7), 4)))
                    best = max(range(len(scores)), key=lambda index: scores[index]) if scores else 0
                    contexts.append(f"Página PDF {page_number}:\n" + "\n".join(lines[max(0, best - 2):best + 8]))
                row["pdf_context"] = "\n".join(contexts)

    packet = {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "parser_sha256": hashlib.sha256((ROOT / "parse_refs.py").read_bytes()).hexdigest(),
        "seed": SEED,
        "design": (
            "Muestra aleatoria simple sin reemplazo de 100 filas tomada de las entradas que no coinciden "
            "literalmente con la muestra de desarrollo de 2026-09-15. Evidencia PDF extraída con pdfplumber."
        ),
        "full_population": data["meta"]["reference_entries"],
        "holdout_population": len(population),
        "sample": sample,
    }
    OUTPUT.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in packet.items() if key != "sample"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
