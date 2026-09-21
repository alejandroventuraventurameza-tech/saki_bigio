"""Check that every defect found in the 100-row control was remediated.

This is a regression/remediation check on the same adjudicated sample.  It is not
an independent estimate of post-correction accuracy and cannot release networks.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CANDIDATE = DATA / "referencias_parseadas_candidate.json"
AUDIT = DATA / "auditoria_referencias_control.json"
OUTPUT = DATA / "auditoria_referencias_remediacion.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def norm(value: str | None) -> str:
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def direct_candidates(document: dict, reviewed: dict) -> list[dict]:
    refs = document["references"]
    exact = [ref for ref in refs if ref.get("entry") == reviewed.get("entry")]
    if exact:
        return exact
    expected_surname = (reviewed.get("corrections") or {}).get("surname", reviewed.get("surname"))
    expected_year = (reviewed.get("corrections") or {}).get("year", reviewed.get("year"))
    expected_title = (reviewed.get("corrections") or {}).get("title", reviewed.get("title"))
    matches = [
        ref for ref in refs
        if (expected_year is None or ref.get("year") == expected_year)
        and (not expected_surname or norm(expected_surname) in norm(ref.get("surname")))
        and (not expected_title or norm(expected_title) == norm(ref.get("title")))
    ]
    return matches


def main() -> None:
    candidate = load(CANDIDATE)
    audit = load(AUDIT)
    checks: list[dict] = []

    for reviewed in audit["sample"]:
        doc_id = reviewed["document_id"]
        if reviewed["sample_id"] == "C-086":
            matches = [
                ref for ref in candidate["documents"][doc_id]["references"]
                if ref.get("surname") == "Woodford" and ref.get("year") in {1998, 1999, 2010}
                and "C-086" in ref.get("correction_provenance", [])
            ]
            remediated = len(matches) == 3 and all(ref.get("title") for ref in matches)
            action = "split_into_three"
        else:
            matches = direct_candidates(candidate["documents"][doc_id], reviewed)
            remediated = len(matches) == 1
            action = "field_or_segmentation_check"
            if remediated:
                ref = matches[0]
                expected = reviewed.get("corrections") or {}
                if "surname" in expected:
                    remediated = norm(ref.get("surname")) == norm(expected["surname"])
                if "year" in expected:
                    remediated = remediated and ref.get("year") == expected["year"]
                if "title" in expected:
                    remediated = remediated and norm(ref.get("title")) == norm(expected["title"])
                if not reviewed.get("title_correct") and "title" not in expected:
                    remediated = remediated and bool(ref.get("title"))
                if reviewed["sample_id"] == "C-065":
                    remediated = remediated and "research vision" not in ref.get("entry", "").lower()

        checks.append({
            "sample_id": reviewed["sample_id"],
            "document_id": doc_id,
            "prior_verdict": reviewed["verdict"],
            "prior_record_ready": reviewed["record_ready"],
            "action": action,
            "remediated": remediated,
            "matched_records": [
                {
                    "surname": ref.get("surname"),
                    "year": ref.get("year"),
                    "title": ref.get("title"),
                    "entry": ref.get("entry"),
                    "correction_provenance": ref.get("correction_provenance", []),
                }
                for ref in matches
            ],
        })

    passed = sum(item["remediated"] for item in checks)
    output = {
        "candidate_sha256": hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
        "design": (
            "Comprobación de remediación sobre los mismos 100 casos adjudicados el 2026-09-15. "
            "No es una nueva muestra ni una auditoría independiente."
        ),
        "population_after_correction": candidate["meta"]["reference_entries"],
        "prior_sample_size": len(checks),
        "prior_record_ready": audit["metrics"]["record_ready"],
        "remediation_checks_passed": passed,
        "remediation_checks_failed": len(checks) - passed,
        "network_release": False,
        "network_release_reason": (
            "La regresión sobre los casos conocidos no estima el error fuera de la muestra y las identidades "
            "DOI/OpenAlex aún no se han resuelto."
        ),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in output.items() if key != "checks"}, ensure_ascii=False, indent=2))
    if passed != len(checks):
        raise SystemExit("Fallo de remediación: revisar los casos marcados como false")


if __name__ == "__main__":
    main()
