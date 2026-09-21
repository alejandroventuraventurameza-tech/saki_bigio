"""Descarga facetas de citantes para las seis obras canónicas más citadas.

La consulta incluye todos los identificadores de versión de esas seis obras. La
operación OR de OpenAlex devuelve cada trabajo citante una sola vez dentro de
cada faceta, evitando seleccionar dos versiones de una misma obra como si
fueran dos trabajos distintos.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CANONICAL = ROOT / "data" / "openalex" / "openalex_02_works_canonical.json"
OUTPUT = ROOT / "data" / "openalex" / "openalex_04_facets_citantes_canonical.json"
MAILTO = "alejandroventuraventurameza@gmail.com"
GROUPS = (
    "publication_year",
    "primary_topic.field.id",
    "institutions.country_code",
    "institutions.type",
    "authorships.institutions.lineage",
)


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": f"saki-bigio-hpe-audit/1.0 (mailto:{MAILTO})"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        return json.load(response)


def main() -> None:
    data = json.loads(CANONICAL.read_text(encoding="utf-8"))
    top_six = data["works"][:6]
    version_ids = sorted(
        {wid for work in top_six for wid in work["member_openalex_ids"]}
    )
    works_filter = "|".join(version_ids)

    results = {}
    urls = {}
    for group in GROUPS:
        url = (
            "https://api.openalex.org/works?"
            f"filter=cites:{works_filter}&group_by={group}&mailto={MAILTO}"
        )
        urls[group] = url
        results[group] = fetch_json(url)

    payload = {
        "meta": {
            "selection_rule": "six canonical works with highest cited_by_count_max_version",
            "canonical_works": [
                {
                    "display_name": work["display_name"],
                    "representative_openalex_id": work["representative_openalex_id"],
                    "member_openalex_ids": work["member_openalex_ids"],
                    "cited_by_count_max_version": work["cited_by_count_max_version"],
                }
                for work in top_six
            ],
            "queried_version_ids": version_ids,
            "urls": urls,
            "warning": "Facets are multi-membership: country and institution groups must not be summed as disjoint categories.",
        },
        **results,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    count = results["publication_year"].get("meta", {}).get("count")
    print(f"{len(top_six)} canonical works, {len(version_ids)} version ids, {count} unique citing works")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
