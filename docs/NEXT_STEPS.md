# Lupa - Data Foundation Complete: Next Steps

**Date**: May 13, 2026  
**Status**: Data model validated. Ready to build frontend.

---

## What we have now

Three working scripts plus a 20,551-medication database, all in the `lupa-data` folder:

### `build_lupa_db.py` — the data pipeline
Loads the Facturación CSV, joins with BOE PVL Referencia data, computes derived PVL via the RD 823/2008 margin formula, and produces `lupa_medication_db.json` — the file the browser app loads. 

Currently includes a **sample of 74 medications from BOE** (covering most common conjuntos: paracetamol equivalents, atorvastatina, alprazolam, amlodipino, amoxicilina, depakine, etc.). The Facturación side covers all 20,551 medications. To get full coverage, the BOE PDF extraction needs to be expanded to all 1,187 pages — see "remaining work" below.

### `check_invoice.py` — the detection engine
Takes a parsed invoice and runs five detection categories:
1. Invoice arithmetic errors (qty × unit ≠ line total)
2. Charges above PVL Referencia (illegal per Art. 2.2 RD 177/2014)
3. Charges above derived PVL (suspicious)
4. Branded medication when cheaper generic exists in same agrupación
5. Invoice-level total mismatches

Output is Spanish-language with explicit legal citations — exactly what a pharmacist needs to challenge a distributor.

### `lupa_medication_db.json` — the database
20,551 records, one per CN code. Each record has:
- Identity: CN, name, principio activo, laboratorio
- Status: estado (ALTA/BAJA), aportación, tipo fármaco
- Prices: PVP+IVA, precio referencia, menor precio agrupación, PVL Ref (BOE), PVL estimated (derived)
- Cross-references: agrupación code, conjunto code

This is the file Lupa loads in the browser — about 5-10 MB compressed.

---

## Critical validation result

The derived PVL formula (RD 823/2008 reverse calculation) matches the authoritative BOE PVL within **0.5-1% error** across every sample tested:

| Medication | BOE PVL | Derived PVL | Error |
|---|---|---|---|
| DEPAKINE 500mg 100c | €7.72 | €7.76 | €0.04 |
| ACICLOVIR MABO 800mg | €33.92 | €34.12 | €0.20 |
| RISEDRONATO SEMANAL | €12.71 | €12.78 | €0.07 |
| AMLODIPINO SANDOZ 10mg | €1.60 | €1.61 | €0.01 |
| ATORVASTATINA CINFA 10mg | €2.31 | €2.33 | €0.02 |

This means: even for medications not yet extracted from BOE, Lupa can derive a defensible expected PVL from PVP+IVA. So we have **full coverage of the 20,551-medication catalog from day one**, with the BOE PVL Ref upgrading specific records as they're extracted.

---

## Data model

### Core: `medication` (one per CN)
```
cn_code                     string (10-digit, primary key)
nombre                      string
principio_activo            string + reference to dictionary
laboratorio                 string + reference to dictionary
forma_farmaceutica          string
via_administracion          string
tipo_farmaco                enum (Etica / Generico / Homeopatico / etc.)
aportacion                  enum (NORMAL / ESPECIAL / SIN_APORTACION)
estado                      enum (ALTA / BAJA / SUSPENDIDO / etc.)
atc_code                    string + descripcion
sw_generico                 bool
sw_envase_clinico           bool
sw_uso_hospitalario         bool
sw_huerfano                 bool
```

### Prices: `prices` (per CN per effective period)
```
cn_code                     string
effective_from              date
effective_to                date (nullable)
pvl_referencia_boe          decimal      <- from BOE annual order
pvl_estimated               decimal      <- derived from PVP+IVA via margins
pvp_iva                     decimal      <- from monthly Facturación
precio_referencia           decimal
menor_precio_agrupacion     decimal
deduccion_rdl_8_2010        decimal      <- 0/4/7.5/15% from BIFIMED
iva_rate                    decimal      <- 0.04, 0.10, 0.21
source_boe_order            string       <- e.g. "SND/1118/2025"
```

### Reference tables
- `agrupacion_homogenea` (code, name, precio_menor, effective_from/to)
- `conjunto_referencia` (code, name, precio_referencia, effective_from/to)
- `laboratorio` (code, name)
- `principio_activo` (code, name)
- `atc` (code, descripcion)

For Lupa v1, all the above is denormalized into a single flat JSON keyed by CN. PharmaOps later can normalize this into a proper relational schema.

---

## Remaining work — week by week

