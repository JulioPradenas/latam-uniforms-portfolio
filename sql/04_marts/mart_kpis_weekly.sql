CREATE OR REPLACE VIEW `latam-uniforms-portfolio.latam_uniforms.mart_kpis_weekly` AS

WITH weekly AS (
  SELECT
    DATE_TRUNC(issue_date, WEEK)  AS week,
    region_code,
    item_name,
    size_code,
    SUM(CASE WHEN transaction_type='ISSUE'  THEN quantity      ELSE 0 END) AS issues_qty,
    SUM(CASE WHEN transaction_type='RETURN' THEN ABS(quantity) ELSE 0 END) AS returns_qty,
    SUM(CASE WHEN transaction_type='ISSUE'  THEN quantity
             ELSE -ABS(quantity) END)                                      AS net_demand
  FROM `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions`
  GROUP BY 1,2,3,4
),

with_inv AS (
  SELECT
    w.*,
    COALESCE(i.stock_qty, 0)                              AS current_stock,
    SAFE_DIVIDE(COALESCE(i.stock_qty,0),
      NULLIF(w.net_demand,0))                             AS days_on_hand,
    lt.lead_time_days
  FROM weekly w
  LEFT JOIN (
    SELECT region_code, item AS item_name, size_code, stock_qty
    FROM `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
    WHERE snapshot_date = (
      SELECT MAX(snapshot_date) FROM `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
    )
  ) i USING (region_code, item_name, size_code)
  LEFT JOIN (
    SELECT region_code, item,
      AVG(SAFE_CAST(lead_time_days AS FLOAT64)) AS lead_time_days
    FROM `latam-uniforms-portfolio.latam_uniforms.stg_lead_times`
    WHERE lead_time_days != ''
    GROUP BY 1,2
  ) lt ON w.region_code=lt.region_code AND w.item_name=lt.item
)

SELECT *,
  CASE
    WHEN current_stock = 0                    THEN 'STOCKOUT'
    WHEN days_on_hand < lead_time_days        THEN 'CRITICO'
    WHEN days_on_hand < lead_time_days * 1.5  THEN 'BAJO'
    ELSE 'OK'
  END AS stock_status
FROM with_inv;