CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.stg_uniform_returns_clean` AS

WITH cleaned AS (
  SELECT
    return_id,
    employee_id,
    item,

    CASE
      WHEN UPPER(TRIM(size)) IN ('XS','S','M','L','XL','XXL') THEN UPPER(TRIM(size))
      WHEN UPPER(TRIM(size)) IN ('EXTRA LARGE','EXTRA-LARGE')  THEN 'XL'
      WHEN UPPER(TRIM(size)) IN ('LL','LARGE LARGE')           THEN 'L'
      WHEN TRIM(size) = '' OR size IS NULL
        OR UPPER(TRIM(size)) = 'NULL'                          THEN 'UNK'
      ELSE 'UNK'
    END AS size_normalized,
    size AS size_original,

    CASE
      WHEN UPPER(TRIM(region_code)) IN ('SCL','LIM','BOG','GRU','EZE','MIA')
                                                           THEN UPPER(TRIM(region_code))
      WHEN LOWER(TRIM(region_code)) IN ('santiago','stgo') THEN 'SCL'
      WHEN LOWER(TRIM(region_code)) = 'lima'               THEN 'LIM'
      WHEN LOWER(TRIM(region_code)) IN ('bogota','bogotá')  THEN 'BOG'
      ELSE 'UNK_REGION'
    END AS region_normalized,
    region_code AS region_original,

    CASE
      WHEN REGEXP_CONTAINS(return_date, r'^\d{4}-\d{2}-\d{2}$')
        THEN PARSE_DATE('%Y-%m-%d', return_date)
      ELSE NULL
    END AS return_date_parsed,

    reason,
    SAFE_CAST(quantity AS INT64) AS quantity_int

  FROM `latam-uniforms-portfolio.latam_uniforms.stg_uniform_returns`
  WHERE return_id IS NOT NULL AND return_id != ''
)

SELECT * FROM cleaned
WHERE return_date_parsed IS NOT NULL
  AND quantity_int IS NOT NULL
  AND quantity_int > 0;