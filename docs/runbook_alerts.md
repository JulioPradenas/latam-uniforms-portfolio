# Runbook de Alertas

## P1 — STOCKOUT_RISK
**Qué significa**: el inventario actual no cubre el lead time de reposición.

**Acción inmediata**:
1. Verificar que el snapshot de inventario es reciente (< 7 días)
2. Contactar proveedor para adelantar entrega
3. Evaluar redistribución desde regiones con stock OK

**Owner**: Procurement

---

## P2 — DATA_QUALITY_SIZE
**Qué significa**: más del 10% de las transacciones de una región
tienen talla no reconocida.

**Acción**:
1. Revisar sistema de origen (HR/WFM) para esa región
2. Solicitar corrección retroactiva de registros
3. Agregar margen +10% al forecast de esa región mientras se corrige

**Owner**: Data Engineering

---

## P2 — FORECAST_DRIFT
**Qué significa**: la demanda real está fuera del rango esperado
entre escenario conservador y estrés.

**Acción**:
1. Verificar si hubo cambio de dotación (ingresos/salidas masivas)
2. Recalibrar forecast con últimos 3 meses
3. Si el drift persiste 3 semanas → escalar a Demand Planning

**Owner**: Demand Planning