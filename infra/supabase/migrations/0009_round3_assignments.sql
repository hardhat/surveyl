-- Which Round 3 variant a specific player was randomly assigned for a given story. Assigned
-- once (on Round 3 entry) and then fixed for the rest of that session; the unique constraint
-- guarantees exactly one variant per story per player attempt. No update policy is defined,
-- so an assignment can never be changed once inserted (matches "stays fixed" in the spec).
create table public.round3_assignments (
  id uuid primary key default gen_random_uuid(),
  attempt_id uuid not null references public.player_attempts (id) on delete cascade,
  canonical_story_id uuid not null references public.canonical_stories (id),
  round3_candidate_id uuid not null references public.round3_candidates (id),
  assigned_at timestamptz not null default now(),
  unique (attempt_id, canonical_story_id)
);

alter table public.round3_assignments enable row level security;

create policy "service role full access to round3_assignments"
  on public.round3_assignments
  for all
  to service_role
  using (true)
  with check (true);

create policy "players read own round3 assignments"
  on public.round3_assignments
  for select
  to authenticated
  using (
    exists (
      select 1 from public.player_attempts a
      where a.id = attempt_id and a.anon_user_id = auth.uid()
    )
  );

create policy "players insert own round3 assignments"
  on public.round3_assignments
  for insert
  to authenticated
  with check (
    exists (
      select 1 from public.player_attempts a
      where a.id = attempt_id and a.anon_user_id = auth.uid()
    )
  );
