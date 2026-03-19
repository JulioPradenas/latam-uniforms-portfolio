from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project="latam-uniforms-portfolio")

df = client.query("""
  SELECT
    region_code          AS Region,
    item_name            AS Prenda,
    size_code            AS Talla,
    on_hand              AS Stock_Actual,
    reorder_point        AS Punto_Reorden,
    safety_stock_95      AS Stock_Seguridad,
    annual_demand_base   AS Demanda_Anual_Base,
    annual_demand_stress AS Demanda_Anual_Estres,
    qty_to_buy_base      AS Compra_Recomendada_Base,
    qty_to_buy_stress    AS Compra_Escenario_Estres,
    priority             AS Prioridad,
    criticality_rank     AS Ranking_Criticidad
  FROM `latam-uniforms-portfolio.latam_uniforms.mart_purchase_reco_2027`
  ORDER BY criticality_rank ASC
""").to_dataframe()

df.to_excel("sheets/purchase_reco_2027.xlsx", index=False)
print(f"Exportado: {len(df)} filas -> sheets/purchase_reco_2027.xlsx")