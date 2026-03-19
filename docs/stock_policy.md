# Política de Stock de Seguridad

## Fórmula
SS = Z × √(LT_avg × σ_demand² + D_avg² × σ_LT²)

| Variable | Descripción |
|---|---|
| Z | Z-score nivel de servicio (95% → 1.645) |
| LT_avg | Lead time promedio por región/prenda (días) |
| σ_demand | Desviación estándar demanda semanal |
| D_avg | Demanda promedio semanal |
| σ_LT | Desviación estándar del lead time |

## Nivel de servicio: 95%
El costo de un empleado sin uniforme (operación detenida) es mayor
que el costo de mantener sobrestock.

## Supuestos
- Lead time default = 14 días cuando no hay dato del proveedor
- Demanda semanal asumida con distribución normal
- Stock actual = último snapshot disponible

## Reorder Point
ROP = D_avg × (LT_avg / 7) + SS

## Prioridades de compra
- P1 STOCKOUT → compra inmediata, sin stock disponible
- P2 CRITICO  → incluir en próxima orden de compra
- P3 BAJO     → planificar para próximo trimestre
- P4 OK       → sin acción inmediata