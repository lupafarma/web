#!/usr/bin/env python3
"""
Parse BOE Orden SND/1118/2025 Anexo 1 (regulated PVL Industrial de Referencia)
and Anexo 2-correction errata into structured CSVs.

Outputs:
  data/boe_anexo_1_full.csv  — full Anexo 1 (every F-conjunto row)
  data/boe_errata.csv        — structured errata rows (if parseable)
  data/boe_errata_raw.txt    — full errata text dump (always written)

Encoding rule: every file open uses encoding="utf-8" explicitly.

PDF text extraction: PyMuPDF (fitz). The investigation in
data/boe_raw_sample.txt confirmed PyMuPDF returns correct Latin-1
codepoints (Á, ó, í, etc.) for every accented character in this PDF —
no mojibake fixup needed.

Page structure (BOE-A-2025-20356.pdf, 1187 pages):
  pages 0–2     preamble (text of the Orden)
  page 3        preamble continues → first Anexo 1 data row (F1)
  pages 3–725   Anexo 1 (F-conjuntos, ambulatory dispensing)
  pages 726+    Anexo 2 (P-conjuntos, hospital — not parsed here)

Each Anexo 1 row, in extraction order, is:
  F<n>                  conjunto code, e.g. F46
  <principio>.          e.g. "Aceclofenaco." or "Ácido valproico."
  <via>.                e.g. "ORAL." (always short, ends in ".")
  <CN>                  6-digit national code
  <name lines>          1+ lines, product name
  <pvl>                 e.g. "1,81" or "13"  (Spanish comma decimal)
  <pvpiva>              e.g. "2,83" or "39"
  <obs>                 single token (UM, MP, EC, UH, DH, ECM, H, EFG) or blank " "
"""
import re
import csv
import sys
from collections import Counter
from pathlib import Path

import pymupdf

# Force stdout to UTF-8 so the summary prints accented chars cleanly on Windows
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
PDF_ANEXO = ROOT / "data" / "BOE-A-2025-20356.pdf"
PDF_ERRATA = ROOT / "data" / "BOE-A-2025-21925.pdf"
OUT_CSV = ROOT / "data" / "boe_anexo_1_full.csv"
OUT_ERRATA_CSV = ROOT / "data" / "boe_errata.csv"
OUT_ERRATA_RAW = ROOT / "data" / "boe_errata_raw.txt"

# Regexes for cell-line classification
RE_CONJUNTO = re.compile(r"^F\d{1,4}$")
RE_CN = re.compile(r"^\d{6}$")
RE_PRICE = re.compile(r"^\d+(?:[.,]\d+)?$")

OBS_VALUES = {"UM", "MP", "EC", "UH", "DH", "ECM", "H", "EFG"}

# Column-header tokens that repeat at the top of every Anexo 1 page. They are
# stripped because they would otherwise confuse the row state machine.
HEADER_TOKENS = {
    "Código", "conjunto", "ATC5", "Grupo vía", "administración",
    "nacional", "Nombre presentación", "PVL", "Referencia",
    "PVPIVA", "Observación",
}

# Page header / footer regexes
RE_PAGE_NOISE = re.compile(
    r"^("
    r"BOLETÍN OFICIAL DEL ESTADO"
    r"|Núm\. \d+"
    r"|(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)\s+\d+\s+de\s+\w+\s+de\s+\d+"
    r"|Sec\. I\.\s+Pág\. \d+"
    r"|cve: BOE-.*"
    r"|Verificable en https?://.*"
    r"|ANEXO\s+\d+"
    r")$"
)


def find_anexo_range(doc) -> tuple[int, int]:
    """Return (first_data_page_idx, first_anexo2_page_idx) — half-open range."""
    anexo1 = anexo2 = None
    for i in range(len(doc)):
        text = doc[i].get_text()
        for raw in text.split("\n"):
            s = raw.strip()
            if anexo1 is None and s == "ANEXO 1":
                anexo1 = i
            if s == "ANEXO 2":
                anexo2 = i
                break
        if anexo2 is not None:
            break
    if anexo1 is None or anexo2 is None:
        raise RuntimeError(f"Could not locate Anexo 1/2 (found {anexo1}/{anexo2})")
    return anexo1, anexo2


def clean_lines_for_page(text: str) -> list[str]:
    """Strip whitespace, drop empty, header-token, and page-noise lines."""
    out = []
    for raw in text.split("\n"):
        s = raw.strip()
        if not s:
            continue
        if s in HEADER_TOKENS:
            continue
        if RE_PAGE_NOISE.match(s):
            continue
        out.append(s)
    return out


