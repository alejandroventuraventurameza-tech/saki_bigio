"""Apply visually verified defects found by the corpus-wide AI-assisted audit."""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "referencias_parseadas_candidate.json"
OUTPUT = SOURCE
PROVENANCE = "exhaustive_ai_audit_2026-09-17"


def refresh_flags(ref: dict) -> None:
    flags = [flag for flag in ref.get("quality_flags", []) if flag not in {"missing_year", "title_not_isolated"}]
    if ref.get("year") is None:
        flags.append("missing_year")
    if not ref.get("title"):
        flags.append("title_not_isolated")
    ref["quality_flags"] = list(dict.fromkeys(flags))


def make_ref(base: dict, *, surname: str, year: int | None, title: str, entry: str, inherited: bool = False,
             extra_flags: list[str] | None = None) -> dict:
    row = {
        "surname": surname,
        "year": year,
        "title": title,
        "title_extraction_method": "manual_exhaustive_ai_audit",
        "entry": entry.strip(),
        "page_start": base["page_start"],
        "page_end": base["page_end"],
        "quality_flags": (["inherited_author_notation"] if inherited else []) + (extra_flags or []),
        "correction_provenance": [PROVENANCE],
    }
    refresh_flags(row)
    return row


def split_two(refs: list[dict], index: int, marker: str, second: dict, first_updates: dict | None = None) -> None:
    base = refs[index - 1]
    if marker not in base["entry"]:
        raise RuntimeError(f"No se encontró el marcador de fusión en R{index:03d}: {marker}")
    first_text, second_tail = base["entry"].split(marker, 1)
    first = copy.deepcopy(base)
    first["entry"] = first_text.strip()
    if first_updates:
        first.update(first_updates)
    first.setdefault("correction_provenance", []).append(PROVENANCE)
    refresh_flags(first)
    second_row = make_ref(base, entry=(marker + second_tail).strip(), **second)
    refs[index - 1:index] = [first, second_row]


