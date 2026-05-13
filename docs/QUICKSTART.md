# Lupa — Quick Start Cheat Sheet

Every command you need, in order. Copy-paste friendly.

---

## Prerequisites (one-time)

Verify these are installed on your machine:

```bash
node --version    # Need v20 or higher
npm --version     # Comes with Node
git --version
gh --version      # GitHub CLI, optional but recommended
npx --version
```

If `gh` is missing: install via `brew install gh` (Mac) or download from cli.github.com (Windows).
Then authenticate: `gh auth login`.

---

## Phase 1 — Manual setup (30 min)

### 1.1 Create folder and seed it

```bash
# Create the project folder
mkdir -p ~/dev/lupafarma-web
cd ~/dev/lupafarma-web

# Create subdirectories
mkdir -p docs reference data scripts

# Initialize git
git init
git branch -m main
```

### 1.2 Copy in the files from this session's outputs

Download all files from the `lupafarma-setup/` folder to your local machine, then:

```bash
# Repo root files
cp ~/Downloads/lupafarma-setup/CLAUDE.md .
cp ~/Downloads/lupafarma-setup/README.md .
cp ~/Downloads/lupafarma-setup/LICENSE .
cp ~/Downloads/lupafarma-setup/.gitignore .
cp ~/Downloads/lupafarma-setup/CODE_OF_CONDUCT.md .
cp ~/Downloads/lupafarma-setup/SECURITY.md .

# Reference materials (from earlier session)
cp ~/Downloads/lupa_demo.html reference/
cp ~/Downloads/check_invoice.py reference/
cp ~/Downloads/build_lupa_db.py reference/
cp ~/Downloads/parse_boe.py reference/

# Data (from earlier session)
cp ~/Downloads/lupa_medication_db.json data/

# Docs (from earlier session)
cp ~/Downloads/NEXT_STEPS.md docs/
```

Adjust paths if your downloads folder differs.

### 1.3 Verify

```bash
ls -la
ls reference/ data/ docs/
head -20 CLAUDE.md
```

You should see all expected files. CLAUDE.md should begin with "# Lupa — Context for Claude Code".

### 1.4 First commit

```bash
git add .
git status     # Eyeball the staged files
git commit -m "chore: seed reference materials and project context"
```

### 1.5 Create remote repo

```bash
gh repo create lupafarma/web --public --source=. --remote=origin \
  --description "Auditor de facturas farmacéuticas para farmacias españolas. Procesamiento 100% local."
git push -u origin main
```

If `gh` not installed, do it manually on GitHub then:
```bash
git remote add origin https://github.com/lupafarma/web.git
git push -u origin main
```

---

## Phase 2 — Deploy placeholder to lupafarma.es (15 min)

### 2.1 Set up placeholder folder

```bash
mkdir -p ~/dev/lupafarma-placeholder
cp ~/Downloads/lupafarma-setup/coming-soon/index.html ~/dev/lupafarma-placeholder/
cd ~/dev/lupafarma-placeholder
```

### 2.2 Deploy with Vercel

```bash
npx vercel
```

Follow prompts:
- Set up and deploy? **Y**
- Which scope? **Your personal account**
- Link to existing project? **N**
- Project name? **lupafarma-placeholder**
- In which directory is your code? **./** (current)
- Want to override settings? **N**

Vercel deploys it and gives you a URL. Test it:
```bash
open https://lupafarma-placeholder.vercel.app
```

### 2.3 Attach lupafarma.es to Vercel

1. Open https://vercel.com/dashboard
2. Click on `lupafarma-placeholder` project
3. Settings → Domains → Add → enter `lupafarma.es`
4. Also add `www.lupafarma.es` and set it to redirect to `lupafarma.es`
5. Vercel shows you DNS records needed at your registrar

### 2.4 Add DNS records at your domain registrar

At wherever you bought lupafarma.es, find DNS settings and add what Vercel showed you. Typically:

| Type | Name | Value |
|---|---|---|
| A | @ | 76.76.21.21 |
| CNAME | www | cname.vercel-dns.com |

(Use the exact values Vercel told you, not these — they may differ.)

### 2.5 Wait and verify

DNS propagation takes 5 minutes to 24 hours (usually under 1 hour for `.es`).

Test:
```bash
dig lupafarma.es
curl -I https://lupafarma.es
```

When `https://lupafarma.es` shows the "Lupa coming soon" page in your browser, you're done.

---

## Phase 3 — Launch Claude Code (now)

```bash
cd ~/dev/lupafarma-web
# Launch Claude Code in this directory (using whatever launcher you prefer)
```

Then paste the **Session 1 prompt** from `SESSION_PROMPTS.md`. Don't paraphrase — paste it verbatim.

---

## Phase 4 — After Session 3 (Lupa app deployed)

When Claude Code Session 3 succeeds and the Next.js scaffold is deployed:

1. Open Vercel dashboard
2. Go to `lupafarma-placeholder` project → Settings → Domains
3. Remove `lupafarma.es` from this project
4. Go to `lupafarma-web` project → Settings → Domains  
5. Add `lupafarma.es` here
6. Confirm DNS is correct (it doesn't change)

Now `lupafarma.es` shows the real Next.js scaffold. The placeholder still exists at `lupafarma-placeholder.vercel.app` (can be deleted from Vercel dashboard later, or kept as a backup).

---

## Phase 5 — Org profile (optional, 10 min)

Make `github.com/lupafarma` look polished:

```bash
mkdir -p ~/dev/lupafarma-org-profile/profile
cp ~/Downloads/lupafarma-setup/org-profile-README.md ~/dev/lupafarma-org-profile/profile/README.md
cd ~/dev/lupafarma-org-profile
git init
git branch -m main
git add .
git commit -m "feat: org profile readme"

# Create the special .github repo
gh repo create lupafarma/.github --public --source=. --remote=origin
git push -u origin main
```

Wait 30 seconds, then visit https://github.com/lupafarma. You'll see the polished org page.

---

## Troubleshooting

**"DNS not propagating after 1 hour"** — Wait. Spanish `.es` DNS can take up to 24 hours in extreme cases. Run `dig lupafarma.es @1.1.1.1` to check from Cloudflare's resolver if your ISP is being slow.

**"Vercel deploy fails"** — Make sure you're in the right directory. `pwd` should match what you expect. Run `vercel --debug` for more info.

**"git push fails: repository not found"** — The `gh repo create` may have failed silently. Check at https://github.com/lupafarma. If repo doesn't exist, recreate manually via web UI.

**"Permission denied (publickey)"** — Set up SSH key with GitHub, or use HTTPS instead: change remote with `git remote set-url origin https://github.com/lupafarma/web.git`

**"Coming soon page shows but no fonts"** — Expected. The page uses only system fonts (no Google Fonts requests, by design). Looks slightly different on different OSes. This is the right behavior.

---

## What success looks like at end of Phase 2

- ✅ `https://lupafarma.es` shows the "Lupa coming soon" page
- ✅ F12 → Network tab on that page shows ONLY a request to `lupafarma.es` itself. No Google Fonts, no analytics, nothing else.
- ✅ `https://github.com/lupafarma/web` is the public repo with all reference materials seeded
- ✅ Local `~/dev/lupafarma-web/` is ready for Claude Code

After this you can start Claude Code Session 1 with confidence.
