CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.dim_date` AS
SELECT
  date_day,
  EXTRACT(YEAR FROM date_day)      AS year,
  EXTRACT(QUARTER FROM date_day)   AS quarter,
  EXTRACT(MONTH FROM date_day)     AS month,
  FORMAT_DATE('%B', date_day)      AS month_name,
  EXTRACT(WEEK FROM date_day)      AS week_of_year,
  DATE_TRUNC(date_day, MONTH)      AS first_day_of_month,
  DATE_TRUNC(date_day, WEEK)       AS first_day_of_week
FROM UNNEST(
  GENERATE_DATE_ARRAY('2022-01-01','2027-12-31', INTERVAL 1 DAY)
) AS date_day;