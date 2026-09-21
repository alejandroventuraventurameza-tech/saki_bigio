"""Attach only cached high-confidence OpenAlex matches to a separate candidate.

The locally audited source remains untouched.  This output is intentionally
partial and cannot be used to release citation networks or historical shares.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "referencias_parseadas_candidate.json"
RESOLUTION = ROOT / "data" / "openalex" / "openalex_reference_resolution_partial.json"
OUTPUT = ROOT / "data" / "referencias_parseadas_candidate_openalex_partial.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resolution", type=Path, default=RESOLUTION)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.resolution = args.resolution.resolve()
    args.output = args.output.resolve()

    candidate = load(SOURCE)
    resolution = load(args.resolution)
    accepted = {
        row["ref_id"]: row
        for row in resolution["references"]
        if row["status"] == "matched_high_confidence"
    }

    attached = 0
    ids: set[str] = set()
    for doc_id, document in candidate["documents"].items():
        for index, reference in enumerate(document["references"], start=1):
            ref_id = f"{doc_id}-R{index:03d}"
            match = accepted.get(ref_id)
            if not match:
                continue
            best = match["best_match"]
            reference["openalex_resolution"] = {
                "status": match["status"],
                "id": best["id"],
                "doi": best["doi"],
                "display_name": best["display_name"],
                "publication_year": best["publication_year"],
                "type": best["type"],
                "authors": best["authors"],
                "evidence": best["evidence"],
                "query_url": match["query_url"],
            }
            attached += 1
            ids.add(best["id"])

    if attached != len(accepted):
        raise RuntimeError(f"Se adjuntaron {attached} de {len(accepted)} coincidencias aceptadas")

    resolution_complete = (
        resolution["meta"]["records_returned"] == candidate["meta"]["reference_entries"]
        and not resolution["meta"].get("errors")
    )
    candidate["meta"].update({
        "status": (
            "candidate_openalex_high_confidence_layer_complete"
            if resolution_complete else "candidate_partially_resolved_openalex_rate_limited"
        ),
        "openalex_resolution_source_sha256": sha256(args.resolution),
        "openalex_resolution_complete": resolution_complete,
        "openalex_high_confidence_rows_attached": attached,
        "openalex_unique_ids_attached": len(ids),
        "openalex_matched_review_rows": resolution["meta"]["status_counts"].get("matched_review", 0),
        "openalex_unresolved_rows": resolution["meta"]["status_counts"].get("unresolved", 0),
        "openalex_rows_without_high_confidence_identity": (
            candidate["meta"]["reference_entries"] - attached
        ),
        "network_release": False,
        "network_release_reason": (
            "Aunque todas las filas fueron consultadas, las coincidencias provisionales y no resueltas "
            "impiden tratar la capa como una enumeración completa de identidades."
            if resolution_complete else
            "La resolución de identidades OpenAlex permanece incompleta."
        ),
        "warning": (
            "Copia separada: adjunta únicamente coincidencias OpenAlex de alta confianza. "
            "No sustituye la candidata local auditada ni promueve coincidencias provisionales."
        ),
    })
    candidate["provenance"] = {
        "local_candidate": str(SOURCE.relative_to(ROOT)),
        "local_candidate_sha256": sha256(SOURCE),
        "partial_resolution": str(args.resolution.relative_to(ROOT)),
        "partial_resolution_sha256": sha256(args.resolution),
    }
    args.output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "attached_rows": attached,
        "unique_openalex_ids": len(ids),
        "network_release": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
