import type { Finding, Severity } from "@/lib/detection";
import { eur } from "@/lib/format";
import { PanelHead } from "./PanelHead";

type FindingsPanelProps = {
  findings: Finding[];
  linesCount: number;
};

const SEVERITY_ORDER: Record<Severity, number> = {
  high: 0,
  medium: 1,
  low: 2,
  info: 3,
};

const SEVERITY_CARD: Record<Severity, string> = {
  high: "bg-warn border-l-accent-red",
  medium: "bg-info border-l-accent-amber",
  low: "bg-card border-l-accent-blue",
  info: "bg-card border-l-ink-faint",
};

export function FindingsPanel({ findings, linesCount }: FindingsPanelProps) {
  const totalImpact = findings.reduce(
    (s, f) => s + Math.max(0, f.impact),
    0,
  );

  const sorted = [...findings].sort(
    (a, b) => SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity],
  );

  const countText =
    findings.length === 0
      ? "Ninguno detectado"
      : findings.length === 1
        ? "1 detectado"
        : `${findings.length} detectados`;

  return (
    <section>
      <PanelHead title="Hallazgos" meta={countText} />

      <div className="bg-card border border-rule p-4 mb-5 grid grid-cols-2 gap-4">
        <div>
          <div className="text-[11px] uppercase tracking-wider text-ink-faint mb-1">
            Líneas analizadas
          </div>
          <div className="font-serif font-medium text-[32px] leading-none text-ink">
            {linesCount}
          </div>
        </div>
        <div>
          <div className="text-[11px] uppercase tracking-wider text-ink-faint mb-1">
            Impacto potencial
          </div>
          <div className="font-serif font-medium text-[32px] leading-none text-accent-red">
            {eur(totalImpact)}
          </div>
        </div>
      </div>

      {findings.length === 0 ? (
        <div className="border border-accent-green bg-good text-accent-green text-center py-6 px-4 italic text-[18px] font-serif">
          No se han detectado anomalías en esta factura.
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {sorted.map((f, i) => (
            <article
              key={i}
              className={`${SEVERITY_CARD[f.severity]} border-l-[3px] py-3.5 px-4`}
            >
              <div className="flex items-baseline justify-between mb-1.5 gap-3">
                <div className="font-serif font-semibold text-[15px] text-ink">
                  {f.title}
                </div>
                {f.impact > 0 && (
                  <div className="font-mono font-semibold text-[14px] text-accent-red whitespace-nowrap">
                    {eur(f.impact)}
                  </div>
                )}
              </div>
              <div className="text-[14px] text-ink-soft leading-snug">
                <span className="inline-block font-mono text-[11px] bg-black/5 px-1.5 py-0.5 rounded-sm text-ink-soft mr-1.5 align-baseline">
                  {f.lineRef}
                </span>
                {f.body.map((seg, j) =>
                  seg.kind === "strong" ? (
                    <strong key={j} className="text-ink font-semibold">
                      {seg.value}
                    </strong>
                  ) : (
                    <span key={j}>{seg.value}</span>
                  ),
                )}
              </div>
              {f.cite && (
                <div className="mt-2 text-[12px] text-ink-faint italic">
                  {f.cite}
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
