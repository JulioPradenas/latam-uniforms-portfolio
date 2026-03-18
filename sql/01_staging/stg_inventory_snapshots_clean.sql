CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.stg_inventory_snapshots_clean` AS

SELECT
  snapshot_id,

  CASE
    WHEN REGEXP_CONTAINS(snapshot_date, r'^\d{4}-\d{2}-\d{2}$')
      THEN PARSE_DATE('%Y-%m-%d', snapshot_date)
    ELSE NULL
  END AS snapshot_date,

  CASE
    WHEN UPPER(TRIM(region_code)) IN ('SCL','LIM','BOG','GRU','EZE','MIA')
                                                         THEN UPPER(TRIM(region_code))
    WHEN LOWER(TRIM(region_code)) IN ('santiago','stgo') THEN 'SCL'
    WHEN LOWER(TRIM(region_code)) = 'lima'               THEN 'LIM'
    WHEN LOWER(TRIM(region_code)) IN ('bogota','bogotá')  THEN 'BOG'
    ELSE 'UNK_REGION'
  END AS region_normalized,

  item,

  CASE
    WHEN UPPER(TRIM(size)) IN ('XS','S','M','L','XL','XXL') THEN UPPER(TRIM(size))
    WHEN TRIM(size) = '' OR size IS NULL                     THEN 'UNK'
    ELSE 'UNK'
  END AS size_normalized,

  GREATEST(0, SAFE_CAST(stock_qty AS INT64)) AS stock_qty

FROM `latam-uniforms-portfolio.latam_uniforms.stg_inventory_snapshots`
WHERE snapshot_date IS NOT NULL AND snapshot_date != '';
```

