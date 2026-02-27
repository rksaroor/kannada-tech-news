import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Article = {
  id: string
  title_kn: string
  title_en: string
  summary_kn: string
  source_url: string
  source_name: string
  thumbnail_url: string | null
  slug: string
  meta_description: string
  is_featured: boolean
  view_count: number
  published_at: string
  categories: {
    name_kn: string
    name_en: string
    slug: string
    color: string
  } | null
}
