#!/usr/bin/env python3
"""
Lupa data pipeline: combine Nomenclátor + full BOE Anexo 1 + errata
into a single CN-keyed JSON for the browser.

Inputs
  data/boe_anexo_1_full.csv    full Anexo 1 (produced by reference/parse_boe.py)
  data/boe_errata.csv          field-level corrections (also from parse_boe.py)
  data/nomenclator.csv         (optional) Nomenclátor de Facturación
                               If missing, falls back to public/medications.json
                               as a cached snapshot of Nomenclátor fields.

Output
  data/lupa_medication_db.json   CN-keyed dict (utf-8, ensure_ascii=False,
                                 no indent so file size stays small)

Encoding rule: every open() in this script uses encoding="utf-8" explicitly.
This is what was missing in earlier runs — the hardcoded BOE_PVL_DATA dict
in the prototype contained mojibake like "�cido valproico" because the
Windows console default codec leaked into a .py literal. The new pipeline
sources every accented character from a UTF-8 CSV and writes UTF-8 JSON
with ensure_ascii=False, so "Ácido valproico" survives end-to-end.
"""
import csv
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
BOE_CSV = ROOT / "data" / "boe_anexo_1_full.csv"
ERRATA_CSV = ROOT / "data" / "boe_errata.csv"
NOMENCLATOR_CSV = ROOT / "data" / "nomenclator.csv"  # optional, latin-1 or utf-8
CACHED_NOMENCLATOR = ROOT / "public" / "medications.json"  # fallback source
OUT_JSON = ROOT / "data" / "lupa_medication_db.json"

# RD 823/2008 margin constants — reverse-derive PVL from PVP+IVA.
PHARMACY_MARGIN = 0.279
DISTRIBUTION_MARGIN = 0.076
IVA_REIMBURSABLE = 0.04

# BOE fields the build owns. We strip these from any cached Nomenclátor
# snapshot before overlaying fresh BOE data — that's how stale mojibake
# like "�cido valproico" gets cleaned out on rebuild.
BOE_FIELDS = (
    "pvl_referencia_boe", "pvpiva_referencia_boe",
    "conjunto_referencia_code", "conjunto_principio_activo",
    "conjunto_via", "boe_observation", "source_boe",
)

SOURCE_BOE = "BOE-A-2025-20356 + BOE-A-2025-21925 (errata)"


def derive_pvl(pvpiva: float | None) -> float | None:
    if pvpiva is None:
        return None
    pvp = pvpiva / (1 + IVA_REIMBURSABLE)
    pvf = pvp * (1 - PHARMACY_MARGIN)
    pvl = pvf / (1 + DISTRIBUTION_MARGIN)
    return round(pvl, 2)


def load_boe_anexo() -> dict[str, dict]:
    """Returns CN → BOE record dict."""
    boe: dict[str, dict] = {}
    with BOE_CSV.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            cn = r["cn_code"].strip()
            # principio_activo column format: "Aceclofenaco. ORAL."
            # Split back into principio + via for the database.
            pa = r["principio_activo"].rstrip(".").strip()
            if ". " in pa:
                principio, via = pa.rsplit(". ", 1)
            else:
                principio, via = pa, ""
            pvpiva = r.get("pvpiva_ref", "").strip()
            boe[cn] = {
                "conjunto_referencia_code": r["conjunto_code"],
                "conjunto_principio_activo": principio.strip(),
                "conjunto_via": via.strip(),
                "pvl_referencia_boe": float(r["pvl_ref"]),
                "pvpiva_referencia_boe": float(pvpiva) if pvpiva else None,
                "boe_observation": r.get("observation", "").strip(),
                "source_boe": SOURCE_BOE,
            }
    return boe


def apply_errata(boe: dict[str, dict]) -> int:
    """Mutates boe in place; returns count of corrections applied."""
    if not ERRATA_CSV.exists():
        return 0
    applied = 0
    with ERRATA_CSV.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            cn = r["cn_code"].strip()
            field = r["field"].strip()
            new = r["new_value"].strip()
            if cn not in boe:
                continue
            # field name in errata maps directly to BOE record key (with _boe suffix
            # for prices) or pass through for product_name / observation.
            if field == "pvl_ref":
                boe[cn]["pvl_referencia_boe"] = float(new)
            elif field == "pvpiva_ref":
                boe[cn]["pvpiva_referencia_boe"] = float(new) if new else None
            elif field == "observation":
                boe[cn]["boe_observation"] = new
            elif field == "product_name":
                # Product name is owned by Nomenclátor, not BOE — skip.
                continue
            else:
                continue
            applied += 1
    return applied


def load_nomenclator_source() -> dict[str, dict]:
    """Read the Nomenclátor-flavored fields keyed by CN.

    Preference order:
      1. data/nomenclator.csv   (raw Sanidad CSV, utf-8 or latin-1)
      2. public/medications.json (cached snapshot, mojibake-stripped on load)
    """
    if NOMENCLATOR_CSV.exists():
        return _load_nomenclator_csv()
    if CACHED_NOMENCLATOR.exists():
        return _load_cached_nomenclator()
    raise SystemExit(
        f"No Nomenclátor source available: tried {NOMENCLATOR_CSV} and "
        f"{CACHED_NOMENCLATOR}"
    )