def parse_anexo_1() -> list[dict]:
    doc = pymupdf.open(PDF_ANEXO)
    anexo1_start, anexo2_start = find_anexo_range(doc)
    print(f"Anexo 1 page range: PDF pages {anexo1_start+1}–{anexo2_start} "
          f"(0-indexed {anexo1_start}–{anexo2_start-1})")

    # Collect (line, page_idx) pairs across all Anexo-1 pages.
    seq: list[tuple[str, int]] = []
    for p in range(anexo1_start, anexo2_start):
        for s in clean_lines_for_page(doc[p].get_text()):
            seq.append((s, p))

    lines = [x[0] for x in seq]
    pages = [x[1] for x in seq]
    n = len(lines)

    rows = []
    skipped_no_conjunto = 0
    # Anchor at every CN line; walk back to find the F-conjunto, walk forward
    # to find PVL / PVPIVA / optional observation.
    for cn_idx, line in enumerate(lines):
        if not RE_CN.match(line):
            continue
        cn = line

        # Walk back at most 8 lines to find the conjunto code. Lines between
        # it and the CN are principio + vía (vía is the line immediately before
        # the CN; principio can occupy one or more lines).
        j = cn_idx - 1
        bw: list[str] = []
        steps = 0
        while j >= 0 and not RE_CONJUNTO.match(lines[j]):
            bw.append(lines[j])
            j -= 1
            steps += 1
            if steps > 8:
                break
        if j < 0 or not RE_CONJUNTO.match(lines[j]):
            skipped_no_conjunto += 1
            continue
        conjunto = lines[j]

        # bw is in reverse order: [via, principio_partN, ..., principio_part1]
        if not bw:
            continue
        via = bw[0].rstrip(".").strip()
        principio = " ".join(reversed(bw[1:])).rstrip(".").strip()
        principio_activo = f"{principio}. {via}." if principio else f"{via}."

        # Walk forward to gather product name lines, then PVL, PVPIVA, obs.
        k = cn_idx + 1
        name_parts: list[str] = []
        while k < n and not RE_PRICE.match(lines[k]):
            name_parts.append(lines[k])
            k += 1
            if k - cn_idx > 20:
                break
        if k >= n:
            continue
        pvl_raw = lines[k]
        pvpiva_raw = ""
        if k + 1 < n and RE_PRICE.match(lines[k + 1]):
            pvpiva_raw = lines[k + 1]
            k += 1
        obs = ""
        if k + 1 < n and lines[k + 1] in OBS_VALUES:
            obs = lines[k + 1]

        try:
            pvl = float(pvl_raw.replace(",", "."))
        except ValueError:
            continue
        pvpiva = None
        if pvpiva_raw:
            try:
                pvpiva = float(pvpiva_raw.replace(",", "."))
            except ValueError:
                pvpiva = None

        rows.append({
            "conjunto_code": conjunto,
            "principio_activo": principio_activo,
            "cn_code": cn,
            "product_name": " ".join(name_parts).strip(),
            "pvl_ref": pvl,
            "pvpiva_ref": pvpiva if pvpiva is not None else "",
            "observation": obs,
            "source_page": pages[cn_idx] + 1,  # 1-indexed for human reference
        })

    print(f"Skipped CNs without nearby conjunto: {skipped_no_conjunto}")
    return rows


def write_csv(rows: list[dict]) -> None:
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "conjunto_code", "principio_activo", "cn_code", "product_name",
            "pvl_ref", "pvpiva_ref", "observation", "source_page",
        ])
        for r in rows:
            w.writerow([
                r["conjunto_code"], r["principio_activo"], r["cn_code"],
                r["product_name"], f"{r['pvl_ref']:.2f}",
                f"{r['pvpiva_ref']:.2f}" if r["pvpiva_ref"] != "" else "",
                r["observation"], r["source_page"],
            ])
    print(f"Wrote {OUT_CSV.relative_to(ROOT)} ({len(rows):,} rows)")


def _parse_anexo_block(lines: list[str]) -> list[dict]:
    """Parse a list of cell-lines into Anexo 1 rows. Used for errata blocks
    which mirror the Anexo 1 cell-line layout."""
    rows = []
    n = len(lines)
    for cn_idx, line in enumerate(lines):
        if not RE_CN.match(line):
            continue
        cn = line
        # Walk back for conjunto
        j = cn_idx - 1
        bw: list[str] = []
        while j >= 0 and not RE_CONJUNTO.match(lines[j]):
            bw.append(lines[j])
            j -= 1
            if cn_idx - j > 8:
                break
        if j < 0 or not RE_CONJUNTO.match(lines[j]):
            continue
        conjunto = lines[j]
        if not bw:
            continue
        via = bw[0].rstrip(".").strip()
        principio = " ".join(reversed(bw[1:])).rstrip(".").strip()
        principio_activo = f"{principio}. {via}." if principio else f"{via}."
        # Forward for name + prices + obs
        k = cn_idx + 1
        name_parts = []
        while k < n and not RE_PRICE.match(lines[k]):
            name_parts.append(lines[k])
            k += 1
            if k - cn_idx > 20:
                break
        if k >= n:
            continue
        pvl_raw = lines[k]
        pvpiva_raw = ""
        if k + 1 < n and RE_PRICE.match(lines[k + 1]):
            pvpiva_raw = lines[k + 1]
            k += 1
        obs = ""
        if k + 1 < n and lines[k + 1] in OBS_VALUES:
            obs = lines[k + 1]
        try:
            pvl = float(pvl_raw.replace(",", "."))
        except ValueError:
            continue
        pvpiva = None
        if pvpiva_raw:
            try:
                pvpiva = float(pvpiva_raw.replace(",", "."))
            except ValueError:
                pvpiva = None
        rows.append({
            "conjunto_code": conjunto,
            "principio_activo": principio_activo,
            "cn_code": cn,
            "product_name": " ".join(name_parts).strip(),
            "pvl_ref": pvl,
            "pvpiva_ref": pvpiva,
            "observation": obs,
        })
    return rows


