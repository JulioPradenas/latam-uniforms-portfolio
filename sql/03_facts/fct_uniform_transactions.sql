CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions`
PARTITION BY issue_date
AS
SELECT
  issue_id                AS transaction_id,
  'ISSUE'                 AS transaction_type,
  employee_id,
  item                    AS item_name,
  size_normalized         AS size_code,
  region_normalized       AS region_code,
  issue_date_parsed       AS issue_date,
  quantity_int            AS quantity,
  is_size_dirty,
  is_date_missing
FROM `latam-uniforms-portfolio.latam_uniforms.stg_uniform_issues_clean`

UNION ALL

SELECT
  return_id                                                   AS transaction_id,
  'RETURN'                                                    AS transaction_type,
  employee_id,
  item                                                        AS item_name,
  size_normalized                                             AS size_code,
  region_normalized                                           AS region_code,
  return_date_parsed                                          AS issue_date,
  -1 * quantity_int                                           AS quantity,
  FALSE                                                       AS is_size_dirty,
  FALSE                                                       AS is_date_missing
FROM `latam-uniforms-portfolio.latam_uniforms.stg_uniform_returns_clean`;