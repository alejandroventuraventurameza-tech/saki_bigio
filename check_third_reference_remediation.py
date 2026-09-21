"""Regression check for the two title defects in the third audit sample."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CANDIDATE = DATA / "referencias_parseadas_candidate.json"
AUDIT = DATA / "auditoria_referencias_tercera_muestra.json"
OUTPUT = DATA / "auditoria_referencias_tercera_muestra_remediacion.json"


def norm(value: str | None) -> str:
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def main() -> None:
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    checks: list[dict] = []
    for reviewed in audit["sample"]:
        corrections = reviewed.get("corrections") or {}
        expected_surname = corrections.get("surname", reviewed.get("surname"))
        expected_year = corrections.get("year", reviewed.get("year"))
        expected_title = corrections.get("title", reviewed.get("title"))
        matches = [
            ref for ref in candidate["documents"][reviewed["document_id"]]["references"]
            if ref.get("year") == expected_year
            and norm(ref.get("surname")) == norm(expected_surname)
            and norm(ref.get("title")) == norm(expected_title)
        ]
        checks.append({
            "sample_id": reviewed["sample_id"],
            "document_id": reviewed["document_id"],
            "prior_record_ready": reviewed["record_ready"],
            "remediated": len(matches) == 1,
            "matched_records": matches,
        })

    passed = sum(row["remediated"] for row in checks)
    output = {
        "candidate_sha256": hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
        "design": "Regresión sobre los 100 casos de la tercera muestra después de aplicar sus dos correcciones; no es una cuarta muestra.",
        "prior_third_sample_record_ready": audit["metrics"]["record_ready"],
        "remediation_checks_passed": passed,
        "remediation_checks_failed": len(checks) - passed,
        "network_release": False,
        "network_release_reason": "La remediación reutiliza la tercera muestra y no reemplaza una auditoría humana externa.",
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in output.items() if key != "checks"}, ensure_ascii=False, indent=2))
    if passed != len(checks):
        raise SystemExit("Fallo de remediación en la tercera muestra")


if __name__ == "__main__":
    main()
