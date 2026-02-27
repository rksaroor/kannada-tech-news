# ಟೆಕ್ ವಾರ್ತೆ — Quick Start Guide
## Kannada Tech News Portal — Launch in 30 Minutes

---

## What You're Getting

A fully automated Kannada tech news website that:
- **Scrapes** the latest tech news from TechCrunch, Wired, The Verge, Ars Technica, NYT Tech
- **Translates** every article to natural Kannada using Claude AI
- **Publishes** automatically 5× per day to your website
- **Categorizes** articles (AI, Smartphones, Startups, Cybersecurity, Space, Gaming, EVs, Social Media)

**Cost: ~₹300–500/month** (Anthropic API only — everything else is free)

---

## Step 1 — Supabase Database (15 mins)

1. Go to **https://supabase.com** → Create free account → New Project
2. Name it `kannada-tech-news` → Set a strong database password → Create
3. Once the project is ready, go to **SQL Editor** (left sidebar)
4. Paste the entire contents of `docs/supabase_schema.sql` → Click **Run**
5. Go to **Project Settings → API** and copy:
   - **Project URL** → save this as `SUPABASE_URL`
   - **anon / public** key → save this as `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **service_role** key → save this as `SUPABASE_SERVICE_KEY` *(keep this secret!)*

---

## Step 2 — Anthropic API Key (5 mins)

1. Go to **https://console.anthropic.com** → Sign up / Log in
2. Go to **Settings → API Keys** → Click **Create Key**
3. Name it `kannada-tech-news-bot`
4. Copy the key (starts with `sk-ant-...`) → save this as `ANTHROPIC_API_KEY`

> **Cost estimate:** The bot runs 5×/day, processing 5 articles each run = 25 articles/day.
> Translation costs ~$0.002 per article = ~$0.05/day = ~₹4/day = ~₹120/month.

---

## Step 3 — GitHub Repository + Bot Automation (10 mins)

1. Go to **https://github.com** → Sign in → Click **New repository**
2. Name it `kannada-tech-news` → Set to **Public** → Create
3. Push this entire folder to it:
   ```bash
   cd kannada-tech-news
   git init
   git add .
   git commit -m "Initial commit: Kannada Tech News Portal"
   git remote add origin https://github.com/YOUR_USERNAME/kannada-tech-news.git
   git push -u origin main
   ```
4. Go to your GitHub repo → **Settings → Secrets and Variables → Actions**
5. Click **New repository secret** for each of these:
   - `SUPABASE_URL` → your Supabase project URL
   - `SUPABASE_SERVICE_KEY` → your Supabase service_role key
   - `ANTHROPIC_API_KEY` → your Anthropic API key

6. Go to **Actions tab** → You'll see **Kannada Tech News Bot** → Click **Run workflow** to test!

The bot will now run automatically at: **7 AM, 10 AM, 1 PM, 4 PM, 7 PM IST** every day.

---

## Step 4 — Website with Your Supabase Keys (5 mins)

Open `site/index.html` and find lines ~721-722:
```javascript
const SUPABASE_URL = 'https://YOUR_PROJECT.supabase.co'
const SUPABASE_ANON_KEY = 'YOUR_ANON_KEY'
```
Replace them with your actual Supabase URL and anon key.

---

## Step 5 — Deploy Your Website (5 mins)

### Option A: GitHub Pages (100% Free, Easiest)
1. Go to your GitHub repo → **Settings → Pages**
2. Source: **Deploy from a branch** → Branch: `main` → Folder: `/site`
3. Click Save → Your site will be live at:
   `https://YOUR_USERNAME.github.io/kannada-tech-news`

### Option B: Netlify (Free, Better Performance)
1. Go to **https://netlify.com** → Import from Git
2. Connect your GitHub repo
3. Build command: *(leave empty)*
4. Publish directory: `site`
5. Deploy!

### Option C: Vercel (Free, Fastest)
1. Go to **https://vercel.com** → New Project → Import from GitHub
2. Framework preset: **Other**
3. Root directory: `site`
4. Deploy!

---

## Your Portal is Live! 🎉

After the bot runs for the first time, your portal will show real Kannada tech news!

---

## Customization Options

| What to change | Where |
|---|---|
| Site name (ಟೆಕ್ ವಾರ್ತೆ) | Search `ಟೆಕ್ ವಾರ್ತೆ` in `site/index.html` |
| Add more RSS feeds | Edit `RSS_FEEDS` list in `bot/bot.py` |
| Articles per day | Change `ARTICLES_PER_RUN` in `bot/bot.py` |
| Bot schedule | Edit cron in `.github/workflows/news-bot.yml` |
| Add Google Analytics | Add GA4 script inside `<head>` in `index.html` |
| Add more categories | Add rows to `categories` table in Supabase SQL Editor |

---

## Troubleshooting

**Bot fails with "No module named..."**
→ Check `bot/requirements.txt` is being read correctly in GitHub Actions

**Website shows "ಇನ್ನೂ ಸುದ್ದಿಗಳಿಲ್ಲ" (No articles yet)**
→ Run the bot manually from GitHub Actions first, then refresh

**Translation looks off**
→ The Claude AI translation prompt is in `bot/bot.py` around line 151 — you can adjust it

**Supabase 403 error**
→ Make sure Row Level Security policies were created (they're in the schema SQL)

---

## File Structure Reference

```
kannada-tech-news/
├── site/
│   ├── index.html          ← Live website (connect to Supabase)
│   ├── demo.html           ← Preview with sample data (no setup needed)
│   ├── lib/supabase.ts     ← TypeScript Supabase types
│   └── package.json        ← (optional) Next.js config
├── bot/
│   ├── bot.py              ← Python news bot
│   └── requirements.txt    ← Python dependencies
├── docs/
│   └── supabase_schema.sql ← Run this in Supabase SQL Editor
├── .github/
│   └── workflows/
│       └── news-bot.yml    ← GitHub Actions (runs bot 5× daily)
├── .env.example            ← Copy to .env for local testing
└── QUICK_START.md          ← This file
```

---

## Suggested Domain Names

- `tekvarte.com` — ₹800/year
- `kannadatech.in` — ₹700/year
- `techwarte.in` — ₹700/year
- `techsuddi.in` — ₹700/year

Buy from Namecheap, GoDaddy, or BigRock → Connect in Vercel/Netlify settings.

---

*Built with Claude AI · Powered by Supabase · Automated via GitHub Actions*