def main() -> None:
    result = json.loads(SOURCE.read_text(encoding="utf-8"))

    # Inherited-author notation was visually confirmed in the source pages.
    inherited_rows = {
        "P10": [15, 25], "P12": [15, 21, 31, 39],
        "P08": [30, 36, 41, 52], "P09": [26, 32, 37, 38],
        "P11": [9, 17, 18, 48, 88, 99], "W03": [26, 27, 28, 55],
        "W07": [23, 30, 34], "W08": [20], "W05": [34],
    }
    for document_id, indexes in inherited_rows.items():
        refs = result["documents"][document_id]["references"]
        for index in indexes:
            ref = refs[index - 1]
            if "inherited_author_notation" not in ref.get("quality_flags", []):
                ref.setdefault("quality_flags", []).append("inherited_author_notation")
            ref.setdefault("correction_provenance", []).append(PROVENANCE)

    # Six surnames were inherited from the preceding row or corrupted by OCR.
    surname_corrections = {
        ("P10", 76): "Nuño",
        ("W04", 26): "Dávila",
        ("W11", 17): "Cerutti",
        ("W11", 29): "Kalemli-Özcan",
        ("W08", 22): "Jordà",
        ("W08", 39): "Méndez",
    }
    for (document_id, index), surname in surname_corrections.items():
        ref = result["documents"][document_id]["references"][index - 1]
        ref["surname"] = surname
        ref.setdefault("correction_provenance", []).append(PROVENANCE)

    # One running header was appended at the page boundary.
    p03 = result["documents"]["P03"]["references"]
    marker = " 42 THE AMERICAN ECONOMIC REVIEW MONTH YEAR"
    if marker not in p03[6]["entry"]:
        raise RuntimeError("P03-R007 no contiene el encabezado esperado")
    p03[6]["entry"] = p03[6]["entry"].split(marker, 1)[0]
    p03[6]["page_end"] = p03[6]["page_start"]
    p03[6].setdefault("correction_provenance", []).append(PROVENANCE)

    # Split every visually verified fused row, processing each document from
    # the highest current index downward so indexes remain stable.
    split_two(p03, 8, " , , and Charles L. Evans,", {
        "surname": "Christiano", "year": 2005,
        "title": "Nominal Rigidities and the Dynamic Effects of a Shock to Monetary Policy",
        "inherited": True,
    })

    p05 = result["documents"]["P05"]["references"]
    split_two(p05, 20, " di Giovanni, Julian,", {
        "surname": "di Giovanni", "year": 2014,
        "title": "Firms, Destinations, and Aggregate Fluctuations",
    })
    split_two(p05, 3, " Antr`as, Pol, Teresa C. Fort,", {
        "surname": "Antràs", "year": 2017,
        "title": "The Margins of Global Sourcing: Theory and Evidence from U.S. Firms",
    }, {"surname": "Antràs"})

    p09 = result["documents"]["P09"]["references"]
    split_two(p09, 41, " andFlorianScheuer,", {
        "surname": "Kurlat", "year": 2020, "title": "Signalling to Experts", "inherited": True,
    })

    p11 = result["documents"]["P11"]["references"]
    split_two(p11, 105, " van der Beck, Philippe,", {
        "surname": "van der Beck", "year": 2025,
        "title": "A Bound on Price Impact and Disagreement",
    })
    split_two(p11, 19, " Boroviˇcka, Jaroslav", {
        "surname": "Borovička", "year": 2019,
        "title": "Risk Premia and Unemployment Fluctuations",
    }, {"quality_flags": ["inherited_author_notation"]})

    w03 = result["documents"]["W03"]["references"]
    appendix = w03[66]
    if not appendix["entry"].startswith("Here, we reproduce formulas derived from Proposition 1"):
        raise RuntimeError("W03-R067 ya no coincide con el texto de apéndice")
    del w03[66]
    w03[45]["surname"] = "Kalemli-Özcan"
    w03[45].setdefault("correction_provenance", []).append(PROVENANCE)
    split_two(w03, 45, " Kalemli- ̈Ozcan,Sebnem,", {
        "surname": "Kalemli-Özcan", "year": 2019,
        "title": "US monetary policy and international risk spillovers",
    }, {"quality_flags": ["inherited_author_notation"]})
    # The following Five Facts row now follows the newly separated Kalemli-Özcan row.
    w03[46]["surname"] = "Kalemli-Özcan"
    w03[46]["quality_flags"] = list(dict.fromkeys(w03[46].get("quality_flags", []) + ["inherited_author_notation"]))
    w03[46].setdefault("correction_provenance", []).append(PROVENANCE)

    w04 = result["documents"]["W04"]["references"]
    split_two(w04, 42, " andCampbellLeith,", {
        "surname": "Leeper", "year": 2016,
        "title": "Understanding inflation as a joint monetary–fiscal phenomenon", "inherited": True,
    })
    split_two(w04, 32, " , , , and , “Macroeconomic implications", {
        "surname": "Guerrieri", "year": 2022,
        "title": "Macroeconomic implications of COVID-19: Can negative supply shocks cause demand shortages?",
        "inherited": True,
    })
    cochrane = w04[19]
    cochrane_markers = [
        " ,“Michelson-Morley,Fisher,andOccam:",
        " , “Stepping on a rake:",
        " , “The fiscal theory of the price level,”",
    ]
    if not all(marker in cochrane["entry"] for marker in cochrane_markers):
        raise RuntimeError("W04-R020 no contiene las cuatro citas de Cochrane esperadas")
    first_text, rest = cochrane["entry"].split(cochrane_markers[0], 1)
    second_text, rest = (cochrane_markers[0] + rest).split(cochrane_markers[1], 1)
    third_text, fourth_tail = (cochrane_markers[1] + rest).split(cochrane_markers[2], 1)
    first = make_ref(cochrane, surname="Cochrane", year=1998, title="A frictionless view of US inflation", entry=first_text)
    second = make_ref(cochrane, surname="Cochrane", year=2018, title="Michelson-Morley, Fisher, and Occam: The radical implications of stable quiet inflation at the zero bound", entry=second_text, inherited=True)
    third = make_ref(cochrane, surname="Cochrane", year=2018, title="Stepping on a rake: The fiscal theory of monetary policy", entry=third_text, inherited=True)
    fourth = make_ref(cochrane, surname="Cochrane", year=2023, title="The fiscal theory of the price level", entry=cochrane_markers[2] + fourth_tail, inherited=True)
    w04[19:20] = [first, second, third, fourth]

    w07 = result["documents"]["W07"]["references"]
    split_two(w07, 27, " Labont ́e, Marc,", {
        "surname": "Labonté", "year": 2021,
        "title": "The Federal Reserve’s Response to COVID-19: Policy Issues",
    })

    w08 = result["documents"]["W08"]["references"]
    split_two(w08, 41, " , “A Theory of Input-Output Architecture,”", {
        "surname": "Oberfield", "year": 2018,
        "title": "A Theory of Input-Output Architecture", "inherited": True,
    })
    split_two(w08, 30, " andRandallWright,", {
        "surname": "Lagos", "year": 2005,
        "title": "Unified Framework for Monetary Theory and Policy Analysis", "inherited": True,
    })
    split_two(w08, 14, " , , and Matthew V. Leduc,", {
        "surname": "Elliott", "year": 2022,
        "title": "Supply Network Formation and Fragility", "inherited": True,
    })

    w05 = result["documents"]["W05"]["references"]
    split_two(w05, 26, " andChi-FuHuang,", {
        "surname": "Duffie", "year": 1985,
        "title": "Implementing Arrow-Debreu Equilibria by Continuous Trading of Few Long-Lived Securities",
        "inherited": True,
    })
    split_two(w05, 2, " , ,HugoHopenhayn,", {
        "surname": "Aguiar", "year": None,
        "title": "Take the short route: Equilibrium default and debt maturity",
        "inherited": True, "extra_flags": ["source_year_malformed"],
    })

    w02 = result["documents"]["W02"]["references"]
    base = w02[27]
    first_text, rest = base["entry"].split(" den Heuvel, Skander J. Van,", 1)
    second_text, third_tail = ("den Heuvel, Skander J. Van," + rest).split(" E.,Jr.LucasRobert", 1)
    w02[27:28] = [
        make_ref(base, surname="Davis", year=2006, title="The Flow Approach to Labor Markets: New Data Sources and Micro-Macro Links", entry=first_text),
        make_ref(base, surname="Van den Heuvel", year=2002, title="The Bank Capital Channel of Monetary Policy", entry=second_text),
        make_ref(base, surname="Lucas", year=1987, title="Money and Interest in a Cash-in-Advance Economy", entry="E.,Jr.LucasRobert" + third_tail),
    ]

    references = [ref for document in result["documents"].values() for ref in document["references"]]
    flags = Counter(flag for ref in references for flag in ref.get("quality_flags", []))
    result["meta"]["reference_entries"] = len(references)
    result["meta"]["quality_flag_counts"] = dict(flags)
    result["meta"].setdefault("structural_corrections_applied", []).extend([
        "P03-R008", "P05-R003", "P05-R020", "P09-R041", "P11-R019", "P11-R105",
        "W03-R045", "W03 appendix false positive", "W04-R020", "W04-R032", "W04-R042",
        "W07-R027", "W08-R014", "W08-R030", "W08-R041", "W05-R002", "W05-R026", "W02-R028",
    ])
    result["meta"]["exhaustive_ai_audit"] = {
        "date": "2026-09-17",
        "scope": "all_rows_with_automatic_screening_and_visual_review_of_flagged_rows",
        "human_external_audit": False,
        "warning": "La cobertura es integral, pero la revisión visual fue realizada por Codex y no es una certificación humana externa.",
    }
    result["quality_control"]["top_surnames"] = Counter(ref["surname"] for ref in references).most_common(30)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "reference_entries": len(references),
        "quality_flag_counts": dict(flags),
        "structural_corrections_added": 18,
        "human_external_audit": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
