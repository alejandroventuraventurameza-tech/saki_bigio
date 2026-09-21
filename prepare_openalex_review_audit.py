"""Build a PDF-grounded review packet for provisional OpenAlex matches."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parent
CANDIDATE = ROOT / "data" / "referencias_parseadas_candidate.json"
RESOLUTION = ROOT / "data" / "openalex" / "openalex_reference_resolution_authenticated.json"
OUTPUT = ROOT / "tmp" / "openalex_review_packet.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    candidate = load(CANDIDATE)
    resolution = load(RESOLUTION)
    rows: list[dict] = []
    pdf_cache: dict[str, pdfplumber.PDF] = {}
    try:
        for match in resolution["references"]:
            if match["status"] != "matched_review":
                continue
            doc_id = match["doc_id"]
            source_pdf = candidate["documents"][doc_id]["source_pdf"]
            if source_pdf not in pdf_cache:
                pdf_cache[source_pdf] = pdfplumber.open(ROOT / source_pdf)
            pdf = pdf_cache[source_pdf]
            contexts = []
            first, last = match["source_pages"]
            for page_number in range(first, last + 1):
                text = pdf.pages[page_number - 1].extract_text() or ""
                contexts.append(f"Página PDF {page_number}:\n{text}")
            rows.append({
                **match,
                "source_pdf": source_pdf,
                "pdf_context": "\n\n".join(contexts),
            })
    finally:
        for pdf in pdf_cache.values():
            pdf.close()

    packet = {
        "candidate_sha256": hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
        "resolution_sha256": hashlib.sha256(RESOLUTION.read_bytes()).hexdigest(),
        "review_population": len(rows),
        "design": (
            "Revisión exhaustiva de todas las coincidencias matched_review. "
            "Cada caso conserva la referencia extraída, el candidato OpenAlex, la evidencia algorítmica "
            "y el texto completo de las páginas PDF declaradas por el extractor."
        ),
        "cases": rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"review_population": len(rows), "output": str(OUTPUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
