# 🛫 Uniform Demand & Stock Reco 2027
### Portfolio Data Analyst — BigQuery · GCP · Looker Studio

![BigQuery](https://img.shields.io/badge/BigQuery-4285F4?style=flat&logo=googlebigquery&logoColor=white)
![GCP](https://img.shields.io/badge/GCP-FF6F00?style=flat&logo=googlecloud&logoColor=white)
![Looker Studio](https://img.shields.io/badge/Looker_Studio-4285F4?style=flat&logo=looker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

---

## 📌 Objetivo

Ciclo completo de análisis de demanda y recomendación de compra de uniformes
para una aerolínea LATAM — desde datos crudos hasta dashboard ejecutivo.

> **Pregunta de negocio**: ¿Qué uniformes comprar en 2027, cuántos y en qué región?

---

## 🎯 Resultados clave

| Métrica | Valor |
|---|---|
| Transacciones procesadas | **~9.000 filas** crudas → modelo dimensional limpio |
| SKU analizados (región × ítem × talla) | **213** combinaciones |
| Plan de compra 2027 | **14.838 unidades** priorizadas por criticidad |
| Riesgos detectados | **6 stockouts · 12 críticos · 18 bajos** |
| Alertas operacionales activas | **3** con owner y SLA asignado |

> El motor prioriza automáticamente los SKU de mayor velocidad de demanda:
> el #1 del ranking es **Zapatos XS — Miami** (demanda 175, stock 0).

---

## 🏗 Arquitectura
```
Fuente (CSV)
    ↓
stg_*          → datos crudos sin tocar
    ↓
stg_*_clean    → limpieza documentada con supuestos
    ↓
dim_* + fct_*  → modelo dimensional (star schema)
    ↓
mart_*         → métricas, forecast, recomendación, alertas
    ↓
Looker Studio / Google Sheets → consumo ejecutivo
```

---

## 📊 Dashboard Looker Studio

🔗 [Ver dashboard en vivo](https://lookerstudio.google.com/reporting/e06687b5-e038-4316-94be-3739edc206b8/page/srjsF/edit)

### Executive Overview
![Executive Overview](looker/screenshots/01_executive_overview.png)

### Operación — Heatmap Talla × Región
![Operación](looker/screenshots/02_operacion.png)

### Alertas y Riesgos
![Alertas](looker/screenshots/03_alertas.png)

---

## 🗂 Estructura del proyecto
```
latam-uniforms-portfolio/
├── data_gen/          ← CSVs sintéticos (~9.000 filas) + generadores
├── sql/
│   ├── 01_staging/    ← limpieza de datos crudos
│   ├── 02_dimensions/ ← dim_date, dim_region, dim_size, dim_item, dim_employee
│   ├── 03_facts/      ← fct_uniform_transactions, fct_inventory_daily
│   └── 04_marts/      ← KPIs, forecast, safety stock, recomendación, alertas
├── scripts/
│   ├── upload_to_bq.py   ← carga CSVs a BigQuery
│   ├── run_all_sql.py    ← ejecuta todos los SQLs en orden
│   └── export_to_sheets.py
├── docs/              ← documentación de supuestos y metodología
├── looker/            ← capturas del dashboard
└── sheets/            ← output ejecutivo Excel
```

---

## 📐 Modelo dimensional

| Tabla | Tipo | Descripción |
|---|---|---|
| `fct_uniform_transactions` | Fact | Entregas y devoluciones de uniformes |
| `fct_inventory_daily` | Fact | Stock por día × región × talla |
| `dim_date` | Dimensión | Calendario 2022–2027 |
| `dim_region` | Dimensión | SCL · LIM · BOG · GRU · EZE · MIA |
| `dim_size` | Dimensión | XS · S · M · L · XL · XXL |
| `dim_item` | Dimensión | Camisa · Pantalon · Chaqueta · Chaleco · Zapatos · Corbata |
| `dim_employee` | Dimensión | Empleados con rol y región |

---

## 🔮 Forecast 2027 — 3 escenarios

| Escenario | Método | Uso |
|---|---|---|
| Base | Promedio histórico semanal | Planificación operacional |
| Conservador | Percentil 25 histórico | Budget mínimo |
| Estrés | Percentil 90 × 1.20 | Shocks de dotación |

---

## 📦 Recomendación de compra

Tabla `mart_purchase_reco_2027` — **213 recomendaciones** priorizadas:

| Prioridad | Significado | Acción | SKU | A comprar |
|---|---|---|---|---|
| P1 STOCKOUT | Sin stock disponible | Compra inmediata | 6 | 1.116 u |
| P2 CRITICO | Stock < Reorder Point | Próxima orden | 12 | 1.798 u |
| P3 BAJO | Stock < ROP × 1.5 | Próximo trimestre | 18 | 2.138 u |
| P4 OK | Stock suficiente | Sin acción | 177 | 9.786 u |

> El *reorder point* y el *safety stock* se calculan con la fórmula estadística de
> servicio al 95% (z = 1.645), combinando varianza de demanda y de *lead time*.
> Ver [Stock Policy](docs/stock_policy.md).

---

## 🚨 Alertas operacionales

3 tipos de alerta en `mart_alerts_daily`:
- **STOCKOUT_RISK** (P1) → Owner: Procurement
- **DATA_QUALITY_SIZE** (P2) → Owner: Data Engineering  
- **FORECAST_DRIFT** (P2) → Owner: Demand Planning

---

## ⚙️ Cómo reproducir el proyecto
```bash
# 1. Clonar el repo
git clone https://github.com/JulioPradenas/latam-uniforms-portfolio.git
cd latam-uniforms-portfolio

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Autenticar GCP
gcloud auth application-default login

# 5. Cargar datos a BigQuery
python scripts/upload_to_bq.py

# 6. Ejecutar todos los SQLs
python scripts/run_all_sql.py
```

---

## 📚 Documentación

| Documento | Descripción |
|---|---|
| [Supuestos de staging](docs/assumptions_staging.md) | Reglas de limpieza y su impacto |
| [Star Schema](docs/star_schema.md) | Modelo dimensional |
| [KPI Definitions](docs/kpi_definitions.md) | Definición de métricas |
| [Forecast Method](docs/forecast_method.md) | Metodología de proyección |
| [Stock Policy](docs/stock_policy.md) | Fórmula de safety stock |
| [Runbook Alertas](docs/runbook_alerts.md) | Acciones ante cada alerta |
| [Executive Pack](docs/executive_pack.md) | Guía del output en Sheets |

---

## 🛠 Stack técnico

- **BigQuery** — SQL avanzado, window functions, modelado dimensional
- **GCP** — BigQuery Sandbox
- **Looker Studio** — dashboards conectados a BigQuery
- **Python** — carga de datos y exportación
- **Google Sheets / Excel** — output ejecutivo

---

## 🧠 Qué demuestra este proyecto

- **Modelado dimensional** — star schema con dimensiones conformadas y dos tablas de hechos.
- **SQL analítico avanzado** — window functions (`ROW_NUMBER`, `RANK`, `PERCENTILE_CONT`),
  CTEs encadenadas, deduplicación y normalización de datos sucios.
- **Limpieza de datos reales** — tallas y regiones inconsistentes (`Extra Large`, `LL`, `xs`)
  normalizadas con reglas documentadas y trazables.
- **Estadística aplicada** — forecast por escenarios y *safety stock* con nivel de servicio.
- **Pensamiento de negocio** — la salida es un plan de compra accionable, no solo tablas.
- **Visualización ejecutiva** — dashboard de 3 páginas orientado a decisión.

---

### Páginas

| Página | Descripción | Fuentes de datos |
|---|---|---|
| Executive Overview | KPIs generales, demanda proyectada 2027 y top críticos | mart_purchase_reco_2027, mart_demand_forecast_2027 |
| Operación | Heatmap talla × región y demanda neta por región | mart_size_heatmap, mart_kpis_weekly |
| Alertas y Riesgos | Alertas activas P1/P2 con owner y detalle | mart_alerts_daily |
