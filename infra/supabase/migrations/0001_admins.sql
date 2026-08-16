-- Admin allowlist: rows here mark a Supabase Auth user as an admin.
create table if not exists public.admins (
  user_id uuid primary key references auth.users (id) on delete cascade,
  created_at timestamptz not null default now()
);

alter table public.admins enable row level security;

-- Only the service role (EC2 admin/ingestion backend) may read or write this table.
-- No policy is defined for anon/authenticated, so PostgREST denies them by default.
create policy "service role full access to admins"
  on public.admins
  for all
  to service_role
  using (true)
  with check (true);

-- Helper used by other tables' RLS policies to check "is this JWT an admin".
create or replace function public.is_admin()
returns boolean
language sql
security definer
set search_path = public
stable
as $$
  select exists (
    select 1 from public.admins where user_id = auth.uid()
  );
$$;
