do $$
declare
  departure_time_type text;
begin
  select data_type
  into departure_time_type
  from information_schema.columns
  where table_schema = 'public'
    and table_name = 'driver_trips'
    and column_name = 'departure_time';

  if departure_time_type = 'timestamp with time zone' then
    alter table public.driver_trips
      add column if not exists departure_date date;

    alter table public.driver_trips
      add column if not exists departure_time_bucket text;

    update public.driver_trips
    set
      departure_date = (departure_time at time zone 'Asia/Aden')::date,
      departure_time_bucket = case
        when extract(hour from departure_time at time zone 'Asia/Aden') < 12 then 'morning'
        when extract(hour from departure_time at time zone 'Asia/Aden') < 18 then 'noon'
        else 'night'
      end
    where departure_date is null
      or departure_time_bucket is null;

    alter table public.driver_trips
      alter column departure_date set not null;

    alter table public.driver_trips
      drop column departure_time;

    alter table public.driver_trips
      rename column departure_time_bucket to departure_time;
  end if;
end;
$$;

alter table public.driver_trips
  alter column departure_time set not null;

alter table public.driver_trips
  drop constraint if exists driver_trips_departure_time_check;

alter table public.driver_trips
  add constraint driver_trips_departure_time_check
  check (departure_time in ('morning', 'noon', 'night'));

drop index if exists public.idx_driver_trips_active_route;

create index if not exists idx_driver_trips_active_route
  on public.driver_trips(status, departure, destination, departure_date, departure_time);
