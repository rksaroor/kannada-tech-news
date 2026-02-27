-- ============================================
-- KANNADA TECH NEWS PORTAL - Supabase Schema
-- Run this in your Supabase SQL editor
-- ============================================

-- Categories table
CREATE TABLE categories (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name_kn TEXT NOT NULL,        -- Kannada name e.g. "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ"
  name_en TEXT NOT NULL,        -- English name e.g. "Artificial Intelligence"
  slug TEXT UNIQUE NOT NULL,    -- e.g. "artificial-intelligence"
  color TEXT DEFAULT '#FF6B35', -- accent color for category badge
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Articles table
CREATE TABLE articles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  
  -- Content
  title_kn TEXT NOT NULL,           -- Translated Kannada title
  title_en TEXT NOT NULL,           -- Original English title
  summary_kn TEXT NOT NULL,         -- Translated Kannada summary
  summary_en TEXT NOT NULL,         -- Original English summary
  body_kn TEXT,                     -- Full article body in Kannada (optional)
  
  -- Metadata
  source_url TEXT NOT NULL,         -- Original article URL
  source_name TEXT NOT NULL,        -- e.g. "TechCrunch"
  source_favicon TEXT,              -- favicon URL of source
  category_id UUID REFERENCES categories(id),
  
  -- Media
  thumbnail_url TEXT,               -- Article image
  
  -- SEO
  slug TEXT UNIQUE NOT NULL,        -- URL slug
  meta_description TEXT,            -- SEO meta description in Kannada
  
  -- Status
  is_published BOOLEAN DEFAULT TRUE,
  is_featured BOOLEAN DEFAULT FALSE,
  view_count INTEGER DEFAULT 0,
  
  -- Timestamps
  original_published_at TIMESTAMPTZ,  -- When source published
  published_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_articles_category ON articles(category_id);
CREATE INDEX idx_articles_slug ON articles(slug);
CREATE INDEX idx_articles_is_published ON articles(is_published);

-- Scrape log (to avoid duplicate articles)
CREATE TABLE scrape_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  source_url TEXT UNIQUE NOT NULL,
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'success',  -- 'success' | 'failed' | 'skipped'
  error_message TEXT
);

CREATE INDEX idx_scrape_log_url ON scrape_log(source_url);

-- Site settings (key-value store for config)
CREATE TABLE site_settings (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Seed default categories
-- ============================================
INSERT INTO categories (name_kn, name_en, slug, color) VALUES
  ('ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ', 'Artificial Intelligence', 'artificial-intelligence', '#FF6B35'),
  ('ಸ್ಮಾರ್ಟ್‌ಫೋನ್', 'Smartphones', 'smartphones', '#4ECDC4'),
  ('ಸ್ಟಾರ್ಟಪ್', 'Startups', 'startups', '#45B7D1'),
  ('ಸೈಬರ್ ಭದ್ರತೆ', 'Cybersecurity', 'cybersecurity', '#F7DC6F'),
  ('ಬಾಹ್ಯಾಕಾಶ', 'Space Tech', 'space-tech', '#BB8FCE'),
  ('ಗೇಮಿಂಗ್', 'Gaming', 'gaming', '#82E0AA'),
  ('ಎಲೆಕ್ಟ್ರಿಕ್ ವಾಹನ', 'Electric Vehicles', 'electric-vehicles', '#F1948A'),
  ('ಸಾಮಾಜಿಕ ಮಾಧ್ಯಮ', 'Social Media', 'social-media', '#85C1E9');

-- ============================================
-- Enable Row Level Security (public read)
-- ============================================
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Public can read published articles
CREATE POLICY "Public can read published articles"
  ON articles FOR SELECT
  USING (is_published = TRUE);

-- Public can read categories
CREATE POLICY "Public can read categories"
  ON categories FOR SELECT
  USING (TRUE);

-- Only service role can insert/update (your bot uses service key)
CREATE POLICY "Service role can manage articles"
  ON articles FOR ALL
  USING (auth.role() = 'service_role');

-- ============================================
-- Helper function to increment view count
-- ============================================
CREATE OR REPLACE FUNCTION increment_view_count(article_slug TEXT)
RETURNS VOID AS $$
  UPDATE articles SET view_count = view_count + 1 WHERE slug = article_slug;
$$ LANGUAGE SQL;
