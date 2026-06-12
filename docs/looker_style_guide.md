# Guía de mejora estética — Dashboard Looker Studio

Guía paso a paso para pulir visualmente el reporte **Uniformes_LATAM** en Looker Studio.
Todo es manual en la UI (Looker no tiene API de edición). Sigue el orden: primero el
tema global, luego la paleta semántica, después cada página, y al final el checklist.

> Datos ya correctos: scorecard *Unidades a Comprar* = **14.838**, mezcla P1/P2/P3/P4.
> Esta guía es solo presentación, no toca el dato.

---

## 0. Tema global (una sola vez)

`Tema y diseño` (barra superior) → pestaña **Tema**:

- **Personalizar** sobre el tema oscuro actual (mantener fondo oscuro, se ve moderno).
- **Fuente**: una sola familia en todo el reporte (ej. *Roboto* o *Open Sans*).
- **Color de acento principal**: azul `#4285F4` (consistente con los badges del README).
- **Bordes de componentes**: radio 8 px, sombra sutil — da aspecto de tarjetas.

`Tema y diseño` → pestaña **Diseño**:

- **Modo de visualización**: ajustar al ancho.
- **Navegación entre páginas**: *Pestañas en la parte superior izquierda* (más limpio que el menú).

---

## 1. Paleta semántica de prioridad (clave para que se vea profesional)

Usa **los mismos 4 colores** para prioridad/severidad en TODAS las páginas:

| Nivel | Color | Hex |
|---|---|---|
| P1 — Stockout | Rojo | `#D93025` |
| P2 — Crítico | Naranja | `#F29900` |
| P3 — Bajo | Amarillo | `#F9D71C` |
| P4 — OK | Verde | `#188038` |

Se aplican vía **Formato condicional** en tablas y **paleta de dimensión** en gráficos
(ver cada página). La coherencia de color es lo que más eleva la percepción de calidad.

---

## 2. Página 1 — Executive Overview

### 2.1 Scorecards (fila superior)
- **Unidades a Comprar (Base)**: formato número → separador de miles, 0 decimales.
  Etiqueta clara: "Unidades a comprar 2027 (base)". Color de número azul acento.
- ⚠️ **Scorecard "priority 0"**: está roto (muestra 0). Reemplázalo por algo útil:
  - *SKU en riesgo* = recuento de filas con `priority` en (P1, P2, P3) → debería dar **36**, o
  - *Inversión estimada* = SUM(`qty_to_buy_base`) × costo unitario si tienes precio.
- **Alertas P1 Activas (3)**: número en rojo `#D93025`, ícono de campana si se puede.
- Igualar tamaño y alineación de las 3 tarjetas; agregar un título de sección arriba.

### 2.2 Gráfico "Demanda Proyectada 2027 — 3 Escenarios" (arregla el diente de sierra)
La forma de sierra es porque grafica por día sobre datos semanales. Arréglalo así:
- Selecciona el gráfico → **Datos** → dimensión de fecha `week` → engranaje → **Tipo: Semana** (o Mes).
- **Estilo** → serie → **Suavizar línea** (curvas), grosor 2 px.
- **Estilo** → **Datos faltantes**: *Saltar* o *Interpolación lineal* (NO "cero").
- Colores de serie: base azul, conservador gris, estrés naranja (escenario de riesgo).
- Leyenda abajo, eje Y con separador de miles.

### 2.3 Tabla de recomendación
- Ocultar columnas técnicas (`criticality_rank`, `reorder_point` si no aporta al ejecutivo).
- **Formato condicional** en la columna `priority` con la paleta de la sección 1.
- `qty_to_buy_base` / `qty_to_buy_stress`: número con separador de miles, alineado a la derecha.
- Encabezados en negrita, filas alternas (banding) sutil, paginación a 10–15 filas.
- Ordenar por `criticality_rank` ascendente (lo más crítico arriba).

---

## 3. Página 2 — Operación

### 3.1 Heatmap Talla × Región (`mart_size_heatmap`)
- Ya usa barra de `pct_share` en rojo — déjala, pero usa **escala de color secuencial**
  (claro→intenso) en vez de un solo rojo plano, para que "lea" como heatmap real.
- Ocultar `total_issues` si satura; o ponerlo como columna fina a la izquierda.
- Considera cambiar a **Tabla dinámica (pivot)** con `size_code` en columnas y `region_code`
  en filas, métrica `total_issues` con mapa de calor — es el formato heatmap canónico.

### 3.2 "Demanda Neta por Región" (barras)
- Ordenar barras de mayor a menor (SCL arriba) — ya está, mantener.
- Una sola serie azul acento, etiquetas de dato visibles con separador de miles.
- Eje X con miles abreviados (2K) o completos, pero consistente con el resto.
- Título descriptivo: "Demanda neta acumulada por región (2022–2025)".

---

## 4. Página 3 — Alertas

### 4.1 Tabla "Alertas Activas" (`mart_alerts_daily`)
- **Formato condicional** por `severity`: P1 rojo, P2 naranja (paleta sección 1).
- Columna `detail`: el texto `DoH=-93 dias` se ve técnico/negativo. Opciones:
  - Manual en Looker: renombrar encabezado a "Días de cobertura vs lead time".
  - O (capa de datos) limpiar el texto en `mart_alerts_daily` para que no muestre negativos.
- `alert_date`, `owner`, `region_code`, `item_name` visibles; ocultar `Record Count`.

### 4.2 "Evolución de Alertas" (serie temporal)
- Hoy muestra un solo punto (12 jun) → se ve vacío. Mejor:
  - Cambiar a **scorecard grande** "Alertas P1 hoy: 3" mientras haya un solo día de datos, o
  - Dejar la línea pero con marcador de punto visible y rango de fechas explícito.

---

## 5. Toques transversales (todas las páginas)

- **Filtros** (region_code, item_name, alert_type, owner): alinear arriba, mismo ancho,
  fondo de tarjeta. **Capturar siempre con los dropdowns cerrados.**
- **Título de cada página** arriba a la izquierda + una línea de subtítulo gris.
- **Espaciado**: alinear componentes a una grilla; márgenes iguales; nada pegado al borde.
- **Pie de página**: "Fuente: BigQuery · latam_uniforms · actualizado [fecha]".
- **Interacciones cruzadas**: activar *Aplicar filtro al hacer clic* en las tablas para que
  seleccionar una región filtre el resto de la página (se siente interactivo en demo).

---

## 6. Checklist final antes de recapturar

- [ ] Tema oscuro consistente, una sola fuente, acento azul.
- [ ] Paleta P1–P4 idéntica en las 3 páginas.
- [ ] Scorecard *Unidades a comprar* = 14.838 con miles; scorecard roto reemplazado.
- [ ] Gráfico de demanda suave (agrupado por semana/mes, sin ceros).
- [ ] Tablas con formato condicional, miles y columnas técnicas ocultas.
- [ ] Títulos y subtítulos por página; filtros alineados y cerrados.
- [ ] Recapturar las 3 páginas → guardar en `looker/screenshots/`
      (`01_executive_overview.png`, `02_operacion.png`, `03_alertas.png`).
