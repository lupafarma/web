#!/usr/bin/env python3
"""
Parse BOE Orden SND/1118/2025 Anexo 1 text -> CSV with PVL Referencia.

The PDF text comes in a structured tabular format:
  F1 13C-urea. ORAL. 654057  UBTEST 100 mg comprimidos...  19,51  30,46
  F2 Acarbosa. ORAL. 662258  ACARBOSA TECNIGEN 50 mg...   4,9   7,65

Strategy: regex match lines that look like a data row.
"""
import re
import csv
import json
import sys
from pathlib import Path

INPUT = Path("/home/claude/lupa-data/boe_extracted_sample.txt")
OUTPUT_CSV = Path("/home/claude/lupa-data/boe_pvl_referencia.csv")
OUTPUT_JSON = Path("/home/claude/lupa-data/boe_pvl_referencia.json")

# Row pattern: conjunto_code  group_name  CN  name  pvl_ref  pvpiva_ref  observation
# Examples (with optional observation at end):
#   F2 Acarbosa. ORAL. 662258 ACARBOSA TECNIGEN 50 mg comprimidos, 100 comprimidos. 4,9 7,65
#   F6 Ácido acetilsalicílico. ORAL. 672099 BIOPLAK 250 mg comprimidos, 30 comprimidos. 1,6 2,5 UM
#
# Strategy: split text into "row chunks" by detecting the start pattern
# (conjunto code F\d+|P\d+|S\d+|EC\d+|H\d+ etc.)
#
# CN codes are 6-digit numbers (mostly 6 digits but legally up to 10).

# Read input
text = INPUT.read_text()

# Combine the text by collapsing newlines (table cells split across lines)
# We'll work line-by-line through "logical lines"

# Strip BOE pagination metadata
text = re.sub(r"BOLETÍN OFICIAL DEL ESTADO.*?Verificable en https://www\.boe\.es",
              " ", text, flags=re.DOTALL)
text = re.sub(r"Núm\. \d+\s+\w+ \d+ de \w+ de \d+\s+Sec\. I\. Pág\. \d+",
              " ", text)
text = re.sub(r"cve: BOE-A-2025-20356", " ", text)
text = re.sub(r"Código\s+conjunto ATC5 Grupo vía administración\s+Código\s+nacional Nombre presentación PVL Referencia\s+PVPIVA\s+Referencia Observación",
              " ", text)

# Now reformat: re-introduce line breaks before each conjunto code
text = re.sub(r"\s+(F\d{1,4})\s+", r"\n\1\t", text)

lines = text.split("\n")

rows = []
errors = []

# Pattern for a data row
# F<num>  <group_name_with_period>  <CN_6digits>  <product_name>  <pvl>  <pvpiva>  [observation]
ROW = re.compile(
    r"^(F\d+)\t"                              # conjunto code
    r"(.+?\.)\s+"                              # group name ending with period
    r"(\d{6})\s+"                              # CN code (6 digits)
    r"(.+?)\s+"                                # product name (any text, lazy)
    r"(\d+(?:,\d+)?)\s+"                       # PVL Referencia (e.g. 4,9 or 19,51)
    r"(\d+(?:,\d+)?)"                          # PVP IVA Referencia
    r"(?:\s+(UM|MP|EC|UH|DH|ECM|H|EFG))?$",    # optional observation
)

for line in lines:
    line = line.strip()
    if not line or not line.startswith("F"):
        continue

    m = ROW.match(line)
    if m:
        conjunto, group_name, cn, product_name, pvl_ref, pvpiva_ref, obs = m.groups()
        rows.append({
            "conjunto_code": conjunto,
            "group_name": group_name.strip(),
            "cn_code": cn,
            "product_name": product_name.strip(),
            "pvl_referencia": float(pvl_ref.replace(",", ".")),
            "pvpiva_referencia": float(pvpiva_ref.replace(",", ".")),
            "observation": obs or "",
            "source": "BOE-A-2025-20356",
        })
    else:
        # Try a looser pattern in case product name spans wrapped text
        # For now log and continue
        errors.append(line[:120])


# Write CSV
with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=[
        "cn_code", "conjunto_code", "group_name", "product_name",
        "pvl_referencia", "pvpiva_referencia", "observation", "source"
    ])
    w.writeheader()
    for r in rows:
        w.writerow(r)

# Write JSON (CN-keyed for easy lookup)
keyed = {r["cn_code"]: r for r in rows}
with OUTPUT_JSON.open("w", encoding="utf-8") as f:
    json.dump(keyed, f, indent=2, ensure_ascii=False)

# Stats
print(f"Extracted {len(rows)} rows")
print(f"Unique CNs: {len(keyed)}")
print(f"Conjuntos covered: {len(set(r['conjunto_code'] for r in rows))}")
print(f"Skipped lines (likely wrapped product names): {len(errors)}")
print(f"\nSample (first 5 rows):")
for r in rows[:5]:
    print(f"  CN={r['cn_code']} | {r['conjunto_code']} {r['group_name']:30s} | "
          f"PVL={r['pvl_referencia']:6.2f}€ | PVPIVA={r['pvpiva_referencia']:6.2f}€ | "
          f"{r['product_name'][:50]}")

print(f"\nFiles written:")
print(f"  CSV:  {OUTPUT_CSV}")
print(f"  JSON: {OUTPUT_JSON}")

if errors:
    print(f"\nFirst 3 unparsed lines (to debug):")
    for e in errors[:3]:
        print(f"  {e!r}")
