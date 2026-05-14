import { describe, it, expect } from "vitest";
import type { Medication } from "./medications";
import {
  checkInvoice,
  derivePVL,
  findCheaperAlternative,
  type Finding,
} from "./detection";

function med(overrides: Partial<Medication> & Pick<Medication, "cn" | "nombre">): Medication {
  return {
    aportacion: "NORMAL",
    huerfano: false,
    source_facturacion: "test",
    tipo_farmaco: null,
    principio_activo: null,
    laboratorio: null,
    estado: null,
    pvp_iva: null,
    precio_referencia: null,
    menor_precio_agrupacion: null,
    agrupacion_code: null,
    agrupacion_nombre: null,
    ...overrides,
  };
}

const db = new Map<string, Medication>([
  [
    "650228",
    med({
      cn: "650228",
      nombre: "ACICLOVIR MABO 800 mg comprimidos",
      tipo_farmaco: "Medicamento Generico",
      principio_activo: "ACICLOVIR",
      laboratorio: "MABO",
      pvp_iva: 40.0,
      pvl_estimated: 25.79,
    }),
  ],
  [
    "651068",
    med({
      cn: "651068",
      nombre:
        "ATORVASTATINA CINFA 10 mg comprimidos recubiertos, 28 comprimidos",
      tipo_farmaco: "Medicamento Generico",
      principio_activo: "ATORVASTATINA",
      laboratorio: "CINFA",
      pvp_iva: 3.61,
      agrupacion_code: "304",
      agrupacion_nombre: "ATORVASTATINA 10 MG 28",
      pvl_estimated: 2.33,
      pvl_referencia_boe: 2.31,
      pvpiva_referencia_boe: 3.61,
    }),
  ],
  [
    "651619",
    med({
      cn: "651619",
      nombre: "ALPRAZOLAM CINFA 2 mg comprimidos EFG, 30 comprimidos",
      tipo_farmaco: "Medicamento Generico",
      principio_activo: "ALPRAZOLAM",
      laboratorio: "CINFA",
      pvp_iva: 4.85,
      agrupacion_code: "A1",
      agrupacion_nombre: "ALPRAZOLAM 2 MG 30",
      pvl_estimated: 2.71,
      pvl_referencia_boe: 3.1,
      pvpiva_referencia_boe: 4.85,
    }),
  ],
  // Branded med with a cheaper generic in same agrupacion
  [
    "662020",
    med({
      cn: "662020",
      nombre: "VALDOXAN 25 mg comprimidos recubiertos, 28 comprimidos",
      tipo_farmaco: "Medicamento Etica",
      principio_activo: "AGOMELATINA",
      laboratorio: "SERVIER",
      pvp_iva: 25.0,
      agrupacion_code: "AGO1",
      agrupacion_nombre: "AGOMELATINA 25 MG 28",
      pvl_estimated: 16.1,
    }),
  ],
  [
    "700001",
    med({
      cn: "700001",
      nombre: "AGOMELATINA CINFA 25 mg EFG, 28 comprimidos",
      tipo_farmaco: "Medicamento Generico",
      principio_activo: "AGOMELATINA",
      laboratorio: "CINFA",
      pvp_iva: 18.0,
      agrupacion_code: "AGO1",
      agrupacion_nombre: "AGOMELATINA 25 MG 28",
      pvl_estimated: 11.59,
    }),
  ],
]);

describe("derivePVL", () => {
  // pvp = 3.61 / 1.04 = 3.471154; pvf = 3.471154 * 0.721 = 2.502702; pvl = 2.502702 / 1.076 ≈ 2.326
  it("derives ~2.33 from ATORVASTATINA pvpiva 3.61 (matches build-time pvl_estimated)", () => {
    expect(derivePVL(3.61)).toBeCloseTo(2.33, 2);
  });

  // pvp = 12.05 / 1.04 = 11.5865; pvf = 11.5865 * 0.721 = 8.3539; pvl = 8.3539 / 1.076 ≈ 7.7639
  it("derives ~7.76 from DEPAKINE pvpiva 12.05 (matches build-time pvl_estimated 7.76)", () => {
    expect(derivePVL(12.05)).toBeCloseTo(7.76, 2);
  });

  it("is monotonic: higher PVP+IVA yields higher PVL", () => {
    expect(derivePVL(20)).toBeGreaterThan(derivePVL(10));
  });
});

