CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.dim_employee` AS
WITH deduped AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY hire_date DESC) AS rn
  FROM `latam-uniforms-portfolio.latam_uniforms.stg_employees`
  WHERE employee_id IS NOT NULL AND employee_id != ''
)
SELECT
  employee_id,
  name,
  role,
  CASE
    WHEN UPPER(TRIM(region_code)) IN ('SCL','LIM','BOG','GRU','EZE','MIA')
      THEN UPPER(TRIM(region_code))
    WHEN LOWER(TRIM(region_code)) IN ('santiago','stgo') THEN 'SCL'
    WHEN LOWER(TRIM(region_code)) = 'lima'               THEN 'LIM'
    WHEN LOWER(TRIM(region_code)) IN ('bogota','bogotá')  THEN 'BOG'
    ELSE 'UNK_REGION'
  END AS region_code,
  CASE
    WHEN REGEXP_CONTAINS(hire_date, r'^\d{4}-\d{2}-\d{2}$')
      THEN PARSE_DATE('%Y-%m-%d', hire_date)
    ELSE NULL
  END AS hire_date,
  CASE WHEN is_active = '1' THEN TRUE ELSE FALSE END AS is_active
FROM deduped
WHERE rn = 1;