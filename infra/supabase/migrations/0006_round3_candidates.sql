-- Shared question-format type, reused by Round 2 and Round 3 questions.
create type public.question_format as enum ('multiple_choice', 'percentage');

-- Round 3 candidate questions test possible next-day Round 2 questions for a story.
-- Each story gets exactly 3 candidates (enforced by variant_order 1-3 + the unique
-- constraint below). There is no correct-answer column here: Round 3 has no answer key,
-- the "correct" value only exists once crowd responses are aggregated and a candidate is
-- promoted into a Round 2 question (see round2_questions.source_round3_candidate_id).
create table public.round3_candidates (
  id uuid primary key default gen_random_uuid(),
  game_day_id uuid not null references public.game_days (id) on delete cascade,
  canonical_story_id uuid not null references public.canonical_stories (id),
  variant_order smallint not null check (variant_order between 1 and 3),
  question_type public.question_format not null,
  prompt text not null,
  options jsonb check (
    (question_type = 'multiple_choice' and jsonb_array_length(options) = 4)
    or (question_type = 'percentage' and options is null)
  ),
  status text not null default 'pending' check (status in ('pending', 'approved', 'rejected')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (game_day_id, canonical_story_id, variant_order)
);

alter table public.round3_candidates enable row level security;

create policy "service role full access to round3_candidates"
  on public.round3_candidates
  for all
  to service_role
  using (true)
  with check (true);
