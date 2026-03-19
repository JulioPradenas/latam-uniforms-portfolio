CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.mart_safety_stock` AS

WITH demand_stats AS (
  SELECT
    region_code,
    item_name,
    size_code,
    AVG(weekly_demand)    AS avg_demand,
    STDDEV(weekly_demand) AS stddev_demand
  FROM `latam-uniforms-portfolio.latam_uniforms.mart_demand_history`
  GROUP BY 1,2,3
),

lead_times AS (
  SELECT
    region_code,
    item AS item_name,
    AVG(SAFE_CAST(lead_time_days AS FLOAT64))    AS avg_lt_days,
    STDDEV(SAFE_CAST(lead_time_days AS FLOAT64)) AS stddev_lt_days
  FROM `latam-uniforms-portfolio.latam_uniforms.stg_lead_times`
  WHERE lead_time_days != ''
  GROUP BY 1,2
)

SELECT
  d.region_code,
  d.item_name,
  d.size_code,
  ROUND(d.avg_demand, 2)                AS avg_demand,
  ROUND(d.stddev_demand, 2)             AS stddev_demand,
  ROUND(COALESCE(l.avg_lt_days, 14), 1) AS avg_lead_time_days,

  -- Safety Stock (nivel de servicio 95% → Z = 1.645)
  -- Fórmula: Z × √(LT_avg × σ_demand² + D_avg² × σ_LT²)
  ROUND(
    1.645 * SQRT(
      COALESCE(l.avg_lt_days, 14) * POW(COALESCE(d.stddev_demand, 0), 2) +
      POW(d.avg_demand, 2) * POW(COALESCE(l.stddev_lt_days, 2), 2)
    ), 0
  ) AS safety_stock_95,

  -- Reorder Point = demanda durante lead time + stock de seguridad
  ROUND(
    d.avg_demand * COALESCE(l.avg_lt_days, 14) / 7 +
    1.645 * SQRT(
      COALESCE(l.avg_lt_days, 14) * POW(COALESCE(d.stddev_demand, 0), 2) +
      POW(d.avg_demand, 2) * POW(COALESCE(l.stddev_lt_days, 2), 2)
    ), 0
  ) AS reorder_point

FROM demand_stats d
LEFT JOIN lead_times l
  ON d.region_code = l.region_code
  AND d.item_name  = l.item_name;