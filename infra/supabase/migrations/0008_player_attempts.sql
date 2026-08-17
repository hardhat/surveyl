-- One row per player (anon auth user) per game day. The unique constraint below is what
-- enforces "one scored attempt per day per browser identity"; RLS policies below enforce
-- that a player can only ever see/modify their own row (no cross-player access).
create table public.player_attempts (
  id uuid primary key default gen_random_uuid(),
  anon_user_id uuid not null references auth.users (id) on delete cascade,
  game_day_id uuid not null references public.game_days (id) on delete cascade,
  is_fallback boolean not null default false,
  round1_state jsonb not null default '{}'::jsonb,
  round1_submitted_at timestamptz,
  round1_score smallint,
  round2_state jsonb not null default '{}'::jsonb,
  round2_submitted_at timestamptz,
  round2_score smallint,
  round3_state jsonb not null default '{}'::jsonb,
  round3_submitted_at timestamptz,
  round3_score smallint,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (anon_user_id, game_day_id)
);

alter table public.player_attempts enable row level security;

create policy "service role full access to player_attempts"
  on public.player_attempts
  for all
  to service_role
  using (true)
  with check (true);

create policy "players read own attempt"
  on public.player_attempts
  for select
  to authenticated
  using (anon_user_id = auth.uid());

create policy "players insert own attempt"
  on public.player_attempts
  for insert
  to authenticated
  with check (anon_user_id = auth.uid());

-- NOTE: round-level submit/lock enforcement (rejecting updates to a round's state once its
-- *_submitted_at is set) is Milestone 8 scope; this policy only enforces row ownership.
create policy "players update own attempt"
  on public.player_attempts
  for update
  to authenticated
  using (anon_user_id = auth.uid())
  with check (anon_user_id = auth.uid());
