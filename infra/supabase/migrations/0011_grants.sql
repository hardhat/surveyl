-- "Automatically expose new tables" is disabled on this project (see 0002_admins_grants.sql),
-- so every table created in this migration set needs an explicit GRANT before its RLS
-- policies have any effect through PostgREST.
grant select, insert, update, delete on public.canonical_stories to service_role;
grant select, insert, update, delete on public.raw_stories to service_role;
grant select, insert, update, delete on public.game_days to service_role;
grant select, insert, update, delete on public.round1_candidates to service_role;
grant select, insert, update, delete on public.round1_clues to service_role;
grant select, insert, update, delete on public.round1_clue_history to service_role;
grant select, insert, update, delete on public.round3_candidates to service_role;
grant select, insert, update, delete on public.round2_questions to service_role;
grant select, insert, update, delete on public.player_attempts to service_role;
grant select, insert, update, delete on public.round3_assignments to service_role;
grant select, insert, update, delete on public.poll_responses to service_role;
grant select, insert, update, delete on public.question_stats to service_role;

-- Player-owned tables: RLS above restricts every row to its owning player, so it's safe to
-- grant authenticated (Supabase Anonymous Auth players) direct table access via PostgREST.
grant select, insert, update on public.player_attempts to authenticated;
grant select, insert on public.round3_assignments to authenticated;
grant select, insert on public.poll_responses to authenticated;

-- Deliberately NOT granted to anon/authenticated: canonical_stories, raw_stories,
-- round1_candidates, round1_clues, round2_questions, round3_candidates, question_stats.
-- These hold pre-reveal secrets (which candidate is real, correct MC/percentage answers) or
-- internal analytics, so row-level RLS alone can't safely expose them column-wise over
-- PostgREST. Game-package delivery and round scoring must go through Supabase Edge Functions
-- (per specification.md section 21), which can filter/redact fields before responding.
