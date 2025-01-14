DROP VIEW IF EXISTS v_new_villages;

CREATE VIEW v_new_villages AS
WITH latest_time AS (
    SELECT MAX(inserted_at) as max_time 
    FROM map_history
),
previous_time AS (
    SELECT MAX(inserted_at) as prev_time 
    FROM map_history 
    WHERE inserted_at < (SELECT max_time FROM latest_time)
)
SELECT 
    curr.inserted_at,
    curr.village_id,
    curr.village_name,
    curr.player_id,
    curr.player_name,
    curr.alliance_id,
    curr.alliance_tag,
    curr.x_coordinate,
    curr.y_coordinate,
    curr.population,
    curr.tribe_id as tribe,
    curr.capital as is_capital
FROM map_history curr
LEFT JOIN map_history prev ON 
    curr.x_coordinate = prev.x_coordinate 
    AND curr.y_coordinate = prev.y_coordinate
    AND prev.inserted_at = (SELECT prev_time FROM previous_time)
WHERE curr.inserted_at = (SELECT max_time FROM latest_time)
    AND prev.village_id IS NULL 
    AND curr.village_id IS NOT NULL; 