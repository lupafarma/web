# Lupa

> Auditor de facturas farmacéuticas para farmacias españolas. Procesamiento 100% local en el navegador.

[lupafarma.es](https://lupafarma.es) · [Probar Lupa](https://lupafarma.es)

---

## Qué hace

Lupa analiza facturas de distribuidores farmacéuticos (Cofares, Bidafarma, Hefame, Alliance, etc.) y detecta:

- **Sobrecargas sobre el PVL Industrial de Referencia** (ilegales según el Art. 2.2 del RD 177/2014)
- **Errores aritméticos** en las líneas de factura
- **Cargos sospechosos** sobre el PVL estimado vía márgenes regulados (RD 823/2008)
- **Oportunidades de sustitución por genérico** dentro de la misma agrupación homogénea
- **Discrepancias en el total** de la factura

Cada hallazgo se presenta con su base legal correspondiente para que el farmacéutico pueda reclamar al distribuidor con fundamento.

---

## Privacidad

**Cero conexiones de red tras la carga inicial.** Verificable abriendo las herramientas de desarrollador del navegador (F12 → pestaña Red).

- Sin registro
- Sin cuenta
- Sin cookies de seguimiento
- Sin telemetría
- Sin envío de datos a ningún servidor
- Las facturas nunca abandonan el navegador del farmacéutico

---

## Fuentes de datos

Todos los datos son públicos y proceden de fuentes oficiales:

| Fuente | Aporta |
|---|---|
| [Nomenclátor de Facturación](https://www.sanidad.gob.es/profesionales/nomenclator.do), Ministerio de Sanidad | PVP+IVA, precio de referencia, menor precio de agrupación |
| [BOE Orden SND/1118/2025](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-20356) | PVL Industrial de Referencia |
| [Real Decreto 823/2008](https://www.boe.es/buscar/act.php?id=BOE-A-2008-9291) | Márgenes regulados (7,6% distribución, 27,9% dispensación) |
| [Real Decreto 177/2014](https://www.boe.es/buscar/act.php?id=BOE-A-2014-3189) | Sistema de precios de referencia |

---

## Cómo usar

1. Abre [lupafarma.es](https://lupafarma.es) en tu navegador
2. Introduce las líneas de tu factura (código nacional, cantidad, precio unitario, total)
3. Lupa analiza automáticamente y muestra los hallazgos con su base legal

No hay que instalar nada. No hay que crear cuenta. No hay que pagar.

---

## Stack técnico

- Next.js (App Router) con TypeScript
- Tailwind CSS
- Exportación estática (`output: 'export'`)
- Despliegue en Vercel sobre dominio propio
- Base de datos de medicamentos incluida como JSON estático (~12 MB)
- Sin backend, sin API, sin base de datos remota

---

## Desarrollo local

```bash
git clone https://github.com/lupafarma/web.git
cd web
npm install
npm run dev
```

Abre `http://localhost:3000`.

Para construir la versión estática:

```bash
npm run build
```

El output va a `out/` y es desplegable a cualquier servicio de hosting estático.

---

## Estado del proyecto

**Versión actual:** v1 (en desarrollo)

Cobertura de datos en v1:
- ✅ 20.551 presentaciones del Nomenclátor de Facturación
- ✅ 74 medicamentos con PVL Referencia validado por BOE
- ⏳ ~14.000 medicamentos restantes pendientes de extracción completa del BOE Orden SND/1118/2025
- ⏳ PVL estimado vía fórmula RD 823/2008 para cobertura completa (validado a 0,5–1% del PVL BOE)

---

## Fuera de alcance para v1

Estas funcionalidades existirán en versiones futuras pero **no en v1**:

- Análisis automático de facturas en PDF (entrada manual línea a línea en v1)
- Histórico entre sesiones (Lupa no guarda nada localmente entre visitas)
- Comparación entre farmacias (esto pertenece a [PharmaOps](https://github.com/luisrdzcruz-maker/Pharmaops), un producto distinto)
- Integración con software de gestión de farmacia (Unycop, Nixfarma, Bitfarma, Farmatic)
- Seguimiento de rappel o descuentos comerciales (requiere datos privados subidos por el farmacéutico)

---

## Contribuir

Lupa es software libre bajo licencia MIT. Si quieres reportar un bug, sugerir mejoras o contribuir código:

- Abre un [issue](https://github.com/lupafarma/web/issues)
- Envía un [pull request](https://github.com/lupafarma/web/pulls)
- Lee el [código de conducta](CODE_OF_CONDUCT.md)
- Consulta la [política de seguridad](SECURITY.md) para reportar vulnerabilidades

---

## Licencia

[MIT](LICENSE) © 2026 Luis Rodriguez Cruz

---

## Aviso legal

Lupa es una herramienta de análisis. Los hallazgos son indicativos y se basan en datos públicos. Cualquier reclamación a un distribuidor debe verificarse contra las fuentes originales (BOE, Nomenclátor vigente, contratos comerciales). Los autores no se responsabilizan del uso que se haga de esta herramienta.
