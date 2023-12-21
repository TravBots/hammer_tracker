DROP VIEW IF EXISTS v_village_ages;

CREATE VIEW v_village_ages AS
WITH recent_inserts AS (
    SELECT village_id, alliance_id, x_coordinate, y_coordinate, MAX(inserted_at) AS most_recent_insert
    FROM map_history
    GROUP BY village_id
),
insert_count AS (
    SELECT village_id, COUNT(DISTINCT inserted_at) AS insert_count
    FROM map_history
    GROUP BY village_id
)
SELECT r.village_id, r.alliance_id, r.x_coordinate, r.y_coordinate, r.most_recent_insert, i.insert_count
FROM recent_inserts r
JOIN insert_count i ON r.village_id = i.village_id;