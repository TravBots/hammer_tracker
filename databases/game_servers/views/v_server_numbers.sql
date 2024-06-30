DROP VIEW IF EXISTS v_server_numbers;

CREATE VIEW v_server_numbers as
with pop_difference as (
  select 
    date, 
    sum(population) as current_pop, 
    lag(sum(population),1) over(order by date) as prev_pop
  from v_map_history 
  where player_name = 'Natars' 
  group by 1 
  order by 1 desc 
), previous_vs_current as (
  select
    date,
    prev_pop,
    current_pop,
    case when current_pop < prev_pop*0.5 then true else false end as new_server
  from pop_difference
)
select 
  date, 
  sum(new_server) over(order by date) as server_number
from previous_vs_current
order by date
;