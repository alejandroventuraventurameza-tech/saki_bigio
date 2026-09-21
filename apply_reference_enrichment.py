"""Apply local title extraction and adjudicated audit corrections.

This step does not call external services and does not claim identity resolution.
It enriches the already controlled 1,413-row candidate in place, then fixes the two
known surname errors, one year error, one contaminated row and one fused row found
by the 100-record control.
"""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path

from parse_refs import parse_entry


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "archive" / "referencias_parseadas_candidate_v2_control.json"
AUDIT = ROOT / "data" / "auditoria_referencias_control.json"
DEFAULT_OUTPUT = ROOT / "tmp" / "referencias_parseadas_enriquecidas.json"

TITLE_OVERRIDES = {
    ("C01", 6): "Endogenous liquidity and the business cycle",
    ("C01", 7): "Private and public supply of liquidity",
    ("C01", 8): "Liquidity, business cycles, and monetary policy",
    ("C01", 9): "Equilibrium in a pure currency economy",
    ("C03", 1): "El Perú heterodoxo: Un modelo económico",
    ("C03", 2): "The ends of four big inflations",
    ("C03", 3): "De la desinflación a la hiperinflación, Perú: 1985-1990",
    ("C03", 4): "El programa económico de agosto de 1990: evaluación del primer año",
    ("E02", 1): "Asymmetric Effects of Monetary Policy Shocks",
    ("E02", 5): "Una Revisión de la Transmisión Monetaria y el Pass-Through en Chile",
    ("E02", 9): "Exchange Rate and Inflation Dynamics in Dollarized Economies",
    ("E02", 10): "Non-Homothetic Preferences and The Asymmetric Effects of Monetary Policy",
    ("E02", 11): "Uncovering Central Bank’s Monetary Policy Objectives: Going Beyond Fear of Floating",
    ("E02", 12): "Política Monetaria en Economías Dolarizadas, Un Aporte Analítico",
    ("E02", 15): "Monetary Policy Shocks: What Have we Learned and to What End?",
    ("E02", 20): "Do Monetary Shocks Exert Non Linear Real Effects on UK Industrial Production?",
    ("E02", 22): "The Asymmetric Effects of Monetary Policy Shocks: A Nonlinear Structural VAR Approach",
    ("E02", 25): "Living with the Fear of Floating: An Optimal Policy Perspective",
    ("E02", 32): "Effects of foreign and domestic monetary policy in a small open economy: the case of Chile",
    ("E02", 33): "Optimal Interest Rate Policy in a Small Open Economy",
    ("E02", 35): "A reconsideration of the empirical Evidence on the Asymmetric Effects of Money-Supply Shocks: Positive vs. Negative or Big vs. Small?",
    ("E02", 36): "Addicted to Dollars",
    ("E02", 44): "Interest and Prices: Foundations of a Theory of Monetary Policy",
    ("P01", 14): "Can sticky price models generate volatile and persistent real exchange rates?",
    ("P01", 33): "Will the fed ever learn?",
    ("P02", 6): "Tax enforcement for SMEs: Lessons from the Italian experience?",
    ("P02", 29): "Countervailing incentives in agency problems",
    ("P02", 30): "Of Coase, Calabresi, and optimal tax liability",
    ("P02", 37): "The economic theory of public enforcement of law",
    ("P02", 43): "Taxpayer’s choices under studi di settore: What do we know and how we can interpret it?",
    ("P02", 53): "Manufacturing firms in developing countries: How well do they do and why?",
    ("P02", 54): "American government finance in the long run: 1790 to 1990",
    ("P06", 53): "The asymmetric effects of financial frictions",
    ("P07", 16): "Monetary Policy Operations and the Financial System",
    ("V01", 67): "This Time Is Different",
    ("W03", 2): "The Non-US Bank Demand for US Dollar Assets",
    ("W03", 41): "World Economic Outlook",
    ("W04", 23): "The Theory of Stochastic Processes",
    ("W07", 24): "The Fed’s “Ample-Reserves” Approach to Implementing Monetary Policy",
    ("W08", 40): "Money, Payment, and Liquidity",
}

