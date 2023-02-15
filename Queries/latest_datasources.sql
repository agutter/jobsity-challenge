SELECT DISTINCT ON (region)
    region,
    datasource
FROM trips
WHERE region IN (SELECT
                    region
                FROM trips
                GROUP BY region
                ORDER BY count(*) DESC
                LIMIT 2
            )
ORDER BY region, datetime DESC;
