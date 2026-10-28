-- 1) Overall fail rate
SELECT COUNT(*) AS units, SUM(fail) AS fails, ROUND(AVG(fail), 4) AS fail_rate
FROM units;

-- 2) Weekly fail rate trend
SELECT strftime('%Y-%W', timestamp) AS week,
       COUNT(*) AS units, SUM(fail) AS fails,
       ROUND(AVG(fail), 3) AS fail_rate
FROM units
GROUP BY week
ORDER BY week;

-- 3) Sensors with most missing values
SELECT sensor, 1567 - COUNT(*) AS missing,
       ROUND(1.0 * (1567 - COUNT(*)) / 1567, 3) AS missing_share
FROM measurements
GROUP BY sensor
ORDER BY missing DESC
LIMIT 15;

-- 4) Mean sensor value for failed vs passed units (top differences)
WITH stats AS (
  SELECT m.sensor,
         AVG(CASE WHEN u.fail = 1 THEN m.value END) AS mean_fail,
         AVG(CASE WHEN u.fail = 0 THEN m.value END) AS mean_pass,
         AVG(m.value) AS mean_all
  FROM measurements m JOIN units u USING (unit_id)
  GROUP BY m.sensor
)
SELECT sensor, mean_fail, mean_pass,
       ABS(mean_fail - mean_pass) / NULLIF(ABS(mean_all), 0) AS rel_diff
FROM stats
ORDER BY rel_diff DESC
LIMIT 10;

-- 5) Rolling 7-unit-window fail rate (window function)
SELECT unit_id, timestamp,
       AVG(fail) OVER (ORDER BY timestamp ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS rolling_fail_50
FROM units
ORDER BY timestamp;