SURNAME_OVERRIDES = {
    ("C01", 7): "Holmström",
    ("C01", 8): "Kiyotaki",
    ("C03", 1): "Carbonetto",
    ("E02", 9): "Carranza",
    ("E02", 36): "Reinhart",
    ("P02", 29): "Lewis",
    ("W07", 2): "Giannone",
    ("W09", 31): "Jarociński",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def refresh_flags(ref: dict) -> None:
    flags = [flag for flag in ref.get("quality_flags", []) if flag not in {"missing_year", "title_not_isolated"}]
    if ref.get("year") is None:
        flags.append("missing_year")
    if not ref.get("title"):
        flags.append("title_not_isolated")
    ref["quality_flags"] = list(dict.fromkeys(flags))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    candidate = load(SOURCE)
    audit = load(AUDIT)
    result = copy.deepcopy(candidate)
    local_titles = 0
    audit_field_corrections = 0

    # First, infer only titles that were blank.  parse_entry reads the existing
    # citation string; segmentation and row order remain unchanged.
    for document in result["documents"].values():
        for ref in document["references"]:
            if ref.get("title"):
                ref.setdefault("title_extraction_method", "legacy_parser")
                continue
            reparsed = parse_entry(
                ref.get("surname") or "",
                ref.get("entry") or "",
                int(ref.get("page_start") or 0),
                int(ref.get("page_end") or 0),
                "inherited_author_notation" in ref.get("quality_flags", []),
            )
            if reparsed and reparsed.get("title"):
                ref["title"] = reparsed["title"]
                ref["title_extraction_method"] = reparsed.get("title_extraction_method")
                ref.setdefault("correction_provenance", []).append("local_citation_grammar_v3")
                local_titles += 1
            refresh_flags(ref)

    # Apply the explicit field corrections recorded by the adjudicated sample.
    for reviewed in audit["sample"]:
        corrections = reviewed.get("corrections") or {}
        if not corrections:
            continue
        doc = result["documents"][reviewed["document_id"]]
        ref = doc["references"][reviewed["reference_index"] - 1]
        for field, value in corrections.items():
            ref[field] = value
            audit_field_corrections += 1
        if "title" in corrections:
            ref["title_extraction_method"] = "manual_control_correction"
        ref.setdefault("correction_provenance", []).append(reviewed["sample_id"])
        refresh_flags(ref)

    # High-certainty corrections read directly from the literal citation
    # string.  These are not external identity assignments.
    for (doc_id, index), title in TITLE_OVERRIDES.items():
        ref = result["documents"][doc_id]["references"][index - 1]
        ref["title"] = title
        ref["title_extraction_method"] = "manual_literal_citation"
        ref.setdefault("correction_provenance", []).append("literal_citation_review_2026-09-16")
        refresh_flags(ref)

    # Two title-boundary defects found in the third independent sample.  The
    # corrected strings are transcribed from the source PDF context.
    for doc_id, index in [("P07", 16), ("W07", 24)]:
        ref = result["documents"][doc_id]["references"][index - 1]
        ref.setdefault("correction_provenance", []).append(
            f"third_sample_{'T-031' if doc_id == 'P07' else 'T-084'}_2026-09-17"
        )
    for (doc_id, index), surname in SURNAME_OVERRIDES.items():
        ref = result["documents"][doc_id]["references"][index - 1]
        ref["surname"] = surname
        ref.setdefault("correction_provenance", []).append("literal_citation_review_2026-09-16")

    # P01-R037 is incomplete in the source PDF itself: author, year and venue
    # are printed, but no title appears.  Do not mistake the venue for a title.
    lubik = result["documents"]["P01"]["references"][36]
    lubik["title"] = None
    lubik["title_extraction_method"] = None
    lubik.setdefault("quality_flags", []).append("source_omits_title")
    lubik.setdefault("correction_provenance", []).append("source_page_28_review_2026-09-16")
    refresh_flags(lubik)

    # C-065: remove a running header accidentally appended on the next page.
    v01 = result["documents"]["V01"]["references"][49]
    v01["entry"] = v01["entry"].split(" liquidity and macroeconomics:", 1)[0]
    v01["page_end"] = 22
    v01.setdefault("correction_provenance", []).append("C-065")

    # Additional running headers and section transitions discovered by the
    # holdout sample.  The reference text before each marker is preserved.
    for doc_id, index, marker, provenance in [
        ("P03", 20, " VOL. VOLUME NO. ISSUE", "H-017"),
        ("P03", 33, " 44 THE AMERICAN ECONOMIC REVIEW", "H-019"),
        ("V01", 74, " PAPERS & WORK IN PROGRESS", "H-065"),
    ]:
        ref = result["documents"][doc_id]["references"][index - 1]
        if marker not in ref["entry"]:
            raise RuntimeError(f"{doc_id}-R{index:03d} no contiene el marcador de contaminación esperado")
        ref["entry"] = ref["entry"].split(marker, 1)[0]
        ref["page_end"] = ref["page_start"]
        ref.setdefault("correction_provenance", []).append(provenance)

    # Two E02 rows contain page headers adjacent to otherwise complete
    # citations.  Remove only the verified header fragments.
    e02 = result["documents"]["E02"]["references"]
    e02[8]["entry"] = e02[8]["entry"].split("Carranza,", 1)[1]
    e02[8]["entry"] = "Carranza," + e02[8]["entry"]
    e02[8].setdefault("correction_provenance", []).append("local_header_cleanup_2026-09-16")
    e02[21]["entry"] = e02[21]["entry"].split(" 54 MONEY AFFAIRS", 1)[0]
    e02[21].setdefault("correction_provenance", []).append("local_header_cleanup_2026-09-16")
    e02[35]["entry"] = e02[35]["entry"].split("Reinhart,", 1)[1]
    e02[35]["entry"] = "Reinhart," + e02[35]["entry"]
    e02[35].setdefault("correction_provenance", []).append("local_header_cleanup_2026-09-16")

    # C-086: the source row contains three Woodford references.  Preserve the
    # literal citation fragments and split them into three auditable records.
    w04 = result["documents"]["W04"]["references"]
    fused = w04[58]
    if not (fused.get("surname") == "Woodford" and fused.get("year") == 1998):
        raise RuntimeError("W04-R059 no longer matches the adjudicated fused row")
    replacements = [
        {
            "surname": "Woodford",
            "year": 1998,
            "title": "Public debt and the price level",
            "title_extraction_method": "manual_control_split",
            "entry": "Woodford, Michael, “Public debt and the price level,” Mimeo, 1998.",
        },
        {
            "surname": "Woodford",
            "year": 1999,
            "title": "Commentary: How should monetary policy be conducted in an era of price stability?",
            "title_extraction_method": "manual_control_split",
            "entry": "———, “Commentary: How should monetary policy be conducted in an era of price stability?,” New challenges for monetary policy, 1999, 277–316.",
        },
        {
            "surname": "Woodford",
            "year": 2010,
            "title": "Optimal monetary stabilization policy",
            "title_extraction_method": "manual_control_split",
            "entry": "———, “Optimal monetary stabilization policy,” Handbook of monetary economics, 2010, 3, 723–828.",
        },
    ]
    for replacement in replacements:
        replacement.update({
            "page_start": fused["page_start"],
            "page_end": fused["page_end"],
            "quality_flags": ["inherited_author_notation"] if replacement["year"] != 1998 else [],
            "correction_provenance": ["C-086"],
        })
    w04[58:59] = replacements

    # P07-R038 is the continuation of P07-R037, not an independent reference.
    p07 = result["documents"]["P07"]["references"]
    continuation = p07[37]
    if not continuation["entry"].startswith("and M. W. Watson"):
        raise RuntimeError("P07-R038 no longer matches the adjudicated continuation")
    p07[36]["entry"] = f"{p07[36]['entry']} {continuation['entry']}"
    p07[36]["page_end"] = max(p07[36]["page_end"], continuation["page_end"])
    p07[36].setdefault("correction_provenance", []).append("fragment_merge_2026-09-16")
    del p07[37]

    # W05-R015/R016 contain one complete Boppart reference followed by a
    # Breedon reference split across the row boundary.  Reconstruct both from
    # the literal fragments without adding bibliographic information.
    w05 = result["documents"]["W05"]["references"]
    if " Breedon," not in w05[14]["entry"] or not w05[15]["entry"].startswith("and Finance"):
        raise RuntimeError("W05-R015/R016 no longer match the adjudicated split")
    boppart_text, breedon_start = w05[14]["entry"].split(" Breedon,", 1)
    boppart = copy.deepcopy(w05[14])
    boppart["entry"] = boppart_text.strip()
    boppart.setdefault("correction_provenance", []).append("fragment_split_2026-09-16")
    breedon = {
        "surname": "Breedon",
        "year": 2018,
        "title": "On the Transactions Costs of UK Quantitative Easing",
        "title_extraction_method": "manual_fragment_reconstruction",
        "entry": f"Breedon,{breedon_start} {w05[15]['entry']}",
        "page_start": w05[14]["page_start"],
        "page_end": w05[15]["page_end"],
        "quality_flags": [],
        "correction_provenance": ["fragment_split_2026-09-16"],
    }
    w05[14:16] = [boppart, breedon]

    # The OpenAlex review exposed a second fused row in P02-R002.  The source
    # page visibly contains two consecutive references: Acemoglu et al. and
    # Allingham-Sandmo.  Split only at the literal author boundary and do not
    # infer a year for the forthcoming Acemoglu article.
    p02 = result["documents"]["P02"]["references"]
    fused_p02 = p02[1]
    p02_marker = " M. G. Allingham and A. Sandmo."
    if (
        fused_p02.get("surname") != "Acemoglu"
        or "Emergence and persistence of inefficient states states" not in fused_p02["entry"]
        or p02_marker not in fused_p02["entry"]
    ):
        raise RuntimeError("P02-R002 no longer matches the visually verified fused row")
    acemoglu_text, allingham_tail = fused_p02["entry"].split(p02_marker, 1)
    acemoglu = copy.deepcopy(fused_p02)
    acemoglu.update({
        "year": None,
        "title": "Emergence and persistence of inefficient states states",
        "title_extraction_method": "manual_openalex_review_split",
        "entry": acemoglu_text.removesuffix("31").strip(),
    })
    acemoglu.setdefault("correction_provenance", []).append("openalex_review_fusion_2026-09-17")
    refresh_flags(acemoglu)
    allingham = {
        "surname": "Allingham",
        "year": 1972,
        "title": "Income tax evasion: A theoretical analysis",
        "title_extraction_method": "manual_openalex_review_split",
        "entry": f"M. G. Allingham and A. Sandmo.{allingham_tail}".removesuffix("2").strip(),
        "page_start": fused_p02["page_start"],
        "page_end": fused_p02["page_end"],
        "quality_flags": [],
        "correction_provenance": ["openalex_review_fusion_2026-09-17"],
    }
    p02[1:2] = [acemoglu, allingham]

    # OpenAlex exposed a DOI/title conflict in P11-R085: the parser had fused
    # Nagel's 2023 article with the following De la O and Myers (2021)
    # reference. Split the literal string before assigning either identity.
    p11 = result["documents"]["P11"]["references"]
    fused_p11 = p11[84]
    p11_marker = " O, Ricardo De La and Sean Myers"
    if fused_p11.get("title") != "Dynamics of subjective risk premia" or p11_marker not in fused_p11["entry"]:
        raise RuntimeError("P11-R085 no longer matches the OpenAlex-discovered fused row")
    nagel_text, de_la_o_tail = fused_p11["entry"].split(p11_marker, 1)
    nagel = copy.deepcopy(fused_p11)
    nagel["entry"] = nagel_text.strip()
    nagel.setdefault("correction_provenance", []).append("openalex_doi_conflict_2026-09-16")
    de_la_o = {
        "surname": "De la O",
        "year": 2021,
        "title": "Subjective Cash Flow and Discount Rate Expectations",
        "title_extraction_method": "manual_openalex_conflict_split",
        "entry": f"O, Ricardo De La and Sean Myers{de_la_o_tail}",
        "page_start": fused_p11["page_start"],
        "page_end": fused_p11["page_end"],
        "quality_flags": [],
        "correction_provenance": ["openalex_doi_conflict_2026-09-16"],
    }
    p11[84:85] = [nagel, de_la_o]

    refs = [ref for doc in result["documents"].values() for ref in doc["references"]]
    flags = Counter(flag for ref in refs for flag in ref.get("quality_flags", []))
    result["meta"].update({
        "status": "candidate_locally_enriched_identity_resolution_pending",
        "reference_entries": len(refs),
        "quality_flag_counts": dict(flags),
        "local_titles_added": local_titles,
        "audit_field_corrections_applied": audit_field_corrections,
        "structural_corrections_applied": [
            "C-065", "C-086", "P07-R037/R038", "W05-R015/R016",
            "H-017", "H-019", "H-065", "E02 page headers", "P02-R002", "P11-R085",
        ],
        "warning": (
            "Los títulos añadidos proceden de la cadena bibliográfica local; no equivalen a una "
            "identidad DOI/OpenAlex resuelta. Las consultas externas ya están completas; las identidades "
            "de alta confianza se conservan en una copia separada."
        ),
    })
    result["quality_control"]["top_surnames"] = Counter(ref["surname"] for ref in refs).most_common(30)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["meta"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
