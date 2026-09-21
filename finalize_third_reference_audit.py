"""Adjudicate the third, non-overlapping 100-row reference sample."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "referencias_parseadas_candidate.json"
PACKET = ROOT / "tmp" / "third_reference_audit_packet.json"
OUTPUT = ROOT / "data" / "auditoria_referencias_tercera_muestra.json"

TITLE_ERRORS = {
    31: (
        "Monetary Policy Operations and the Financial System",
        "El campo incorporó la editorial y la indicación de primera edición después del título.",
    ),
    84: (
        "The Fed’s “Ample-Reserves” Approach to Implementing Monetary Policy",
        "El título quedó truncado dentro de la expresión entre comillas «Ample-Reserves».",
    ),
}


def wilson(successes: int, total: int) -> list[float]:
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return [center - half, center + half]


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != packet["source_sha256"]:
        raise RuntimeError("La base cambió después de preparar la tercera muestra")

    for row in packet["sample"]:
        number = int(row["sample_id"].split("-")[1])
        corrections: dict[str, object] = {}
        row["verdict"] = "correcta"
        row["surname_correct"] = True
        row["year_correct"] = True
        row["title_correct"] = number not in TITLE_ERRORS
        if number in TITLE_ERRORS:
            corrections["title"] = TITLE_ERRORS[number][0]
            row["review_note"] = TITLE_ERRORS[number][1]
        else:
            row["review_note"] = "Una referencia completa; apellido, año y título concuerdan con el PDF."
        row["corrections"] = corrections
        row["basic_fields_ready"] = True
        row["record_ready"] = row["title_correct"]
        row["reviewer"] = "Codex (tercera muestra independiente asistida; no auditor humano externo)"
        row["review_date"] = "2026-09-17"

    rows = packet["sample"]
    total = len(rows)
    metrics = {
        "sample_size": total,
        "segmentation_correct": sum(row["verdict"] == "correcta" for row in rows),
        "basic_fields_ready": sum(row["basic_fields_ready"] for row in rows),
        "record_ready": sum(row["record_ready"] for row in rows),
        "verdict_counts": dict(Counter(row["verdict"] for row in rows)),
        "incorrect_titles": len(TITLE_ERRORS),
        "incorrect_surnames": 0,
        "incorrect_years": 0,
        "release_threshold": 0.95,
    }
    for key in ("segmentation_correct", "basic_fields_ready", "record_ready"):
        metrics[f"{key}_rate"] = metrics[key] / total
        metrics[f"{key}_wilson95"] = wilson(metrics[key], total)

    packet["metrics"] = metrics
    packet["network_release"] = False
    packet["network_release_reason"] = (
        "La muestra supera el umbral puntual local después de corregir dos títulos, pero no constituye "
        "una auditoría humana externa y la cobertura de identidad OpenAlex continúa incompleta."
    )
    packet["definitions"] = {
        "third_sample": (
            "Muestra aleatoria nueva que excluye los 200 registros de los controles de desarrollo y reserva; "
            "fue revisada por el mismo sistema y no por un auditor humano externo."
        ),
        "segmentation_correct": "La fila contiene una referencia y no incorpora encabezados, tablas ni otra referencia.",
        "basic_fields_ready": "Segmentación correcta, apellido inicial y año fieles al PDF.",
        "record_ready": "Criterio básico más título completo aislado.",
    }
    OUTPUT.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
