-- "Automatically expose new tables" is disabled on this project, so new tables get
-- no role grants at all; RLS policies alone don't substitute for table-level GRANTs.
grant select, insert, update, delete on public.admins to service_role;
