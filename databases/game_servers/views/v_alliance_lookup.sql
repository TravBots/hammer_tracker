-- Drop the view if it exists
DROP VIEW IF EXISTS v_alliance_lookup;

-- Create the alliance_view
CREATE VIEW v_alliance_lookup AS
WITH alliance_data AS (
    -- Select relevant columns from the alliances table
    SELECT
        alliance_id,
        alliance_tag
    FROM x_world
),
aggregated_alliance_data AS (
    -- Aggregate the data if necessary; here it's just a pass-through
    SELECT
        alliance_id,
        MAX(alliance_tag) AS alliance_name
    FROM alliance_data
    GROUP BY alliance_id
)
-- Select the final data for the view
SELECT
    alliance_id,
    alliance_name
FROM aggregated_alliance_data;
