# ಟೆಕ್ ವಾರ್ತೆ — Setup Guide
## Kannada Tech News Portal — Complete Setup

---

## What's included

```
kannada-tech-news/
├── bot/
│   ├── bot.py              ← Python bot (scrapes + translates + posts)
│   └── requirements.txt    ← Python dependencies
├── site/
│   └── index.html          ← Your complete website (single file!)
├── docs/
│   └── supabase_schema.sql ← Database schema
├── .github/
│   └── workflows/
│       └── news-bot.yml    ← GitHub Actions (runs 5x daily, free)
└── .env.example            ← Environment variables template
```

---

## Step 1: Supabase (Database) — 15 minutes

1. Go to **https://supabase.com** → Create free account
2. Click "New Project" → name it `kannada-tech-news`
3. Once created, go to **SQL Editor** → paste contents of `docs/supabase_schema.sql` → Run
4. Go to **Project Settings → API** → copy:
   - `Project URL` → your `SUPABASE_URL`
   - `anon public` key → your `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `service_role` key → your `SUPABASE_SERVICE_KEY` (keep secret!)

---

## Step 2: Anthropic API Key — 5 minutes

1. Go to **https://console.anthropic.com** → Sign up / Log in
2. Go to **Settings → API Keys** → Create new key
3. Copy the key (starts with `sk-ant-...`)

---

## Step 3: GitHub (Bot + Automation) — 10 minutes

1. Create a new GitHub repo: `kannada-tech-news`
2. Push this entire folder to it
3. Go to **Settings → Secrets and Variables → Actions** → Add these secrets:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `ANTHROPIC_API_KEY`
4. The bot will now run automatically 5x daily (7am, 10am, 1pm, 4pm, 7pm IST)
5. To test manually: go to **Actions** tab → **Kannada Tech News Bot** → **Run workflow**

---

## Step 4: Website Deployment — 10 minutes

**Option A: Vercel (Recommended — Free)**
1. Go to **https://vercel.com** → Connect your GitHub repo
2. It will auto-deploy on every push
3. Go to Vercel project settings → Environment Variables → add:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Option B: Netlify (Also Free)**
1. Go to **https://netlify.com** → Import from GitHub
2. Build command: leave empty (static HTML)
3. Publish directory: `site/`

**Option C: GitHub Pages (Completely Free)**
1. Go to repo Settings → Pages
2. Source: Deploy from branch → main → `/site` folder
3. Your site will be at `https://yourusername.github.io/kannada-tech-news`

---

## Step 5: Update Website with Your Supabase Keys

Open `site/index.html` and replace line ~340:
```javascript
const SUPABASE_URL = 'https://YOUR_PROJECT.supabase.co'
const SUPABASE_ANON_KEY = 'YOUR_ANON_KEY'
```
with your actual values from Step 1.

---

## Monthly Cost Estimate

| Service        | Cost          |
|----------------|---------------|
| Supabase       | Free (500MB)  |
| Vercel hosting | Free          |
| GitHub Actions | Free          |
| Anthropic API  | ~₹300-500/mo  |
| **Total**      | **~₹300-500** |

---

## Customization

**Change site name:** Search for `ಟೆಕ್ ವಾರ್ತೆ` in `index.html` and replace

**Add more RSS feeds:** Edit the `RSS_FEEDS` list in `bot/bot.py`

**Post more/less per day:** Change `ARTICLES_PER_RUN` in `bot/bot.py`

**Change posting times:** Edit cron schedule in `.github/workflows/news-bot.yml`
(Remember: GitHub Actions uses UTC, IST = UTC+5:30)

**Add Google Analytics:** Add your GA4 script tag inside `<head>` in `index.html`

---

## Domain Name (Optional)

1. Buy a `.com` or `.in` domain (₹800-1200/year on GoDaddy, Namecheap)
2. Go to Vercel → Settings → Domains → Add your domain
3. Done!

Suggested names: `tekvarte.com`, `kannadatech.in`, `techwarte.in`
