-- Clue copy for a Round 1 story. clue_order 1 is the default clue, 2 is the optional
-- second clue (taking it costs the player 25% of that story's points, only if they end up
-- identifying the story correctly).
create table public.round1_clues (
  id uuid primary key default gen_random_uuid(),
  canonical_story_id uuid not null references public.canonical_stories (id) on delete cascade,
  clue_order smallint not null check (clue_order in (1, 2)),
  clue_type text not null check (clue_type in ('satirical_summary', 'redacted_headline', 'keyword_cluster')),
  content text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (canonical_story_id, clue_order)
);

alter table public.round1_clues enable row level security;

create policy "service role full access to round1_clues"
  on public.round1_clues
  for all
  to service_role
  using (true)
  with check (true);

-- Append-only edit history: the pre-edit content of a clue, captured by the trigger below
-- whenever an admin edit changes round1_clues.content.
create table public.round1_clue_history (
  id uuid primary key default gen_random_uuid(),
  clue_id uuid not null references public.round1_clues (id) on delete cascade,
  content text not null,
  edited_by uuid references auth.users (id),
  edited_at timestamptz not null default now()
);

alter table public.round1_clue_history enable row level security;

create policy "service role full access to round1_clue_history"
  on public.round1_clue_history
  for all
  to service_role
  using (true)
  with check (true);

create or replace function public.round1_clues_record_history()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if new.content is distinct from old.content then
    insert into public.round1_clue_history (clue_id, content, edited_by)
    values (old.id, old.content, auth.uid());
    new.updated_at := now();
  end if;
  return new;
end;
$$;

create trigger round1_clues_before_update
  before update on public.round1_clues
  for each row
  execute function public.round1_clues_record_history();
