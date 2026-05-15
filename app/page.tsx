"use client";

import { useEffect, useMemo, useState } from "react";
import { loadMedications } from "@/lib/medications";
import type { Medication } from "@/lib/medications";
import { checkInvoice, type InvoiceLine } from "@/lib/detection";
import { MESSAGES } from "@/lib/messages";
import { SAMPLE_LINES } from "@/lib/sample";
import { InvoiceGrid } from "@/components/InvoiceGrid";
import { FindingsPanel } from "@/components/FindingsPanel";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { PanelHead } from "@/components/PanelHead";

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
                onClearAll={() => {
                  if (window.confirm(MESSAGES.invoiceGrid.clearAllConfirm)) {
                    setLines([]);
                  }
                }}
                onLoadSample={() => setLines(SAMPLE_LINES)}
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
