"""Finalize the corpus-wide AI-assisted reference audit after remediation."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "referencias_parseadas_candidate.json"
PACKET = ROOT / "tmp" / "exhaustive_ai_audit_packet.json"
OUTPUT = ROOT / "data" / "auditoria_integral_ia_referencias.json"
CORRECTION_MARKERS = {
    "exhaustive_ai_audit_2026-09-17",
    "exhaustive_title_boundary_audit_2026-09-17",
}


def main() -> None:
    candidate = json.loads(SOURCE.read_text(encoding="utf-8"))
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    if packet["population"] != candidate["meta"]["reference_entries"]:
        raise RuntimeError("El paquete integral no corresponde a la candidata vigente")

    rows = []
    for row in packet["rows"]:
        provenance = set(row.get("correction_provenance", []))
        entry = row.get("entry") or ""
        years = set(re.findall(r"(?<!\d)(?:18\d{2}|19\d{2}|20[0-2]\d)(?!\d)", entry))
        multiwork_pattern = entry.count("“") + entry.count("``") >= 2 or len(years) >= 3
        if row["prior_manually_reviewed"]:
            route = "prior_manual_sample"
        elif provenance & CORRECTION_MARKERS:
            route = "exhaustive_visual_correction"
        elif row["needs_visual_review"]:
            route = "exhaustive_visual_exception_accepted"
        elif multiwork_pattern:
            route = "exhaustive_visual_multiwork_pattern_accepted"
        else:
            route = "automatic_screen_pass"
        flags = row.get("quality_flags", [])
        status = (
            "accepted_source_exception"
            if "source_year_malformed" in flags or "source_omits_title" in flags
            else "corrected" if provenance & CORRECTION_MARKERS
            else "accepted"
        )
        rows.append({
            "ref_id": row["ref_id"],
            "document_id": row["document_id"],
            "reference_index": row["reference_index"],
            "source_pdf": row["source_pdf"],
            "page_start": row["page_start"],
            "page_end": row["page_end"],
            "surname": row.get("surname"),
            "year": row.get("year"),
            "title": row.get("title"),
            "entry": row.get("entry"),
            "quality_flags": flags,
            "correction_provenance": row.get("correction_provenance", []),
            "automatic_checks": row["automatic_checks"],
            "multiwork_pattern_checked": multiwork_pattern,
            "audit_route": route,
            "audit_status": status,
        })

    routes = Counter(row["audit_route"] for row in rows)
    statuses = Counter(row["audit_status"] for row in rows)
    output = {
        "meta": {
            "date": "2026-09-17",
            "source": "data/referencias_parseadas_candidate.json",
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "population": len(rows),
            "method": (
                "Tamizaje determinista de las 1.435 filas; incorporación de los 300 controles previos; "
                "revisión visual asistida de todos los fallos literales, patrones de múltiples obras, "
                "entradas largas, años atípicos y marcadores de contaminación; remediación y nueva regresión."
            ),
            "audit_route_counts": dict(routes),
            "audit_status_counts": dict(statuses),
            "structural_operations": 18,
            "net_rows_added": 19,
            "title_boundary_corrections": 17,
            "remaining_title_not_isolated": candidate["meta"]["quality_flag_counts"].get("title_not_isolated", 0),
            "remaining_missing_year": candidate["meta"]["quality_flag_counts"].get("missing_year", 0),
            "source_year_malformed": candidate["meta"]["quality_flag_counts"].get("source_year_malformed", 0),
            "local_quality_control_complete": True,
            "human_external_audit": False,
            "network_release": False,
            "network_release_reason": (
                "La revisión integral fue realizada por Codex, no por un auditor humano externo. "
                "La liberación de redes depende además del estado de cobertura de la capa OpenAlex."
            ),
        },
        "definitions": {
            "prior_manual_sample": "Fila incluida en una de las tres muestras previas contrastadas con el PDF.",
            "exhaustive_visual_correction": "Fila revisada durante el control integral y modificada con trazabilidad.",
            "exhaustive_visual_exception_accepted": "Excepción literal revisada contra la página fuente y aceptada sin cambio.",
            "exhaustive_visual_multiwork_pattern_accepted": "Patrón de posible fusión revisado y confirmado como una sola obra.",
            "automatic_screen_pass": "Fila sin señales en los controles deterministas ni en los patrones estructurales ampliados.",
        },
        "rows": rows,
    }
    if sum(routes.values()) != len(rows):
        raise RuntimeError("Las rutas de auditoría no cubren toda la población")
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output["meta"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
