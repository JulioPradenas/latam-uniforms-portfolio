CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.mart_demand_forecast_2027` AS

WITH aggregated AS (
  SELECT
    region_code,
    item_name,
    size_code,
    AVG(weekly_demand)    AS avg_demand,
    STDDEV(weekly_demand) AS stddev_demand,
    COUNT(*)              AS weeks_of_data
  FROM `latam-uniforms-portfolio.latam_uniforms.mart_demand_history`
  GROUP BY region_code, item_name, size_code
),

with_percentiles AS (
  SELECT
    region_code,
    item_name,
    size_code,
    avg_demand,
    stddev_demand,
    weeks_of_data,
    PERCENTILE_CONT(avg_demand, 0.25) OVER (
      PARTITION BY region_code, item_name, size_code) AS p25,
    PERCENTILE_CONT(avg_demand, 0.90) OVER (
      PARTITION BY region_code, item_name, size_code) AS p90
  FROM aggregated
),

weeks_2027 AS (
  SELECT DISTINCT DATE_TRUNC(d, WEEK) AS week
  FROM UNNEST(
    GENERATE_DATE_ARRAY('2027-01-01','2027-12-31', INTERVAL 1 WEEK)
  ) AS d
),

cross_data AS (
  SELECT w.week, s.*
  FROM weeks_2027 w
  CROSS JOIN with_percentiles s
)

SELECT
  week,
  region_code,
  item_name,
  size_code,
  ROUND(avg_demand, 1)        AS demand_base,
  ROUND(p25, 1)               AS demand_conservative,
  ROUND(p90 * 1.20, 1)       AS demand_stress,
  weeks_of_data,
  ROUND(stddev_demand, 2)     AS stddev_demand
FROM cross_data;