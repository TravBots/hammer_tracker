DROP VIEW IF EXISTS v_player_change;
CREATE VIEW v_player_change AS
WITH date_range AS (
    SELECT
        MAX(date) AS today_timestamp,
        DATE(MAX(date), '-1 day') AS yesterday_timestamp
    FROM v_map_history
),
player_data AS (
    SELECT
        m.player_id,
        m.player_name,
        m.alliance_id,
        m.village_id,
        m.population,
        CASE WHEN m.date = d.today_timestamp THEN 'current' ELSE 'previous' END AS data_type
    FROM v_map_history m
    CROSS JOIN date_range d
    WHERE m.date IN (d.today_timestamp, d.yesterday_timestamp)
),
aggregated_data AS (
    SELECT
        player_id,
        player_name,
        MAX(CASE WHEN data_type = 'current' THEN alliance_id END) AS current_alliance_id,
        MAX(CASE WHEN data_type = 'previous' THEN alliance_id END) AS previous_alliance_id,
        COUNT(DISTINCT CASE WHEN data_type = 'current' THEN village_id END) AS current_villages_count,
        COUNT(DISTINCT CASE WHEN data_type = 'previous' THEN village_id END) AS previous_villages_count,
        SUM(CASE WHEN data_type = 'current' THEN population ELSE 0 END) AS current_population,
        SUM(CASE WHEN data_type = 'previous' THEN population ELSE 0 END) AS previous_population
    FROM player_data
    GROUP BY player_id, player_name
)
SELECT
    player_id,
    player_name,
    COALESCE(current_alliance_id, 'Unspecified') AS current_alliance_id,
    COALESCE(previous_alliance_id, 'Unspecified') AS previous_alliance_id,
    current_villages_count,
    previous_villages_count,
    current_population,
    previous_population,
    (current_villages_count != previous_villages_count) AS villages_changed,
    (COALESCE(current_alliance_id, 'Unspecified') != COALESCE(previous_alliance_id, 'Unspecified')) AS alliance_changed,
    (current_population - previous_population) AS population_change,
    (SELECT today_timestamp FROM date_range) AS created_at
FROM aggregated_data;

