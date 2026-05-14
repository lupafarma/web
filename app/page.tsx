"use client";

import { useEffect, useMemo, useState } from "react";
import { loadMedications } from "@/lib/medications";
import type { Medication } from "@/lib/medications";
import { checkInvoice, type InvoiceLine } from "@/lib/detection";
import { MESSAGES } from "@/lib/messages";
import { InvoiceGrid } from "@/components/InvoiceGrid";
import { FindingsPanel } from "@/components/FindingsPanel";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { PanelHead } from "@/components/PanelHead";

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

  const findings = useMemo(
    () => (medications ? checkInvoice(lines, medications) : []),
    [lines, medications],
  );

  const flaggedHigh = useMemo(
    () =>
      new Set(
        findings.filter((f) => f.severity === "high").map((f) => f.lineIdx),
      ),
    [findings],
  );

  const flaggedMedium = useMemo(
    () =>
      new Set(
        findings
          .filter((f) => f.severity === "medium" || f.severity === "low")
          .map((f) => f.lineIdx),
      ),
    [findings],
  );

  return (
    <div className="max-w-[1200px] mx-auto w-full px-6 pt-8 pb-20">
      <Header />

      <main>
        {error && (
          <p className="text-sm text-accent-red">{MESSAGES.app.error(error)}</p>
        )}
        {!error && !medications && (
          <p className="text-sm text-ink-soft">{MESSAGES.app.loading}</p>
        )}

        {medications && (
          <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-8 lg:gap-10">
            <section>
              <PanelHead
                title={MESSAGES.panels.factura.title}
                meta={MESSAGES.panels.factura.meta}
              />
              <InvoiceGrid
                lines={lines}
                medications={medications}
                onChange={setLines}
                flaggedHigh={flaggedHigh}
                flaggedMedium={flaggedMedium}
              />
            </section>
            <section>
              <FindingsPanel findings={findings} linesCount={lines.length} />
            </section>
          </div>
        )}
      </main>

      <Footer count={medications?.size ?? 0} />
    </div>
  );
}
