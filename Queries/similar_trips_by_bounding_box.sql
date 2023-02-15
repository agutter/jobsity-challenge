WITH clustered_trips AS (
    SELECT
        *,
        unnest(ST_ClusterWithin(origin_coord, 1.5)) AS "origin_cluster",
        unnest(ST_ClusterWithin(destination_coord, 1.5)) AS "destination_cluster"
    FROM trips 
    GROUP BY id),
filtered_trips AS (
    SELECT
        max(region) AS "region",
        ST_Union(origin_coord) AS "origin_coord",
        ST_Union(destination_coord) AS "destination_coord",
        date_trunc('minute', datetime) AS "datetime",
        count(*) AS "similar_trips"
    FROM clustered_trips
    WHERE ST_Contains(ST_MakeBox2D(ST_PointFromText('{bottom_left}', 4326), ST_PointFromText('{top_right}', 4326)), ST_MakeBox2D(origin_coord,origin_coord)) AND
        ST_Contains(ST_MakeBox2D(ST_PointFromText('{bottom_left}', 4326), ST_PointFromText('{top_right}', 4326)), ST_MakeBox2D(destination_coord, destination_coord))
    GROUP BY date_trunc('minute', datetime), origin_cluster, destination_cluster
    ),
weekly_trips AS (
    SELECT
        '{bottom_left}' AS "bottom_left",
        '{top_right}' AS "top_right",
        date_trunc('week', datetime) AS "week",
        count(*) AS "weekly_trips"
    FROM filtered_trips
    GROUP BY date_trunc('week', datetime)
    ORDER BY bottom_left, top_right, date_trunc('week', datetime)
    ),
weekly_averages AS (
    SELECT
        bottom_left,
        top_right,
        avg(weekly_trips) AS "weekly_average"
    FROM weekly_trips
    GROUP BY bottom_left, top_right
    )
SELECT
    bottom_left,
    top_right,
    weekly_average
FROM weekly_averages;
