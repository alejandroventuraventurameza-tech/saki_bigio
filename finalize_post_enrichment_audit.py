"""Adjudicate the 100-row holdout sample prepared after local enrichment."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "referencias_parseadas_candidate.json"
PACKET = ROOT / "tmp" / "post_enrichment_control.json"
OUTPUT = ROOT / "data" / "auditoria_referencias_holdout.json"

SEGMENT_ERRORS = {
    17: "Se añadió el encabezado de la página 43 después de la referencia de Gomes.",
    19: "Se añadió el encabezado de la página 44 después de la referencia de Shimer.",
    65: "La entrada de Zetlin-Jones incorporó la tabla PAPERS & WORK IN PROGRESS que sigue a la bibliografía.",
}
SURNAME_ERRORS = {
    84: ("Giannone", "El campo conserva nombre y apellido concatenados; el apellido inicial es Giannone."),
    92: ("Jarociński", "El campo quedó truncado por la marca diacrítica separada del PDF."),
}
TITLE_ERRORS = {
    1: ("Endogenous liquidity and the business cycle", "Se aisló el inicio del DOI, no el título."),
    2: ("El programa económico de agosto de 1990: evaluación del primer año", "Se aisló el bloque de autores posterior a la etiqueta BibTeX."),
    6: ("Una Revisión de la Transmisión Monetaria y el Pass-Through en Chile", "El campo incluyó institución y número del documento."),
    8: ("Uncovering Central Bank’s Monetary Policy Objectives: Going Beyond Fear of Floating", "El campo incluyó la institución editora."),
    10: ("A reconsideration of the empirical Evidence on the Asymmetric Effects of Money-Supply Shocks: Positive vs. Negative or Big vs. Small?", "El título quedó cortado en la abreviatura «vs.»"),
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
        raise RuntimeError("La base cambió después de preparar la muestra de reserva")

    for row in packet["sample"]:
        number = int(row["sample_id"].split("-")[1])
        notes: list[str] = []
        corrections: dict[str, object] = {}
        row["verdict"] = "contaminada" if number in SEGMENT_ERRORS else "correcta"
        row["surname_correct"] = number not in SURNAME_ERRORS
        row["year_correct"] = True
        row["title_correct"] = number not in TITLE_ERRORS
        if number in SEGMENT_ERRORS:
            notes.append(SEGMENT_ERRORS[number])
        if number in SURNAME_ERRORS:
            corrections["surname"] = SURNAME_ERRORS[number][0]
            notes.append(SURNAME_ERRORS[number][1])
        if number in TITLE_ERRORS:
            corrections["title"] = TITLE_ERRORS[number][0]
            notes.append(TITLE_ERRORS[number][1])
        row["corrections"] = corrections
        row["basic_fields_ready"] = row["verdict"] == "correcta" and row["surname_correct"] and row["year_correct"]
        row["record_ready"] = row["basic_fields_ready"] and row["title_correct"]
        row["review_note"] = " ".join(notes) or "Una referencia completa; apellido, año y título concuerdan con el PDF."
        row["reviewer"] = "Codex (muestra de reserva; no auditor humano externo)"
        row["review_date"] = "2026-09-16"

    rows = packet["sample"]
    total = len(rows)
    metrics = {
        "sample_size": total,
        "segmentation_correct": sum(row["verdict"] == "correcta" for row in rows),
        "basic_fields_ready": sum(row["basic_fields_ready"] for row in rows),
        "record_ready": sum(row["record_ready"] for row in rows),
        "verdict_counts": dict(Counter(row["verdict"] for row in rows)),
        "incorrect_titles": len(TITLE_ERRORS),
        "incorrect_surnames": len(SURNAME_ERRORS),
        "incorrect_years": 0,
        "release_threshold": 0.95,
    }
    for key in ("segmentation_correct", "basic_fields_ready", "record_ready"):
        metrics[f"{key}_rate"] = metrics[key] / total
        metrics[f"{key}_wilson95"] = wilson(metrics[key], total)
    packet["metrics"] = metrics
    packet["network_release"] = False
    packet["network_release_reason"] = (
        "La muestra de reserva obtuvo 90/100 fichas localmente utilizables, por debajo del umbral de 95 %, "
        "y las identidades DOI/OpenAlex siguen sin resolverse."
    )
    packet["definitions"] = {
        "holdout": "Se excluyeron las entradas literales de la muestra de desarrollo; no es una auditoría humana externa.",
        "segmentation_correct": "La fila contiene una referencia y no incorpora encabezados, tablas ni otra referencia.",
        "basic_fields_ready": "Segmentación correcta, apellido inicial y año fieles al PDF.",
        "record_ready": "Criterio básico más título completo aislado.",
    }
    OUTPUT.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
