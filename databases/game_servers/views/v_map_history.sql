DROP VIEW IF EXISTS v_map_history;

CREATE VIEW v_map_history as
select 
    strftime('%Y-%m-%d', datetime(inserted_at, 'unixepoch', 'localtime')) as date, 
    player_id, 
    player_name, 
    village_id, 
    village_name, 
    alliance_id, 
    alliance_tag, 
    x_coordinate, 
    y_coordinate, 
    population, 
    case 
        when tribe_id = 1 then 'Romans' 
        when tribe_id = 2 then 'Teutons' 
        when tribe_id = 3 then 'Gauls' 
        when tribe_id = 5 then 'Natars'
    end as tribe, 
    capital as is_capital 
from map_history;
