#!/usr/bin/env python3
"""
Kannada Tech News Bot
Scrapes trending tech news → Translates to Kannada → Posts to Supabase
Run via GitHub Actions 5x daily
"""

import os
import re
import time
import json
import hashlib
import logging
import feedparser
import requests
from datetime import datetime, timezone
from anthropic import Anthropic
from supabase import create_client, Client

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ─── Config ─────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

# How many articles to post per run (5 posts/day, bot runs once → 5 articles)
ARTICLES_PER_RUN = 5

# RSS Feeds — mix of reliable tech sources
RSS_FEEDS = [
    {"url": "https://techcrunch.com/feed/",            "name": "TechCrunch"},
    {"url": "https://feeds.wired.com/wired/index",     "name": "Wired"},
    {"url": "https://www.theverge.com/rss/index.xml",  "name": "The Verge"},
    {"url": "https://feeds.arstechnica.com/arstechnica/index", "name": "Ars Technica"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "name": "NYT Tech"},
]

# Category keyword mapping (English keywords → category slug)
CATEGORY_KEYWORDS = {
    "artificial-intelligence": ["ai", "artificial intelligence", "machine learning", "gpt", "llm", "chatgpt", "gemini", "claude", "openai", "deepmind", "neural"],
    "smartphones":             ["iphone", "android", "smartphone", "samsung", "pixel", "oneplus", "mobile phone"],
    "startups":                ["startup", "funding", "series a", "series b", "venture", "ipo", "unicorn", "valuation"],
    "cybersecurity":           ["hack", "breach", "ransomware", "malware", "vulnerability", "security", "phishing", "cyber"],
    "space-tech":              ["spacex", "nasa", "rocket", "satellite", "mars", "moon", "space", "orbit", "starship"],
    "gaming":                  ["game", "gaming", "playstation", "xbox", "nintendo", "steam", "esports"],
    "electric-vehicles":       ["electric vehicle", "tesla", "ev ", "battery", "charging", "self-driving", "autonomous"],
    "social-media":            ["twitter", "x.com", "meta", "instagram", "tiktok", "youtube", "facebook", "linkedin"],
}

# ─── Clients ────────────────────────────────────────────────────────────────
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_slug(text: str, url: str) -> str:
    """Create a URL-safe slug from title + url hash to ensure uniqueness."""
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]
    url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{base}-{url_hash}"


def detect_category(title: str, summary: str) -> str | None:
    """Detect article category from keywords. Returns slug or None."""
    text = (title + " " + summary).lower()
    for slug, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return slug
    return None


def already_scraped(url: str) -> bool:
    """Check if this URL was already processed."""
    result = supabase.table("scrape_log").select("id").eq("source_url", url).execute()
    return len(result.data) > 0


def log_scrape(url: str, status: str = "success", error: str = None):
    """Record this URL in scrape_log."""
    supabase.table("scrape_log").insert({
        "source_url": url,
        "status": status,
        "error_message": error
    }).execute()


def get_category_id(slug: str) -> str | None:
    """Get category UUID from slug."""
    if not slug:
        return None
    result = supabase.table("categories").select("id").eq("slug", slug).execute()
    return result.data[0]["id"] if result.data else None


# ─── Fetching ────────────────────────────────────────────────────────────────

def fetch_articles_from_feeds() -> list[dict]:
    """Pull articles from all RSS feeds, newest first."""
    articles = []
    for feed_info in RSS_FEEDS:
        try:
            log.info(f"Fetching: {feed_info['name']}")
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:15]:
                url = entry.get("link", "")
                title = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                # Strip HTML tags from summary
                summary = re.sub(r"<[^>]+>", "", summary).strip()[:800]

                if not url or not title or len(summary) < 50:
                    continue

                articles.append({
                    "title_en": title,
                    "summary_en": summary,
                    "source_url": url,
                    "source_name": feed_info["name"],
                    "thumbnail_url": entry.get("media_thumbnail", [{}])[0].get("url") if entry.get("media_thumbnail") else None,
                    "original_published_at": entry.get("published", None),
                })
        except Exception as e:
            log.error(f"Failed to fetch {feed_info['name']}: {e}")

    # Deduplicate by URL
    seen = set()
    unique = []
    for a in articles:
        if a["source_url"] not in seen:
            seen.add(a["source_url"])
            unique.append(a)

    log.info(f"Total unique articles found: {len(unique)}")
    return unique


# ─── Translation ─────────────────────────────────────────────────────────────

def translate_article(title_en: str, summary_en: str) -> dict:
    """
    Translate title and summary to authentic Kannada using Claude.
    Returns dict with title_kn, summary_kn, meta_description.
    """
    prompt = f"""You are a professional Kannada journalist. Translate the following tech news article title and summary into natural, readable Kannada that a general Kannada-speaking audience would enjoy reading.

Guidelines:
- Write in clear, journalistic Kannada (not overly literary or academic)
- Keep proper nouns, brand names, and tech terms in English or transliterate them naturally (e.g., AI, iPhone, ChatGPT, Samsung)
- Numbers stay as digits
- The tone should be informative and engaging
- Do NOT add your own opinions or extra information

Return ONLY a JSON object with these exact keys:
{{
  "title_kn": "Kannada translation of the title",
  "summary_kn": "Kannada translation of the summary",
  "meta_description": "A short 1-sentence Kannada SEO description (max 120 chars)"
}}

Title: {title_en}

Summary: {summary_en}"""

    response = anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    # Extract JSON safely
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not json_match:
        raise ValueError(f"No JSON found in translation response: {raw[:200]}")

    return json.loads(json_match.group())


# ─── Main Pipeline ───────────────────────────────────────────────────────────

def run():
    log.info("=" * 50)
    log.info(f"Bot started at {datetime.now(timezone.utc).isoformat()}")
    log.info("=" * 50)

    # 1. Fetch all articles
    all_articles = fetch_articles_from_feeds()

    # 2. Filter out already-scraped ones
    new_articles = [a for a in all_articles if not already_scraped(a["source_url"])]
    log.info(f"New (unscraped) articles: {len(new_articles)}")

    if not new_articles:
        log.info("No new articles to process. Exiting.")
        return

    # 3. Pick top N articles to process
    to_process = new_articles[:ARTICLES_PER_RUN]
    posted = 0

    for article in to_process:
        url = article["source_url"]
        log.info(f"Processing: {article['title_en'][:60]}...")

        try:
            # Translate
            translated = translate_article(article["title_en"], article["summary_en"])
            time.sleep(1)  # Rate limit buffer

            # Detect category
            cat_slug = detect_category(article["title_en"], article["summary_en"])
            cat_id = get_category_id(cat_slug)

            # Build slug
            slug = make_slug(article["title_en"], url)

            # Insert into Supabase
            supabase.table("articles").insert({
                "title_kn": translated["title_kn"],
                "title_en": article["title_en"],
                "summary_kn": translated["summary_kn"],
                "summary_en": article["summary_en"],
                "source_url": url,
                "source_name": article["source_name"],
                "thumbnail_url": article.get("thumbnail_url"),
                "category_id": cat_id,
                "slug": slug,
                "meta_description": translated.get("meta_description", ""),
                "is_published": True,
                "original_published_at": article.get("original_published_at"),
            }).execute()

            log_scrape(url, "success")
            posted += 1
            log.info(f"✅ Posted: {translated['title_kn'][:50]}")

        except Exception as e:
            log.error(f"❌ Failed for {url}: {e}")
            log_scrape(url, "failed", str(e))

    log.info(f"\nDone. Posted {posted}/{len(to_process)} articles.")


if __name__ == "__main__":
    run()
