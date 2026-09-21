"""Apply title-boundary corrections found by the exhaustive AI audit."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "referencias_parseadas_candidate.json"
PROVENANCE = "exhaustive_title_boundary_audit_2026-09-17"


CORRECTIONS = {
    ("C02", 4): {"title": "Skewness and Time-Varying Second Moments in a Nonlinear Production Network: Theory and Evidence"},
    ("P01", 5): {"title": "Policy Rules for Open Economies"},
    ("P01", 31): {"title": "Why do countries float the way they float?"},
    ("P02", 52): {"title": "Coercion, Capital and European States, AD 990-1992"},
    ("P06", 5): {"title": "Agency costs, net worth and business fluctuations"},
    ("P06", 18): {"title": "Waiting for news in the market for lemons"},
    ("P06", 27): {"title": "Reallocation in the great recession: cleansing or not?"},
    ("P06", 33): {"year": 2010, "title": "Slapped by the invisible hand: The panic of 2007"},
    ("P07", 38): {"title": "A Monetary History of the United States, 1867-1960"},
    ("P07", 40): {"surname": "Galí", "title": "Monetary Policy, Inflation, and the Business Cycle: An Introduction to the New Keynesian Framework and Its Applications"},
    ("P07", 80): {"title": "Interest and Prices: Foundations of a Theory of Monetary Policy"},
    ("P13", 26): {"title": "Will the Developing World’s Growing Middle Class Support Low Carbon Policies?"},
    ("W09", 16): {"title": "Bank leverage and monetary policy’s risk-taking channel: Evidence from the United States"},
    ("W09", 20): {"title": "Does bank capital affect lending behavior?"},
    ("W09", 36): {"title": "What do a million observations on banks say about the transmission of monetary policy?"},
    ("W07", 48): {"title": "The Tariff on Animal and Vegetable Oils"},
    ("W06", 19): {"title": "Recursive Macroeconomic Theory"},
}


def main() -> None:
    result = json.loads(SOURCE.read_text(encoding="utf-8"))
    changed = []
    for (document_id, index), fields in CORRECTIONS.items():
        ref = result["documents"][document_id]["references"][index - 1]
        before = {field: ref.get(field) for field in fields}
        ref.update(fields)
        ref["title_extraction_method"] = "manual_exhaustive_title_boundary_audit"
        ref.setdefault("correction_provenance", []).append(PROVENANCE)
        changed.append({"ref_id": f"{document_id}-R{index:03d}", "before": before, "after": fields})

    references = [ref for document in result["documents"].values() for ref in document["references"]]
    result["meta"]["quality_flag_counts"] = dict(Counter(
        flag for ref in references for flag in ref.get("quality_flags", [])
    ))
    result["meta"]["exhaustive_title_boundary_corrections"] = len(changed)
    result["quality_control"]["top_surnames"] = Counter(ref["surname"] for ref in references).most_common(30)
    SOURCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"corrections": len(changed), "changed": changed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