def _load_nomenclator_csv() -> dict[str, dict]:
    out: dict[str, dict] = {}
    # Sanidad publishes UTF-8 these days; if you hit mojibake, try
    # encoding="latin-1" and rerun — never let Python guess via default.
    with NOMENCLATOR_CSV.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            cn = (r.get("Código Nacional") or "").strip()
            if not cn:
                continue
            out[cn] = {
                "cn": cn,
                "nombre": (r.get("Nombre del producto farmacéutico") or "").strip(),
                "tipo_farmaco": (r.get("Tipo de fármaco") or "").strip() or None,
                "principio_activo": (r.get("Principio activo o asociación de principios activos") or "").strip() or None,
                "laboratorio": (r.get("Nombre del laboratorio ofertante") or "").strip() or None,
                "estado": (r.get("Estado") or "").strip() or None,
                "aportacion": (r.get("Aportación del beneficiario") or "").strip() or "NORMAL",
                "pvp_iva": _decimal(r.get("Precio venta al público con IVA")
                                    or r.get("Precio de venta al público con IVA")),
                "precio_referencia": _decimal(r.get("Precio de referencia")),
                "menor_precio_agrupacion": _decimal(
                    r.get("Menor precio de la agrupación homogénea del producto sanitario")
                    or r.get("Menor precio de la agrupación homogéna del producto sanitario")
                ),
                "agrupacion_code": (
                    r.get("Código de la agrupación homogénea del producto sanitario")
                    or r.get("Código de la agrupación homegénea del productor sanitario")
                    or "").strip() or None,
                "agrupacion_nombre": (r.get("Nombre de la agrupación homogénea del producto sanitario") or "").strip() or None,
                "huerfano": (r.get("Medicamento huérfano") or "").strip().upper() == "SI",
                "source_facturacion": "Nomenclator-2026-05",
            }
    return out


def _load_cached_nomenclator() -> dict[str, dict]:
    """Treat public/medications.json as a cached Nomenclátor snapshot.
    Strip the BOE fields so we can repopulate from the fresh CSV."""
    with CACHED_NOMENCLATOR.open(encoding="utf-8") as f:
        cached = json.load(f)
    out: dict[str, dict] = {}
    for cn, rec in cached.items():
        clean = {k: v for k, v in rec.items() if k not in BOE_FIELDS}
        # Drop pvl_estimated too — we re-derive it below.
        clean.pop("pvl_estimated", None)
        out[cn] = clean
    return out


def _decimal(s: str | None) -> float | None:
    if not s:
        return None
    s = s.replace(",", ".").strip()
    try:
        return float(s)
    except (ValueError, AttributeError):
        return None


def build() -> None:
    print(f"Loading BOE Anexo 1 ({BOE_CSV.relative_to(ROOT)})…")
    boe = load_boe_anexo()
    print(f"  {len(boe):,} BOE rows")

    print(f"Applying errata ({ERRATA_CSV.relative_to(ROOT)})…")
    applied = apply_errata(boe)
    print(f"  {applied} field corrections applied")

    if NOMENCLATOR_CSV.exists():
        print(f"Loading Nomenclátor from CSV ({NOMENCLATOR_CSV.relative_to(ROOT)})…")
    else:
        print(f"data/nomenclator.csv missing — falling back to cached snapshot "
              f"{CACHED_NOMENCLATOR.relative_to(ROOT)}")
    nom = load_nomenclator_source()
    print(f"  {len(nom):,} Nomenclátor records")

    matched = 0
    db: dict[str, dict] = {}
    for cn, rec in nom.items():
        entry = dict(rec)
        if cn in boe:
            entry.update(boe[cn])
            matched += 1
        # Re-derive pvl_estimated from pvp_iva (RD 823/2008)
        pvp_iva = entry.get("pvp_iva")
        if pvp_iva:
            entry["pvl_estimated"] = derive_pvl(pvp_iva)
        db[cn] = entry

    # BOE rows whose CN is not in Nomenclátor — typically hospital-only meds
    # that should never appear on an ambulatory pharmacy invoice. Counted for
    # transparency but not added to the runtime DB.
    boe_unused = sum(1 for cn in boe if cn not in nom)
    nom_without_boe = sum(1 for cn in nom if cn not in boe)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, separators=(",", ":"))

    print()
    print("=== Build summary ===")
    print(f"Total medications written:      {len(db):,}")
    print(f"  with BOE PVL Referencia:      {matched:,}")
    print(f"  without (OTC / non-conjunto): {nom_without_boe:,}")
    print(f"BOE rows unused (no Nomenclátor CN): {boe_unused:,}")
    print()
    print(f"Wrote {OUT_JSON.relative_to(ROOT)} "
          f"({OUT_JSON.stat().st_size / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    build()
