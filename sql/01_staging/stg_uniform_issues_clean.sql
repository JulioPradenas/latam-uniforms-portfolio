CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.stg_uniform_issues_clean` AS

WITH deduped AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY issue_id ORDER BY issue_date DESC
    ) AS rn
  FROM `latam-uniforms-portfolio.latam_uniforms.stg_uniform_issues`
  WHERE issue_id IS NOT NULL AND issue_id != ''
),

cleaned AS (
  SELECT
    issue_id,
    employee_id,
    item,

    CASE
      WHEN UPPER(TRIM(size)) IN ('XS','S','M','L','XL','XXL') THEN UPPER(TRIM(size))
      WHEN UPPER(TRIM(size)) IN ('EXTRA LARGE','EXTRA-LARGE')  THEN 'XL'
      WHEN UPPER(TRIM(size)) IN ('LL','LARGE LARGE')           THEN 'L'
      WHEN UPPER(TRIM(size)) IN ('XSMALL','X-SMALL')           THEN 'XS'
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
      WHEN REGEXP_CONTAINS(issue_date, r'^\d{4}-\d{2}-\d{2}$')
        THEN PARSE_DATE('%Y-%m-%d', issue_date)
      ELSE NULL
    END AS issue_date_parsed,

    SAFE_CAST(quantity AS INT64) AS quantity_int,

    CASE WHEN UPPER(TRIM(size)) NOT IN ('XS','S','M','L','XL','XXL')
      THEN TRUE ELSE FALSE END AS is_size_dirty,
    CASE WHEN issue_date = '' OR issue_date IS NULL
      THEN TRUE ELSE FALSE END AS is_date_missing

  FROM deduped WHERE rn = 1
)

SELECT * FROM cleaned
WHERE issue_date_parsed IS NOT NULL
  AND quantity_int IS NOT NULL
  AND quantity_int > 0;