import type { Medication } from "./medications";

export type Severity = "high" | "medium" | "low" | "info";

export type BodySegment =
  | { kind: "text"; value: string }
  | { kind: "strong"; value: string };

export type InvoiceLine = {
  cn: string;
  qty: number;
  unit: number;
  total: number;
};

export type Finding = {
  severity: Severity;
  title: string;
  lineRef: string;
  lineIdx: number;
  body: BodySegment[];
  impact: number;
  cite: string;
};

export const PHARM_MARGIN = 0.279;
export const DIST_MARGIN = 0.076;
export const IVA_REIMB = 0.04;
export const PVL_TOLERANCE = 0.01;
export const EST_TOLERANCE = 0.05;

export function derivePVL(pvpiva: number): number {
  const pvp = pvpiva / (1 + IVA_REIMB);
  const pvf = pvp * (1 - PHARM_MARGIN);
  return pvf / (1 + DIST_MARGIN);
}

export function findCheaperAlternative(
  med: Medication,
  db: Map<string, Medication>,
): Medication | null {
  if (!med.agrupacion_code) return null;
  let cheapest: Medication | null = null;
  for (const [cn, e] of db) {
    if (
      e.agrupacion_code === med.agrupacion_code &&
      cn !== med.cn &&
      e.pvp_iva != null
    ) {
      if (cheapest === null || e.pvp_iva < (cheapest.pvp_iva ?? Infinity)) {
        cheapest = e;
      }
    }
  }
  if (cheapest && (cheapest.pvp_iva ?? Infinity) < (med.pvp_iva ?? 999)) {
    return cheapest;
  }
  return null;
}

function eur(n: number | null | undefined): string {
  if (n == null || isNaN(n)) return "—";
  return (
    "€" +
    Number(n)
      .toFixed(2)
      .replace(".", ",")
      .replace(/\B(?=(\d{3})+(?!\d))/g, ".")
  );
}

// Implements the four rules from reference/lupa_demo.html. Rule 5 from
// reference/check_invoice.py (invoice total mismatch) is intentionally dropped
// for v1 — the demo's UI has no declared-total entry, so the rule can't fire.
// Revisit in v2 alongside PDF parsing where declared totals are extracted.
export function checkInvoice(
  lines: InvoiceLine[],
  db: Map<string, Medication>,
): Finding[] {
  const findings: Finding[] = [];

  lines.forEach((line, idx) => {
    const lineNum = idx + 1;
    const lineRef = `L${lineNum}`;
    const med = db.get(line.cn);

    if (!med) {
      findings.push({
        severity: "info",
        title: "CN no reconocido",
        lineRef,
        lineIdx: idx,
        body: [
          { kind: "text", value: "El código nacional " },
          { kind: "strong", value: line.cn },
          {
            kind: "text",
            value: " no figura en el Nomenclátor cargado. Verificar manualmente.",
          },
        ],
        impact: 0,
        cite: "",
      });
      return;
    }

    const nombre = med.nombre || "?";

    // CHECK 1: Math error on line
    const expected = Math.round(line.qty * line.unit * 100) / 100;
    if (Math.abs(line.total - expected) > 0.01) {
      const diff = line.total - expected;
      findings.push({
        severity: "high",
        title: "Error aritmético en línea",
        lineRef,
        lineIdx: idx,
        body: [
          { kind: "strong", value: nombre.slice(0, 50) },
          {
            kind: "text",
            value: `: ${line.qty} × ${eur(line.unit)} = ${eur(expected)}, pero la factura indica ${eur(line.total)}. Diferencia: `,
          },
          { kind: "strong", value: eur(diff) },
          {
            kind: "text",
            value: ` ${diff > 0 ? "a favor del distribuidor" : "a tu favor"}.`,
          },
        ],
        impact: diff,
        cite: "",
      });
    }

    // CHECK 2: Above PVL Referencia (illegal)
    const pvlRef = med.pvl_referencia_boe;
    if (pvlRef != null && line.unit > pvlRef * (1 + PVL_TOLERANCE)) {
      const overUnit = line.unit - pvlRef;
      const overTotal = overUnit * line.qty;
      findings.push({
        severity: "high",
        title: "Sobrecarga sobre PVL Referencia (ilegal)",
        lineRef,
        lineIdx: idx,
        body: [
          { kind: "strong", value: nombre.slice(0, 50) },
          {
            kind: "text",
            value: `: precio facturado ${eur(line.unit)} supera el PVL Industrial de Referencia `,
          },
          { kind: "strong", value: eur(pvlRef) },
          {
            kind: "text",
            value: `. Sobrecarga: ${eur(overUnit)}/u × ${line.qty} = `,
          },
          { kind: "strong", value: eur(overTotal) },
          {
            kind: "text",
            value:
              ". El PVL Referencia tiene carácter de máximo según el Art. 2.2 del RD 177/2014.",
          },
        ],
        impact: overTotal,
        cite: "Fuente: BOE-A-2025-20356, Art. 2.2 RD 177/2014",
      });
    }

    // CHECK 3: Above derived PVL when no BOE Ref available
    if (pvlRef == null && med.pvp_iva != null) {
      const pvlEst = med.pvl_estimated ?? derivePVL(med.pvp_iva);
      if (pvlEst != null && line.unit > pvlEst * (1 + EST_TOLERANCE)) {
        const overUnit = line.unit - pvlEst;
        const overTotal = overUnit * line.qty;
        findings.push({
          severity: "medium",
          title: "Sobrecarga sospechosa (PVL estimado)",
          lineRef,
          lineIdx: idx,
          body: [
            { kind: "strong", value: nombre.slice(0, 50) },
            {
              kind: "text",
              value: `: precio ${eur(line.unit)} supera el PVL estimado ${eur(pvlEst)} (calculado vía márgenes RD 823/2008). Posible sobrecarga: `,
            },
            { kind: "strong", value: eur(overTotal) },
            { kind: "text", value: ". Verificar contrato comercial." },
          ],
          impact: overTotal,
          cite: "Fuente: RD 823/2008, márgenes regulados",
        });
      }
    }

    // CHECK 4: Branded medication when cheaper generic available
    if (
      med.tipo_farmaco &&
      (med.tipo_farmaco.includes("Etica") ||
        (med.principio_activo && !nombre.toUpperCase().includes("EFG")))
    ) {
      const cheaper = findCheaperAlternative(med, db);
      if (cheaper && med.pvp_iva != null && cheaper.pvp_iva != null) {
        const savingsUnit = med.pvp_iva - cheaper.pvp_iva;
        const savingsTotal = savingsUnit * line.qty;
        if (savingsTotal > 0.5) {
          findings.push({
            severity: "low",
            title: "Oportunidad: genérico equivalente más económico",
            lineRef,
            lineIdx: idx,
            body: [
              { kind: "strong", value: nombre.slice(0, 50) },
              {
                kind: "text",
                value: `: existe ${cheaper.nombre.slice(0, 45)} (${cheaper.laboratorio ?? "?"}) a ${eur(cheaper.pvp_iva)} en la misma agrupación homogénea. Ahorro potencial: `,
              },
              { kind: "strong", value: eur(savingsTotal) },
              { kind: "text", value: "." },
            ],
            impact: savingsTotal,
            cite: `Agrupación homogénea: ${med.agrupacion_nombre ?? med.agrupacion_code}`,
          });
        }
      }
    }
  });

  return findings;
}
