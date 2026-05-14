"use client";

import { useEffect, useState } from "react";
import { loadMedications, type Medication } from "@/lib/medications";
import type { InvoiceLine } from "@/lib/detection";
import { InvoiceGrid } from "@/components/InvoiceGrid";

const SAMPLE_LINES: InvoiceLine[] = [
  { cn: "650005", qty: 2, unit: 8.5, total: 17.0 },
  { cn: "651068", qty: 5, unit: 2.31, total: 11.55 },
  { cn: "650789", qty: 3, unit: 1.6, total: 4.8 },
  { cn: "650228", qty: 2, unit: 34.0, total: 72.0 },
  { cn: "662020", qty: 1, unit: 19.64, total: 19.64 },
  { cn: "651619", qty: 4, unit: 3.5, total: 14.0 },
  { cn: "667451", qty: 2, unit: 9.22, total: 18.44 },
  { cn: "651076", qty: 3, unit: 4.61, total: 13.83 },
];

export default function Home() {
  const [medications, setMedications] = useState<Map<
    string,
    Medication
  > | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lines, setLines] = useState<InvoiceLine[]>(SAMPLE_LINES);

  useEffect(() => {
    loadMedications()
      .then(setMedications)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : String(e)),
      );
  }, []);

  return (
    <main className="max-w-[1200px] mx-auto px-6 py-8 pb-20 w-full">
      <h1 className="font-medium text-3xl tracking-tight">
        Lupa — en desarrollo
      </h1>

      {error && (
        <p className="mt-2 text-sm text-accent-red">Error: {error}</p>
      )}
      {!error && !medications && (
        <p className="mt-2 text-sm text-ink-soft">Cargando base de datos…</p>
      )}

      {medications && (
        <>
          <div className="mt-8">
            <InvoiceGrid
              lines={lines}
              medications={medications}
              onChange={setLines}
            />
          </div>
          <p className="mt-12 text-[11px] text-ink-faint font-mono uppercase tracking-wider">
            Base de datos: {medications.size.toLocaleString("es-ES")}{" "}
            presentaciones cargadas
          </p>
        </>
      )}
    </main>
  );
}