def parse_errata() -> tuple[list[dict], str]:
    """Parse BOE-A-2025-21925.pdf.

    The errata rewrites whole table blocks: «...donde dice: «[OLD TABLE]» Debe
    decir: «[NEW TABLE]»». We diff each (OLD, NEW) pair on (cn, field) and
    emit one correction row per changed field. Returns (structured_rows, raw).
    """
    doc = pymupdf.open(PDF_ERRATA)
    full_text = "\n".join(doc[i].get_text() for i in range(len(doc)))

    # Each guillemet block is either an OLD ("donde dice:") or NEW ("Debe
    # decir:") table. Use the preceding text to label each block, then pair
    # adjacent OLD/NEW for diffing.
    labeled: list[tuple[str, str]] = []  # (label, content)
    for m in re.finditer(r"«([\s\S]*?)»", full_text):
        # Inspect the 80 chars before the block start
        prefix = full_text[max(0, m.start() - 80): m.start()].lower()
        if "donde dice" in prefix:
            labeled.append(("OLD", m.group(1)))
        elif "debe decir" in prefix:
            labeled.append(("NEW", m.group(1)))
        # else: citation block, skip

    corrections = []
    i = 0
    while i < len(labeled) - 1:
        if labeled[i][0] == "OLD" and labeled[i + 1][0] == "NEW":
            old_lines = clean_lines_for_page(labeled[i][1])
            new_lines = clean_lines_for_page(labeled[i + 1][1])
            old_rows = _parse_anexo_block(old_lines)
            new_rows = _parse_anexo_block(new_lines)
            old_by_cn = {r["cn_code"]: r for r in old_rows}
            for nr in new_rows:
                cn = nr["cn_code"]
                o = old_by_cn.get(cn)
                if not o:
                    continue
                for field in ("pvl_ref", "pvpiva_ref", "product_name", "observation"):
                    if o.get(field) != nr.get(field):
                        corrections.append({
                            "cn_code": cn,
                            "field": field,
                            "old_value": str(o.get(field, "")),
                            "new_value": str(nr.get(field, "")),
                            "source_page": "",
                        })
            i += 2
        else:
            i += 1
    return corrections, full_text


def write_errata(rows: list[dict], raw: str) -> None:
    with OUT_ERRATA_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cn_code", "field", "old_value", "new_value", "source_page"])
        for r in rows:
            w.writerow([r["cn_code"], r["field"], r["old_value"],
                        r["new_value"], r["source_page"]])
    with OUT_ERRATA_RAW.open("w", encoding="utf-8") as f:
        f.write(raw)
    print(f"Wrote {OUT_ERRATA_CSV.relative_to(ROOT)} ({len(rows)} structured rows)")
    print(f"Wrote {OUT_ERRATA_RAW.relative_to(ROOT)} ({len(raw):,} chars raw)")


def summarize(rows: list[dict]) -> None:
    print()
    print(f"=== Anexo 1 summary ===")
    print(f"Total rows:        {len(rows):,}")
    print(f"Distinct conjuntos:{len(set(r['conjunto_code'] for r in rows)):,}")
    print(f"With observation:  {sum(1 for r in rows if r['observation']):,}")
    obs_counter = Counter(r["observation"] for r in rows if r["observation"])
    for obs, n in obs_counter.most_common():
        print(f"  {obs:5s}  {n:,}")
    missing_pvpiva = sum(1 for r in rows if r["pvpiva_ref"] == "")
    print(f"Rows missing PVPIVA: {missing_pvpiva:,}")
    print()
    # First 5 rows
    print("First 5 rows:")
    for r in rows[:5]:
        print(f"  {r['conjunto_code']:6s} {r['cn_code']}  PVL={r['pvl_ref']:6.2f}  "
              f"PVPIVA={r['pvpiva_ref']!s:>6s}  obs={r['observation']:3s}  "
              f"{r['principio_activo'][:32]:32s}  {r['product_name'][:50]}")

    if not (10_000 <= len(rows) <= 20_000):
        print()
        print(f"  ⚠ WARNING: row count {len(rows):,} outside expected [10,000, 20,000].")
        print(f"             Inspect data/boe_anexo_1_full.csv before proceeding.")


def main() -> None:
    if not PDF_ANEXO.exists():
        raise SystemExit(f"Missing PDF: {PDF_ANEXO}")
    rows = parse_anexo_1()
    write_csv(rows)
    summarize(rows)

    if PDF_ERRATA.exists():
        print()
        print("=== Errata pass ===")
        errata_rows, raw = parse_errata()
        write_errata(errata_rows, raw)
    else:
        print(f"(Errata PDF not present at {PDF_ERRATA}, skipping)")


if __name__ == "__main__":
    main()
