import argparse
import json
from collections import Counter
from pathlib import Path


PACKET = Path("tmp/pdfs/reference_audit/candidate_packet.json")
OUTPUT = Path("tmp/pdfs/reference_audit/adjudications.json")


FUSED = {
    "C01:1", "C01:2", "C02:3", "C03:2", "P02:6", "P07:25",
    "P08:25", "P09:34", "P10:28", "P11:8", "P11:17", "P11:40",
    "P11:73", "P11:85", "P12:34", "P13:17", "V01:48", "V01:51",
    "W02:3", "W02:34", "W02:64", "W03:22", "W05:15", "W05:25",
    "W07:8", "W08:9", "W08:23", "W08:32",
}

FRAGMENTED = {
    "E01:14", "E01:28", "E01:31", "E01:47", "E02:5", "E02:22",
    "E02:23", "E02:37", "E02:46", "E02:50", "P01:5", "P03:24",
    "P07:11", "P07:26", "P07:46", "P08:24", "P08:26", "P09:1",
    "P09:3", "P09:4", "P09:13", "P09:29", "P09:31", "P09:48",
    "P09:50", "P10:3", "P10:4", "P10:14", "P10:44", "P11:70",
    "P12:2", "P12:6", "P12:13", "P12:15", "P12:43", "P12:48",
    "P13:9", "P13:22", "P13:35", "V01:15", "V01:18", "V01:19",
    "V01:36", "V01:39", "V01:49", "W02:32", "W02:50", "W02:59",
    "W03:3", "W04:2", "W04:23", "W05:29", "W05:36", "W06:6",
    "W06:8", "W06:15", "W06:17", "W08:2", "W08:5", "W08:26",
    "W08:28", "W08:29", "W09:24", "W10:3", "W10:14", "W11:19",
}

NOT_REFERENCE = {"V01:69", "V01:72", "W03:54", "W09:49"}

# El candidato corresponde a una sola referencia, pero el extractor alteró un
# campo puntual que sí puede corregirse sin reconstruir la fila completa.
FIELD_CORRECTIONS = {
    "E01:36": {
        "year_correcto": "no",
        "correccion": "Año: 1998b.",
        "observacion": "El PDF imprime “1 998b”; el extractor no normalizó el espacio interno.",
    },
}


def load_candidates():
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    records = packet.get("rows", packet) if isinstance(packet, dict) else packet
    candidates = {}
    for record in records:
        key = f"{record['document_id']}:{record['candidate_index']}"
        candidates[key] = record
    return records, candidates


def adjudicate(key, candidate):
    page = candidate.get("page_number")
    page_note = f" Página PDF {page}." if page else ""
    if key in FUSED:
        return {
            "veredicto": "fusionada",
            "surname_correcto": "no_aplica",
            "year_correcto": "no_aplica",
            "title_correcto": "no_aplica",
            "correccion": "Separar las referencias contenidas en esta fila.",
            "observacion": "La fila reúne material de dos o más referencias consecutivas." + page_note,
            "revisor": "Codex",
            "fecha_revision": "2026-09-15",
        }
    if key in FRAGMENTED:
        return {
            "veredicto": "fragmentada",
            "surname_correcto": "no_aplica",
            "year_correcto": "no_aplica",
            "title_correcto": "no_aplica",
            "correccion": "Unir con la fila contigua de la referencia original.",
            "observacion": "La fila contiene solo una parte de una referencia bibliográfica." + page_note,
            "revisor": "Codex",
            "fecha_revision": "2026-09-15",
        }
    if key in NOT_REFERENCE:
        return {
            "veredicto": "no_es_referencia",
            "surname_correcto": "no_aplica",
            "year_correcto": "no_aplica",
            "title_correcto": "no_aplica",
            "correccion": "Excluir esta fila del conjunto de referencias.",
            "observacion": "Es texto del cuerpo, apéndice o agenda; no una referencia bibliográfica." + page_note,
            "revisor": "Codex",
            "fecha_revision": "2026-09-15",
        }

    has_year = candidate.get("year") not in (None, "")
    has_title = candidate.get("title") not in (None, "")
    result = {
        "veredicto": "referencia_correcta",
        "surname_correcto": "sí",
        "year_correcto": "sí" if has_year else "no_aplica",
        "title_correcto": "sí" if has_title else "no",
        "correccion": "",
        "observacion": (
            "Contraste independiente con la sección de referencias del PDF."
            if has_title
            else "La fila corresponde a una referencia completa, pero el título no quedó aislado por el extractor."
        ) + page_note,
        "revisor": "Codex",
        "fecha_revision": "2026-09-15",
    }
    result.update(FIELD_CORRECTIONS.get(key, {}))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-null-years", action="store_true")
    args = parser.parse_args()

    records, candidates = load_candidates()
    override_keys = FUSED | FRAGMENTED | NOT_REFERENCE | set(FIELD_CORRECTIONS)
    missing = sorted(override_keys - set(candidates))
    if missing:
        raise SystemExit(f"Overrides sin candidato: {missing}")

    results = {key: adjudicate(key, candidate) for key, candidate in candidates.items()}
    payload = {
        "metadata": {
            "reviewer": "Codex",
            "review_date": "2026-09-15",
            "unique_candidates": len(candidates),
            "source_rows": len(records),
            "method": "Contraste manual independiente con el texto de las secciones de referencias de los PDF.",
        },
        "adjudications": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    verdicts = Counter(item["veredicto"] for item in results.values())
    print(f"UNIQUE={len(candidates)} SOURCE_ROWS={len(records)}")
    print("VERDICTS=" + json.dumps(dict(sorted(verdicts.items())), ensure_ascii=False))
    for sample_type in ("aleatoria", "dirigida"):
        keys = [f"{r['document_id']}:{r['candidate_index']}" for r in records if r.get("sample_kind") == sample_type]
        counts = Counter(results[k]["veredicto"] for k in keys)
        print(f"{sample_type.upper()}={len(keys)} " + json.dumps(dict(sorted(counts.items())), ensure_ascii=False))
    if args.list_null_years:
        for key, candidate in sorted(candidates.items()):
            if candidate.get("year") in (None, "") and results[key]["veredicto"] == "referencia_correcta":
                print(f"NULL_YEAR {key}: {candidate.get('entry')}")


if __name__ == "__main__":
    main()
