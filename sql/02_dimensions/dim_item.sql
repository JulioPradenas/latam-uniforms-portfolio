CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.dim_item` AS
SELECT DISTINCT
  item AS item_name,
  CASE
    WHEN item IN ('Camisa','Corbata')    THEN 'Parte Superior'
    WHEN item = 'Pantalon'              THEN 'Parte Inferior'
    WHEN item IN ('Chaqueta','Chaleco') THEN 'Abrigo'
    WHEN item = 'Zapatos'               THEN 'Calzado'
    ELSE 'Otro'
  END AS category
FROM `latam-uniforms-portfolio.latam_uniforms.stg_uniform_issues_clean`;