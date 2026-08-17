-- One row per daily game; game_date is the calendar day the game is published for.
create table public.game_days (
  id uuid primary key default gen_random_uuid(),
  game_date date not null unique,
  status text not null default 'draft' check (status in ('draft', 'published', 'fallback')),
  created_at timestamptz not null default now()
);

alter table public.game_days enable row level security;

create policy "service role full access to game_days"
  on public.game_days
  for all
  to service_role
  using (true)
  with check (true);

-- Round 1 candidate stories shown to players: 12 per game day, 5 of which are real
-- (rank 1-5, matching the day's top-story ranking) and the rest are decoys (rank is null).
-- points is the hidden score for correctly identifying that story; derived from rank so it
-- can never drift out of sync (rank 1 = 5 pts ... rank 5 = 1 pt).
create table public.round1_candidates (
  id uuid primary key default gen_random_uuid(),
  game_day_id uuid not null references public.game_days (id) on delete cascade,
  canonical_story_id uuid not null references public.canonical_stories (id),
  rank smallint check (rank between 1 and 5),
  points smallint generated always as (case when rank is null then null else 6 - rank end) stored,
  created_at timestamptz not null default now(),
  unique (game_day_id, canonical_story_id)
);

-- Partial unique index: enforces at most one story per rank per day (decoys have rank null,
-- so they're excluded from this constraint rather than colliding with each other).
create unique index round1_candidates_one_per_rank_idx
  on public.round1_candidates (game_day_id, rank)
  where rank is not null;

alter table public.round1_candidates enable row level security;

create policy "service role full access to round1_candidates"
  on public.round1_candidates
  for all
  to service_role
  using (true)
  with check (true);
