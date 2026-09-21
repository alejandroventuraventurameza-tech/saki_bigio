"""Extrae referencias del corpus con trazabilidad y controles de calidad.

El resultado predeterminado es un archivo candidato. No reemplaza la base histórica
usada por el análisis hasta que una muestra haya sido validada manualmente.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Falta pypdf. Instale las dependencias de requirements.txt") from exc


ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "data" / "corpus.csv"
DEFAULT_OUTPUT = ROOT / "data" / "referencias_parseadas_candidate.json"

REFERENCE_HEADING = re.compile(
    r"(?i)^\s*(?:(?:\d+(?:\.\d+)*|[A-Z])\.?\s+)?"
    r"(references|bibliography|bibliograf[ií]a|referencias|literature cited|works cited)\s*$"
)
END_HEADING = re.compile(
    r"(?i)^\s*(?:(?:\d+(?:\.\d+)*|[A-Z])\.?\s+)?"
    r"(appendix|appendices|online appendix|ap[eé]ndice|anexo|supplementary material|for online publication)(?:\b|[A-Z]).*$"
)
APPENDIX_SECTION_HEADING = re.compile(
    r"^(?:[A-Z]\.?|[IVX]+\.)\s+(?:First|Data|Proofs?|Additional|Calibration|Regression|Model|Figures?|Tables?|"
    r"Robustness|Derivations?|Numerical|Estimation|Empirical|Expressions|Equilibrium|Appendix)\b.*$",
    re.I,
)
YEAR = re.compile(r"(?<!\d)(18\d{2}|19\d{2}|20[0-2]\d)(?:[a-z])?(?!\d)", re.I)
AUTHOR_PREFIX = re.compile(
    r"^(?P<surname>(?:(?:[Dd]e|[Dd]el|[Ll]a|[Ll]as|[Ll]os|[Vv]an|[Vv]on|[Uu]l|e)\s+){0,2}"
    r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]+)"
    r",\s*(?:[A-ZÀ-ÖØ-Þ]|[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ])"
)
AUTHOR_YEAR_PREFIX = re.compile(
    r"^(?P<surname>(?:(?:[Dd]e|[Dd]el|[Ll]a|[Ll]as|[Ll]os|[Vv]an|[Vv]on|[Uu]l|e)\s+){0,2}"
    r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]+)"
    r"\s+\((?:18\d{2}|19\d{2}|20[0-2]\d)(?:[a-z])?\)"
)
CORPORATE_YEAR_PREFIX = re.compile(
    r"^(?P<surname>[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ&'’\-.]+"
    r"(?:\s+[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ&'’\-.]+){1,10})"
    r"\s+\((?:18\d{2}|19\d{2}|20[0-2]\d)(?:[a-z])?\)"
)
BRACKET_START = re.compile(r"^\[(?P<label>[^\]]{2,1200})\]")
NUMBERED_START = re.compile(r"^(?:\[\d+\]|\d{1,3}[.)])\s+\S")
REPEATED_AUTHOR_START = re.compile(
    r"^(?:[—–_]{2,}\s*|,\s*[A-ZÀ-ÖØ-Þ]|and\s+(?:,|[A-ZÀ-ÖØ-Þ])|"
    r"y\s+(?:,|[A-ZÀ-ÖØ-Þ])|e\s+(?:,|[A-ZÀ-ÖØ-Þ]))"
)
NORMAL_ORDER_PREFIX = re.compile(
    r"^[A-ZÀ-ÖØ-Þ](?:\.|[A-Za-zÀ-ÖØ-öø-ÿ.'’\-]*)"
    r"(?:\s+(?:[A-ZÀ-ÖØ-Þ](?:\.|[A-Za-zÀ-ÖØ-öø-ÿ.'’\-]*)|and|y|e)){1,15}"
    r"(?:,|\.\s)"
)

FALSE_SURNAMES = {
    "American", "Annual", "Article", "Bank", "Banking", "Board", "Book",
    "Cambridge", "Chapter", "Chicago", "Columbia", "Conference", "Control",
    "Data", "Discussion", "Draft", "Dynamic", "Econometrica", "Economic",
    "Economics", "Elsevier", "Federal", "Finance", "Financial", "Forthcoming",
    "Governance", "Harvard", "International", "Journal", "Letters", "Liquidity",
    "London", "Macroeconomics", "Manuscript", "Mimeo", "Monetary", "Money",
    "National", "NBER", "Notes", "Number", "OECD", "Oxford", "Paper", "Papers",
    "Policy", "Press", "Princeton", "Proceedings", "Quarterly", "Report", "Reserve",
    "Review", "Series", "Society", "Springer", "Staff", "Stanford", "Studies",
    "Technical", "Theory", "University", "Volume", "Washington", "Wiley",
    "Working", "World", "Research", "Results", "Table", "Figure",
    "Evidence", "Stability", "Structure", "Fund", "Funds", "Government",
}


def compact_text(value: str) -> str:
    """ASCII alphanumerics for conservative local string comparisons."""
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def load_corpus(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {row["slug"]: row for row in csv.DictReader(handle)}


def extract_layout_pages(path: Path) -> list[list[str]]:
    """Extrae líneas conservando la sangría horizontal del PDF."""
    reader = PdfReader(str(path))
    pages: list[list[str]] = []
    for page in reader.pages:
        try:
            text = page.extract_text(extraction_mode="layout") or ""
        except (TypeError, ValueError):
            text = page.extract_text() or ""
        if not text.strip():
            text = page.extract_text() or ""
        text = re.sub(r"/uni([0-9A-Fa-f]{4})", lambda m: chr(int(m[1], 16)), text)
        text = unicodedata.normalize('NFKC', text)
        pages.append(text.splitlines())
    return pages


def _heading_locations(pages: list[list[str]]) -> list[tuple[int, int]]:
    locations: list[tuple[int, int]] = []
    for page_index, lines in enumerate(pages):
        for line_index, line in enumerate(lines):
            if REFERENCE_HEADING.fullmatch(line.strip()):
                locations.append((page_index, line_index))
    return locations


def reference_lines(path: Path) -> list[dict[str, object]]:
    """Devuelve el último bloque bibliográfico como líneas con página y sangría."""
    pages = extract_layout_pages(path)
    headings = _heading_locations(pages)
    if not headings:
        return []
    start_page, start_line = headings[-1]
    result: list[dict[str, object]] = []
    stopped = False
    blank_before = True
    for page_index in range(start_page, len(pages)):
        first_line = start_line + 1 if page_index == start_page else 0
        for line_index in range(first_line, len(pages[page_index])):
            raw = pages[page_index][line_index].rstrip()
            text = raw.strip()
            if not text:
                blank_before = True
                continue
            if END_HEADING.match(text) or APPENDIX_SECTION_HEADING.match(text):
                stopped = True
                break
            if re.fullmatch(r"(?:\[?\d{1,3}/\d{1,3}\]?|\d{1,3})", text):
                continue
            if text.upper() in {"ACCEPTED MANUSCRIPT", "REFERENCES", "BIBLIOGRAPHY", "REFERENCIAS"}:
                continue
            result.append({
                "page": page_index + 1,
                "line": line_index + 1,
                "indent": len(raw) - len(raw.lstrip()),
                "text": text,
                "blank_before": blank_before,
            })
            blank_before = False
        if stopped:
            break
    return result


def _bracket_surname(text: str) -> str | None:
    match = BRACKET_START.match(re.sub(r"\s+", " ", text).strip())
    if not match:
        return None
    label = re.sub(r"\([^)]*\).*", "", match.group("label")).strip()
    label = re.split(r"\s+(?:and|y|et\s+al\.?)(?:\s|$)", label, maxsplit=1, flags=re.I)[0]
    return label.split(",", 1)[0].strip() or None


def _explicit_surname(text: str) -> str | None:
    bracket = _bracket_surname(text)
    if bracket:
        return bracket
    for pattern in (AUTHOR_PREFIX, AUTHOR_YEAR_PREFIX, CORPORATE_YEAR_PREFIX):
        match = pattern.match(text)
        if match:
            return match.group("surname").strip()
    initials = re.match(r"^(?:[A-ZÀ-ÖØ-Þ]\.\s*)+([A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]+)", text)
    if initials:
        return initials[1]
    particle = re.match(r"^((?:d['’]|von|van)[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]+),", text)
    if particle:
        return particle[1]
    corporate = re.match(r"^([^,]{5,100}(?:Corporation|Committee|Supervision|Bank)),", text)
    if corporate:
        return corporate[1]
    return None


def _looks_like_start(line: dict[str, object], base_indent: int) -> tuple[bool, str | None, bool]:
    text = str(line["text"])
    indent = int(line["indent"])
    bracket_surname = _bracket_surname(text)
    if bracket_surname:
        return True, bracket_surname, False
    if NUMBERED_START.match(text):
        return True, None, False
    if REPEATED_AUTHOR_START.match(text) and indent <= base_indent + 4:
        return True, None, True
    surname = _explicit_surname(text)
    if surname and (
        CORPORATE_YEAR_PREFIX.match(text) or surname.split()[0] not in FALSE_SURNAMES
    ) and indent <= base_indent + 1:
        return True, surname, False
    first_token = re.split(r"[\s,.]", text, maxsplit=1)[0]
    if (
        indent <= base_indent + 1
        and bool(line.get("blank_before"))
        and first_token not in FALSE_SURNAMES
        and (
            NORMAL_ORDER_PREFIX.match(text)
            or (YEAR.search(text) and re.match(r"^[A-ZÀ-ÖØ-Þ].{25,}", text))
        )
    ):
        normal_surname = None
        prefix = re.split(r"(?<=[a-zà-öø-ÿ])\.\s", text, maxsplit=1)[0]
        prefix = re.split(r"\s+(?:and|y)\s+", prefix, maxsplit=1)[0]
        if "," in prefix:
            first_author = prefix.split(",", 1)[0]
        else:
            first_author = prefix
        name_tokens = re.findall(r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]+", first_author)
        if name_tokens:
            normal_surname = name_tokens[-1]
        return True, normal_surname, False
    return False, None, False


def _join_entry_lines(lines: list[dict[str, object]]) -> str:
    pieces: list[str] = []
    for item in lines:
        text = re.sub(r"\s+", " ", str(item["text"])).strip()
        if not text:
            continue
        if pieces and re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]-$", pieces[-1]) and re.match(r"^[a-zà-öø-ÿ]", text):
            pieces[-1] = pieces[-1][:-1] + text
        else:
            pieces.append(text)
    return " ".join(pieces).strip(" ,;•")


def _split_embedded_parenthetical_entries(entry: str) -> list[str]:
    """Separa referencias que el PDF colocó en una misma línea física."""
    parenthetical_parts: list[str] = []
    last = 0
    for match in re.finditer(
        r"(?P<end>(?:\d{2,4}|[A-Za-zÀ-ÖØ-öø-ÿ]{3,}))\.\s*"
        r"(?P<next>(?:(?:(?:[Dd]e|[Dd]el|[Ll]a|[Vv]an|[Vv]on|[Uu]l|e)\s+)?"
        r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]+),\s+)"
        r"(?=.{0,150}?\((?:18\d{2}|19\d{2}|20[0-2]\d)(?:[a-z])?\))",
        entry,
    ):
        split_at = match.start("next")
        # Un punto dentro de la lista de autores (p. ej. ``Jeremy I. and``)
        # no puede cerrar una referencia: el tramo izquierdo debe contener su año.
        if YEAR.search(entry[last:split_at]) is None:
            continue
        parenthetical_parts.append(entry[last:split_at])
        last = split_at
    parenthetical_parts.append(entry[last:])

    parts: list[str] = []
    for parenthetical_part in parenthetical_parts:
        last = 0
        boundary_matches = re.finditer(
            r"(?P<end>(?:\d{2,4}|[A-Za-zÀ-ÖØ-öø-ÿ]{3,}))\.\s*"
            r"(?P<next>(?:(?:,\s*)+(?:and\s*)?(?:,\s*)*(?:[A-ZÀ-ÖØ-Þ]|[\"“])|"
            r"and\s*[A-ZÀ-ÖØ-Þ]|"
            r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ/0-9]{2,35},\s*[A-ZÀ-ÖØ-Þ]))",
            parenthetical_part,
        )
        for match in boundary_matches:
            split_at = match.start("next")
            if YEAR.search(parenthetical_part[last:split_at]) is None:
                continue
            right_context = parenthetical_part[split_at:split_at + 500]
            if YEAR.search(right_context) is None and not re.search(r"\bforthcoming\b", right_context, re.I):
                continue
            parts.append(parenthetical_part[last:split_at])
            last = split_at
        parts.append(parenthetical_part[last:])

    numbered_parts: list[str] = []
    for part in parts:
        last = 0
        for match in re.finditer(
            r"(?<=\.)(?:\d+(?:[,.]\d+)*)\s+"
            r"(?P<next>(?:(?:,\s*)+(?:and\s*)?(?:,\s*)*)?"
            r"[A-ZÀ-ÖØ-Þ][^.;]{2,120}?,)",
            part,
        ):
            split_at = match.start("next")
            if YEAR.search(part[last:split_at]) is None:
                continue
            if YEAR.search(part[split_at:split_at + 500]) is None:
                continue
            numbered_parts.append(part[last:split_at])
            last = split_at
        numbered_parts.append(part[last:])

    url_parts: list[str] = []
    for part in numbered_parts:
        last = 0
        for match in re.finditer(
            r"https?://\S+\s+"
            r"(?P<next>[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ˜'’\-]+"
            r"(?:\s+[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ˜.'’\-]*){0,4},\s*"
            r"[A-Za-zÀ-ÖØ-öø-ÿ])",
            part,
        ):
            split_at = match.start("next")
            if YEAR.search(part[last:split_at]) is None:
                continue
            if YEAR.search(part[split_at:split_at + 500]) is None:
                continue
            url_parts.append(part[last:split_at])
            last = split_at
        url_parts.append(part[last:])
    return [part.strip() for part in url_parts if part.strip()]


def split_entries(lines: list[dict[str, object]]) -> list[tuple[str, str, int, int, bool]]:
    if not lines:
        return []
    explicit_indents = [
        int(line["indent"])
        for line in lines
        if _explicit_surname(str(line["text"]))
        and _explicit_surname(str(line["text"])).split()[0] not in FALSE_SURNAMES
    ]
    base_indent = min(explicit_indents) if explicit_indents else min(int(line["indent"]) for line in lines)

    entries: list[tuple[str, str, int, int, bool]] = []
    current: list[dict[str, object]] = []
    current_surname: str | None = None
    current_inherited = False
    last_explicit_surname: str | None = None

    def flush() -> None:
        nonlocal current, current_surname, current_inherited, last_explicit_surname
        if not current:
            return
        entry = _join_entry_lines(current)
        if 30 <= len(entry) <= 5000:
            part_surname = current_surname or last_explicit_surname or ""
            for part_index, part in enumerate(_split_embedded_parenthetical_entries(entry)):
                explicit = _explicit_surname(part)
                surname = explicit or part_surname
                part_surname = surname
                if explicit:
                    last_explicit_surname = explicit
                entries.append((
                    surname,
                    part,
                    int(current[0]["page"]),
                    int(current[-1]["page"]),
                    current_inherited if part_index == 0 else False,
                ))
        current = []
        current_surname = None
        current_inherited = False

    for line in lines:
        is_start, surname, inherited = _looks_like_start(line, base_indent)
        if is_start and current:
            current_text = _join_entry_lines(current)
            # Una comilla abierta indica que la línea siguiente continúa el título.
            if inherited and '”' in str(line['text']) and '“' not in str(line['text']):
                is_start = False
            if (
                YEAR.search(current_text) is None
                and len(current_text) < 100
                and re.search(r"(?:,|\b[A-ZÀ-ÖØ-Þ]\.)$", current_text)
            ):
                is_start = False
            elif (
                YEAR.search(current_text) is None
                and len(current_text) < 300
                and not re.search(r"[.!?;:\"”’]$", current_text)
            ):
                is_start = False
        if is_start:
            flush()
            current = [line]
            current_surname = surname or last_explicit_surname
            current_inherited = inherited
            if surname:
                last_explicit_surname = surname
        elif current:
            current.append(line)
    flush()
    return entries


def parse_entry(
    surname: str,
    entry: str,
    page_start: int,
    page_end: int,
    inherited_author: bool,
) -> dict[str, object] | None:
    if surname in FALSE_SURNAMES:
        return None
    quoted_spans = re.compile(r'“[^”]*”|"[^"]*"|‘[^’]*’')
    date_text = quoted_spans.sub('', entry[:1000])
    date_text = re.sub(r'\d+\s*[-–—]\s*\d+', '', date_text)
    date_text = re.sub(r'(?<!\d)(?:0[1-9]|1[0-2])((?:19|20)\d{2})(?!\d)', r' \1', date_text)
    first_year = YEAR.search(date_text)
    year = int(first_year.group(1)) if first_year else None
    quoted_title = re.search(r'“([^”]{8,500})”|"([^"\n]{8,500})"|‘([^’]{8,500})’', entry)
    title = next((g for g in quoted_title.groups() if g is not None), '').strip(' ,.') if quoted_title else None
    title_method = "quoted" if title else None
    if title is None:
        after_year = re.search(
            r"\((?:18\d{2}|19\d{2}|20[0-2]\d)(?:[a-z])?\)\s*[:.]?\s*(.{8,240}?)(?:\.\s+[A-Z]|$)",
            entry,
        )
        if after_year:
            title = after_year.group(1).strip(" ,.;:")
            title_method = "after_parenthetical_year"
    if title is None:
        # Several economics styles put the year before the title without
        # parentheses: ``Authors, 2004. Title. Journal ...``.  Limit the
        # match to a sentence followed by a recognizable source label.
        source = (
            r"(?:The\s*)?(?:American|Annual|Annals|European|International|Journal|Quarterly|Review|"
            r"Econometrica|Economic|Federal|NBER|Working|Discussion|Technical|Unpublished|"
            r"University|Oxford|Princeton|MIT|Cambridge|Blackwell|Elsevier|Springer|IMF|"
            r"World\s+Bank|Brookings|Handbook|Macroeconomic|FMG|Bank|Rand|Bell|eJournal|"
            r"Giornale|National\s+Tax|FinanzArchiv|North-?\s*Holland|Harvard|Grove|London|"
            r"New\s+Haven|Chicago|Washington|McGraw|CRC|Mimeo|SSRN|Social|In\s+)"
        )
        after_plain_year = re.search(
            rf"(?:18\d{{2}}|19\d{{2}}|20[0-2]\d)(?:[a-z])?\.\s*"
            rf"([^\.\n]{{8,320}}?)\.\s+(?={source})",
            entry,
            re.I,
        )
        if after_plain_year:
            title = after_plain_year.group(1).strip(" ,.;:")
            title_method = "after_plain_year"
    if title is None:
        # Safe fallback for the same author-year style when the following
        # journal is not in the source vocabulary.
        after_plain_year = re.search(
            r"(?:18\d{2}|19\d{2}|20[0-2]\d)(?:[a-z])?\.\s*([^\.\n]{8,320})\.",
            entry,
            re.I,
        )
        if (
            after_plain_year
            and after_plain_year.start() < max(120, int(len(entry) * 0.45))
            and len(after_plain_year.group(1).split()) >= 2
            and not re.match(
                r"(?i)\s*(?:ISSN|URL|https?://|Journal\b|Review\b|Econometrica\b|"
                r"Economic\b|American\b|Quarterly\b|University\b)",
                after_plain_year.group(1),
            )
        ):
            title = after_plain_year.group(1).strip(" ,.;:")
            title_method = "after_plain_year_sentence"
    if title is None:
        # Other bibliographies put the year at the end.  Search for the
        # sentence immediately before the journal/report/publisher marker.
        # Initials such as ``D. Acemoglu.`` can enter the broad capture; the
        # final sentence is the bibliographic title.
        source = (
            r"(?:The\s*)?(?:American|Annual|Annals|European|International|Journal|Quarterly|Review|"
            r"Econometrica|Economic|Federal|NBER|Working|Discussion|Technical|Unpublished|"
            r"University|Oxford|Princeton|MIT|Cambridge|Blackwell|Elsevier|Springer|IMF|"
            r"World\s+Bank|Brookings|Handbook|Macroeconomic|FMG|Bank|Rand|Bell|eJournal|"
            r"Giornale|National\s+Tax|FinanzArchiv|North-?\s*Holland|Harvard|Grove|London|"
            r"New\s+Haven|Chicago|Washington|McGraw|CRC|Mimeo|SSRN|Social|In\s+)"
        )
        before_source = re.search(
            rf"\.\s*(.{{8,420}}?)\.\s*(?={source})",
            entry,
            re.I,
        )
        if before_source:
            candidate = before_source.group(1).rsplit(". ", 1)[-1].strip(" ,.;:")
            if len(candidate.split()) >= 2:
                title = candidate
                title_method = "sentence_before_source"
    if title is None:
        # In book/report styles the title lies between the author block and a
        # publisher marker.  Remove only the leading author block and retain
        # commas that belong to the title itself.
        publisher = re.search(
            r",\s*(?=(?:Annual\s+Review|Econometrica|Journal|Oxford|Princeton|MIT|Cambridge|Blackwell|Springer|Hoover|Harvard|"
            r"University\s+of|McGraw|CRC|Grove|London:|New\s+Haven|Chicago:|Washington|"
            r"International\s+Monetary\s+Fund|Social\s+Science\s+Research\s+Network))",
            entry,
            re.I,
        )
        prefix = entry[:publisher.start()].strip(" ,.;:") if publisher else re.sub(
            r",?\s*(?:18\d{2}|19\d{2}|20[0-2]\d)(?:[a-z])?(?:\.[A-Z0-9.]*)?\s*$",
            "",
            entry,
        ).strip(" ,.;:")
        title_candidate = None
        surname_prefix = re.match(rf"^{re.escape(surname)}\s*,\s*(.*)$", prefix, re.I)
        if surname_prefix:
            rest = surname_prefix.group(1).strip()
            oxford_authors = re.search(r",\s*and\s+[^,]+,\s*(.+)$", rest, re.I)
            joined_authors = re.search(r"\band\s+[^,]+,\s*(.+)$", rest, re.I)
            if oxford_authors:
                title_candidate = oxford_authors.group(1)
            elif joined_authors:
                title_candidate = joined_authors.group(1)
            elif "," in rest:
                title_candidate = rest.split(",", 1)[1]
            elif len(rest.split()) >= 3:
                title_candidate = rest
        elif prefix.startswith(",") or re.match(r"^\s*,", entry):
            title_candidate = prefix.rsplit(",", 1)[-1]
        elif publisher and surname and compact_text(surname) not in compact_text(prefix) and len(prefix.split()) >= 2:
            title_candidate = prefix
        if title_candidate:
            title_candidate = title_candidate.strip(" ,.;:")
            if len(title_candidate) >= 8 and len(title_candidate.split()) >= 2:
                title = title_candidate
                title_method = "between_author_and_publisher"
    flags: list[str] = []
    if year is None:
        flags.append("missing_year")
    if title is None:
        flags.append("title_not_isolated")
    if inherited_author:
        flags.append("inherited_author_notation")
    if len(entry) > 1800:
        flags.append("possible_merged_entries")
    return {
        "surname": surname,
        "year": year,
        "title": title,
        "title_extraction_method": title_method,
        "entry": entry,
        "page_start": page_start,
        "page_end": page_end,
        "quality_flags": flags,
    }


def discover_pdfs(root: Path, corpus: dict[str, dict[str, str]]) -> list[tuple[Path, dict[str, str]]]:
    found: list[tuple[Path, dict[str, str]]] = []
    for path in sorted(root.rglob("*.pdf")):
        row = corpus.get(path.stem)
        if row:
            found.append((path, row))
    return found


def build_output(root: Path, corpus_path: Path) -> dict[str, object]:
    corpus = load_corpus(corpus_path)
    documents: dict[str, object] = {}
    no_heading: list[str] = []
    pdfs = discover_pdfs(root, corpus)
    for pdf, row in pdfs:
        lines = reference_lines(pdf)
        if not lines:
            no_heading.append(row["id"])
            continue
        parsed = [parse_entry(*entry) for entry in split_entries(lines)]
        references = [item for item in parsed if item is not None]
        documents[row["id"]] = {
            "slug": row["slug"],
            "source_pdf": pdf.relative_to(root).as_posix(),
            "references": references,
        }

    all_refs = [ref for doc in documents.values() for ref in doc["references"]]
    flag_counts = Counter(flag for ref in all_refs for flag in ref["quality_flags"])
    surname_counts = Counter(ref["surname"] for ref in all_refs)
    return {
        "meta": {
            "status": "candidate_requires_manual_validation",
            "parser": "parse_refs.py",
            "corpus_rows": len(corpus),
            "matched_pdfs": len(pdfs),
            "documents_with_reference_section": len(documents),
            "documents_without_detected_reference_section": no_heading,
            "reference_entries": len(all_refs),
            "quality_flag_counts": dict(flag_counts),
            "warning": (
                "No usar porcentajes históricos ni redes de referencias como resultados "
                "hasta validar manualmente una muestra estratificada."
            ),
        },
        "documents": documents,
        "quality_control": {"top_surnames": surname_counts.most_common(30)},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--corpus", type=Path, default=CORPUS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = build_output(args.root.resolve(), args.corpus.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    meta = result["meta"]
    print(
        f"{meta['documents_with_reference_section']} documentos; "
        f"{meta['reference_entries']} entradas; estado: {meta['status']}"
    )
    print(f"Salida: {args.output}")


if __name__ == "__main__":
    main()
