"""Construye una capa de obras canónicas sobre la descarga bruta de OpenAlex.

OpenAlex asigna identificadores distintos a versiones NBER, SSRN, RePEc y de
revista. Este script conserva todos esos registros, pero impide tratarlos como
si fueran obras intelectuales independientes. No suma citas entre versiones:
sin los identificadores de los trabajos citantes, los solapamientos no son
observables.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "openalex" / "openalex_02_works.json"
OUTPUT = ROOT / "data" / "openalex" / "openalex_02_works_canonical.json"


# Familias cuya continuidad no se recupera normalizando el título. Se incluyen
# solo cuando los autores, los títulos sucesivos y/o el propio paper documentan
# la relación. Las equivalencias que todavía son dudosas se mantienen separadas.
MANUAL_FAMILIES = {
    "corruption_development_indicators": {
        "ids": {"W1601126220", "W2786276706"},
        "confidence": "high",
        "basis": "mismos autores; versión inglesa y revisión en castellano",
    },
    "distortions_in_production_networks": {
        "ids": {"W2242249047", "W2970593871", "W3186721982", "W3122067708"},
        "confidence": "high",
        "basis": "el artículo final declara que subsume Financial Frictions in Production Networks",
    },
    "banks_liquidity_management_monetary_policy": {
        "ids": {"W2188338937", "W2108244218", "W3121178068"},
        "confidence": "high",
        "basis": "misma pareja de autores y secuencia Columbia/NBER/Econometrica",
    },
    "credit_money_interest_prices": {
        "ids": {"W2593597393", "W2969728067", "W3135805255", "W3159360076"},
        "confidence": "high",
        "basis": "mismos autores y variantes sucesivas del mismo título",
    },
    "debt_maturity_management": {
        "ids": {"W2890929517", "W2944329140", "W3167816113", "W4309092133"},
        "confidence": "high",
        "basis": "el NBER WP declara que reemplaza A Framework for Debt-Maturity Management",
    },
    "q_theory_of_banks": {
        "ids": {"W2913699286", "W3125501673", "W2971371240", "W3151617833"},
        "confidence": "high",
        "basis": "el artículo final identifica Data Lessons on Bank Behavior y Banks Adjust Slowly como títulos anteriores",
    },
    "theory_of_payments_chain_crises": {
        "ids": {"W2295818883", "W4320018833", "W4317790378"},
        "confidence": "medium",
        "basis": "mismo autor y título casi idéntico; se mantiene separado del trabajo conjunto de 2026",
    },
    "heterogeneous_beliefs_asset_prices_business_cycles": {
        "ids": {"W3001875066", "W4409422010", "W4409411736"},
        "confidence": "medium",
        "basis": "Speculation-Driven Business Cycles es el antecedente indexado con autores parcialmente coincidentes",
    },
    "transfers_credit_policy": {
        "ids": {"W3023069640", "W3162692805", "W7160518259"},
        "confidence": "high",
        "basis": "mismos autores y ampliación del título de Covid-19 a crisis en general",
    },
}


def work_id(work: dict) -> str:
    return str(work.get("id", "")).rsplit("/", 1)[-1]


def normalize_title(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def source_name(work: dict) -> str | None:
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    return source.get("display_name") or location.get("raw_source_name")


def main() -> None:
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    records = raw.get("results", raw)
    research = [w for w in records if w.get("type") not in {"dataset", "software"}]

    explicit_by_id = {}
    family_meta = {}
    for family, spec in MANUAL_FAMILIES.items():
        family_meta[family] = {k: v for k, v in spec.items() if k != "ids"}
        for wid in spec["ids"]:
            if wid in explicit_by_id:
                raise ValueError(f"{wid} aparece en dos familias manuales")
            explicit_by_id[wid] = family

    grouped: dict[str, list[dict]] = defaultdict(list)
    for work in research:
        wid = work_id(work)
        key = explicit_by_id.get(wid, f"title::{normalize_title(work.get('display_name', ''))}")
        grouped[key].append(work)

    canonical = []
    for key, members in grouped.items():
        members = sorted(
            members,
            key=lambda w: (
                -(w.get("cited_by_count") or 0),
                0 if w.get("type") == "article" else 1,
                -(w.get("publication_year") or 0),
            ),
        )
        representative = members[0]
        years = [w.get("publication_year") for w in members if w.get("publication_year")]
        types = sorted({w.get("type") for w in members if w.get("type")})
        ids = [work_id(w) for w in members]
        fields = sorted(
            {
                (((w.get("primary_topic") or {}).get("field") or {}).get("display_name"))
                for w in members
                if (((w.get("primary_topic") or {}).get("field") or {}).get("display_name"))
            }
        )
        canonical.append(
            {
                "canonical_id": key.replace("title::", "title_"),
                "display_name": representative.get("display_name"),
                "representative_openalex_id": work_id(representative),
                "member_openalex_ids": ids,
                "member_titles": sorted({w.get("display_name") for w in members}),
                "authors": [
                    a.get("author", {}).get("display_name")
                    for a in representative.get("authorships", [])
                    if a.get("author", {}).get("display_name")
                ],
                "first_indexed_year": min(years) if years else None,
                "latest_indexed_year": max(years) if years else None,
                "record_types": types,
                "sources": sorted({name for w in members if (name := source_name(w))}),
                "fields": fields,
                "cited_by_count_max_version": max((w.get("cited_by_count") or 0) for w in members),
                "cited_by_count_sum_versions": sum((w.get("cited_by_count") or 0) for w in members),
                "citation_count_rule": "usar max_version como indicador conservador; no sumar sin deduplicar trabajos citantes",
                "mapping_confidence": family_meta.get(key, {}).get("confidence", "high"),
                "mapping_basis": family_meta.get(key, {}).get(
                    "basis", "título idéntico después de normalizar mayúsculas, acentos y puntuación"
                ),
            }
        )

    canonical.sort(
        key=lambda w: (-w["cited_by_count_max_version"], w["first_indexed_year"] or 9999)
    )

    health_pattern = re.compile(r"medic|health|psych|hospital|clinic|nurs", re.I)
    health_hits = []
    for work in records:
        location = work.get("primary_location") or {}
        source = location.get("source") or {}
        topic = work.get("primary_topic") or {}
        search_text = " ".join(
            str(v or "")
            for v in (
                source.get("display_name"),
                topic.get("display_name"),
                (topic.get("subfield") or {}).get("display_name"),
                (topic.get("field") or {}).get("display_name"),
            )
        )
        if health_pattern.search(search_text):
            health_hits.append(work_id(work))

    result = {
        "meta": {
            "source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
            "raw_records": len(records),
            "research_records": len(research),
            "canonical_works": len(canonical),
            "excluded_record_types": {"dataset": 12, "software": 2},
            "health_or_medical_topic_source_hits": health_hits,
            "method": "manual title-lineage families, then exact normalized-title grouping",
            "warning": "Canonicalization resolves work identity, not overlapping citation events. cited_by_count values across versions must not be summed.",
        },
        "works": canonical,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"{len(records)} raw records -> {len(research)} research records -> "
        f"{len(canonical)} canonical works"
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
