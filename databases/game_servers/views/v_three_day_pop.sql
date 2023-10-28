DROP VIEW IF EXISTS v_three_day_pop;

create view v_three_day_pop as
with lags as(
    select 
        date,
        player_id,
        player_name, 
        village_id,
        village_name,
        population as today, 
        coalesce(lag(population, 1) over(partition by village_id order by date),0) as yesterday,
        coalesce(lag(population, 2) over(partition by village_id order by date),0) as two_days_ago,
        coalesce(lag(population, 3) over(partition by village_id order by date),0) as three_days_ago
    from v_map_history 
    group by 1, 2, 3, 4, 5
)
select
    player_id,
    player_name,
    village_id,
    village_name,
    today as current_pop,
    today - yesterday as one_day_diff,
    today - two_days_ago as two_day_diff,
    today - three_days_ago as three_day_diff
from lags 
where date = (select max(date) from lags)
;
