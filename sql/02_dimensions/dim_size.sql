CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.dim_size` AS
SELECT
  size_code,
  size_label,
  SAFE_CAST(sort_order AS INT64) AS sort_order,
  notes
FROM `latam-uniforms-portfolio.latam_uniforms.stg_sizes`
WHERE size_code IN ('XS','S','M','L','XL','XXL','UNK');