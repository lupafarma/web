"use client";

import { useState } from "react";
import type { Medication } from "@/lib/medications";
import type { InvoiceLine } from "@/lib/detection";
import { eur } from "@/lib/format";

type InvoiceGridProps = {
  lines: InvoiceLine[];
  medications: Map<string, Medication>;
  onChange: (lines: InvoiceLine[]) => void;
};

type NumField = "qty" | "unit" | "total";

const COLS = "grid-cols-[100px_1fr_60px_90px_90px_32px]";

const cellInput =
  "w-full bg-transparent border border-transparent rounded-sm px-1.5 py-1 " +
  "font-mono text-[13px] text-ink hover:bg-white/50 hover:border-rule " +
  "focus:outline-none focus:bg-white focus:border-accent-blue";

export function InvoiceGrid({
  lines,
  medications,
  onChange,
}: InvoiceGridProps) {
  // Per-cell edit buffer: holds raw input strings during editing so the
  // user keeps their literal keystrokes (incl. trailing zeros, "1,5" vs "1.5")
  // until they blur. Without this, controlled inputs reformat mid-typing.
  const [drafts, setDrafts] = useState<Record<string, string>>({});

  function key(idx: number, field: NumField) {
    return `${idx}:${field}`;
  }

  function display(idx: number, field: NumField, value: number): string {
    const k = key(idx, field);
    if (k in drafts) return drafts[k];
    return String(value);
  }

  function parseNum(raw: string): number {
    const n = parseFloat(raw.replace(",", ".").trim());
    return isNaN(n) ? 0 : n;
  }

  function onNumChange(idx: number, field: NumField, raw: string) {
    setDrafts((d) => ({ ...d, [key(idx, field)]: raw }));
    onChange(
      lines.map((l, i) =>
        i === idx ? { ...l, [field]: raw === "" ? 0 : parseNum(raw) } : l,
      ),
    );
  }

  function onNumBlur(idx: number, field: NumField) {
    setDrafts((d) => {
      const k = key(idx, field);
      if (!(k in d)) return d;
      const { [k]: _drop, ...rest } = d;
      return rest;
    });
  }

  function onCnChange(idx: number, raw: string) {
    onChange(
      lines.map((l, i) => (i === idx ? { ...l, cn: raw.trim() } : l)),
    );
  }

  function removeRow(idx: number) {
    setDrafts({});
    onChange(lines.filter((_, i) => i !== idx));
  }

  function addRow() {
    onChange([...lines, { cn: "", qty: 1, unit: 0, total: 0 }]);
  }

  const subtotal = lines.reduce((s, l) => s + (l.total || 0), 0);

  const headerCell =
    "px-2 py-2.5 text-[11px] uppercase tracking-wider text-ink-faint font-medium";

  return (
    <div>
      <div className="bg-card border border-rule overflow-hidden">
        <div className={`grid ${COLS} bg-bg border-b border-rule`}>
          <div className={headerCell}>CN</div>
          <div className={headerCell}>Producto</div>
          <div className={`${headerCell} text-right`}>Cant.</div>
          <div className={`${headerCell} text-right`}>P. unit.</div>
          <div className={`${headerCell} text-right`}>Total</div>
          <div></div>
        </div>

        {lines.map((line, idx) => {
          const med = medications.get(line.cn);
          return (
            <div
              key={idx}
              className={`grid ${COLS} items-center border-b border-rule-soft last:border-b-0`}
            >
              <div className="px-2 py-2.5">
                <input
                  type="text"
                  inputMode="numeric"
                  value={line.cn}
                  onChange={(e) => onCnChange(idx, e.target.value)}
                  className={`${cellInput} text-left font-medium`}
                />
              </div>
              <div className="px-2 py-2.5 text-[13px] leading-snug">
                {med ? (
                  <>
                    {med.nombre.slice(0, 55)}
                    <div className="text-[11px] text-ink-faint mt-0.5">
                      {(med.principio_activo ?? "") +
                        (med.principio_activo && med.laboratorio ? " · " : "") +
                        (med.laboratorio ?? "")}
                    </div>
                  </>
                ) : (
                  <em className="text-ink-faint">CN no encontrado</em>
                )}
              </div>
              <div className="px-2 py-2.5">
                <input
                  type="text"
                  inputMode="numeric"
                  value={display(idx, "qty", line.qty)}
                  onChange={(e) => onNumChange(idx, "qty", e.target.value)}
                  onBlur={() => onNumBlur(idx, "qty")}
                  className={`${cellInput} text-right`}
                />
              </div>
              <div className="px-2 py-2.5">
                <input
                  type="text"
                  inputMode="decimal"
                  value={display(idx, "unit", line.unit)}
                  onChange={(e) => onNumChange(idx, "unit", e.target.value)}
                  onBlur={() => onNumBlur(idx, "unit")}
                  className={`${cellInput} text-right`}
                />
              </div>
              <div className="px-2 py-2.5">
                <input
                  type="text"
                  inputMode="decimal"
                  value={display(idx, "total", line.total)}
                  onChange={(e) => onNumChange(idx, "total", e.target.value)}
                  onBlur={() => onNumBlur(idx, "total")}
                  className={`${cellInput} text-right`}
                />
              </div>
              <button
                type="button"
                aria-label="Eliminar línea"
                title="Eliminar línea"
                onClick={() => removeRow(idx)}
                className="text-center text-ink-faint cursor-pointer select-none text-base hover:text-accent-red bg-transparent border-0 leading-none"
              >
                ×
              </button>
            </div>
          );
        })}
      </div>

      <div className="bg-bg border border-rule border-t-0 px-4 py-3 flex justify-end gap-8 items-baseline font-mono">
        <div>
          <span className="text-[12px] uppercase tracking-wider text-ink-faint mr-2">
            Subtotal:
          </span>
          <span className="text-base font-medium text-ink">{eur(subtotal)}</span>
        </div>
      </div>

      <button
        type="button"
        onClick={addRow}
        className="mt-3 w-full border border-dashed border-rule text-ink-soft py-3 text-[13px] hover:border-ink-soft hover:text-ink transition-colors bg-transparent"
      >
        + Añadir línea
      </button>
    </div>
  );
}
