CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.mart_purchase_reco_2027` AS

WITH annual AS (
  SELECT
    region_code,
    item_name,
    size_code,
    SUM(demand_base)   AS annual_demand_base,
    SUM(demand_stress) AS annual_demand_stress
  FROM `latam-uniforms-portfolio.latam_uniforms.mart_demand_forecast_2027`
  GROUP BY 1,2,3
),

inventory AS (
  SELECT
    region_code,
    item        AS item_name,
    size_code,
    SUM(stock_qty) AS on_hand
  FROM `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
  WHERE snapshot_date = (
    SELECT MAX(snapshot_date)
    FROM `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
  )
  GROUP BY 1,2,3
)

SELECT
  a.region_code,
  a.item_name,
  a.size_code,
  COALESCE(i.on_hand, 0)                            AS on_hand,
  COALESCE(s.reorder_point, 0)                      AS reorder_point,
  COALESCE(s.safety_stock_95, 0)                    AS safety_stock_95,
  ROUND(a.annual_demand_base, 0)                    AS annual_demand_base,
  ROUND(a.annual_demand_stress, 0)                  AS annual_demand_stress,

  -- Cantidad a comprar escenario base
  GREATEST(0, CEIL(
    a.annual_demand_base + COALESCE(s.safety_stock_95, 0) - COALESCE(i.on_hand, 0)
  ))                                                AS qty_to_buy_base,

  -- Cantidad a comprar escenario estrés
  GREATEST(0, CEIL(
    a.annual_demand_stress + COALESCE(s.safety_stock_95, 0) - COALESCE(i.on_hand, 0)
  ))                                                AS qty_to_buy_stress,

  -- Prioridad
  CASE
    WHEN COALESCE(i.on_hand, 0) = 0                       THEN 'P1 - STOCKOUT'
    WHEN COALESCE(i.on_hand, 0) < COALESCE(s.reorder_point, 0)         THEN 'P2 - CRITICO'
    WHEN COALESCE(i.on_hand, 0) < COALESCE(s.reorder_point, 0) * 1.5  THEN 'P3 - BAJO'
    ELSE 'P4 - OK'
  END                                               AS priority,

  RANK() OVER (
    ORDER BY COALESCE(i.on_hand, 0) ASC,
             a.annual_demand_base DESC
  )                                                 AS criticality_rank

FROM annual a
LEFT JOIN inventory i USING (region_code, item_name, size_code)
LEFT JOIN `latam-uniforms-portfolio.latam_uniforms.mart_safety_stock` s
  USING (region_code, item_name, size_code)
WHERE a.annual_demand_base > 0;