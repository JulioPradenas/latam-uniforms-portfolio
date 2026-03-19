CREATE OR REPLACE VIEW `latam-uniforms-portfolio.latam_uniforms.mart_size_heatmap` AS

WITH base AS (
  SELECT
    region_code,
    item_name,
    size_code,
    SUM(quantity)    AS total_issues,
    STDDEV(quantity) AS demand_stddev
  FROM `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions`
  WHERE transaction_type = 'ISSUE'
  GROUP BY 1,2,3
),

totals AS (
  SELECT
    region_code,
    item_name,
    SUM(total_issues) AS region_item_total
  FROM base
  GROUP BY 1,2
)

SELECT
  b.*,
  SAFE_DIVIDE(b.total_issues, t.region_item_total) AS pct_share,
  RANK() OVER (
    PARTITION BY b.region_code, b.item_name
    ORDER BY b.total_issues DESC
  ) AS rank_by_volume
FROM base b
JOIN totals t USING (region_code, item_name);