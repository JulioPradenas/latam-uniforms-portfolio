from google.cloud import bigquery
import pandas as pd
import os

PROJECT = "latam-uniforms-portfolio"
DATASET = "latam_uniforms"
DATA_DIR = "data_gen"

SCHEMAS = {
    "stg_employees": [
        bigquery.SchemaField("employee_id","STRING"),
        bigquery.SchemaField("name","STRING"),
        bigquery.SchemaField("role","STRING"),
        bigquery.SchemaField("region_code","STRING"),
        bigquery.SchemaField("hire_date","STRING"),
        bigquery.SchemaField("is_active","STRING"),
    ],
    "stg_uniform_issues": [
        bigquery.SchemaField("issue_id","STRING"),
        bigquery.SchemaField("employee_id","STRING"),
        bigquery.SchemaField("item","STRING"),
        bigquery.SchemaField("size","STRING"),
        bigquery.SchemaField("region_code","STRING"),
        bigquery.SchemaField("issue_date","STRING"),
        bigquery.SchemaField("quantity","STRING"),
    ],
    "stg_uniform_returns": [
        bigquery.SchemaField("return_id","STRING"),
        bigquery.SchemaField("employee_id","STRING"),
        bigquery.SchemaField("item","STRING"),
        bigquery.SchemaField("size","STRING"),
        bigquery.SchemaField("region_code","STRING"),
        bigquery.SchemaField("return_date","STRING"),
        bigquery.SchemaField("reason","STRING"),
        bigquery.SchemaField("quantity","STRING"),
    ],
    "stg_inventory_snapshots": [
        bigquery.SchemaField("snapshot_id","STRING"),
        bigquery.SchemaField("snapshot_date","STRING"),
        bigquery.SchemaField("region_code","STRING"),
        bigquery.SchemaField("item","STRING"),
        bigquery.SchemaField("size","STRING"),
        bigquery.SchemaField("stock_qty","STRING"),
    ],
    "stg_lead_times": [
        bigquery.SchemaField("lt_id","STRING"),
        bigquery.SchemaField("region_code","STRING"),
        bigquery.SchemaField("item","STRING"),
        bigquery.SchemaField("supplier","STRING"),
        bigquery.SchemaField("lead_time_days","STRING"),
        bigquery.SchemaField("valid_from","STRING"),
        bigquery.SchemaField("valid_to","STRING"),
    ],
    "stg_regions": [
        bigquery.SchemaField("region_code","STRING"),
        bigquery.SchemaField("region_name","STRING"),
        bigquery.SchemaField("country","STRING"),
        bigquery.SchemaField("cluster","STRING"),
    ],
    "stg_sizes": [
        bigquery.SchemaField("size_code","STRING"),
        bigquery.SchemaField("size_label","STRING"),
        bigquery.SchemaField("sort_order","STRING"),
        bigquery.SchemaField("notes","STRING"),
    ],
}

CSV_MAP = {
    "stg_employees":           "employees.csv",
    "stg_uniform_issues":      "uniform_issues.csv",
    "stg_uniform_returns":     "uniform_returns.csv",
    "stg_inventory_snapshots": "inventory_snapshots.csv",
    "stg_lead_times":          "lead_times.csv",
    "stg_regions":             "regions.csv",
    "stg_sizes":               "sizes.csv",
}

client = bigquery.Client(project=PROJECT)

for table_id, csv_file in CSV_MAP.items():
    path = os.path.join(DATA_DIR, csv_file)
    df = pd.read_csv(path, dtype=str).fillna("")
    full_table = f"{PROJECT}.{DATASET}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        schema=SCHEMAS[table_id],
        write_disposition="WRITE_TRUNCATE",
    )
    job = client.load_table_from_dataframe(df, full_table, job_config=job_config)
    job.result()
    print(f"✅ {full_table} ({len(df)} filas)")

print("\n🎉 Carga completa — revisa BigQuery Console")