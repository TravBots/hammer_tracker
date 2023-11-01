DROP VIEW IF EXISTS v_three_day_pop;
DROP VIEW IF EXISTS v_seven_day_pop;

create view v_seven_day_pop as
with lags as(
    select 
        date,
        player_id,
        player_name, 
        village_id,
        village_name,
        first_value(date) over(partition by village_id order by date) as founded,
        population as today, 
        coalesce(lag(population, 1) over(partition by village_id order by date),0) as yesterday,
        coalesce(lag(population, 2) over(partition by village_id order by date),0) as two_days_ago,
        coalesce(lag(population, 3) over(partition by village_id order by date),0) as three_days_ago,
        coalesce(lag(population, 4) over(partition by village_id order by date),0) as four_days_ago,
        coalesce(lag(population, 5) over(partition by village_id order by date),0) as five_days_ago,
        coalesce(lag(population, 6) over(partition by village_id order by date),0) as six_days_ago
    from v_map_history 
    group by 1, 2, 3, 4, 5
)
select
    date as load_date,
    founded,
    player_id,
    player_name,
    village_id,
    village_name,
    today,
    yesterday,
    two_days_ago,
    three_days_ago,
    four_days_ago,
    five_days_ago,
    six_days_ago
from lags 
where date = (select max(date) from lags)
;
