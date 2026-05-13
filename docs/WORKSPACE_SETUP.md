# Lupa — Workspace Setup Guide

Decisions are locked. Follow these steps in order. Estimated time: **30-45 minutes** end-to-end.

---

## Decisions already made

| Decision | Value |
|---|---|
| Product name | Lupa |
| Brand / org | Lupafarma |
| Domain | `lupafarma.es` (registered) |
| GitHub org | `lupafarma` (created) |
| Repo name | `web` (final path: `github.com/lupafarma/web`) |
| License | MIT |
| Deploy target | Vercel free tier |
| Custom email at lupafarma.es | **Not now** (deferred upgrade) |

---

## Step 1 — Create the local folder

```bash
mkdir -p ~/dev/lupafarma-web
cd ~/dev/lupafarma-web
```

Keep this folder isolated. Don't nest it under your PharmaOps directory.

---

## Step 2 — Initialize git BEFORE Claude Code touches anything

```bash
git init
git branch -m main
```

This gives Claude Code a clean repo to work in from commit zero.

---

## Step 3 — Create the folder structure

```bash
mkdir -p docs reference data scripts
```

Target tree:
```
lupafarma-web/
├── CLAUDE.md
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── NEXT_STEPS.md
│   └── value-streams.pdf       (optional)
├── reference/
│   ├── lupa_demo.html
│   ├── check_invoice.py
│   ├── build_lupa_db.py
│   └── parse_boe.py
├── data/
│   ├── lupa_medication_db.json
│   └── nomenclator.csv         (optional, source file)
└── scripts/
    (Python scripts get copied here later)
```

---

## Step 4 — Drop in the files

From the `lupafarma-setup/` outputs folder of this session:

**Repository root** (drop into `~/dev/lupafarma-web/`):
- `CLAUDE.md` — Claude Code instructions
- `README.md` — Public-facing repo readme (Spanish)
- `LICENSE` — MIT license
- `.gitignore` — Standard Next.js ignores

**`docs/`** (from prior session):
- `NEXT_STEPS.md`

**`reference/`** (from prior session):
- `lupa_demo.html` — THE SPEC
- `check_invoice.py`
- `build_lupa_db.py`
- `parse_boe.py`

**`data/`** (from prior session):
- `lupa_medication_db.json` — 20,551 medications
- `nomenclator.csv` — optional source (the Sanidad CSV)

---

## Step 5 — Verify the seed

```bash
cd ~/dev/lupafarma-web
ls -la
ls -la reference/ data/ docs/
cat CLAUDE.md | head -20
```

You should see all the files in the right places. CLAUDE.md should start with "# Lupa — Context for Claude Code".

---

## Step 6 — First commit BEFORE Claude Code

```bash
cd ~/dev/lupafarma-web
git add .
git status     # eyeball the staged files
git commit -m "chore: seed reference materials and project context"
```

This means Claude Code's first commits will be additive to a clean baseline. Easier to review and roll back later.

---

## Step 7 — Create and push to GitHub

You already have the `lupafarma` org. Now create the repo:

**Option A — with `gh` CLI (faster):**
```bash
gh repo create lupafarma/web --public --source=. --remote=origin --description "Auditor de facturas farmacéuticas para farmacias españolas. Procesamiento 100% local."
git push -u origin main
```

**Option B — manual via GitHub web:**
1. Go to https://github.com/organizations/lupafarma/repositories/new
2. Repository name: `web`
3. Description: `Auditor de facturas farmacéuticas para farmacias españolas. Procesamiento 100% local.`
4. Public
5. **Do NOT initialize with README, .gitignore, or license** (you already have them)
6. Create repository
7. Then locally:
```bash
git remote add origin https://github.com/lupafarma/web.git
git push -u origin main
```

---

## Step 8 — Also set up the org profile (optional, 10 min)

While you're here, polish your org page. Create a special repo for the org README:

```bash
cd ~/dev
mkdir -p lupafarma-org-profile
cd lupafarma-org-profile
git init
mkdir profile
# Then create profile/README.md with the org profile content from this session's outputs
# Filename in the org must be exactly `.github` repo
```

Then create a repo named `.github` (yes, with the dot) under the `lupafarma` org and push. The `profile/README.md` will render at `github.com/lupafarma`.

If this is too fiddly right now, skip it — do it later. Not blocking.

---

## Step 9 — Deploy a "Coming Soon" placeholder TODAY

Before any code, plant the flag on `lupafarma.es`. This takes 10 minutes:

1. Take the file `coming-soon/index.html` from this session's outputs.
2. Drop it in a new empty folder: `mkdir ~/dev/lupafarma-placeholder && cp coming-soon/index.html ~/dev/lupafarma-placeholder/`
3. Deploy to Vercel:
   ```bash
   cd ~/dev/lupafarma-placeholder
   npx vercel
   ```
   Follow the prompts. Link to a new project named `lupafarma-placeholder`.

4. In Vercel dashboard, add custom domain `lupafarma.es`. Vercel will give you DNS records to add at your registrar.

5. At your domain registrar (where you bought lupafarma.es), add the DNS records Vercel showed you. Usually:
   - `A` record for `@` → `76.76.21.21` (Vercel's IP)
   - `CNAME` for `www` → `cname.vercel-dns.com`
   (Exact values are what Vercel tells you — use those.)

6. Wait for DNS to propagate (5 minutes to 24 hours, usually under 1 hour).

Now `lupafarma.es` shows "Coming soon" with a clean black-on-cream design that signals "this is serious." Pharmacists who hear about you and check the domain see legitimacy, not a 404.

When the real app deploys later (Claude Code Session 3), you'll **redeploy the same domain** to the real project. Vercel handles this seamlessly — no DNS changes needed, just point the new project at `lupafarma.es` in the dashboard and Vercel detaches the placeholder.

---

## Step 10 — Now launch Claude Code

Open Claude Code in `~/dev/lupafarma-web/`. Use the **Session 1 prompt** from `SESSION_PROMPTS.md`.

---

## Optional but recommended (do anytime in week 1)

- [ ] Verify WHOIS privacy is on for `lupafarma.es`
- [ ] Reserve `@lupafarma` on Twitter/X and LinkedIn page (15 min, prevents squatting)
- [ ] Add a `CODE_OF_CONDUCT.md` and `SECURITY.md` to the repo (do this in Session 10)

Not now:
- Custom email at `@lupafarma.es` — you said upgrade later
- Google Analytics / any analytics — hard rule, never
- Domain renewals — set a calendar reminder for ~11 months from registration

---

## What to watch for in Session 1

✅ **Good signs:**
- Claude Code references specific things from the demo (color values, the 5 detection types named correctly).
- It proposes static export (`output: 'export'`) without you prompting.
- Its questions are about specific decisions, not "what should we do."

🚩 **Red flags — if you see these, stop and re-anchor:**
- Suggests adding a backend "just for the database."
- Wants to use a CSS-in-JS library or a UI kit (Material UI, Chakra, etc.).
- Mentions "user accounts" or "authentication."
- Proposes telemetry "for product improvement."
- Wants to redesign the visual approach.

If any of these come up, respond: "Re-read CLAUDE.md, specifically the hard rules section. Then revise your proposal."

---

## After Session 1 succeeds

Move to Session 2 (scaffold) — see `SESSION_PROMPTS.md`.
