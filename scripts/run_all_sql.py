"""
run_all_sql.py
Ejecuta todos los SQLs del proyecto en orden correcto.
Uso: python scripts/run_all_sql.py
"""

from google.cloud import bigquery
import os
import time

PROJECT = "latam-uniforms-portfolio"
client  = bigquery.Client(project=PROJECT)

# ── Orden de ejecución ────────────────────────────────────────────────────
# Cada tupla es (descripcion, sql)
# Se definen inline para no depender de leer archivos externos

SQLS = [

  # ── STAGING LIMPIO ────────────────────────────────────────────────────
  ("stg_uniform_issues_clean", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.stg_uniform_issues_clean` AS
    WITH deduped AS (
      SELECT *,
        ROW_NUMBER() OVER (PARTITION BY issue_id ORDER BY issue_date DESC) AS rn
      FROM `latam-uniforms-portfolio.latam_uniforms.stg_uniform_issues`
      WHERE issue_id IS NOT NULL AND issue_id != ''
    ),
    cleaned AS (
      SELECT
        issue_id, employee_id, item,
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
          WHEN LOWER(TRIM(region_code)) IN ('bogota','bogota')  THEN 'BOG'
          WHEN LOWER(TRIM(region_code)) IN ('sao paulo','gru')  THEN 'GRU'
          WHEN LOWER(TRIM(region_code)) IN ('buenos aires','eze') THEN 'EZE'
          WHEN LOWER(TRIM(region_code)) = 'miami'               THEN 'MIA'
          ELSE 'UNK_REGION'
        END AS region_normalized,
        region_code AS region_original,
        CASE
          WHEN REGEXP_CONTAINS(issue_date, r'^\\d{4}-\\d{2}-\\d{2}$')
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
      AND quantity_int > 0
  """),

  ("stg_uniform_returns_clean", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.stg_uniform_returns_clean` AS
    WITH cleaned AS (
      SELECT
        return_id, employee_id, item,
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
          WHEN LOWER(TRIM(region_code)) IN ('bogota','bogota')  THEN 'BOG'
          WHEN LOWER(TRIM(region_code)) IN ('sao paulo','gru')  THEN 'GRU'
          WHEN LOWER(TRIM(region_code)) IN ('buenos aires','eze') THEN 'EZE'
          WHEN LOWER(TRIM(region_code)) = 'miami'               THEN 'MIA'
          ELSE 'UNK_REGION'
        END AS region_normalized,
        region_code AS region_original,
        CASE
          WHEN REGEXP_CONTAINS(return_date, r'^\\d{4}-\\d{2}-\\d{2}$')
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
      AND quantity_int > 0
  """),

  ("stg_inventory_snapshots_clean", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.stg_inventory_snapshots_clean` AS
    SELECT
      snapshot_id,
      CASE
        WHEN REGEXP_CONTAINS(snapshot_date, r'^\\d{4}-\\d{2}-\\d{2}$')
          THEN PARSE_DATE('%Y-%m-%d', snapshot_date)
        ELSE NULL
      END AS snapshot_date,
      CASE
        WHEN UPPER(TRIM(region_code)) IN ('SCL','LIM','BOG','GRU','EZE','MIA')
                                                           THEN UPPER(TRIM(region_code))
        WHEN LOWER(TRIM(region_code)) IN ('santiago','stgo') THEN 'SCL'
        WHEN LOWER(TRIM(region_code)) = 'lima'               THEN 'LIM'
        WHEN LOWER(TRIM(region_code)) IN ('bogota','bogota')  THEN 'BOG'
        WHEN LOWER(TRIM(region_code)) IN ('sao paulo','gru')  THEN 'GRU'
        WHEN LOWER(TRIM(region_code)) IN ('buenos aires','eze') THEN 'EZE'
        WHEN LOWER(TRIM(region_code)) = 'miami'               THEN 'MIA'
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
    WHERE snapshot_date IS NOT NULL AND snapshot_date != ''
  """),

  # ── DIMENSIONES ───────────────────────────────────────────────────────
  ("dim_region", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.dim_region` AS
    SELECT region_code, region_name, country, cluster
    FROM `latam-uniforms-portfolio.latam_uniforms.stg_regions`
    WHERE region_code IN ('SCL','LIM','BOG','GRU','EZE','MIA')
  """),

  ("dim_size", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.dim_size` AS
    SELECT size_code, size_label,
      SAFE_CAST(sort_order AS INT64) AS sort_order, notes
    FROM `latam-uniforms-portfolio.latam_uniforms.stg_sizes`
    WHERE size_code IN ('XS','S','M','L','XL','XXL','UNK')
  """),

  ("dim_item", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.dim_item` AS
    SELECT DISTINCT item AS item_name,
      CASE
        WHEN item IN ('Camisa','Corbata')    THEN 'Parte Superior'
        WHEN item = 'Pantalon'              THEN 'Parte Inferior'
        WHEN item IN ('Chaqueta','Chaleco') THEN 'Abrigo'
        WHEN item = 'Zapatos'               THEN 'Calzado'
        ELSE 'Otro'
      END AS category
    FROM `latam-uniforms-portfolio.latam_uniforms.stg_uniform_issues_clean`
  """),

  ("dim_employee", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.dim_employee` AS
    WITH deduped AS (
      SELECT *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY hire_date DESC) AS rn
      FROM `latam-uniforms-portfolio.latam_uniforms.stg_employees`
      WHERE employee_id IS NOT NULL AND employee_id != ''
    )
    SELECT
      employee_id, name, role,
      CASE
        WHEN UPPER(TRIM(region_code)) IN ('SCL','LIM','BOG','GRU','EZE','MIA')
          THEN UPPER(TRIM(region_code))
        WHEN LOWER(TRIM(region_code)) IN ('santiago','stgo') THEN 'SCL'
        WHEN LOWER(TRIM(region_code)) = 'lima'               THEN 'LIM'
        WHEN LOWER(TRIM(region_code)) IN ('bogota','bogota')  THEN 'BOG'
        ELSE 'UNK_REGION'
      END AS region_code,
      CASE
        WHEN REGEXP_CONTAINS(hire_date, r'^\\d{4}-\\d{2}-\\d{2}$')
          THEN PARSE_DATE('%Y-%m-%d', hire_date)
        ELSE NULL
      END AS hire_date,
      CASE WHEN is_active = '1' THEN TRUE ELSE FALSE END AS is_active
    FROM deduped WHERE rn = 1
  """),

  ("dim_date", """
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
    ) AS date_day
  """),

  # ── FACTS ─────────────────────────────────────────────────────────────
  ("DROP fct_uniform_transactions", """
    DROP TABLE IF EXISTS `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions`
  """),

  ("fct_uniform_transactions", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions` 
    AS
    SELECT
      issue_id          AS transaction_id,
      'ISSUE'           AS transaction_type,
      employee_id,
      item              AS item_name,
      size_normalized   AS size_code,
      region_normalized AS region_code,
      issue_date_parsed AS issue_date,
      quantity_int      AS quantity,
      is_size_dirty,
      is_date_missing
    FROM `latam-uniforms-portfolio.latam_uniforms.stg_uniform_issues_clean`
    UNION ALL
    SELECT
      return_id           AS transaction_id,
      'RETURN'            AS transaction_type,
      employee_id,
      item                AS item_name,
      size_normalized     AS size_code,
      region_normalized   AS region_code,
      return_date_parsed  AS issue_date,
      -1 * quantity_int   AS quantity,
      FALSE               AS is_size_dirty,
      FALSE               AS is_date_missing
    FROM `latam-uniforms-portfolio.latam_uniforms.stg_uniform_returns_clean`
  """),

  ("DROP fct_inventory_daily", """
    DROP TABLE IF EXISTS `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
  """),

  ("fct_inventory_daily", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
    AS
    SELECT
      snapshot_id,
      snapshot_date,
      region_normalized AS region_code,
      item,
      size_normalized   AS size_code,
      stock_qty
    FROM `latam-uniforms-portfolio.latam_uniforms.stg_inventory_snapshots_clean`
  """),

  # ── MARTS ─────────────────────────────────────────────────────────────
  ("mart_kpis_weekly", """
    CREATE OR REPLACE VIEW `latam-uniforms-portfolio.latam_uniforms.mart_kpis_weekly` AS
    WITH weekly AS (
      SELECT
        DATE_TRUNC(issue_date, WEEK) AS week,
        region_code, item_name, size_code,
        SUM(CASE WHEN transaction_type='ISSUE'  THEN quantity      ELSE 0 END) AS issues_qty,
        SUM(CASE WHEN transaction_type='RETURN' THEN ABS(quantity) ELSE 0 END) AS returns_qty,
        SUM(CASE WHEN transaction_type='ISSUE'  THEN quantity
                 ELSE -ABS(quantity) END)                                      AS net_demand
      FROM `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions`
      GROUP BY 1,2,3,4
    ),
    with_inv AS (
      SELECT w.*,
        COALESCE(i.stock_qty, 0)                          AS current_stock,
        SAFE_DIVIDE(COALESCE(i.stock_qty,0),
          NULLIF(w.net_demand,0))                         AS days_on_hand,
        lt.lead_time_days
      FROM weekly w
      LEFT JOIN (
        SELECT region_code, item AS item_name, size_code, stock_qty
        FROM `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
        WHERE snapshot_date = (
          SELECT MAX(snapshot_date)
          FROM `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
        )
      ) i USING (region_code, item_name, size_code)
      LEFT JOIN (
        SELECT region_code, item,
          AVG(SAFE_CAST(lead_time_days AS FLOAT64)) AS lead_time_days
        FROM `latam-uniforms-portfolio.latam_uniforms.stg_lead_times`
        WHERE lead_time_days != ''
        GROUP BY 1,2
      ) lt ON w.region_code=lt.region_code AND w.item_name=lt.item
    )
    SELECT *,
      CASE
        WHEN current_stock = 0                    THEN 'STOCKOUT'
        WHEN days_on_hand < lead_time_days        THEN 'CRITICO'
        WHEN days_on_hand < lead_time_days * 1.5  THEN 'BAJO'
        ELSE 'OK'
      END AS stock_status
    FROM with_inv
  """),

  ("mart_size_heatmap", """
    CREATE OR REPLACE VIEW `latam-uniforms-portfolio.latam_uniforms.mart_size_heatmap` AS
    WITH base AS (
      SELECT region_code, item_name, size_code,
        SUM(quantity)    AS total_issues,
        STDDEV(quantity) AS demand_stddev
      FROM `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions`
      WHERE transaction_type = 'ISSUE'
      GROUP BY 1,2,3
    ),
    totals AS (
      SELECT region_code, item_name, SUM(total_issues) AS region_item_total
      FROM base GROUP BY 1,2
    )
    SELECT b.*,
      SAFE_DIVIDE(b.total_issues, t.region_item_total) AS pct_share,
      RANK() OVER (
        PARTITION BY b.region_code, b.item_name
        ORDER BY b.total_issues DESC
      ) AS rank_by_volume
    FROM base b JOIN totals t USING (region_code, item_name)
  """),

  ("mart_demand_history", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.mart_demand_history` AS
    SELECT
      DATE_TRUNC(issue_date, WEEK) AS week,
      region_code, item_name, size_code,
      SUM(quantity)               AS weekly_demand,
      COUNT(DISTINCT employee_id) AS active_employees
    FROM `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions`
    WHERE transaction_type = 'ISSUE'
      AND size_code   != 'UNK'
      AND region_code != 'UNK_REGION'
    GROUP BY 1,2,3,4
  """),

  ("mart_demand_forecast_2027", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.mart_demand_forecast_2027` AS
    WITH aggregated AS (
      SELECT region_code, item_name, size_code,
        AVG(weekly_demand)    AS avg_demand,
        STDDEV(weekly_demand) AS stddev_demand,
        COUNT(*)              AS weeks_of_data
      FROM `latam-uniforms-portfolio.latam_uniforms.mart_demand_history`
      GROUP BY 1,2,3
    ),
    with_percentiles AS (
      SELECT *,
        PERCENTILE_CONT(avg_demand, 0.25) OVER (
          PARTITION BY region_code, item_name, size_code) AS p25,
        PERCENTILE_CONT(avg_demand, 0.90) OVER (
          PARTITION BY region_code, item_name, size_code) AS p90
      FROM aggregated
    ),
    weeks_2027 AS (
      SELECT DISTINCT DATE_TRUNC(d, WEEK) AS week
      FROM UNNEST(
        GENERATE_DATE_ARRAY('2027-01-01','2027-12-31', INTERVAL 1 WEEK)
      ) AS d
    )
    SELECT
      w.week, s.region_code, s.item_name, s.size_code,
      ROUND(s.avg_demand, 1)       AS demand_base,
      ROUND(s.p25, 1)              AS demand_conservative,
      ROUND(s.p90 * 1.20, 1)      AS demand_stress,
      s.weeks_of_data,
      ROUND(s.stddev_demand, 2)    AS stddev_demand
    FROM weeks_2027 w
    CROSS JOIN with_percentiles s
  """),

  ("mart_safety_stock", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.mart_safety_stock` AS
    WITH demand_stats AS (
      SELECT region_code, item_name, size_code,
        AVG(weekly_demand)    AS avg_demand,
        STDDEV(weekly_demand) AS stddev_demand
      FROM `latam-uniforms-portfolio.latam_uniforms.mart_demand_history`
      GROUP BY 1,2,3
    ),
    lead_times AS (
      SELECT region_code, item AS item_name,
        AVG(SAFE_CAST(lead_time_days AS FLOAT64))    AS avg_lt_days,
        STDDEV(SAFE_CAST(lead_time_days AS FLOAT64)) AS stddev_lt_days
      FROM `latam-uniforms-portfolio.latam_uniforms.stg_lead_times`
      WHERE lead_time_days != ''
      GROUP BY 1,2
    )
    SELECT
      d.region_code, d.item_name, d.size_code,
      ROUND(d.avg_demand, 2)                AS avg_demand,
      ROUND(d.stddev_demand, 2)             AS stddev_demand,
      ROUND(COALESCE(l.avg_lt_days, 14), 1) AS avg_lead_time_days,
      ROUND(
        1.645 * SQRT(
          COALESCE(l.avg_lt_days,14) * POW(COALESCE(d.stddev_demand,0),2) +
          POW(d.avg_demand,2) * POW(COALESCE(l.stddev_lt_days,2),2)
        ), 0
      ) AS safety_stock_95,
      ROUND(
        d.avg_demand * COALESCE(l.avg_lt_days,14) / 7 +
        1.645 * SQRT(
          COALESCE(l.avg_lt_days,14) * POW(COALESCE(d.stddev_demand,0),2) +
          POW(d.avg_demand,2) * POW(COALESCE(l.stddev_lt_days,2),2)
        ), 0
      ) AS reorder_point
    FROM demand_stats d
    LEFT JOIN lead_times l
      ON d.region_code=l.region_code AND d.item_name=l.item_name
  """),

  ("mart_purchase_reco_2027", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.mart_purchase_reco_2027` AS
    WITH annual AS (
      SELECT region_code, item_name, size_code,
        SUM(demand_base)   AS annual_demand_base,
        SUM(demand_stress) AS annual_demand_stress
      FROM `latam-uniforms-portfolio.latam_uniforms.mart_demand_forecast_2027`
      GROUP BY 1,2,3
    ),
    inventory AS (
      SELECT region_code, item AS item_name, size_code,
        SUM(stock_qty) AS on_hand
      FROM `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
      WHERE snapshot_date = (
        SELECT MAX(snapshot_date)
        FROM `latam-uniforms-portfolio.latam_uniforms.fct_inventory_daily`
      )
      GROUP BY 1,2,3
    )
    SELECT
      a.region_code, a.item_name, a.size_code,
      COALESCE(i.on_hand, 0)                         AS on_hand,
      COALESCE(s.reorder_point, 0)                   AS reorder_point,
      COALESCE(s.safety_stock_95, 0)                 AS safety_stock_95,
      ROUND(a.annual_demand_base, 0)                 AS annual_demand_base,
      ROUND(a.annual_demand_stress, 0)               AS annual_demand_stress,
      GREATEST(0, CEIL(
        a.annual_demand_base + COALESCE(s.safety_stock_95,0) - COALESCE(i.on_hand,0)
      ))                                             AS qty_to_buy_base,
      GREATEST(0, CEIL(
        a.annual_demand_stress + COALESCE(s.safety_stock_95,0) - COALESCE(i.on_hand,0)
      ))                                             AS qty_to_buy_stress,
      CASE
        WHEN COALESCE(i.on_hand,0) = 0                            THEN 'P1 - STOCKOUT'
        WHEN COALESCE(i.on_hand,0) < COALESCE(s.reorder_point,0)          THEN 'P2 - CRITICO'
        WHEN COALESCE(i.on_hand,0) < COALESCE(s.reorder_point,0) * 1.5   THEN 'P3 - BAJO'
        ELSE 'P4 - OK'
      END                                            AS priority,
      RANK() OVER (
        ORDER BY COALESCE(i.on_hand,0) ASC, a.annual_demand_base DESC
      )                                              AS criticality_rank
    FROM annual a
    LEFT JOIN inventory i USING (region_code, item_name, size_code)
    LEFT JOIN `latam-uniforms-portfolio.latam_uniforms.mart_safety_stock` s
      USING (region_code, item_name, size_code)
    WHERE a.annual_demand_base > 0
  """),

  ("mart_alerts_daily", """
    CREATE OR REPLACE TABLE `latam-uniforms-portfolio.latam_uniforms.mart_alerts_daily` AS
    WITH stockout_alerts AS (
      SELECT region_code, item_name, size_code,
        'STOCKOUT_RISK' AS alert_type, 'P1' AS severity, 'Procurement' AS owner,
        CONCAT('DoH=', ROUND(days_on_hand,1),
               ' dias < LT=', ROUND(lead_time_days,0), ' dias') AS detail
      FROM `latam-uniforms-portfolio.latam_uniforms.mart_kpis_weekly`
      WHERE stock_status IN ('STOCKOUT','CRITICO')
        AND week = (SELECT MAX(week) FROM `latam-uniforms-portfolio.latam_uniforms.mart_kpis_weekly`)
    ),
    dirty_size_alerts AS (
      SELECT region_code, 'N/A' AS item_name, 'N/A' AS size_code,
        'DATA_QUALITY_SIZE' AS alert_type, 'P2' AS severity,
        'Data Engineering' AS owner,
        CONCAT(ROUND(pct_unk*100,1), '% tallas UNK en region') AS detail
      FROM (
        SELECT region_code,
          COUNTIF(size_code='UNK') / COUNT(*) AS pct_unk
        FROM `latam-uniforms-portfolio.latam_uniforms.fct_uniform_transactions`
        GROUP BY region_code
      )
      WHERE pct_unk > 0.10
    ),
    forecast_drift_alerts AS (
      SELECT h.region_code, h.item_name, h.size_code,
        'FORECAST_DRIFT' AS alert_type, 'P2' AS severity,
        'Demand Planning' AS owner,
        'Demanda real fuera del rango conservador-estres' AS detail
      FROM `latam-uniforms-portfolio.latam_uniforms.mart_demand_history` h
      JOIN `latam-uniforms-portfolio.latam_uniforms.mart_demand_forecast_2027` f
        ON h.region_code=f.region_code AND h.item_name=f.item_name
        AND h.size_code=f.size_code AND h.week=f.week
      WHERE h.weekly_demand > f.demand_stress
         OR h.weekly_demand < f.demand_conservative * 0.5
    )
    SELECT CURRENT_DATE() AS alert_date, * FROM stockout_alerts
    UNION ALL SELECT CURRENT_DATE(), * FROM dirty_size_alerts
    UNION ALL SELECT CURRENT_DATE(), * FROM forecast_drift_alerts
  """),
]

# ── Ejecutar en orden ──────────────────────────────────────────────────────
print("🚀 Iniciando ejecución de SQLs...\n")
start_total = time.time()

for name, sql in SQLS:
    print(f"⏳ {name}...", end=" ", flush=True)
    start = time.time()
    try:
        job = client.query(sql.strip())
        job.result()
        elapsed = round(time.time()-start, 1)
        print(f"✅ ({elapsed}s)")
    except Exception as e:
        print(f"❌ ERROR")
        print(f"   {str(e)[:200]}")
        print("\n⚠️  Ejecución detenida. Corrige el error y vuelve a ejecutar.")
        break

total = round(time.time()-start_total, 1)