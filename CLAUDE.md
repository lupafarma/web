# Lupa — Context for Claude Code

You are helping build **Lupa**, a browser-local invoice auditor for Spanish pharmacies. Read this file first, every session.

---

## Identity

- **Product name (wordmark)**: Lupa
- **Brand / org**: Lupafarma
- **Domain**: https://lupafarma.es
- **GitHub**: https://github.com/lupafarma/web
- **License**: MIT
- **Author**: Luis Rodriguez Cruz

The displayed brand in the UI is just **Lupa** (clean, short, memorable). "Lupafarma" appears only in domain, organization, and corporate identity. Same pattern as Apple using "Apple" in product but `apple.com`.

---

## What Lupa is

A free, single-page web app where a Spanish pharmacist enters their distributor invoice (Cofares, Bidafarma, Hefame, Alliance, etc.) line by line, and Lupa flags:

1. Charges above the regulated **PVL Industrial de Referencia** (illegal per Art. 2.2 RD 177/2014).
2. Charges above derived expected PVL (suspicious — calculated via margin reversal from PVP+IVA).
3. Invoice arithmetic errors (quantity × unit price ≠ line total).
4. Branded medications charged when a cheaper generic exists in the same agrupación homogénea.
5. Invoice total mismatches.

Each finding is rendered in Spanish with the specific legal citation (BOE order, RD article).

---

## What Lupa is NOT

- **Not a backend.** No server, no API, no database in the cloud. Everything runs in the user's browser.
- **Not a SaaS.** No signup, no login, no email collection, no tier system.
- **Not analytics.** No Google Analytics, no Plausible, no Vercel Analytics, no telemetry of any kind. Not even an opt-in counter.
- **Not a PDF parser** (in v1). Manual line entry only. PDF.js drop-zone comes in v2.
- **Not cross-pharmacy comparison.** That's PharmaOps, a separate product. Lupa never talks to PharmaOps in v1.

---

## The differentiator

**Verifiable privacy.** A pharmacist can press F12, open the Network tab, drop in their full daily invoice book, and see zero outgoing requests. That's the entire trust mechanism. The whole architecture exists to support this claim.

This is also why the source code is open (MIT license, public repo). Obfuscation breaks the trust mechanism.

---

## Stack (non-negotiable)

- **Next.js (App Router) + TypeScript**
- **Static export** (`output: 'export'` in `next.config.js`). No server-side rendering. No API routes. No middleware. Anything that would force a backend request at runtime is forbidden.
- **Tailwind CSS** for styling.
- **Deploy to Vercel free tier** (static hosting only). Domain `lupafarma.es` to be connected.
- **No runtime fetch calls** to anything except the bundled medication database in `/public`. No external APIs.

Allowed dependencies: React, Next, Tailwind, TypeScript, plus any pure client-side utility library (e.g. `clsx`, `zod` for validation, `pdfjs-dist` when we add PDF parsing in v2).

Forbidden: anything that requires a server (NextAuth, Prisma, database clients, server actions), anything that phones home (Sentry, PostHog, GA), anything that requires API keys at runtime.

---

## What exists already in `/reference`

Read these before making decisions:

- **`lupa_demo.html`** — A working single-file prototype. **This is the visual and functional spec for v1.** Don't reinvent the UI; port it. The findings layout, the editable invoice grid, the typography choices, the color palette — all of that has been thought through. Match the demo's behavior exactly unless I tell you otherwise.
- **`check_invoice.py`** — The detection engine in Python. Port the five rules verbatim to TypeScript. Same constants (`PVL_TOLERANCE = 0.01`, `EST_TOLERANCE = 0.05`, etc.), same legal citations in the messages, same severity levels.
- **`build_lupa_db.py`** — The data pipeline that produced the medication database. This is a build-time script, not a runtime concern. Keep it in `/scripts/` in the Next.js project. Re-run monthly when the Nomenclátor refreshes and annually when BOE publishes the new order.
- **`parse_boe.py`** — Regex-based parser for the BOE Orden PDF text. Used by `build_lupa_db.py`. Also build-time.
- **`lupa_medication_db.json`** — Full database, 20,551 medications. Currently has 74 BOE-validated entries; the rest use derived PVL. This is the file to bundle in `/public`.

---

## Data sources (all public, all Spanish government)

| Source | Provides | Refresh |
|---|---|---|
| Nomenclátor de Facturación (Sanidad) | PVP+IVA, precio de referencia, menor precio de la agrupación homogénea, código de agrupación, principio activo, laboratorio | Monthly |
| BOE Orden SND/1118/2025 | PVL Industrial de Referencia (regulated wholesale maximum), conjuntos de referencia | Annually (October) |
| RD 823/2008 | Margin formulas: distribución 7.6%, dispensación 27.9% for PVL ≤ €91.63 | Stable |
| RD 177/2014 | Legal framework: Art. 2.2 (PVL Ref as max), Disposición adicional octava (agrupaciones) | Stable |

