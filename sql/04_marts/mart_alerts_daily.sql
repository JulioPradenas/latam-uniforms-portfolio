CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.mart_alerts_daily` AS

WITH stockout_alerts AS (
  SELECT
    region_code,
    item_name,
    size_code,
    'STOCKOUT_RISK'  AS alert_type,
    'P1'             AS severity,
    'Procurement'    AS owner,
    CONCAT('DoH=', ROUND(days_on_hand, 1),
           ' días < LT=', ROUND(lead_time_days, 0), ' días') AS detail
  FROM `latam-uniforms-portfolio.latam_uniforms.mart_kpis_weekly`
  WHERE stock_status IN ('STOCKOUT','CRITICO')
    AND week = (
      SELECT MAX(week)
      FROM `latam-uniforms-portfolio.latam_uniforms.mart_kpis_weekly`
    )
),

dirty_size_alerts AS (
  SELECT
    region_code,
    'N/A'               AS item_name,
    'N/A'               AS size_code,
    'DATA_QUALITY_SIZE' AS alert_type,
    'P2'                AS severity,
    'Data Engineering'  AS owner,
    CONCAT(ROUND(pct_unk * 100, 1), '% tallas UNK en región') AS detail
  FROM (
    SELECT
      region_code,
      COUNTIF(size_code = 'UNK') / COUNT(*) AS pct_unk
    FROM `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions`
    GROUP BY region_code
  )
  WHERE pct_unk > 0.10
),

forecast_drift_alerts AS (
  SELECT
    h.region_code,
    h.item_name,
    h.size_code,
    'FORECAST_DRIFT'  AS alert_type,
    'P2'              AS severity,
    'Demand Planning' AS owner,
    'Demanda real fuera del rango conservador-estrés' AS detail
  FROM `latam-uniforms-portfolio.latam_uniforms.mart_demand_history` h
  JOIN `latam-uniforms-portfolio.latam_uniforms.mart_demand_forecast_2027` f
    ON  h.region_code = f.region_code
    AND h.item_name   = f.item_name
    AND h.size_code   = f.size_code
    AND h.week        = f.week
  WHERE h.weekly_demand > f.demand_stress
     OR h.weekly_demand < f.demand_conservative * 0.5
)

SELECT CURRENT_DATE() AS alert_date, * FROM stockout_alerts
UNION ALL
SELECT CURRENT_DATE(), * FROM dirty_size_alerts
UNION ALL
SELECT CURRENT_DATE(), * FROM forecast_drift_alerts;