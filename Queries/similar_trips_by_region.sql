WITH clustered_trips AS (
    SELECT
        *,
        unnest(ST_ClusterWithin(origin_coord, 1.5)) AS "origin_cluster",
        unnest(ST_ClusterWithin(destination_coord, 1.5)) AS "destination_cluster"
    FROM trips 
    GROUP BY id),
filtered_trips AS (
    SELECT max(region) AS "region", date_trunc('minute', datetime) AS "datetime", count(*) AS "similar_trips"
    FROM clustered_trips
    GROUP BY date_trunc('minute', datetime), origin_cluster, destination_cluster
    ),
weekly_trips AS (
    SELECT region AS "region", date_trunc('week', datetime) AS "week", count(*) AS "weekly_trips"
    FROM filtered_trips
    GROUP BY region, date_trunc('week', datetime)
    ORDER BY region, date_trunc('week', datetime)
    ),
weekly_averages AS (
    SELECT region, avg(weekly_trips) AS "weekly_average"
    FROM weekly_trips
    GROUP BY region
    )
SELECT region, weekly_average
FROM weekly_averages
WHERE region = '{region}';
