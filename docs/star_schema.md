# Star Schema — latam_uniforms

## Diagrama
```
                        dim_date
                           |
          dim_employee — — | — — dim_region
                      \    |    /
                       fct_uniform_transactions
                      /         \
                dim_item       dim_size


          dim_region — fct_inventory_daily — dim_size
```

## Tablas

| Tabla | Tipo | Granularidad | Partición |
|---|---|---|---|
| fct_uniform_transactions | Fact | 1 fila por entrega o devolución | — |
| fct_inventory_daily | Fact | 1 fila por snapshot × región × item × talla | — |
| dim_date | Dimensión | 1 fila por día 2022–2027 | — |
| dim_region | Dimensión | 1 fila por región | — |
| dim_size | Dimensión | 1 fila por talla | — |
| dim_item | Dimensión | 1 fila por prenda | — |
| dim_employee | Dimensión | 1 fila por empleado | — |

## Joins principales

| Fact | Dimensión | Llave |
|---|---|---|
| fct_uniform_transactions | dim_region | region_code |
| fct_uniform_transactions | dim_size | size_code |
| fct_uniform_transactions | dim_item | item_name |
| fct_uniform_transactions | dim_employee | employee_id |
| fct_uniform_transactions | dim_date | issue_date = date_day |
| fct_inventory_daily | dim_region | region_code |
| fct_inventory_daily | dim_size | size_code |
| fct_inventory_daily | dim_item | item = item_name |

## Decisiones de diseño
- Todos los campos de tipo STRING en staging para manejar datos sucios
- Tipos correctos se asignan en dims y facts
- Tallas y regiones no reconocidas se mapean a UNK / UNK_REGION
- Facts sin partición (volumen sintético pequeño)