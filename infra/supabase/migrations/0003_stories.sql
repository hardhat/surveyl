-- Canonical (deduplicated) news stories, clustered from raw ingested articles.
-- game_date is the daily game this story is ingested for (Round 1/2 top-5 candidate,
-- or a future Round 3 testing story), not necessarily the date the news broke.
create table public.canonical_stories (
  id uuid primary key default gen_random_uuid(),
  game_date date not null,
  headline text not null,
  summary text,
  created_at timestamptz not null default now()
);

create index canonical_stories_game_date_idx on public.canonical_stories (game_date);

alter table public.canonical_stories enable row level security;

create policy "service role full access to canonical_stories"
  on public.canonical_stories
  for all
  to service_role
  using (true)
  with check (true);

-- Raw articles as fetched from source outlets, before clustering into a canonical story.
create table public.raw_stories (
  id uuid primary key default gen_random_uuid(),
  canonical_story_id uuid references public.canonical_stories (id) on delete set null,
  source text not null,
  source_url text,
  headline text not null,
  article_text text,
  published_at timestamptz,
  fetched_at timestamptz not null default now()
);

create index raw_stories_canonical_story_id_idx on public.raw_stories (canonical_story_id);

alter table public.raw_stories enable row level security;

create policy "service role full access to raw_stories"
  on public.raw_stories
  for all
  to service_role
  using (true)
  with check (true);
