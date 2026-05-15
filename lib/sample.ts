import type { InvoiceLine } from "./detection";

// Demo invoice rows shown on first load. Mix of clean lines and ones that
// trip every detection rule (PVL Ref violation, derived PVL overcharge,
// math error, cheaper-generic alternative) so the demo lights up findings
// without manual entry. Used by app/page.tsx initial state and the
// "Cargar ejemplo" button (lib/messages.ts → invoiceGrid.loadSample).
export const SAMPLE_LINES: InvoiceLine[] = [
  { cn: "650005", qty: 2, unit: 8.5, total: 17.0 },
  { cn: "651068", qty: 5, unit: 2.31, total: 11.55 },
  { cn: "650789", qty: 3, unit: 1.6, total: 4.8 },
  { cn: "650228", qty: 2, unit: 34.0, total: 72.0 },
  { cn: "662020", qty: 1, unit: 19.64, total: 19.64 },
  { cn: "651619", qty: 4, unit: 3.5, total: 14.0 },
  { cn: "667451", qty: 2, unit: 9.22, total: 18.44 },
  { cn: "651076", qty: 3, unit: 4.61, total: 13.83 },
];
