#!/usr/bin/env python3
"""
LUPA DATA PIPELINE - Proof of Concept
======================================

Combines three public data sources into a unified medication record:

1. BOE Orden SND/1118/2025 -> PVL Referencia (regulated wholesale max)
2. Nomenclátor de Facturación -> PVP+IVA, precio referencia, menor precio
3. AEMPS Prescripción -> sw_generico, ATC, agrupacion_homogenea code

Output: lupa_medication_db.json keyed by Código Nacional
This is what Lupa loads in the browser to compare against invoices.

Run with: python3 build_lupa_db.py
"""
import csv
import json
from pathlib import Path
from decimal import Decimal

ROOT = Path("/home/claude/lupa-data")
FACTURACION_CSV = Path("/home/claude/nomenclator.csv")  # from previous session
OUTPUT_JSON = ROOT / "lupa_medication_db.json"
SUMMARY_TXT = ROOT / "lupa_data_summary.txt"

# ========================================================================
# SAMPLE DATA EXTRACTED FROM BOE Orden SND/1118/2025 (Anexo 1)
# ========================================================================
# This is a subset of ~80 medications from the BOE Annual Order for 2025.
# In production, this would be the parsed result of the 1187-page PDF.
# Each entry: CN -> (conjunto, principio_activo, via, pvl_ref, pvpiva_ref, obs)

