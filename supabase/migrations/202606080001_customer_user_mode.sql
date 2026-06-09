alter table public.customers
  add column if not exists user_mode text
  check (user_mode in ('driver', 'passenger'));
