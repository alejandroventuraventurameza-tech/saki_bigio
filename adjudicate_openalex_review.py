"""Adjudicate the provisional OpenAlex matches against the source citations.

This script does not call the network.  It records the documentary decisions
made on 2026-09-17 and creates a separate candidate layer; the conservative
high-confidence file remains untouched.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "tmp" / "openalex_review_packet.json"
CANDIDATE = ROOT / "data" / "referencias_parseadas_candidate_openalex.json"
ARCHIVE_V5 = ROOT / "data" / "archive" / "referencias_parseadas_candidate_v5_openalex_conflict.json"
AUDIT_OUTPUT = ROOT / "data" / "auditoria_openalex_coincidencias_provisionales.json"
ADJUDICATED_OUTPUT = ROOT / "data" / "referencias_parseadas_candidate_openalex_adjudicada.json"


ACCEPTED = {
    "P10-R022": "Mismos tres autores y mismo núcleo distintivo del título; OpenAlex describe la versión de trabajo de 2019 y la fuente cita la publicación AER de 2023.",
    "P10-R044": "Mismos autores y mismo título base; la coincidencia es una versión anterior con el subtítulo 'A Fiscal Explanation'.",
    "P07-R024": "Mismos autores y misma frase distintiva 'Quantitative Model of Banking Industry Dynamics'; el registro corresponde a una versión posterior retitulada.",
    "P07-R055": "Mismos autores y mismo trabajo; la fuente cita el título publicado y OpenAlex conserva una versión anterior abreviada.",
    "P03-R014": "Mismos cuatro autores y mismo comienzo distintivo del título; 'Non-Standard Policies' y 'Liquidity Facilities' son títulos de versiones del mismo trabajo.",
    "P13-R009": "Mismos tres autores, año y objeto empírico; DIW registra las variantes 'Incidence' y 'Distributional Effects' del mismo documento.",
    "P13-R029": "Mismos dos autores y mismo estudio Europa-Canadá; el título de OpenAlex corresponde a una versión posterior retitulada como 'Greenflation'.",
    "P05-R036": "Mismo autor y estructura distintiva del título; OpenAlex conserva la versión de trabajo anterior con 'and Superstars'.",
    "P01-R036": "Mismos autores y título; OpenAlex registra la versión de trabajo de 2000 y la fuente la publicación de 2003.",
    "P01-R038": "Mismos autores, año y libro; la fuente abrevia el título completo con subtítulo.",
    "P08-R046": "Mismos autores y mismo trabajo; la fuente cita el título publicado y OpenAlex conserva una versión anterior abreviada.",
    "P11-R006": "Mismos cuatro autores y mismo mecanismo de momentum/reversal; la coincidencia es una versión anterior retitulada.",
    "P11-R018": "Mismos cuatro autores y año; el manuscrito 'Expectations of Fundamentals...' fue retitulado 'Belief Overreaction...' en NBER y publicación posterior.",
    "P02-R015": "Mismos autores y título casi idéntico; OpenAlex registra una versión de trabajo anterior.",
    "P02-R038": "Mismos autores y mismo trabajo; la diferencia es solo de versión/año y omisión de 'economic' en el título posterior.",
    "W09-R005": "Mismos cuatro autores y mismo trabajo; la fuente usa el título publicado y OpenAlex una versión de trabajo abreviada.",
    "W10-R023": "Mismo autor y trabajo; OpenAlex registra la versión de trabajo anterior con el subtítulo 'Evidence and Theory'.",
    "W08-R006": "Mismos autores; el manuscrito de 2013 'Financial Frictions in Production Networks' evolucionó al trabajo 'Distortions in Production Networks'.",
    "W05-R037": "Mismos autores y mismo trabajo; la fuente cita el título publicado y OpenAlex conserva una versión anterior abreviada.",
}

REJECTED = {
    "P06-R028": "La fuente cita el libro Microeconomics of Banking de Freixas y Rochet; OpenAlex devuelve Microeconometrics of Banking de Degryse, Kim y Ongena.",
    "P01-R021": "Aunque coincide autora y año, son dos trabajos distintos: la fuente cita 'Monetary policy and welfare...' y OpenAlex otro artículo sobre estructuras alternativas de mercados de activos.",
    "P11-R053": "La fuente cita 'Five facts about beliefs and portfolios' de cuatro autores; OpenAlex devuelve otro trabajo ESG, con título y lista de seis autores diferentes.",
    "W04-R024": "La fuente cita a Coibion, Gorodnichenko y Weber sobre política fiscal; OpenAlex devuelve otro experimento sobre consumo con Georgarakos y van Rooij.",
    "W10-R011": "La fuente cita el artículo de Gabaix y Laibson; OpenAlex devuelve el comentario de Monika Piazzesi, no el artículo comentado.",
}

EXTERNAL_VERIFICATION = {
    "P10-R022": [
        "https://www.aeaweb.org/articles?id=10.1257/aer.20190149",
        "https://www.aeaweb.org/conference/2024/program/paper/DbRTB7Hz",
    ],
    "P13-R009": [
        "https://www.diw.de/en/diw_01.c.620265.en/publications/discussion_papers.html",
        "https://www.diw.de/de/diw_01.c.457061.de/publikationen/sonstige_aufsaetze/2012_0000/distributional_effects_of_the_european_emissions_trading_sys___al_evidence_from_combined_industry-_and_household-level_data.html",
    ],
    "P11-R018": [
        "https://www.nber.org/papers/w27283",
        "https://scholar.harvard.edu/files/shleifer/files/bgls_may25.pdf",
    ],
    "W08-R006": [
        "https://users.nber.org/~confer/2013/EFGs13/Bigio_La%27O.pdf",
    ],
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_match(case: dict, status: str) -> dict:
    best = case["best_match"]
    return {
        "status": status,
        "id": best["id"],
        "doi": best.get("doi"),
        "display_name": best.get("display_name"),
        "publication_year": best.get("publication_year"),
        "type": best.get("type"),
        "authors": best.get("authors", []),
        "evidence": best.get("evidence", {}),
        "query_url": case.get("query_url"),
    }


def main() -> None:
    packet = load(PACKET)
    candidate = load(CANDIDATE)
    adjudicated = copy.deepcopy(candidate)
    case_ids = {case["ref_id"] for case in packet["cases"]}
    decision_ids = set(ACCEPTED) | set(REJECTED)
    if case_ids != decision_ids:
        raise RuntimeError(
            f"Decision map does not match review packet: missing={case_ids-decision_ids}, extra={decision_ids-case_ids}"
        )

    audit_cases = []
    for case in packet["cases"]:
        ref_id = case["ref_id"]
        accepted = ref_id in ACCEPTED
        decision = "accepted_same_work" if accepted else "rejected_different_work"
        rationale = ACCEPTED.get(ref_id) or REJECTED[ref_id]
        audit_case = copy.deepcopy(case)
        audit_case["decision"] = decision
        audit_case["rationale"] = rationale
        audit_case["external_verification"] = EXTERNAL_VERIFICATION.get(ref_id, [])
        audit_cases.append(audit_case)

        if accepted:
            ref = adjudicated["documents"][case["doc_id"]]["references"][case["reference_index"] - 1]
            if ref.get("title") != case["parsed"].get("title"):
                raise RuntimeError(f"Reference drift detected for {ref_id}")
            ref["openalex_resolution"] = compact_match(case, "matched_review_adjudicated")
            ref.setdefault("correction_provenance", []).append("openalex_review_adjudication_2026-09-21")
        else:
            ref = adjudicated["documents"][case["doc_id"]]["references"][case["reference_index"] - 1]
            ref["openalex_rejected_candidate"] = compact_match(case, "rejected_different_work")

    # The P02 split created a new Allingham-Sandmo row after the text-search
    # batch.  The publisher DOI was verified and then resolved directly in
    # OpenAlex; keep this distinct from the 25 provisional-match decisions.
    allingham = adjudicated["documents"]["P02"]["references"][2]
    if allingham.get("surname") != "Allingham" or allingham.get("year") != 1972:
        raise RuntimeError("P02-R003 no longer matches the verified Allingham-Sandmo row")
    allingham["openalex_resolution"] = {
        "status": "matched_doi_verified_after_split",
        "id": "https://openalex.org/W2088435028",
        "doi": "https://doi.org/10.1016/0047-2727(72)90010-2",
        "display_name": "Income tax evasion: a theoretical analysis",
        "publication_year": 1972,
        "type": "article",
        "authors": ["Michael Allingham", "Agnar Sandmo"],
        "evidence": {
            "title_similarity": 1.0,
            "author_match": True,
            "year_distance": 0,
            "resolution_method": "publisher_doi_then_openalex_direct_lookup",
        },
        "query_url": "https://api.openalex.org/works/doi:10.1016%2F0047-2727%2872%2990010-2?select=id,doi,display_name,publication_year,type,authorships,primary_location&mailto=alejandroventuraventurameza@gmail.com",
        "publisher_url": "https://www.sciencedirect.com/science/article/pii/0047272772900102",
    }
    allingham.setdefault("correction_provenance", []).append("openalex_doi_verification_2026-09-17")

    old_candidate = load(ARCHIVE_V5)
    old_fused = old_candidate["documents"]["P02"]["references"][1]
    new_refs = adjudicated["documents"]["P02"]["references"][1:3]
    structural_case = {
        "original_ref_id": "P02-R002",
        "decision": "split_fused_reference",
        "source_pdf": "saki_research/published_papers/bigio_ramirez_ridruejo_optimal_taxation_enforcement_informal_economy.pdf",
        "source_page": 38,
        "before": old_fused,
        "after": new_refs,
        "rationale": "La inspección visual de la página 38 muestra dos entradas independientes: Acemoglu–Ticchi–Vindigni y Allingham–Sandmo. El DOI editorial de la segunda entrada resolvió directamente a OpenAlex W2088435028.",
        "external_verification": [
            "https://www.sciencedirect.com/science/article/pii/0047272772900102",
            "https://api.openalex.org/works/doi:10.1016%2F0047-2727%2872%2990010-2?select=id,doi,display_name,publication_year,type,authorships,primary_location&mailto=alejandroventuraventurameza@gmail.com",
        ],
        "applied_by": "apply_reference_enrichment.py",
    }

    all_resolved = [
        ref["openalex_resolution"]
        for doc in adjudicated["documents"].values()
        for ref in doc["references"]
        if "openalex_resolution" in ref
    ]
    status_counts = Counter(match["status"] for match in all_resolved)
    unique_ids = len({match["id"] for match in all_resolved})
    adjudicated["meta"].update({
        "status": "candidate_openalex_adjudicated_layer_complete",
        "openalex_review_audit": str(AUDIT_OUTPUT.relative_to(ROOT)),
        "openalex_algorithmic_high_confidence_rows": status_counts.get("matched_high_confidence", 0),
        "openalex_review_rows_accepted": status_counts.get("matched_review_adjudicated", 0),
        "openalex_structural_doi_verified_rows": status_counts.get("matched_doi_verified_after_split", 0),
        "openalex_review_rows_rejected": len(REJECTED),
        "openalex_resolved_rows_after_adjudication": len(all_resolved),
        "openalex_unique_ids_after_adjudication": unique_ids,
        "openalex_unresolved_rows": adjudicated["meta"]["reference_entries"] - len(all_resolved),
        "network_release": False,
        "network_release_reason": "La adjudicación resuelve las coincidencias provisionales, pero quedan filas sin identidad OpenAlex y falta la auditoría independiente final.",
        "warning": "Capa separada con decisiones documentales de coincidencias provisionales; no sustituye la candidata local ni constituye liberación final de la red.",
    })

    audit = {
        "meta": {
            "status": "complete",
            "date": "2026-09-21",
            "reviewer": "Codex (revisión documental asistida; no auditor humano externo)",
            "method": "Comparación de la cita literal en el PDF con título, autores, año y tipo del mejor candidato OpenAlex; verificación externa primaria en casos limítrofes.",
            "candidate_sha256": sha256(CANDIDATE),
            "review_packet_sha256": sha256(PACKET),
            "review_population": len(packet["cases"]),
            "accepted_same_work": len(ACCEPTED),
            "rejected_different_work": len(REJECTED),
            "structural_corrections": 1,
            "structural_doi_verified_rows": status_counts.get("matched_doi_verified_after_split", 0),
            "resolved_rows_after_adjudication": len(all_resolved),
            "unique_openalex_ids_after_adjudication": unique_ids,
            "unresolved_rows_after_adjudication": adjudicated["meta"]["reference_entries"] - len(all_resolved),
            "adjudicated_output": str(ADJUDICATED_OUTPUT.relative_to(ROOT)),
            "network_release": False,
        },
        "structural_corrections": [structural_case],
        "cases": audit_cases,
    }

    AUDIT_OUTPUT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    adjudicated["meta"]["openalex_review_audit_sha256"] = sha256(AUDIT_OUTPUT)
    ADJUDICATED_OUTPUT.write_text(json.dumps(adjudicated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "reviewed": len(audit_cases),
        "accepted": len(ACCEPTED),
        "rejected": len(REJECTED),
        "structural_corrections": 1,
        "resolved_rows_after_adjudication": len(all_resolved),
        "unique_openalex_ids_after_adjudication": unique_ids,
        "audit": str(AUDIT_OUTPUT),
        "adjudicated_candidate": str(ADJUDICATED_OUTPUT),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
