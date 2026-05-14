const LINK_CLASS =
  "text-ink-soft underline decoration-rule hover:decoration-ink-soft";

export function Footer() {
  return (
    <footer className="mt-16 pt-6 border-t border-rule text-[12px] text-ink-faint font-mono">
      <div>
        <strong className="text-ink-soft">Fuentes consultadas:</strong>
      </div>
      <div className="mt-2 leading-relaxed">
        · Nomenclátor de Facturación, Ministerio de Sanidad — datos de mayo
        2026 (PVP+IVA, precio de referencia, agrupaciones homogéneas)
        <br />
        ·{" "}
        <a
          className={LINK_CLASS}
          href="https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-20356"
        >
          BOE Orden SND/1118/2025
        </a>{" "}
        — Actualización del sistema de precios de referencia de medicamentos
        (PVL Referencia)
        <br />
        ·{" "}
        <a
          className={LINK_CLASS}
          href="https://www.boe.es/buscar/act.php?id=BOE-A-2014-3189"
        >
          Real Decreto 177/2014
        </a>{" "}
        — Sistema de precios de referencia (Art. 2.2 carácter de PVL máximo,
        Disposición adicional octava)
        <br />
        ·{" "}
        <a
          className={LINK_CLASS}
          href="https://www.boe.es/buscar/act.php?id=BOE-A-2008-9291"
        >
          Real Decreto 823/2008
        </a>{" "}
        — Márgenes regulados de distribución (7,6%) y dispensación (27,9%)
      </div>
      <div className="mt-4">
        Lupa es software libre y auditable. Tus facturas nunca abandonan este
        navegador.
        <br />
        Versión de demostración · 20.551 presentaciones cargadas · Lupafarma ·
        2026 ·{" "}
        <a className={LINK_CLASS} href="https://github.com/lupafarma/web">
          github.com/lupafarma
        </a>
      </div>
    </footer>
  );
}
