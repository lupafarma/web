export function Header() {
  return (
    <header className="border-b border-rule pb-6 mb-8">
      <div className="flex items-baseline gap-4 flex-wrap">
        <h1 className="font-serif italic font-semibold text-5xl tracking-tight m-0 leading-none">
          Lupa
        </h1>
        <p className="font-serif text-lg text-ink-soft m-0">
          Auditor de facturas farmacéuticas — España
        </p>
      </div>

      <div className="inline-flex items-center gap-2 mt-4 px-3 py-1.5 bg-good border border-accent-green rounded-sm text-[13px] text-accent-green font-medium">
        <span className="w-1.5 h-1.5 rounded-full bg-accent-green inline-block" />
        <span>
          Procesamiento 100% local en tu navegador. Cero conexiones de red tras
          la carga.
        </span>
      </div>

      <p className="mt-6 max-w-[720px] text-[15px] text-ink-soft leading-relaxed">
        Lupa compara cada línea de tu factura contra el{" "}
        <strong className="text-ink font-semibold">
          Nomenclátor de Facturación
        </strong>
        , el{" "}
        <strong className="text-ink font-semibold">
          PVL Industrial de Referencia
        </strong>{" "}
        publicado en BOE, y los márgenes regulados por RD 823/2008. Detecta
        sobrecargas ilegales, errores aritméticos, y alternativas genéricas más
        económicas. Esta es una demostración con datos reales. Modifica
        cualquier campo para ver el análisis actualizarse.
      </p>
    </header>
  );
}
