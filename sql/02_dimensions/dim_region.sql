CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.dim_region` AS
SELECT region_code, region_name, country, cluster
FROM `latam-uniforms-portfolio.latam_uniforms.stg_regions`
WHERE region_code IN ('SCL','LIM','BOG','GRU','EZE','MIA');