The derived PVL formula validates to within 0.5–1% of authoritative BOE PVL on every tested sample. This means full coverage of all 20,551 medications from day one, with BOE-validated entries as the higher-confidence subset.

---

## Hard rules — violate these and the product breaks

1. **Zero network requests after initial page load.** Fonts can be self-hosted or omitted. No CDN scripts. No tracking pixels. A pharmacist who opens F12 must see Network tab empty when they audit an invoice.
2. **No telemetry.** Not anonymous, not opt-in, not "just for product improvement." None.
3. **No accounts, no auth, no email collection.** Not even a newsletter signup.
4. **Spanish UI by default.** No language toggle in v1.
5. **Every finding cites its legal basis.** "Sobrecarga sobre PVL Referencia" must be followed by "Art. 2.2 RD 177/2014" or similar. Pharmacists need the citation to challenge their distributor.
6. **No external assets at runtime.** Self-host fonts, inline SVG icons, bundle the medication DB.
7. **Static export only.** If a feature can't ship as static HTML/CSS/JS, it doesn't ship.

---

## Out of scope for v1 (don't build these, even if asked)

- PDF parsing of invoices (v2 — uses pdf.js client-side)
- User accounts, sessions, history
- Saving invoices between sessions (no localStorage even — keep it stateless)
- Multi-language support
- Mobile app (responsive web is enough)
- Email reports
- Print-friendly view (v2)
- Cross-pharmacy benchmarking (this is PharmaOps territory)
- Commercial discount tracking (rappel) — requires private uploaded data
- Integration with pharmacy management systems (Unycop, Nixfarma, Bitfarma, Farmatic)
- Custom email at lupafarma.es (planned upgrade; not now)

---

## Project conventions

- **Push back once.** If you disagree with a request, say so clearly, give your reasoning, then execute as instructed. Don't re-argue.
- **Never use git worktrees** with Claude Code. Past experience: they cause more confusion than benefit.
- **Read `/reference/lupa_demo.html` before any UI decision.** It's the spec.
- **Read `/reference/check_invoice.py` before any detection logic decision.** It's the spec.
- **Spanish text is canonical.** All UI strings, all finding messages, all legal citations. Pull strings to a `messages.ts` so they're easy to audit.
- **Commit often** with focused commits. Conventional commit format (`feat:`, `fix:`, `chore:`, `docs:`).
- **No new dependencies without asking.** Justify each one.
- **No premature abstraction.** This is a simple app. Resist the urge to create a service layer, a state management library, or a custom hook for everything.
- **Spanish register: use `tú` (informal) consistently across all UI copy.** Modern Spanish web convention. Pharmacists are professionals but `tú` reads contemporary, not stuffy. Avoid `usted` unless quoting legal text (BOE references preserve formal Spanish since they're verbatim).

---

## Definition of done for v1

- [ ] Static Next.js app deploys to Vercel free tier, accessible at `lupafarma.es`
- [ ] Pharmacist enters invoice lines (CN, qty, unit price, line total) in an editable grid
- [ ] Database of 20,551 medications loaded from `/public/medications.json`
- [ ] All 5 detection rules from `check_invoice.py` produce findings
- [ ] Findings render in Spanish with severity color coding and legal citations
- [ ] F12 Network tab shows zero outgoing requests after initial page load
- [ ] Source code is public on GitHub (`lupafarma/web`) with MIT license
- [ ] README in Spanish explains what it does and how to use it
- [ ] Privacy badge on the page is verifiable
- [ ] Lighthouse score: 95+ on all metrics

---

## Definition of NOT done (don't claim victory until)

- Lighthouse Performance below 95
- Any third-party request fires after page load
- A real distributor invoice doesn't produce sensible findings
- The Spanish copy reads like a translation (have a native speaker review before launch)

---

## Background context (skim if needed)

The founder is Luis Rodriguez Cruz, a Spanish national in Finland building this from his home office. The longer-term play is PharmaOps (private SaaS, paid). Lupa is the free entry point — distribution via word-of-mouth among Spanish pharmacists. The goal: pharmacists try Lupa, see immediate value from public data alone, and become candidates for PharmaOps when they realize private data (their own historical pricing, commercial agreements, sales) unlocks more value.

Lupa needs to feel professional, trustworthy, and Spanish-native — not like a generic AI-generated tool. Pharmacists are conservative and detail-oriented. They will notice anything that looks "off."

---

**Before doing anything, confirm:** Have you read `/reference/lupa_demo.html` and `/reference/check_invoice.py`? If not, read them now.
