import type { BodySegment } from "./detection";
import { toTitleCase } from "./format";

// Header intro is rendered with <strong> emphasis on key BOE/Nomenclátor terms.
// Keep as a BodySegment[] so the Header component can render React fragments
// the same way the findings body does, without dangerouslySetInnerHTML.
const HEADER_INTRO: BodySegment[] = [
  { kind: "text", value: "Lupa compara cada línea de tu factura contra el " },
  { kind: "strong", value: "Nomenclátor de Facturación" },
  { kind: "text", value: ", el " },
  { kind: "strong", value: "PVL Industrial de Referencia" },
  {
    kind: "text",
    value:
      " publicado en BOE, y los márgenes regulados por RD 823/2008. Detecta sobrecargas ilegales, errores aritméticos, y alternativas genéricas más económicas. Esta es una demostración con datos reales. Modifica cualquier campo y verás el análisis al instante.",
  },
];

export const MESSAGES = {
  meta: {
    title: "Lupa — Auditor de facturas farmacéuticas",
    description:
      "Auditor de facturas farmacéuticas para farmacias españolas con procesamiento 100% local en el navegador.",
  },

  app: {
    loading: "Cargando base de datos…",
    error: (msg: string) => `No se pudo cargar la base de datos: ${msg}`,
    baseInfo: (count: number) =>
      `Base de datos: ${count.toLocaleString("es-ES")} presentaciones cargadas`,
  },

  brand: {
    wordmark: "Lupa",
    tagline: "Auditor de facturas farmacéuticas",
  },

  header: {
    privacyBadge:
      "Procesamiento 100% local en tu navegador. Cero conexiones de red tras la carga.",
    intro: HEADER_INTRO,
  },

  panels: {
    factura: {
      title: "Factura",
      meta: "DEMO · Cofares simulado",
    },
    hallazgos: {
      title: "Hallazgos",
      count: (n: number) =>
        n === 0
          ? "Ninguno detectado"
          : n === 1
            ? "1 detectado"
            : `${n} detectados`,
    },
  },

  invoiceGrid: {
    headers: {
      cn: "CN",
      producto: "Producto",
      cantidad: "Cant.",
      unitario: "P. unit.",
      total: "Total",
    },
    removeRow: "Eliminar línea",
    cnNotFound: "CN no reconocido",
    subtotal: "Subtotal:",
    addRow: "+ Añadir línea",
    clearAll: "Vaciar",
    clearAllConfirm: "¿Vaciar la factura? Se borrarán todas las líneas.",
    loadSample: "Cargar ejemplo",
  },

  findings: {
    linesAnalyzed: "Líneas analizadas",
    totalImpact: "Impacto potencial",
    empty: "No se han detectado anomalías en esta factura.",
  },

  // Detection-rule strings: titles + body templates + legal citations.
  // Body templates receive already-eur-formatted price strings so the engine
  // keeps its formatting decisions in one place (lib/format.ts via lib/detection.ts).
  detection: {
    unknownCn: {
      title: "CN no reconocido",
      body: (cn: string): BodySegment[] => [
        { kind: "text", value: "El código nacional " },
        { kind: "strong", value: cn },
        {
          kind: "text",
          value:
            " no figura en el Nomenclátor cargado. Verifícalo manualmente.",
        },
      ],
    },
    mathError: {
      title: "Error aritmético en línea",
      body: (p: {
        nombre: string;
        qty: number;
        unitEur: string;
        expectedEur: string;
        totalEur: string;
        diffEur: string;
        diffPositive: boolean;
      }): BodySegment[] => [
        { kind: "strong", value: p.nombre },
        {
          kind: "text",
          value: `: ${p.qty} × ${p.unitEur} = ${p.expectedEur}, pero la factura indica ${p.totalEur}. Diferencia: `,
        },
        { kind: "strong", value: p.diffEur },
        {
          kind: "text",
          value: ` ${p.diffPositive ? "a favor del distribuidor" : "a tu favor"}.`,
        },
      ],
    },
    pvlViolation: {
      title: "Cobro superior al PVL de Referencia (ilegal)",
      body: (p: {
        nombre: string;
        unitEur: string;
        pvlRefEur: string;
        overUnitEur: string;
        qty: number;
        overTotalEur: string;
      }): BodySegment[] => [
        { kind: "strong", value: p.nombre },
        {
          kind: "text",
          value: `: precio facturado ${p.unitEur} supera el PVL Industrial de Referencia `,
        },
        { kind: "strong", value: p.pvlRefEur },
        {
          kind: "text",
          value: `. Sobrecarga: ${p.overUnitEur}/u × ${p.qty} = `,
        },
        { kind: "strong", value: p.overTotalEur },
        {
          kind: "text",
          value:
            ". El PVL Referencia tiene carácter de máximo según el Art. 2.2 del RD 177/2014.",
        },
      ],
      cite: "Fuente: BOE-A-2025-20356, Art. 2.2 RD 177/2014",
    },
    pvlEstimated: {
      title: "Sobrecarga sospechosa (PVL estimado)",
      body: (p: {
        nombre: string;
        unitEur: string;
        pvlEstEur: string;
        overTotalEur: string;
      }): BodySegment[] => [
        { kind: "strong", value: p.nombre },
        {
          kind: "text",
          value: `: precio ${p.unitEur} supera el PVL estimado ${p.pvlEstEur} (calculado vía márgenes RD 823/2008). Posible sobrecarga: `,
        },
        { kind: "strong", value: p.overTotalEur },
        { kind: "text", value: ". Revisa tu contrato comercial." },
      ],
      cite: "Fuente: RD 823/2008, márgenes regulados",
    },
    cheaperAlt: {
      title: "Oportunidad: genérico equivalente más económico",
      body: (p: {
        nombre: string;
        altNombre: string;
        altLab: string;
        altEur: string;
        savingsEur: string;
      }): BodySegment[] => [
        { kind: "strong", value: p.nombre },
        {
          kind: "text",
          value: `: existe ${p.altNombre} (${p.altLab}) a ${p.altEur} en la misma agrupación homogénea. Ahorro potencial: `,
        },
        { kind: "strong", value: p.savingsEur },
        { kind: "text", value: "." },
      ],
      cite: (agrupacion: string) => `Agrupación homogénea: ${toTitleCase(agrupacion)}`,
    },
  },

  footer: {
    sourcesHeading: "Fuentes consultadas:",
    sources: {
      nomenclator:
        "Nomenclátor de Facturación, Ministerio de Sanidad — datos de mayo 2026 (PVP+IVA, precio de referencia, agrupaciones homogéneas)",
      boe: {
        label: "BOE Orden SND/1118/2025",
        href: "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-20356",
        desc: "Actualización del sistema de precios de referencia de medicamentos (PVL Referencia)",
      },
      rd177: {
        label: "Real Decreto 177/2014",
        href: "https://www.boe.es/buscar/act.php?id=BOE-A-2014-3189",
        desc: "Sistema de precios de referencia (Art. 2.2 carácter de PVL máximo, Disposición adicional octava)",
      },
      rd823: {
        label: "Real Decreto 823/2008",
        href: "https://www.boe.es/buscar/act.php?id=BOE-A-2008-9291",
        desc: "Márgenes regulados de distribución (7,6%) y dispensación (27,9%)",
      },
    },
    privacy:
      "Lupa es software libre y auditable. Tus facturas nunca abandonan este navegador.",
    buildInfo: (count: number) =>
      `Versión de demostración · ${count.toLocaleString("es-ES")} presentaciones cargadas · Lupafarma · 2026 ·`,
    repoLabel: "github.com/lupafarma",
    repoHref: "https://github.com/lupafarma/web",
  },
};
