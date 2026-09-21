"""Controles de consistencia para la versión refinada del proyecto."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, median

import nbformat


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parsed_json = 0
    for path in DATA.rglob("*.json"):
        load_json(path)
        parsed_json += 1

    with (DATA / "corpus.csv").open(encoding="utf-8-sig", newline="") as handle:
        corpus = list(csv.DictReader(handle))
    assert len(corpus) == 48
    assert sum(int(row["paginas"]) for row in corpus) == 1995
    assert sum(int(row["chars"]) for row in corpus) == 3416048
    by_id = {row["id"]: row for row in corpus}
    assert by_id["D15"]["slug"] == "bigio_safety_traps_caballero_farhi"
    assert by_id["P12"]["anio_primera_version"] == "2017"
    assert by_id["W09"]["anio_primera_version"] == "2025"
    assert all(int(row["anio_primera_version"]) <= int(row["anio"]) for row in corpus)

    with (DATA / "first_version_sources.csv").open(encoding="utf-8-sig", newline="") as handle:
        first = list(csv.DictReader(handle))
    assert len(first) == 13
    assert sum(row["confianza"] == "alta" for row in first) == 7
    assert sum(row["confianza"] == "media" for row in first) == 6
    lags = [int(row["anio_publicacion"]) - int(row["anio_primera_version"]) for row in first]
    assert round(mean(lags), 1) == 4.8 and median(lags) == 6 and max(lags) == 9

    raw = load_json(DATA / "openalex" / "openalex_02_works.json")
    assert len(raw["results"]) == 89
    canonical = load_json(DATA / "openalex" / "openalex_02_works_canonical.json")
    assert canonical["meta"]["raw_records"] == 89
    assert canonical["meta"]["research_records"] == 75
    assert canonical["meta"]["canonical_works"] == 34
    assert canonical["meta"]["health_or_medical_topic_source_hits"] == []
    top_ids = [work["representative_openalex_id"] for work in canonical["works"][:6]]
    assert len(top_ids) == len(set(top_ids)) == 6
    assert top_ids == [
        "W3122067708", "W2120166711", "W2108244218",
        "W1992090825", "W4244212591", "W3023069640",
    ]

    facets = load_json(DATA / "openalex" / "openalex_04_facets_citantes_canonical.json")
    assert len(facets["meta"]["queried_version_ids"]) == 14
    assert facets["publication_year"]["meta"]["count"] == 774

    timeline = load_json(DATA / "linea_tiempo.json")
    assert [item["valor"] for item in timeline["ventajas_medidas"]] == ["21", "3", "4,8"]
    assert any(event["anio"] == "2013" and "Bianchi" in event["titulo"] for event in timeline["eventos"])
    timeline_text = json.dumps(timeline, ensure_ascii=False)
    assert "Decreto Legislativo 1455" in timeline_text
    for obsolete in ("35 971", "doce referencias", "162 veces", "710 trabajos citantes"):
        assert obsolete not in timeline_text

    candidate = load_json(DATA / "referencias_parseadas_candidate.json")
    assert candidate["meta"]["status"] == "candidate_locally_enriched_identity_resolution_pending"
    assert candidate["meta"]["reference_entries"] == 1435
    assert candidate["meta"]["quality_flag_counts"]["missing_year"] == 6
    assert candidate["meta"]["quality_flag_counts"]["title_not_isolated"] == 1
    assert candidate["meta"]["quality_flag_counts"]["inherited_author_notation"] == 127
    assert candidate["meta"]["quality_flag_counts"]["source_year_malformed"] == 1
    audit = load_json(DATA / "auditoria_referencias_control.json")
    assert len(audit['sample']) == audit['metrics']['sample_size'] == 100
    assert sum(r['verdict']=='correcta' for r in audit['sample']) == 98
    assert sum(r['record_ready'] for r in audit['sample']) == 77
    assert not audit['network_release']
    assert all(c['expected']==c['extracted'] for c in audit['count_checks'])
    assert all(row['pdf_context'] and row['verdict']!='pendiente' for row in audit['sample'])
    remediation = load_json(DATA / "auditoria_referencias_remediacion.json")
    assert remediation['population_after_correction'] == 1414
    assert remediation['prior_sample_size'] == 100
    assert remediation['remediation_checks_passed'] == 100
    assert remediation['remediation_checks_failed'] == 0
    assert not remediation['network_release']
    assert all(row['remediated'] for row in remediation['checks'])
    holdout = load_json(DATA / "auditoria_referencias_holdout.json")
    assert len(holdout['sample']) == holdout['metrics']['sample_size'] == 100
    assert holdout['metrics']['segmentation_correct'] == 97
    assert holdout['metrics']['basic_fields_ready'] == 95
    assert holdout['metrics']['record_ready'] == 90
    assert holdout['metrics']['verdict_counts']['contaminada'] == 3
    assert holdout['metrics']['incorrect_titles'] == 5
    assert holdout['metrics']['incorrect_surnames'] == 2
    assert not holdout['network_release']
    holdout_remediation = load_json(DATA / "auditoria_referencias_holdout_remediacion.json")
    assert holdout_remediation['prior_holdout_record_ready'] == 90
    assert holdout_remediation['remediation_checks_passed'] == 100
    assert holdout_remediation['remediation_checks_failed'] == 0
    assert not holdout_remediation['network_release']
    assert all(row['remediated'] for row in holdout_remediation['checks'])
    third_audit = load_json(DATA / "auditoria_referencias_tercera_muestra.json")
    assert len(third_audit['sample']) == third_audit['metrics']['sample_size'] == 100
    assert third_audit['prior_reviewed_records'] == 200
    assert third_audit['eligible_population'] == 1216
    assert third_audit['metrics']['segmentation_correct'] == 100
    assert third_audit['metrics']['basic_fields_ready'] == 100
    assert third_audit['metrics']['record_ready'] == 98
    assert third_audit['metrics']['incorrect_titles'] == 2
    assert third_audit['metrics']['incorrect_surnames'] == 0
    assert third_audit['metrics']['incorrect_years'] == 0
    assert not third_audit['network_release']
    third_remediation = load_json(DATA / "auditoria_referencias_tercera_muestra_remediacion.json")
    assert third_remediation['prior_third_sample_record_ready'] == 98
    assert third_remediation['remediation_checks_passed'] == 100
    assert third_remediation['remediation_checks_failed'] == 0
    assert not third_remediation['network_release']
    assert all(row['remediated'] for row in third_remediation['checks'])
    integral_audit = load_json(DATA / "auditoria_integral_ia_referencias.json")
    assert integral_audit["meta"]["population"] == len(integral_audit["rows"]) == 1435
    assert sum(integral_audit["meta"]["audit_route_counts"].values()) == 1435
    assert integral_audit["meta"]["audit_route_counts"] == {
        "automatic_screen_pass": 1012,
        "prior_manual_sample": 300,
        "exhaustive_visual_multiwork_pattern_accepted": 30,
        "exhaustive_visual_correction": 90,
        "exhaustive_visual_exception_accepted": 3,
    }
    assert integral_audit["meta"]["audit_status_counts"] == {
        "accepted": 1343, "corrected": 90, "accepted_source_exception": 2,
    }
    assert integral_audit["meta"]["structural_operations"] == 18
    assert integral_audit["meta"]["net_rows_added"] == 19
    assert integral_audit["meta"]["title_boundary_corrections"] == 17
    assert integral_audit["meta"]["local_quality_control_complete"]
    assert not integral_audit["meta"]["human_external_audit"]
    assert not integral_audit["meta"]["network_release"]
    assert sum(
        ref.get('title') is None
        for document in candidate['documents'].values()
        for ref in document['references']
    ) == 1
    assert sum(
        ref.get('surname') == 'Woodford' and ref.get('year') in {1998, 1999, 2010}
        and 'C-086' in ref.get('correction_provenance', [])
        for ref in candidate['documents']['W04']['references']
    ) == 3
    assert sum(
        ref.get('surname') == 'De la O' and ref.get('year') == 2021
        and 'openalex_doi_conflict_2026-09-16' in ref.get('correction_provenance', [])
        for ref in candidate['documents']['P11']['references']
    ) == 1
    assert sum(
        ref.get('surname') in {'Acemoglu', 'Allingham'}
        and 'openalex_review_fusion_2026-09-17' in ref.get('correction_provenance', [])
        for ref in candidate['documents']['P02']['references']
    ) == 2
    assert candidate['documents']['P07']['references'][15]['title'] == "Monetary Policy Operations and the Financial System"
    assert candidate['documents']['W07']['references'][23]['title'] == "The Fed’s “Ample-Reserves” Approach to Implementing Monetary Policy"
    assert "Saki" not in dict(candidate["quality_control"]["top_surnames"])

    partial_resolution = load_json(DATA / "openalex" / "openalex_reference_resolution_partial.json")
    assert partial_resolution["meta"]["records_returned"] == 94
    assert partial_resolution["meta"]["unique_queries_cached"] == 80
    assert partial_resolution["meta"]["status_counts"] == {
        "matched_review": 10, "unresolved": 64, "matched_high_confidence": 20,
    }
    partial_candidate = load_json(DATA / "referencias_parseadas_candidate_openalex_partial.json")
    assert partial_candidate["meta"]["openalex_high_confidence_rows_attached"] == 20
    assert partial_candidate["meta"]["openalex_unique_ids_attached"] == 16
    assert not partial_candidate["meta"]["network_release"]
    full_resolution = load_json(DATA / "openalex" / "openalex_reference_resolution_authenticated.json")
    assert full_resolution["meta"]["records_returned"] == 1435
    assert full_resolution["meta"]["unique_queries_cached"] == 1267
    assert full_resolution["meta"]["errors"] == []
    assert all(
        "mailto=alejandroventuraventurameza%40gmail.com" in row["query_url"]
        for row in full_resolution["references"]
    )
    assert full_resolution["meta"]["status_counts"] == {
        "matched_high_confidence": 370, "unresolved": 1041, "matched_review": 24,
    }
    full_candidate = load_json(DATA / "referencias_parseadas_candidate_openalex.json")
    assert full_candidate["meta"]["openalex_resolution_complete"]
    assert full_candidate["meta"]["openalex_high_confidence_rows_attached"] == 370
    assert full_candidate["meta"]["openalex_unique_ids_attached"] == 303
    assert not full_candidate["meta"]["network_release"]
    review_audit = load_json(DATA / "auditoria_openalex_coincidencias_provisionales.json")
    assert review_audit["meta"]["review_population"] == 24
    assert review_audit["meta"]["accepted_same_work"] == 19
    assert review_audit["meta"]["rejected_different_work"] == 5
    assert review_audit["meta"]["structural_corrections"] == 1
    assert {case["decision"] for case in review_audit["cases"]} == {
        "accepted_same_work", "rejected_different_work",
    }
    adjudicated_candidate = load_json(DATA / "referencias_parseadas_candidate_openalex_adjudicada.json")
    assert adjudicated_candidate["meta"]["openalex_resolved_rows_after_adjudication"] == 390
    assert adjudicated_candidate["meta"]["openalex_unique_ids_after_adjudication"] == 320
    assert adjudicated_candidate["meta"]["openalex_unresolved_rows"] == 1045
    assert adjudicated_candidate["meta"]["openalex_structural_doi_verified_rows"] == 1
    assert not adjudicated_candidate["meta"]["network_release"]
    resolution_status = load_json(DATA / "openalex" / "openalex_reference_resolution_status.json")
    assert resolution_status["status"] == "api_queries_and_provisional_match_adjudication_complete"
    assert resolution_status["rows_with_response"] == 1435
    assert resolution_status["errors"] == []
    assert not resolution_status["network_release"]

    notebook = nbformat.read(ROOT / "analisis_bibliometrico.ipynb", as_version=4)
    nbformat.validate(notebook)
    errors = [
        output for cell in notebook.cells for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    assert not errors

    expected_figures = {
        "01_corpus.png", "02_impacto.png", "03_rezago.png", "04_cobertura_textual.png",
        "05_terminos_distintivos.png", "06_red_copalabras.png", "07_jel.png",
        "08_red_coautoria.png", "09_colaboracion.png", "10_quien_lo_cita.png",
        "11_autores_citantes.png", "12_referencias_calidad.png", "13_anclas_doctrinales.png",
    }
    assert expected_figures <= {path.name for path in (ROOT / "figs").glob("*.png")}
    assert not (ROOT / "figs" / "04_nubes_periodo.png").exists()
    assert not (ROOT / "figs" / "12_tradicion.png").exists()

    assert (ROOT / "reporte_final_refinado.md").exists()
    for name in ("reporte_bibliometrico.md", "reporte_fase2b_y_H6.md", "reporte_textual_y_bibliometrico.md"):
        assert "DOCUMENTO HISTÓRICO, SUSTITUIDO" in (ROOT / name).read_text(encoding="utf-8")

    print(f"OK · {parsed_json} JSON válidos · corpus, OpenAlex, cuaderno y figuras consistentes")


if __name__ == "__main__":
    main()