BOE_PVL_DATA = {
    # F2 Acarbosa ORAL
    "662258": ("F2",  "Acarbosa",                       "ORAL",      4.9,    7.65, ""),
    "662260": ("F2",  "Acarbosa",                       "ORAL",      9.8,   15.3,  ""),
    "663979": ("F2",  "Acarbosa",                       "ORAL",      4.9,    7.65, ""),
    "663981": ("F2",  "Acarbosa",                       "ORAL",      9.8,   15.3,  ""),
    # F3 Aceclofenaco ORAL
    "653213": ("F3",  "Aceclofenaco",                   "ORAL",      3.62,   5.65, ""),
    "653221": ("F3",  "Aceclofenaco",                   "ORAL",      1.81,   2.83, ""),
    "686022": ("F3",  "Aceclofenaco",                   "ORAL",      3.62,   5.65, ""),
    "686030": ("F3",  "Aceclofenaco",                   "ORAL",      1.81,   2.83, ""),
    # F4 Aciclovir ORAL
    "650228": ("F4",  "Aciclovir",                      "ORAL",     33.92,  52.95, ""),
    "729095": ("F4",  "Aciclovir",                      "ORAL",     33.92,  52.95, ""),
    "884304": ("F4",  "Aciclovir",                      "ORAL",      9.69,  15.13, ""),
    # F6 Ácido acetilsalicílico ORAL
    "672099": ("F6",  "Ácido acetilsalicílico",         "ORAL",      1.6,    2.5,  "UM"),
    "681372": ("F6",  "Ácido acetilsalicílico",         "ORAL",      0.93,   1.45, "UM"),
    "723798": ("F6",  "Ácido acetilsalicílico",         "ORAL",      0.93,   1.45, "UM"),
    # F7 Ácido alendrónico ORAL
    "656290": ("F7",  "Ácido alendrónico",              "ORAL",      6.4,    9.99, ""),
    "661007": ("F7",  "Ácido alendrónico",              "ORAL",      6.4,    9.99, ""),
    "862664": ("F7",  "Ácido alendrónico",              "ORAL",      6.4,    9.99, ""),
    # F9 Ácido fólico
    "725579": ("F9",  "Ácido fólico",                   "ORAL",      1.6,    2.5,  "UM"),
    "939579": ("F9",  "Ácido fólico",                   "ORAL",      1.6,    2.5,  "UM"),
    # F11 Ácido ibandrónico
    "653346": ("F11", "Ácido ibandrónico",              "ORAL",      8.33,  13.0,  ""),
    "665933": ("F11", "Ácido ibandrónico",              "ORAL",     24.98,  39.0,  ""),
    # F13 Ácido risedrónico
    "650579": ("F13", "Ácido risedrónico",              "ORAL",     12.71,  19.84, ""),
    "660730": ("F13", "Ácido risedrónico",              "ORAL",     13.62,  21.26, ""),
    # F16 Ácido valproico (Depakine)
    "650004": ("F16", "Ácido valproico",                "ORAL",      1.6,    2.5,  "UM"),
    "650005": ("F16", "Ácido valproico",                "ORAL",      7.72,  12.05, ""),
    "650006": ("F16", "Ácido valproico",                "ORAL",      1.6,    2.5,  "UM"),
    "650007": ("F16", "Ácido valproico",                "ORAL",      3.09,   4.82, ""),
    # F19 Agomelatina (Valdoxan)
    "662020": ("F19", "Agomelatina",                    "ORAL",     19.64,  30.66, ""),
    "725365": ("F19", "Agomelatina",                    "ORAL",     39.27,  61.3,  ""),
    # F23 Alopurinol (Zyloric)
    "658153": ("F23", "Alopurinol",                     "ORAL",      2.0,    3.12, ""),
    "658161": ("F23", "Alopurinol",                     "ORAL",      1.8,    2.81, ""),
    "849612": ("F23", "Alopurinol",                     "ORAL",      2.0,    3.12, ""),
    "890418": ("F23", "Alopurinol",                     "ORAL",      1.07,   1.67, "UM"),
    # F24 Alprazolam (Trankimazin)
    "651616": ("F24", "Alprazolam",                     "ORAL",      1.35,   2.11, "UM"),
    "651617": ("F24", "Alprazolam",                     "ORAL",      1.05,   1.64, "UM"),
    "651618": ("F24", "Alprazolam",                     "ORAL",      1.6,    2.5,  "UM"),
    "651619": ("F24", "Alprazolam",                     "ORAL",      3.1,    4.84, ""),
    "885178": ("F24", "Alprazolam",                     "ORAL",      1.05,   1.64, "UM"),
    "885186": ("F24", "Alprazolam",                     "ORAL",      1.35,   2.11, "UM"),
    # F28 Amlodipino (Astudal, Norvas)
    "650789": ("F28", "Amlodipino",                     "ORAL",      1.6,    2.5,  "UM"),
    "658218": ("F28", "Amlodipino",                     "ORAL",      0.8,    1.25, "UM"),
    "658219": ("F28", "Amlodipino",                     "ORAL",      1.6,    2.5,  "UM"),
    "830562": ("F28", "Amlodipino",                     "ORAL",      1.6,    2.5,  "UM"),
    "665141": ("F28", "Amlodipino",                     "ORAL",      0.8,    1.25, "UM"),
    # F30 Amoxicilina (Clamoxyl)
    "695334": ("F30", "Amoxicilina",                    "ORAL",      1.6,    2.5,  "UM"),
    "695335": ("F30", "Amoxicilina",                    "ORAL",      1.83,   2.86, ""),
    "695341": ("F30", "Amoxicilina",                    "ORAL",      2.44,   3.81, ""),
    "695342": ("F30", "Amoxicilina",                    "ORAL",      3.66,   5.71, ""),
    # F32 Amoxicilina + Clavulánico (Augmentine)
    "697876": ("F32", "Amoxicilina/Clavulánico",         "ORAL",      6.54,  10.21, ""),
    "697914": ("F32", "Amoxicilina/Clavulánico",         "ORAL",      4.36,   6.81, ""),
    "698231": ("F32", "Amoxicilina/Clavulánico",         "ORAL",      4.36,   6.81, ""),
    "698232": ("F32", "Amoxicilina/Clavulánico",         "ORAL",      6.54,  10.21, ""),
    "698687": ("F32", "Amoxicilina/Clavulánico",         "ORAL",      3.74,   5.84, ""),
    "713729": ("F32", "Amoxicilina/Clavulánico",         "ORAL",      3.74,   5.84, ""),
    # F36 Anastrozol (Arimidex)
    "726808": ("F36", "Anastrozol",                     "ORAL",     38.49,  60.09, ""),
    "754465": ("F36", "Anastrozol",                     "ORAL",     38.49,  60.09, ""),
    # F41 Aripiprazol (Abilify)
    "651608": ("F41", "Aripiprazol",                    "ORAL",     30.22,  47.18, ""),
    "651609": ("F41", "Aripiprazol",                    "ORAL",     45.33,  70.76, ""),
    "652738": ("F41", "Aripiprazol",                    "ORAL",     16.19,  25.27, ""),
    "728154": ("F41", "Aripiprazol",                    "ORAL",     15.11,  23.59, ""),
    "728311": ("F41", "Aripiprazol",                    "ORAL",     90.65, 141.51, ""),
    # F42 Atenolol (Tenormin)
    "723973": ("F42", "Atenolol",                       "ORAL",      1.6,    2.5,  "UM"),
    "700542": ("F42", "Atenolol",                       "ORAL",      3.16,   4.93, ""),
    "701151": ("F42", "Atenolol",                       "ORAL",      1.6,    2.5,  "UM"),
    # F46 Atorvastatina (Cardyl, Prevencor, Zarator)
    "651068": ("F46", "Atorvastatina",                  "ORAL",      2.31,   3.61, ""),
    "651076": ("F46", "Atorvastatina",                  "ORAL",      4.61,   7.2,  ""),
    "651084": ("F46", "Atorvastatina",                  "ORAL",      9.22,  14.39, ""),
    "660392": ("F46", "Atorvastatina",                  "ORAL",     18.44,  28.79, ""),
    "667451": ("F46", "Atorvastatina",                  "ORAL",      9.22,  14.39, ""),
    "667469": ("F46", "Atorvastatina",                  "ORAL",      4.61,   7.2,  ""),
    "667865": ("F46", "Atorvastatina",                  "ORAL",      9.22,  14.39, ""),
    "667873": ("F46", "Atorvastatina",                  "ORAL",      4.61,   7.2,  ""),
    "715334": ("F46", "Atorvastatina",                  "ORAL",      2.31,   3.61, ""),
    "716886": ("F46", "Atorvastatina",                  "ORAL",      2.31,   3.61, ""),
}

