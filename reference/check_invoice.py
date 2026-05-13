#!/usr/bin/env python3
"""
LUPA INVOICE CHECKER - Proof of Concept
========================================

Takes a parsed invoice (list of line items) and detects:

  1. Charges above PVL Referencia (illegal overcharge)
  2. Charges suspiciously above derived PVL (probable overcharge)
  3. Branded medication charged when generic equivalent exists
  4. Reference price violations
  5. Invoice math errors (subtotal, VAT, total)

Input: a "fake invoice" with line items, simulating what a real Cofares/Bidafarma
       invoice would look like after PDF parsing.

Output: detection results, formatted as Spanish-pharmacist-friendly findings.
"""
import json
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

DB_PATH = Path("/home/claude/lupa-data/lupa_medication_db.json")
TOLERANCE_PCT = 0.05  # 5% tolerance for "suspicious" overcharge

# =====================================================================
# FAKE INVOICE - this is what a parsed PDF invoice would yield in v1
# =====================================================================
# Real invoice would come from PDF OCR. For this PoC we hardcode it.

FAKE_INVOICE = {
    "distribuidor": "Cofares (simulado)",
    "numero_factura": "F2026-001234",
    "fecha": "2026-04-15",
    "pharmacy_nif": "B12345678",
    "lineas": [
        # CN, qty, unit_price_charged, line_total_charged
        # Line 1: DEPAKINE 500mg 100 comprimidos - charged €8.50 each (overcharge!)
        {"cn": "650005", "cantidad": 2, "precio_unitario": 8.50, "total_linea": 17.00},
        # Line 2: ATORVASTATINA CINFA 10 mg - normal price
        {"cn": "651068", "cantidad": 5, "precio_unitario": 2.31, "total_linea": 11.55},
        # Line 3: AMLODIPINO SANDOZ 10 mg - normal
        {"cn": "650789", "cantidad": 3, "precio_unitario": 1.60, "total_linea": 4.80},
        # Line 4: ACICLOVIR MABO 800 mg - INVOICE ARITHMETIC ERROR
        # 2 units * €34.00 should be €68.00 but invoice says €72.00
        {"cn": "650228", "cantidad": 2, "precio_unitario": 34.00, "total_linea": 72.00},
        # Line 5: AGOMELATINA - branded purchase when generic at lower price exists
        {"cn": "662020", "cantidad": 1, "precio_unitario": 19.64, "total_linea": 19.64},
        # Line 6: ALPRAZOLAM 2mg 30 caps - charged €3.50 (above PVL Ref of €3.10!)
        {"cn": "651619", "cantidad": 4, "precio_unitario": 3.50, "total_linea": 14.00},
    ],
    "subtotal_factura": 138.99,
    "iva_factura": 5.56,
    "total_factura": 144.55,
}

# Spanish formatting
def eur(n):
    return f"€{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def pct(n):
    return f"{n*100:.1f}%".replace(".", ",")


def load_db():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run build_lupa_db.py first.")
    with DB_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def find_cheaper_in_agrupacion(med, db):
    """Find cheaper alternatives in same agrupación homogénea."""
    agrupacion = med.get("agrupacion_code")
    if not agrupacion:
        return None
    
    # Find all entries in same agrupacion
    alts = []
    for cn, entry in db.items():
        if entry.get("agrupacion_code") == agrupacion and cn != med["cn"]:
            if entry.get("pvp_iva"):
                alts.append({
                    "cn": cn,
                    "nombre": entry.get("nombre", "")[:50],
                    "lab": entry.get("laboratorio", "?"),
                    "pvp_iva": entry["pvp_iva"],
                })
    
    if not alts:
        return None
    
    cheapest = min(alts, key=lambda x: x["pvp_iva"])
    return cheapest if cheapest["pvp_iva"] < med.get("pvp_iva", 999) else None


