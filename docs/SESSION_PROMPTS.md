# Lupa — Claude Code Session Prompts

Use these prompts in order. Don't skip sessions. Don't combine sessions.

Each session should produce ONE focused outcome, get committed, then you stop and review before next session.

---

## SESSION 1 — Context absorption (no code)

**Goal:** Confirm Claude Code understands the project before writing anything.

**Prompt:**

> Read `CLAUDE.md` first. Then read `reference/lupa_demo.html` completely (the entire file, including all the CSS and JavaScript). Then read `reference/check_invoice.py`.
>
> After reading, do NOT write any code. Instead, respond with:
>
> 1. A summary of what you understand Lupa to be (3-5 sentences max).
> 2. The five detection rules, named, in your own words.
> 3. The file structure you propose for the Next.js project — directory tree only, no code.
> 4. Three specific questions you have before scaffolding. Wait for my answers.
>
> Don't propose changes to the demo's UI approach. Don't suggest "improvements" to the detection logic. Don't add features beyond what the demo shows. The demo is the spec.

**You answer Claude Code's three questions.** Then commit nothing (no code yet). Move to Session 2.

---

## SESSION 2 — Scaffold

**Goal:** A working empty Next.js app that builds.

**Prompt:**

> Scaffold the Next.js project per your proposed structure. Use:
>
> - Next.js latest stable with App Router
> - TypeScript strict mode
> - Tailwind CSS
> - `output: 'export'` configured in `next.config.js`
> - `.gitignore` for Node, Next, and IDE files (extend the existing one, don't replace)
> - No other dependencies yet
>
> Create a placeholder home page (`app/page.tsx`) that just renders "Lupa — en desarrollo" so we can verify the build works.
>
> After scaffolding:
> 1. Run `npm install`
> 2. Run `npm run build` and confirm it succeeds with static export
> 3. Commit with message `chore: scaffold Next.js project with static export`
>
> Stop after the commit. Don't start porting the demo yet.

**You verify:** `npm run dev` works locally. The build produced static files in `out/`. Commit is clean.

---

## SESSION 3 — Deploy to lupafarma.es

**Goal:** Replace the "coming soon" placeholder at `lupafarma.es` with the (still-placeholder) Next.js scaffold. Proves the deploy pipeline.

**Prompt:**

> Set up Vercel deployment for static export. Specifically:
>
> 1. Confirm `next.config.js` has `output: 'export'` so Vercel serves it as static.
> 2. Add a `vercel.json` if needed for cleanest static hosting.
> 3. Walk me through the Vercel CLI setup commands I need to run locally to (a) link this repo to a new Vercel project named `lupafarma-web`, and (b) transfer the `lupafarma.es` custom domain from the placeholder project to this one. Don't run the commands yourself — I have to authenticate.
> 4. Commit any config changes with message `chore: configure for vercel static deployment`.
>
> Constraints:
> - The domain `lupafarma.es` is currently attached to a placeholder Vercel project. We need to move the domain to this new project. In Vercel dashboard: remove the domain from placeholder project, then add it to `lupafarma-web` project. DNS records don't change.
> - Do NOT add Vercel Analytics. Do NOT add Speed Insights. Do NOT add any telemetry. Re-read CLAUDE.md hard rule #2 if you're tempted.

**You do:** Run `npx vercel` locally, link to project, deploy to production. In Vercel dashboard, move `lupafarma.es` from the placeholder project to the new `lupafarma-web` project.

**Acceptance:** The Next.js scaffold is live at `https://lupafarma.es`. Press F12 → Network tab. Reload. Confirm only the static assets load (no analytics, no telemetry, no third-party fonts).

---

## SESSION 4 — Port the medication database

**Goal:** The 20,551-medication database is bundled and loadable.

**Prompt:**

> The medication database is in `data/lupa_medication_db.json` (20,551 records, ~12 MB uncompressed).
>
> Tasks:
>
> 1. Move it to `public/medications.json` so it's served as a static asset.
> 2. Create `lib/medications.ts` that:
>    - Defines a TypeScript type `Medication` matching the JSON schema (look at one record to derive the shape — don't invent fields)
>    - Exports `loadMedications(): Promise<Map<string, Medication>>` that fetches `/medications.json` once, caches the result in a module-level variable, and returns a Map keyed by `cn`
> 3. Add a temporary test in `app/page.tsx`: load the DB on mount, display the count (`Cargadas 20.551 presentaciones`). Use `useEffect` and `useState`.
> 4. Run `npm run build` to confirm the static export still works with the JSON in `public/`.
> 5. Commit: `feat: bundle medication database with typed loader`
>
> Constraints:
> - The JSON must be loaded with `fetch('/medications.json')` not imported. We do not want it bundled into the JS chunk — it should be a separate file that the browser caches independently.
> - No external state management library. `useState` is fine for v1.

**You verify:** The page loads, displays the count, network tab shows exactly one request for `medications.json` after the initial page load (cached on reload).

---

## SESSION 5 — Port detection rules to TypeScript

**Goal:** The 5 detection rules from `check_invoice.py` work in TypeScript, with unit tests.

**Prompt:**

> Port the detection engine from `reference/check_invoice.py` to TypeScript.
>
> Create `lib/detection.ts` with:
>
> 1. Types: `InvoiceLine`, `Finding`, `Severity` (`'high' | 'medium' | 'low' | 'info'`)
> 2. Constants: `PHARM_MARGIN`, `DIST_MARGIN`, `IVA_REIMB`, `PVL_TOLERANCE`, `EST_TOLERANCE` — use the exact values from `check_invoice.py`
> 3. Function `derivePVL(pvpiva: number): number` — same formula as Python
> 4. Function `findCheaperAlternative(med, db)` — same logic
> 5. Function `checkInvoice(lines: InvoiceLine[], db: Map<string, Medication>): Finding[]` — same five rules
>
> The Spanish-language finding messages must be character-for-character identical to the Python version. Same legal citations. Same severity assignments.
>
> Add unit tests in `lib/detection.test.ts` using `vitest`:
> - Math error detection: 2 × 34.00 = 68 but total says 72 → finding with impact €4.00
> - PVL violation: ALPRAZOLAM unit €3.50 vs PVL Ref €3.10 → finding with positive impact
> - Clean line: ATORVASTATINA at PVL Ref €2.31 → no finding
> - Cheaper alternative detection
> - Unknown CN → info finding
>
> Install vitest if needed: `npm install -D vitest`.
>
> Don't wire this to the UI yet. Just lib + tests.
>
> Commit: `feat: port 5-rule detection engine with tests`

**You verify:** `npm test` passes. Tests are not trivially passing — they actually verify finding messages and impacts.

---

## SESSION 6 — Build the invoice grid

**Goal:** The editable invoice table from the demo, in React/TypeScript.

**Prompt:**

> Read `reference/lupa_demo.html` again, specifically the invoice grid section.
>
> Build the invoice grid as a React component in `components/InvoiceGrid.tsx`. Match the demo's:
> - Column layout (CN | Producto | Cant. | P. unit. | Total | ×)
> - Editable inputs that update on every keystroke
> - The subtotal at the bottom
> - The "+ Añadir línea" button
> - The × button to remove a row
> - Header row visual style
> - Mono font for numbers (use Tailwind `font-mono`)
>
> Use Tailwind for all styling. Don't use the demo's CSS variables directly — translate them to Tailwind config in `tailwind.config.ts`. Match colors exactly.
>
> Wire it to a parent component in `app/page.tsx` that:
> - Loads the medication DB on mount
> - Initializes with the 8 sample invoice lines from the demo (DEPAKINE, ATORVASTATINA, etc.)
> - Passes lines + DB to InvoiceGrid
> - Receives line updates back via callback
>
> Don't render findings yet. That's the next session.
>
> Commit: `feat: editable invoice grid with sample data`

**You verify:** You can type in cells, add rows, remove rows. The subtotal updates. Looks visually like the demo.

---

## SESSION 7 — Render findings

**Goal:** Findings panel from the demo, wired to the detection engine.

**Prompt:**

> Read the findings panel section of `reference/lupa_demo.html` again.
>
> Build `components/FindingsPanel.tsx`. It receives `findings: Finding[]` as a prop and renders:
> - The summary bar at top (lines analyzed, total potential impact)
> - The findings list sorted by severity (high → medium → low → info)
> - Each finding card matches the demo's visual style (colored left border by severity, title, body with line reference badge, impact amount in mono, legal citation in italic)
> - Empty state: green "No se han detectado anomalías en esta factura." panel
>
> Wire it to `app/page.tsx`: whenever invoice lines change, call `checkInvoice()` and pass the result to FindingsPanel.
>
> Performance: detection should run synchronously on every keystroke. With 8 lines and 20,551 medications in a Map, this is fast — don't add debouncing unless profiling shows it's needed.
>
> Also: highlight flagged rows in the invoice grid. Pass the findings array to InvoiceGrid so it can apply the warning/info background to rows with high/medium-severity findings on that line index.
>
> Commit: `feat: findings panel with severity routing and row highlighting`

**You verify:** The 8 sample lines produce exactly the findings predicted in the demo: DEPAKINE overcharge, ACICLOVIR math error, ALPRAZOLAM overcharge, plus generic suggestions. Edit a cell — findings update instantly.

---

## SESSION 8 — Header, footer, polish

**Goal:** The header (brand + privacy badge + intro) and footer (sources) from the demo.

**Prompt:**

> Read the header and footer sections of `reference/lupa_demo.html`.
>
> Build:
> - `components/Header.tsx` — brand mark ("Lupa"), tagline, privacy badge, intro paragraph
> - `components/Footer.tsx` — sources with links to BOE / RD references
>
> Typography: use Fraunces (display, italic for the "Lupa" wordmark) and IBM Plex Sans (body) and IBM Plex Mono (numbers). Self-host these via `next/font/google` so they're served from your own domain, not Google's CDN — this preserves the zero-third-party-request property.
>
> Verify in F12 Network tab after this change: NO requests to fonts.googleapis.com or fonts.gstatic.com after page load. The fonts must be inlined or served from your origin.
>
> Wire Header and Footer into `app/page.tsx` layout. Match the demo's spacing exactly.
>
> Commit: `feat: header, footer, self-hosted typography`

**You verify:** Page looks like the demo. F12 Network tab is clean. Lighthouse score still 95+.

---

## SESSION 9 — Spanish copy review

**Goal:** Every visible string is in idiomatic Spanish, not translation-y Spanish.

**Prompt:**

> Extract all visible Spanish text strings to `lib/messages.ts` as a constants module. This includes:
> - UI labels (button text, column headers, placeholders)
> - Finding messages (currently in `lib/detection.ts`)
> - Header/footer text
> - Empty state messages
>
> Don't add i18n machinery — just centralize the strings so I can review and edit them in one file.
>
> Replace inline strings with imports from `messages.ts`.
>
> Commit: `refactor: centralize Spanish strings for review`
>
> After commit, output the full contents of `messages.ts` so I can review it.

**You do:** Read every string. Edit anything that sounds translated. Get a native Spanish speaker to review if you can. Pharmacists will notice awkward phrasing.

---

## SESSION 10 — Pre-launch checklist

**Goal:** Ship-ready v1.

**Prompt:**

> We're preparing v1 launch at lupafarma.es. Run this checklist and fix anything that fails:
>
> 1. `npm run build` — succeeds, output goes to `out/`
> 2. `npm test` — all tests pass
> 3. Lighthouse — run against the production build (`npm run build && npx serve out`) and report scores
> 4. F12 Network tab after page load — list every request fired. Should be zero after `medications.json` and the initial static assets.
> 5. Spanish strings — confirm no English placeholders left over
> 6. Update `README.md` — keep it Spanish, add a working "live demo" link to https://lupafarma.es and a screenshot. Brief English `README.en.md` for international developers.
> 7. Confirm LICENSE — MIT, year 2026, author "Luis Rodriguez Cruz" (already added at setup)
> 8. Meta tags in `app/layout.tsx` — Spanish title (`Lupa — Auditor de facturas farmacéuticas`), Spanish description, canonical URL `https://lupafarma.es`, OG tags
> 9. Favicon — generate a simple one (magnifying glass icon, or stylized "L" wordmark). SVG preferred, with PNG fallbacks for older browsers.
> 10. `robots.txt` and `sitemap.xml` — basic versions, allow all crawling
> 11. Add `CODE_OF_CONDUCT.md` and `SECURITY.md` to the repo root
>
> Report any failures. Do NOT add features. Only fix what's broken.
>
> Commit: `chore: pre-launch polish and documentation`

**You verify:** All checks pass. Deploy to production. Test on mobile. Have one pharmacist friend (if available) try it.

---

## SESSION 11+ — After launch

Don't plan these in advance. After launch, the priorities depend on what real pharmacists tell you. Possible next sessions:

- **Full BOE PDF extraction** — upgrade from 74 to ~14,000 BOE-validated entries. About 1-2 days work. Can be done by Cowork in parallel.
- **PDF drop-zone for invoices** — pdf.js based, distributor-specific parsers. 2-3 days.
- **Print-friendly view** — for pharmacists to share findings with their distributor.
- **Localization to PT (for Portuguese pharmacies)** — much later.

Do NOT promise these to users in advance. Ship v1, get feedback, then decide.

---

## Universal session-ending checklist

Every session ends with:

1. Working code (no broken tests, no failed builds)
2. A single focused commit
3. You verifying the change manually
4. Stopping. Closing Claude Code. Doing something else for at least 30 minutes before the next session.

The 30-minute break is important. It separates building from reviewing.

---

## When things go wrong

If Claude Code does something you didn't ask for, **immediately:**

1. `git diff` to see what changed
2. Tell Claude Code: "Revert that change. Re-read CLAUDE.md hard rule #X. Then propose what to do without making changes."
3. If the agent insists, `git reset --hard HEAD` and start the session over

Don't let Claude Code "fix it" by adding more changes. Reset and re-prompt. Cheaper than untangling.

---

## Time estimate

If everything goes smoothly, sessions 1-10 take about **15-20 working hours total** spread over 1-2 weeks. Some sessions are 30 minutes (Session 3 deploy), some are 2-3 hours (Session 6 invoice grid).

Don't try to do this in a weekend. Each session needs review time. Each commit needs to be solid before the next one.

---

## When you're stuck

If a session goes sideways and you don't know how to recover:

1. Stop the session.
2. Don't make more changes.
3. Open a new conversation with me (Claude). Share: the current state of the repo (`git log --oneline -20`), the session prompt that failed, what Claude Code produced.
4. I'll help you diagnose and either roll back or course-correct.