### Week 1: Complete data foundation
**1.1** Download the BOE PDF locally on your machine:
```bash
curl -o boe_2025.pdf "https://www.boe.es/boe/dias/2025/10/13/pdfs/BOE-A-2025-20356.pdf"
curl -o boe_2025_errata.pdf "https://www.boe.es/boe/dias/2025/10/31/pdfs/BOE-A-2025-21925.pdf"
```

**1.2** Install pdfplumber and extract all anexos. The PDF structure is consistent: column 1 = conjunto code, column 2 = principio activo + via, column 3 = CN, column 4 = product name, column 5 = PVL Ref, column 6 = PVP+IVA Ref. Use the regex pattern in `parse_boe.py` as a starting point.

**1.3** Run the full extraction. Expected output: ~14,000 rows for Anexo 1 (community pharmacy), ~4,000 for Anexo 2 (hospital), ~500 for Anexo 5 (innovaciones galénicas), ~1,000 for Anexo 6 (sin conjunto), ~200 for Anexo 7 (new).

**1.4** Apply the errata PDF on top of the main extraction.

**1.5** Re-run `build_lupa_db.py` with the full BOE data. Now every medication in a conjunto has its real PVLRef.

**Time estimate: 2-3 days.**

### Week 2-3: Frontend
**2.1** Set up Next.js project in a new repo (separate from PharmaOps): `lupa-web`. Domain not yet chosen — consider `lupa.es`, `lupafarma.es`, `lupafactura.es`.

**2.2** Build the page structure:
- Drop zone for invoice PDF
- Bundle the medication DB as a JSON file in `/public/`
- Use `pdfjs-dist` for in-browser PDF parsing
- Use regex / heuristics to extract CN, qty, unit_price, line_total from invoice lines
- Run the detection logic from `check_invoice.py` ported to TypeScript
- Render results as a list of findings with Spanish legal citations

**2.3** Privacy proof: ensure zero network requests after page load. Open dev tools → Network tab → show pharmacist there are no outgoing calls. This is the verifiable privacy claim that distinguishes Lupa from any cloud-based alternative.

**2.4** No analytics, no auth, no backend. Lupa v1 is purely browser-local.

**Time estimate: 5-7 days.**

### Week 4: Cold outreach
**3.1** Compile a list of 30-50 pharmacies in regions where you have any connection (Andalucía, Madrid, Cataluña). Look up their public NIF and ownership.

**3.2** Write a short cold outreach message — emphasize:
- It's free
- All data stays on their device (verifiable)
- They can try it on one invoice and see results in 60 seconds
- No signup required

**3.3** Track responses. Goal: 10 pharmacists actually try it.

**3.4** Schedule 30-min calls with the 3-5 who respond most positively. Ask what they wish it did. This is your validation phase.

---

## What we won't have on day one

- **Hospital/Mutua-specific deductions (deducción RDL 8/2010)** at 4%, 7.5%, 15% — these are in BIFIMED but not in Facturación. Adding requires a separate BIFIMED scrape or Excel export.
- **Commercial discount tracking (rappel)** — requires the pharmacy to upload their commercial agreement with the distributor. v1 only catches what's legally regulated.
- **Cross-pharmacy benchmarking** — requires the data network effect (need 30+ contributing pharmacies). This is the Tier 1 moat for PharmaOps, but Lupa v1 can't have it.
- **PMS integration (Unycop/Nixfarma/Bitfarma/Farmatic)** — these are private APIs. Out of scope for v1.

---

## What this proves to a pharmacist

When you sit down with a pharmacist for the first time, the demo is:

1. They give you a real invoice PDF.
2. You drop it in Lupa.
3. In 60 seconds it produces a Spanish-language audit report citing BOE Orden SND/1118/2025 with specific euro impact.
4. Even if Lupa finds €0 on this particular invoice (which can happen if the distributor is clean), the pharmacist now knows:
   - There's a free, private tool to audit their invoices
   - The author understands their world (regulated PVL, RD 177/2014, conjuntos vs agrupaciones)
   - More value comes when they share data (PharmaOps).

This is the pitch:

> **"The public data already finds money. Sharing your data finds much more, and lets you compare against other pharmacies. Lupa is free forever. PharmaOps unlocks the comparison network."**

---

## Files in `/home/claude/lupa-data/`

| File | Purpose |
|---|---|
| `build_lupa_db.py` | Data pipeline (Facturación + BOE → unified JSON) |
| `check_invoice.py` | Invoice detection engine |
| `parse_boe.py` | BOE PDF text → CSV/JSON parser (for full extraction) |
| `lupa_medication_db.json` | 20,551-medication database |
| `lupa_data_summary.txt` | Auto-generated summary of the DB |