def check_invoice(invoice, db):
    findings = []
    
    for i, linea in enumerate(invoice["lineas"], 1):
        cn = linea["cn"]
        qty = linea["cantidad"]
        precio_unitario = linea["precio_unitario"]
        total_linea = linea["total_linea"]
        
        med = db.get(cn)
        if not med:
            findings.append({
                "tipo": "CN_DESCONOCIDO",
                "linea": i,
                "cn": cn,
                "gravedad": "info",
                "mensaje": f"Línea {i}: CN {cn} no encontrado en Nomenclátor. Verificar.",
                "impacto_eur": 0,
            })
            continue
        
        nombre = med.get("nombre", "?")[:50]
        
        # CHECK 1: Math error on line
        expected_total = round(qty * precio_unitario, 2)
        if abs(total_linea - expected_total) > 0.01:
            diff = total_linea - expected_total
            findings.append({
                "tipo": "ERROR_ARITMETICO",
                "linea": i,
                "cn": cn,
                "gravedad": "alta",
                "mensaje": (
                    f"Línea {i} ({nombre}): "
                    f"{qty} × {eur(precio_unitario)} = {eur(expected_total)}, "
                    f"pero la factura indica {eur(total_linea)}. "
                    f"Diferencia: {eur(diff)} {'a favor del distribuidor' if diff > 0 else 'a tu favor'}."
                ),
                "impacto_eur": diff,
            })
        
        # CHECK 2: Above PVL Referencia (illegal overcharge)
        pvl_ref = med.get("pvl_referencia_boe")
        if pvl_ref and precio_unitario > pvl_ref * 1.01:  # 1% rounding tolerance
            overcharge_per_unit = precio_unitario - pvl_ref
            total_overcharge = overcharge_per_unit * qty
            findings.append({
                "tipo": "PVL_SUPERADO",
                "linea": i,
                "cn": cn,
                "gravedad": "alta",
                "mensaje": (
                    f"Línea {i} ({nombre}): "
                    f"Precio facturado {eur(precio_unitario)} supera el PVL de referencia "
                    f"{eur(pvl_ref)} (BOE Orden SND/1118/2025). "
                    f"Sobrecarga: {eur(overcharge_per_unit)}/unidad × {qty} = {eur(total_overcharge)}. "
                    f"Reclamar al distribuidor con base legal del Art. 2.2 RD 177/2014."
                ),
                "impacto_eur": total_overcharge,
            })
        
        # CHECK 3: Above derived PVL with no BOE Ref (suspicious)
        pvl_est = med.get("pvl_estimated")
        if not pvl_ref and pvl_est and precio_unitario > pvl_est * (1 + TOLERANCE_PCT):
            overcharge_per_unit = precio_unitario - pvl_est
            total_overcharge = overcharge_per_unit * qty
            findings.append({
                "tipo": "PVL_ESTIMADO_SUPERADO",
                "linea": i,
                "cn": cn,
                "gravedad": "media",
                "mensaje": (
                    f"Línea {i} ({nombre}): "
                    f"Precio facturado {eur(precio_unitario)} supera el PVL estimado "
                    f"{eur(pvl_est)} (calculado vía RD 823/2008 a partir de PVP+IVA). "
                    f"Posible sobrecarga: {eur(total_overcharge)}. Verificar contrato comercial."
                ),
                "impacto_eur": total_overcharge,
            })
        
        # CHECK 4: Cheaper generic exists in same agrupación
        cheaper = find_cheaper_in_agrupacion(med, db)
        if cheaper and med.get("tipo_farmaco") == "Medicamento Etica":
            savings_per_unit = med.get("pvp_iva", 0) - cheaper["pvp_iva"]
            potential_savings = savings_per_unit * qty
            if potential_savings > 0.50:  # meaningful threshold
                findings.append({
                    "tipo": "GENERICO_DISPONIBLE",
                    "linea": i,
                    "cn": cn,
                    "gravedad": "baja",
                    "mensaje": (
                        f"Línea {i} ({nombre}): "
                        f"Existe equivalente genérico en la misma agrupación homogénea "
                        f"a {eur(cheaper['pvp_iva'])} ({cheaper['nombre']} de {cheaper['lab']}). "
                        f"Ahorro potencial: {eur(potential_savings)}."
                    ),
                    "impacto_eur": potential_savings,
                })
    
    # CHECK 5: Invoice-level math
    sum_lineas = sum(linea["total_linea"] for linea in invoice["lineas"])
    if abs(sum_lineas - invoice["subtotal_factura"]) > 0.02:
        findings.append({
            "tipo": "TOTAL_FACTURA_ERROR",
            "linea": "TOTAL",
            "gravedad": "alta",
            "mensaje": (
                f"Suma de líneas: {eur(sum_lineas)}. "
                f"Subtotal factura: {eur(invoice['subtotal_factura'])}. "
                f"Diferencia: {eur(sum_lineas - invoice['subtotal_factura'])}."
            ),
            "impacto_eur": sum_lineas - invoice["subtotal_factura"],
        })
    
    return findings


def render_report(findings, invoice):
    print("=" * 75)
    print(f"  LUPA - INFORME DE AUDITORÍA DE FACTURA")
    print(f"  Distribuidor: {invoice['distribuidor']}")
    print(f"  Factura: {invoice['numero_factura']}  |  Fecha: {invoice['fecha']}")
    print(f"  Total factura: {eur(invoice['total_factura'])}")
    print("=" * 75)
    print()
    
    if not findings:
        print("  ✓ No se han detectado anomalías en esta factura.")
        return
    
    total_impact = sum(f["impacto_eur"] for f in findings if f["impacto_eur"] > 0)
    
    print(f"  HALLAZGOS: {len(findings)}")
    print(f"  IMPACTO ECONÓMICO TOTAL POTENCIAL: {eur(total_impact)}")
    print()
    
    by_severity = {"alta": [], "media": [], "baja": [], "info": []}
    for f in findings:
        by_severity[f.get("gravedad", "info")].append(f)
    
    sev_labels = {
        "alta":  "GRAVEDAD ALTA",
        "media": "GRAVEDAD MEDIA",
        "baja":  "OPORTUNIDAD DE AHORRO",
        "info":  "INFORMACIÓN",
    }
    
    for sev in ["alta", "media", "baja", "info"]:
        items = by_severity[sev]
        if not items:
            continue
        print("-" * 75)
        print(f"  {sev_labels[sev]} ({len(items)})")
        print("-" * 75)
        for f in items:
            print(f"  • {f['mensaje']}")
            print()
    
    print("=" * 75)
    print(f"  Fuentes consultadas:")
    print(f"  - Nomenclátor de Facturación, Ministerio de Sanidad (mayo 2026)")
    print(f"  - BOE Orden SND/1118/2025 (precios industriales de referencia)")
    print(f"  - Real Decreto 823/2008 (márgenes regulados)")
    print(f"  - Real Decreto 177/2014 (sistema de precios de referencia)")
    print("=" * 75)


if __name__ == "__main__":
    db = load_db()
    print(f"Base de datos cargada: {len(db):,} medicamentos\n")
    findings = check_invoice(FAKE_INVOICE, db)
    render_report(findings, FAKE_INVOICE)
