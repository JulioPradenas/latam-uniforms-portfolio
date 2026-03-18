CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
PARTITION BY snapshot_date
AS
SELECT
  snapshot_id,
  snapshot_date,
  region_normalized       AS region_code,
  item,
  size_normalized         AS size_code,
  stock_qty
FROM `latam-uniforms-portfolio.latam_uniforms.stg_inventory_snapshots_clean`;