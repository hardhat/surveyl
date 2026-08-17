-- A player's answer (or explicit skip) to one Round 2 or Round 3 question. Exactly one of
-- round2_question_id / round3_candidate_id is set, matching which round the question belongs
-- to. No update policy is defined, so a submitted response can never be changed (each
-- question is submitted and locked immediately, per spec).
create table public.poll_responses (
  id uuid primary key default gen_random_uuid(),
  attempt_id uuid not null references public.player_attempts (id) on delete cascade,
  round2_question_id uuid references public.round2_questions (id),
  round3_candidate_id uuid references public.round3_candidates (id),
  selected_option smallint check (selected_option between 0 and 3),
  percentage_value smallint check (percentage_value between 0 and 100),
  is_skip boolean not null default false,
  points_awarded smallint not null default 0,
  responded_at timestamptz not null default now(),
  unique (attempt_id, round2_question_id),
  unique (attempt_id, round3_candidate_id),
  check (
    (round2_question_id is not null and round3_candidate_id is null)
    or (round2_question_id is null and round3_candidate_id is not null)
  )
);

alter table public.poll_responses enable row level security;

create policy "service role full access to poll_responses"
  on public.poll_responses
  for all
  to service_role
  using (true)
  with check (true);

create policy "players read own poll responses"
  on public.poll_responses
  for select
  to authenticated
  using (
    exists (
      select 1 from public.player_attempts a
      where a.id = attempt_id and a.anon_user_id = auth.uid()
    )
  );

create policy "players insert own poll responses"
  on public.poll_responses
  for insert
  to authenticated
  with check (
    exists (
      select 1 from public.player_attempts a
      where a.id = attempt_id and a.anon_user_id = auth.uid()
    )
  );

-- Aggregate counters per question, used by the Round 2 canonical-selection logic (lowest
-- skip rate, then highest total answers) and by analytics. Internal only: no player access.
create table public.question_stats (
  id uuid primary key default gen_random_uuid(),
  round2_question_id uuid references public.round2_questions (id),
  round3_candidate_id uuid references public.round3_candidates (id),
  total_answers integer not null default 0,
  total_skips integer not null default 0,
  option_counts jsonb not null default '{}'::jsonb,
  percentage_sum bigint not null default 0,
  updated_at timestamptz not null default now(),
  check (
    (round2_question_id is not null and round3_candidate_id is null)
    or (round2_question_id is null and round3_candidate_id is not null)
  )
);

create unique index question_stats_round2_question_id_idx
  on public.question_stats (round2_question_id) where round2_question_id is not null;
create unique index question_stats_round3_candidate_id_idx
  on public.question_stats (round3_candidate_id) where round3_candidate_id is not null;

alter table public.question_stats enable row level security;

create policy "service role full access to question_stats"
  on public.question_stats
  for all
  to service_role
  using (true)
  with check (true);

create or replace function public.poll_responses_update_stats()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if new.round2_question_id is not null then
    insert into public.question_stats (round2_question_id)
    values (new.round2_question_id)
    on conflict (round2_question_id) where round2_question_id is not null do nothing;
  else
    insert into public.question_stats (round3_candidate_id)
    values (new.round3_candidate_id)
    on conflict (round3_candidate_id) where round3_candidate_id is not null do nothing;
  end if;

  update public.question_stats
  set
    total_answers = total_answers + case when new.is_skip then 0 else 1 end,
    total_skips = total_skips + case when new.is_skip then 1 else 0 end,
    percentage_sum = percentage_sum + coalesce(new.percentage_value, 0),
    option_counts = case
      when new.selected_option is not null then
        jsonb_set(
          option_counts,
          array[new.selected_option::text],
          to_jsonb(coalesce((option_counts ->> new.selected_option::text)::int, 0) + 1)
        )
      else option_counts
    end,
    updated_at = now()
  where (new.round2_question_id is not null and round2_question_id = new.round2_question_id)
     or (new.round3_candidate_id is not null and round3_candidate_id = new.round3_candidate_id);

  return new;
end;
$$;

create trigger poll_responses_after_insert
  after insert on public.poll_responses
  for each row
  execute function public.poll_responses_update_stats();
