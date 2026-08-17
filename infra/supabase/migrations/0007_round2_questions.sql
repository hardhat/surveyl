-- Round 2's canonical question per top story: the automatically promoted winner from the
-- previous day's Round 3 candidate testing (source_round3_candidate_id), or admin-authored
-- directly if no candidate data exists yet (e.g. early launch days). Unlike Round 3, Round 2
-- has a resolved correct answer that's revealed to the player immediately after they submit.
-- The unique constraint on round1_candidate_id is what guarantees "one question per story
-- per day" (a round1_candidates row already ties one story to one game day).
create table public.round2_questions (
  id uuid primary key default gen_random_uuid(),
  round1_candidate_id uuid not null references public.round1_candidates (id) on delete cascade,
  source_round3_candidate_id uuid references public.round3_candidates (id),
  question_type public.question_format not null,
  prompt text not null,
  options jsonb,
  correct_option_index smallint check (correct_option_index between 0 and 3),
  correct_percentage smallint check (correct_percentage between 0 and 100),
  explanation text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (round1_candidate_id),
  check (
    (question_type = 'multiple_choice' and jsonb_array_length(options) = 4
      and correct_option_index is not null and correct_percentage is null)
    or
    (question_type = 'percentage' and options is null
      and correct_percentage is not null and correct_option_index is null)
  )
);

alter table public.round2_questions enable row level security;

create policy "service role full access to round2_questions"
  on public.round2_questions
  for all
  to service_role
  using (true)
  with check (true);