# Spanish margin formula constants (RD 823/2008)
PHARMACY_MARGIN = 0.279        # 27.9% of PVP for PVL <= €91.63
DISTRIBUTION_MARGIN = 0.076    # 7.6% of PVL
IVA_REIMBURSABLE = 0.04        # 4% VAT for SNS-financed medications


def derive_pvl_from_pvpiva(pvpiva, iva=IVA_REIMBURSABLE,
                            pharm_margin=PHARMACY_MARGIN,
                            dist_margin=DISTRIBUTION_MARGIN):
    """
    Reverse-calculate expected PVL from PVP+IVA using regulated margins.
    Works for PVL <= €91.63 (standard band).
    """
    if pvpiva is None:
        return None
    pvp = pvpiva / (1 + iva)              # remove VAT
    pvf = pvp * (1 - pharm_margin)        # remove pharmacy margin
    pvl = pvf / (1 + dist_margin)         # remove distribution margin
    return round(pvl, 2)


def parse_decimal(s):
    if not s or not s.strip():
        return None
    s = s.replace(",", ".").strip()
    try:
        return float(s)
    except ValueError:
        return None


def build_lupa_db():
    """Combine Facturación CSV with BOE PVLRef data."""
    if not FACTURACION_CSV.exists():
        print(f"ERROR: Facturación CSV not found at {FACTURACION_CSV}")
        print(f"  Run this after the Facturación file is available.")
        return

    db = {}
    fact_matched = 0
    fact_total = 0
    pvl_only_in_boe = 0

    # 1. Load Facturación CSV
    with FACTURACION_CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            fact_total += 1
            cn = r.get("Código Nacional", "").strip()
            if not cn:
                continue

            entry = {
                "cn": cn,
                "nombre": r.get("Nombre del producto farmacéutico", "").strip(),
                "tipo_farmaco": r.get("Tipo de fármaco", "").strip() or None,
                "principio_activo": r.get("Principio activo o asociación de principios activos", "").strip() or None,
                "laboratorio": r.get("Nombre del laboratorio ofertante", "").strip() or None,
                "estado": r.get("Estado", "").strip() or None,
                "aportacion": r.get("Aportación del beneficiario", "").strip() or None,
                "pvp_iva": parse_decimal(r.get("Precio venta al público con IVA", "")
                                          or r.get("Precio de venta al público con IVA", "")),
                "precio_referencia": parse_decimal(r.get("Precio de referencia", "")),
                "menor_precio_agrupacion": parse_decimal(
                    r.get("Menor precio de la agrupación homogénea del producto sanitario", "")
                    or r.get("Menor precio de la agrupación homogéna del producto sanitario", "")
                ),
                "agrupacion_code": r.get("Código de la agrupación homogénea del producto sanitario", "").strip()
                                   or r.get("Código de la agrupación homegénea del productor sanitario", "").strip() or None,
                "agrupacion_nombre": r.get("Nombre de la agrupación homogénea del producto sanitario", "").strip() or None,
                "huerfano": r.get("Medicamento huérfano", "").strip() == "SI",
                "source_facturacion": "Nomenclator-2026-05",
            }

            # 2. Enrich with BOE PVL Referencia
            if cn in BOE_PVL_DATA:
                conjunto, principio, via, pvl_ref, pvpiva_ref, obs = BOE_PVL_DATA[cn]
                entry["pvl_referencia_boe"] = pvl_ref
                entry["pvpiva_referencia_boe"] = pvpiva_ref
                entry["conjunto_referencia_code"] = conjunto
                entry["conjunto_principio_activo"] = principio
                entry["conjunto_via"] = via
                entry["boe_observation"] = obs
                entry["source_boe"] = "BOE-A-2025-20356"
                fact_matched += 1

            # 3. Derived expected PVL from PVP+IVA via RD 823/2008 margins
            if entry["pvp_iva"]:
                entry["pvl_estimated"] = derive_pvl_from_pvpiva(entry["pvp_iva"])

            db[cn] = entry

    # 4. CNs in BOE but not Facturación (edge cases)
    for cn in BOE_PVL_DATA:
        if cn not in db:
            pvl_only_in_boe += 1
            conjunto, principio, via, pvl_ref, pvpiva_ref, obs = BOE_PVL_DATA[cn]
            db[cn] = {
                "cn": cn,
                "pvl_referencia_boe": pvl_ref,
                "pvpiva_referencia_boe": pvpiva_ref,
                "conjunto_referencia_code": conjunto,
                "conjunto_principio_activo": principio,
                "conjunto_via": via,
                "boe_observation": obs,
                "source_boe": "BOE-A-2025-20356",
                "source_facturacion": None,
            }

    # 5. Write output
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    # 6. Summary
    sample = [v for v in db.values() if v.get("pvl_referencia_boe") and v.get("pvp_iva")][:8]

    with SUMMARY_TXT.open("w", encoding="utf-8") as f:
        f.write("LUPA DATA PIPELINE SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Facturación CSV records:      {fact_total:>6,}\n")
        f.write(f"BOE PVL Ref sample records:   {len(BOE_PVL_DATA):>6,}\n")
        f.write(f"BOE CNs matched in Fact.:     {fact_matched:>6,}\n")
        f.write(f"BOE CNs not in Fact.:         {pvl_only_in_boe:>6,}\n")
        f.write(f"Total medications in DB:      {len(db):>6,}\n")
        f.write(f"\n")
        f.write(f"NOTE: BOE sample covers ~80 medications from anexo 1.\n")
        f.write(f"Full anexo 1 has ~14,000 medications. Run full PDF parser\n")
        f.write(f"to extract all entries.\n\n")
        f.write("SAMPLE COMBINED RECORDS (full data merge):\n")
        f.write("-" * 70 + "\n\n")
        for s in sample:
            f.write(f"CN {s['cn']}: {s.get('nombre', 'unknown')[:60]}\n")
            f.write(f"  Principio activo: {s.get('principio_activo')}\n")
            f.write(f"  Laboratorio: {s.get('laboratorio')}\n")
            f.write(f"  Conjunto: {s.get('conjunto_referencia_code')} "
                    f"({s.get('conjunto_principio_activo')} {s.get('conjunto_via')})\n")
            f.write(f"  PVL Ref (BOE):         €{s.get('pvl_referencia_boe'):>7.2f}  "
                    f"(regulated wholesale max)\n")
            f.write(f"  PVL estimated (margin):€{s.get('pvl_estimated'):>7.2f}  "
                    f"(derived from PVP+IVA)\n")
            f.write(f"  PVP+IVA (Facturación): €{s.get('pvp_iva'):>7.2f}  "
                    f"(retail max)\n")
            f.write(f"  PVP+IVA Ref (BOE):     €{s.get('pvpiva_referencia_boe'):>7.2f}  "
                    f"(reference retail)\n")
            f.write(f"  Menor precio agrup.:   €{s.get('menor_precio_agrupacion') or 0:>7.2f}  "
                    f"(lowest in homogeneous group)\n")
            f.write(f"  Aportación: {s.get('aportacion')}\n")
            f.write(f"\n")

        f.write("\nDETECTION CAPABILITIES (with this data):\n")
        f.write("-" * 70 + "\n")
        f.write("[x] Invoice price > PVL Ref         (illegal overcharge)\n")
        f.write("[x] Invoice price > derived PVL     (suspicious overcharge)\n")
        f.write("[x] Charged for branded when generic available at menor precio\n")
        f.write("[x] Reference price violations on financed medications\n")
        f.write("[x] Invoice math errors (VAT, totals, line sums)\n")
        f.write("[ ] Commercial discount non-compliance (requires user upload of terms)\n")
        f.write("[ ] Cross-pharmacy benchmarking (requires data network)\n")

    print(open(SUMMARY_TXT).read())
    print(f"\nFiles written:")
    print(f"  Database: {OUTPUT_JSON}")
    print(f"  Summary:  {SUMMARY_TXT}")


if __name__ == "__main__":
    build_lupa_db()
