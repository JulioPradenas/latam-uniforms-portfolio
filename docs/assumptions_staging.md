# Supuestos de limpieza — Staging

## uniform_issues

| Campo | Problema encontrado | Regla aplicada | Impacto en negocio |
|---|---|---|---|
| size | Valores: "xs","M.","LL","Extra Large","" | Mapeo a códigos estándar; no reconocidos → UNK | Filas con UNK excluidas de recomendación de compra |
| issue_date | ~8% nulo o vacío | Excluir fila | Se pierde ~8% del historial; sesgo leve en estacionalidad |
| quantity | Vacío o no numérico | Excluir fila | Afecta < 5% de registros |
| issue_id | Duplicados ~5% | Conservar fila más reciente (ROW_NUMBER) | Evita sobrecontar demanda |
| region_code | "Santiago", "lima", etc. | Mapeo a código interno | Sin pérdida de datos |

## uniform_returns

| Campo | Problema encontrado | Regla aplicada | Impacto en negocio |
|---|---|---|---|
| size | Valores sucios ~12% | Mismo mapeo que issues | Devoluciones con UNK no afectan forecast |
| return_date | ~6% nulo | Excluir fila | Pérdida menor en historial de devoluciones |
| quantity | No numérico | Excluir fila | Afecta < 5% de registros |

## inventory_snapshots

| Campo | Problema encontrado | Regla aplicada | Impacto en negocio |
|---|---|---|---|
| stock_qty | Valores negativos ~4% | Reemplazar por 0 con GREATEST(0,...) | Puede subestimar quiebres reales |
| snapshot_date | Nulo ~5% | Excluir fila | Gaps en serie de inventario diario |
| size | Valores sucios ~10% | Mapeo a UNK | Stock UNK no se usa en recomendación |
| region_code | Valores inconsistentes ~10% | Mapeo a código interno o UNK_REGION | Pérdida menor de registros |

## Reglas generales
- Tallas válidas: XS · S · M · L · XL · XXL
- Regiones válidas: SCL · LIM · BOG · GRU · EZE · MIA
- Todo valor no reconocido → UNK o UNK_REGION
- Filas sin fecha válida → excluidas (no se pueden usar en series de tiempo)

## Alertas de calidad
- Si % tallas UNK > 10% en cualquier región → alerta P2
- Si % fechas nulas > 15% → revisar fuente de datos origen