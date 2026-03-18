from google.cloud import bigquery

client = bigquery.Client(project="latam-uniforms-portfolio")
result = client.query("SELECT 1 AS test").result()
for row in result:
    print(f"✅ Conexión exitosa. Resultado: {row.test}")