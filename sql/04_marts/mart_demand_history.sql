CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.mart_demand_history` AS

SELECT
  DATE_TRUNC(issue_date, WEEK) AS week,
  region_code,
  item_name,
  size_code,
  SUM(quantity)               AS weekly_demand,
  COUNT(DISTINCT employee_id) AS active_employees
FROM `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions`
WHERE transaction_type = 'ISSUE'
  AND size_code   != 'UNK'
  AND region_code != 'UNK_REGION'
GROUP BY 1,2,3,4;