describe("findCheaperAlternative", () => {
  it("returns the cheaper alt for a branded med with same agrupacion_code", () => {
    const valdoxan = db.get("662020")!;
    const cheaper = findCheaperAlternative(valdoxan, db);
    expect(cheaper).not.toBeNull();
    expect(cheaper?.cn).toBe("700001");
    expect(cheaper?.pvp_iva).toBe(18.0);
  });

  it("returns null when no agrupacion_code is set", () => {
    const aciclovir = db.get("650228")!;
    expect(findCheaperAlternative(aciclovir, db)).toBeNull();
  });

  it("returns null when the med itself is already the cheapest in agrupacion", () => {
    const cinfa = db.get("700001")!;
    expect(findCheaperAlternative(cinfa, db)).toBeNull();
  });
});

describe("checkInvoice — rule 1 (math error)", () => {
  it("flags 2 × €34,00 = €68,00 but invoice says €72,00 with impact €4,00", () => {
    const findings = checkInvoice(
      [{ cn: "650228", qty: 2, unit: 34.0, total: 72.0 }],
      db,
    );
    const math = findings.filter((f) => f.title === "Error aritmético en línea");
    expect(math).toHaveLength(1);
    expect(math[0].severity).toBe("high");
    expect(math[0].impact).toBeCloseTo(4.0, 2);
    expect(math[0].lineRef).toBe("L1");
    expect(math[0].lineIdx).toBe(0);
    // Body should contain the eur-formatted diff "€4,00" as a strong segment
    const strongValues = math[0].body
      .filter((s) => s.kind === "strong")
      .map((s) => s.value);
    expect(strongValues).toContain("€4,00");
    expect(strongValues).toContain("ACICLOVIR MABO 800 mg comprimidos");
  });
});

describe("checkInvoice — rule 2 (PVL Referencia violation)", () => {
  it("flags ALPRAZOLAM unit €3,50 over PVL Ref €3,10 with impact €1,60 (qty=4)", () => {
    const findings = checkInvoice(
      [{ cn: "651619", qty: 4, unit: 3.5, total: 14.0 }],
      db,
    );
    const violations = findings.filter(
      (f) => f.title === "Cobro superior al PVL de Referencia (ilegal)",
    );
    expect(violations).toHaveLength(1);
    const v: Finding = violations[0];
    expect(v.severity).toBe("high");
    expect(v.impact).toBeCloseTo(1.6, 2);
    expect(v.cite).toBe("Fuente: BOE-A-2025-20356, Art. 2.2 RD 177/2014");
    // No PVL-estimated rule fires when BOE ref exists
    const estViolations = findings.filter(
      (f) => f.title === "Sobrecarga sospechosa (PVL estimado)",
    );
    expect(estViolations).toHaveLength(0);
  });
});

describe("checkInvoice — clean line", () => {
  it("ATORVASTATINA at €2,31 (= PVL Ref) with correct math produces no overcharge or math finding", () => {
    const findings = checkInvoice(
      [{ cn: "651068", qty: 5, unit: 2.31, total: 11.55 }],
      db,
    );
    const blocking = findings.filter(
      (f) =>
        f.title === "Cobro superior al PVL de Referencia (ilegal)" ||
        f.title === "Sobrecarga sospechosa (PVL estimado)" ||
        f.title === "Error aritmético en línea",
    );
    expect(blocking).toHaveLength(0);
  });
});

describe("checkInvoice — rule 4 (cheaper alternative)", () => {
  it("flags VALDOXAN (branded) when AGOMELATINA generic in same agrupacion is cheaper", () => {
    const findings = checkInvoice(
      [{ cn: "662020", qty: 1, unit: 16.1, total: 16.1 }],
      db,
    );
    const cheaper = findings.filter(
      (f) => f.title === "Oportunidad: genérico equivalente más económico",
    );
    expect(cheaper).toHaveLength(1);
    expect(cheaper[0].severity).toBe("low");
    // 25.00 - 18.00 = 7.00 per unit, qty=1 → savings 7.00
    expect(cheaper[0].impact).toBeCloseTo(7.0, 2);
    expect(cheaper[0].cite).toBe("Agrupación homogénea: Agomelatina 25 Mg 28");
  });
});

describe("checkInvoice — unknown CN", () => {
  it("emits a single info finding for a CN missing from the DB", () => {
    const findings = checkInvoice(
      [{ cn: "999999", qty: 1, unit: 10.0, total: 10.0 }],
      db,
    );
    expect(findings).toHaveLength(1);
    expect(findings[0].severity).toBe("info");
    expect(findings[0].title).toBe("CN no reconocido");
    expect(findings[0].impact).toBe(0);
    expect(findings[0].lineRef).toBe("L1");
    const strongValues = findings[0].body
      .filter((s) => s.kind === "strong")
      .map((s) => s.value);
    expect(strongValues).toContain("999999");
  });
});
