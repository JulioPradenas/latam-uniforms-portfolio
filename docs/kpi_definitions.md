# Definiciones de KPIs

| KPI | Definición | Unidad | Cómo leerlo |
|---|---|---|---|
| issues_qty | Total entregas de uniformes en la semana | unidades | Demanda bruta |
| returns_qty | Total devoluciones en la semana | unidades | Uniformes recuperados |
| net_demand | Entregas − devoluciones | unidades | Positivo = consumo neto real |
| current_stock | Stock disponible en el último snapshot | unidades | Inventario actual |
| days_on_hand (DoH) | stock_actual ÷ demanda_semanal | días | < lead_time = riesgo de quiebre |
| stock_status | Semáforo de riesgo | categoría | STOCKOUT / CRITICO / BAJO / OK |
| pct_share | % que representa una talla del total región+prenda | % | Priorizar compra por volumen |
| rank_by_volume | Ranking de tallas por volumen dentro de región+prenda | número | 1 = talla más demandada |
| demand_stddev | Desviación estándar de demanda | unidades | Alta = mayor variabilidad = más stock de seguridad |