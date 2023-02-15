SELECT region
FROM trips
WHERE datasource = 'cheap_mobile'
GROUP BY region;
