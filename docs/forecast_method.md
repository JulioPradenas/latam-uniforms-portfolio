# Metodología de Forecast

## Método
Forecast estadístico basado en historial 2022–2024, implementado en SQL puro (BigQuery).
No se usan modelos de ML — se prioriza transparencia y reproducibilidad.

## Escenarios

| Escenario | Fórmula | Cuándo usarlo |
|---|---|---|
| Base | Promedio histórico semanal | Planificación operacional normal |
| Conservador | Percentil 25 histórico | Budget mínimo, evitar sobrestock |
| Estrés | Percentil 90 × 1.20 | Incorporaciones masivas, shocks de dotación |

## Supuestos
- Estacionalidad no modelada (menos de 3 años de datos históricos)
- Crecimientos de dotación no incluidos — ajustar manualmente si se conocen
- Tallas UNK y regiones UNK_REGION excluidas del forecast
- Semanas con demanda = 0 incluidas, no imputadas

## Limitaciones
- Con 1 semana de historial por combinación, conservador = base
- No captura eventos extraordinarios (cambios de uniforme, fusiones)
- Revisar y recalibrar el forecast cada trimestre con datos actualizados