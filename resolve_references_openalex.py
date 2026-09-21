"""Resolve extracted bibliography entries against the public OpenAlex API.

The script keeps the original parsed record untouched, stores every API response in
an incremental cache, and separates high-confidence matches from records that still
need review.  It is intentionally conservative: an approximate search result is not
promoted to a resolved identity unless its title, author and year evidence agree.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.client import IncompleteRead
import json
import os
import re
import time
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "referencias_parseadas_candidate.json"
CACHE = ROOT / "data" / "openalex" / "reference_resolution_cache.json"
OUTPUT = ROOT / "data" / "referencias_resueltas_openalex.json"
MAILTO = "alejandroventuraventurameza@gmail.com"
API = "https://api.openalex.org/works"
API_KEY = os.environ.get("OPENALEX_API_KEY")

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
URL_RE = re.compile(r"https?://\S+", re.I)
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a", "an", "and", "as", "at", "by", "de", "del", "der", "des", "do",
    "el", "en", "for", "from", "in", "la", "las", "le", "los", "of", "on",
    "or", "the", "to", "un", "una", "und", "with", "working", "paper",
}


def norm(value: str | None) -> str:
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    return " ".join(TOKEN_RE.findall(ascii_value.lower()))


def compact(value: str | None) -> str:
    return norm(value).replace(" ", "")


def tokens(value: str | None) -> set[str]:
    return {token for token in norm(value).split() if len(token) > 1 and token not in STOPWORDS}


def clean_doi(value: str) -> str | None:
    match = DOI_RE.search(value.replace(" ", ""))
    if not match:
        return None
    doi = match.group(0)
    # PDF references often concatenate the following ``URL http...`` token
    # to a DOI after whitespace normalization.  It is not part of the DOI.
    doi = re.split(r"(?i)(?:\.url|urlhttps?://|https?://)", doi, maxsplit=1)[0]
    return doi.rstrip(".,;:)]}").lower()


def citation_query(entry: str) -> str:
    value = URL_RE.sub(" ", entry)
    value = DOI_RE.sub(" ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:700]


def work_authors(work: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for authorship in work.get("authorships") or []:
        author = authorship.get("author") or {}
        if author.get("display_name"):
            names.append(author["display_name"])
    return names


def surname_agrees(surname: str | None, work: dict[str, Any]) -> bool:
    target = compact(surname)
    if not target:
        return False
    for name in work_authors(work):
        candidate = compact(name)
        if target in candidate or candidate.endswith(target):
            return True
        # PDF extraction sometimes removes spaces from a compound surname.
        if len(target) >= 6 and target[:6] in candidate:
            return True
    return False


@dataclass
class Evidence:
    title_similarity: float
    citation_title_coverage: float
    author_match: bool
    year_distance: int | None
    score: float


def score_work(ref: dict[str, Any], work: dict[str, Any]) -> Evidence:
    parsed_title = ref.get("title")
    work_title = work.get("display_name") or ""
    title_similarity = (
        SequenceMatcher(None, norm(parsed_title), norm(work_title)).ratio()
        if parsed_title else 0.0
    )
    work_title_tokens = tokens(work_title)
    citation_tokens = tokens(ref.get("entry"))
    citation_title_coverage = (
        len(work_title_tokens & citation_tokens) / len(work_title_tokens)
        if work_title_tokens else 0.0
    )
    author_match = surname_agrees(ref.get("surname"), work)
    ref_year = ref.get("year")
    work_year = work.get("publication_year")
    year_distance = abs(ref_year - work_year) if ref_year and work_year else None
    year_score = 0.5 if year_distance is None else (1.0 if year_distance == 0 else 0.7 if year_distance == 1 else 0.0)
    title_score = title_similarity if parsed_title else citation_title_coverage
    score = 0.68 * title_score + 0.20 * float(author_match) + 0.12 * year_score
    return Evidence(title_similarity, citation_title_coverage, author_match, year_distance, score)


def classify(ref: dict[str, Any], work: dict[str, Any], evidence: Evidence, doi: str | None) -> str:
    work_doi = (work.get("doi") or "").removeprefix("https://doi.org/").lower()
    if doi and work_doi == doi:
        return "matched_high_confidence"
    year_ok = evidence.year_distance is None or evidence.year_distance <= 1
    if ref.get("title"):
        # Economics papers often circulate as working papers years before the
        # indexed journal version. Near-identical title plus matching author is
        # stronger identity evidence than publication-year agreement.
        if evidence.title_similarity >= 0.95 and evidence.author_match:
            return "matched_high_confidence"
        if evidence.title_similarity >= 0.88 and evidence.author_match and year_ok:
            return "matched_high_confidence"
        if evidence.title_similarity >= 0.96 and year_ok:
            return "matched_high_confidence"
    else:
        title_word_count = len(tokens(work.get("display_name")))
        if (
            title_word_count >= 3
            and evidence.citation_title_coverage >= 0.80
            and evidence.author_match
            and year_ok
        ):
            return "matched_high_confidence"
    if evidence.score >= 0.72:
        return "matched_review"
    return "unresolved"


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def api_url(ref: dict[str, Any]) -> tuple[str, str, str | None]:
    doi = clean_doi(ref.get("entry") or "")
    if doi:
        query = f"https://doi.org/{doi}"
        params = {
            "select": "id,doi,display_name,publication_year,type,authorships,primary_location",
            "mailto": MAILTO,
        }
        return f"{API}/{quote(query, safe=':/')}?{urlencode(params)}", f"doi:{doi}", doi
    query = ref.get("title") or citation_query(ref.get("entry") or "")
    if ref.get("surname") and ref.get("title"):
        query = f"{query} {ref['surname']}"
    # In OpenAlex advanced-search syntax, ``?`` and ``*`` are wildcard
    # operators. Literal punctuation from publication titles therefore causes
    # HTTP 400. Remove only those operators from the request; the stored title
    # and the normalized cache key remain unchanged.
    request_query = re.sub(r"[?*]+", " ", query)
    request_query = re.sub(r"\s+", " ", request_query).strip()
    params = {
        "search": request_query,
        "per-page": "5",
        "select": "id,doi,display_name,publication_year,type,authorships,primary_location",
        "mailto": MAILTO,
    }
    return f"{API}?{urlencode(params)}", f"search:{norm(query)}", None


def fetch(url: str, retries: int = 5) -> dict[str, Any]:
    headers = {"User-Agent": f"SakiBigioReferenceAudit/1.0 (mailto:{MAILTO})"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    request = Request(url, headers=headers)
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            last_error = exc
            if exc.code == 429:
                retry_after = int(exc.headers.get("Retry-After", "0") or 0)
                # A long Retry-After signals an exhausted daily budget rather
                # than a momentary request-rate burst. Preserve the 429 now;
                # the next run resumes from the incremental cache.
                if retry_after > 60:
                    raise
                time.sleep(min(2 ** attempt, 20))
                continue
            if 500 <= exc.code < 600:
                time.sleep(min(2 ** attempt, 20))
                continue
            raise
        except (URLError, TimeoutError, IncompleteRead) as exc:
            last_error = exc
            if attempt + 1 == retries:
                raise
            time.sleep(min(2 ** attempt, 20))
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"No response after {retries} attempts: {url}")


def flatten(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for doc_id, document in candidate["documents"].items():
        for index, ref in enumerate(document["references"], start=1):
            rows.append({"ref_id": f"{doc_id}-R{index:03d}", "doc_id": doc_id, "index": index, **ref})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("pending", "doi", "all"), default="all")
    parser.add_argument("--delay", type=float, default=0.12)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    candidate = load_json(INPUT, {})
    rows = flatten(candidate)
    if args.scope == "pending":
        rows = [row for row in rows if "title_not_isolated" in row.get("quality_flags", [])]
    elif args.scope == "doi":
        rows = [row for row in rows if clean_doi(row.get("entry") or "")]

    cache = load_json(CACHE, {"meta": {"mailto": MAILTO}, "queries": {}})
    cache.setdefault("meta", {}).update({
        "mailto": MAILTO,
        "api_key_configured": bool(API_KEY),
        "authentication": "Bearer header" if API_KEY else "anonymous",
    })
    queries = cache.setdefault("queries", {})
    resolved: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    plans = [(ref, *api_url(ref)) for ref in rows]
    pending = {
        cache_key: url
        for _ref, url, cache_key, _doi in plans
        if cache_key not in queries and not args.cache_only
    }
    query_errors: dict[str, dict[str, str]] = {}

    def fetch_one(url: str) -> dict[str, Any]:
        payload = fetch(url)
        time.sleep(args.delay)
        return payload

    if pending:
        completed = 0
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            future_to_query = {
                executor.submit(fetch_one, url): (cache_key, url)
                for cache_key, url in pending.items()
            }
            for future in as_completed(future_to_query):
                cache_key, url = future_to_query[future]
                try:
                    queries[cache_key] = {"url": url, "response": future.result()}
                except Exception as exc:  # preserve the exact failed URL for audit
                    query_errors[cache_key] = {
                        "error": type(exc).__name__, "status_code": getattr(exc, "code", None),
                        "message": str(exc), "url": url,
                    }
                completed += 1
                if completed % 100 == 0:
                    save_json(CACHE, cache)
                    print(f"consultas nuevas: {completed}/{len(pending)}", flush=True)
        save_json(CACHE, cache)

    for ref, url, cache_key, doi in plans:
        if cache_key not in queries:
            failure = query_errors.get(cache_key, {
                "error": "NotRequestedCacheOnly" if args.cache_only else "MissingResponse",
                "status_code": None,
                "message": "No response stored in the incremental cache", "url": url,
            })
            errors.append({"ref_id": ref["ref_id"], **failure})
            continue

        payload = queries[cache_key]["response"]
        candidates = payload.get("results") or ([payload] if payload.get("id") else [])
        ranked = sorted(
            ((score_work(ref, work), work) for work in candidates),
            key=lambda item: item[0].score,
            reverse=True,
        )
        if not ranked:
            status = "unresolved"
            best_work: dict[str, Any] | None = None
            evidence: Evidence | None = None
        else:
            evidence, best_work = ranked[0]
            status = classify(ref, best_work, evidence, doi)

        result: dict[str, Any] = {
            "ref_id": ref["ref_id"],
            "doc_id": ref["doc_id"],
            "reference_index": ref["index"],
            "source_pages": [ref.get("page_start"), ref.get("page_end")],
            "parsed": {
                "surname": ref.get("surname"),
                "year": ref.get("year"),
                "title": ref.get("title"),
                "entry": ref.get("entry"),
                "quality_flags": ref.get("quality_flags") or [],
            },
            "extracted_doi": doi,
            "status": status,
            "query_url": url,
            "candidate_count": len(candidates),
        }
        if best_work is not None and evidence is not None:
            result["best_match"] = {
                "id": best_work.get("id"),
                "doi": best_work.get("doi"),
                "display_name": best_work.get("display_name"),
                "publication_year": best_work.get("publication_year"),
                "type": best_work.get("type"),
                "authors": work_authors(best_work),
                "primary_location": best_work.get("primary_location"),
                "evidence": {
                    "title_similarity": round(evidence.title_similarity, 6),
                    "citation_title_coverage": round(evidence.citation_title_coverage, 6),
                    "author_match": evidence.author_match,
                    "year_distance": evidence.year_distance,
                    "score": round(evidence.score, 6),
                },
            }
        resolved.append(result)

    save_json(CACHE, cache)
    counts: dict[str, int] = {}
    for row in resolved:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    output = {
        "meta": {
            "source": str(INPUT.relative_to(ROOT)),
            "api": API,
            "mailto": MAILTO,
            "api_key_configured": bool(API_KEY),
            "scope": args.scope,
            "records_attempted": len(rows),
            "records_returned": len(resolved),
            "unique_queries_total": len({cache_key for _ref, _url, cache_key, _doi in plans}),
            "unique_queries_cached": len({cache_key for _ref, _url, cache_key, _doi in plans if cache_key in queries}),
            "status_counts": counts,
            "errors": errors,
            "warning": "Only matched_high_confidence records are safe for automatic identity assignment; matched_review remains provisional.",
        },
        "references": resolved,
    }
    save_json(args.output, output)
    print(json.dumps(output["meta"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
