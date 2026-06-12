"""
gen_inventory_topup.py
Genera un snapshot final completo de inventario (2025-12-31) que cubre las 213
combinaciones region×item×talla con demanda proyectada 2027, con stock calibrado
contra el reorder_point real para producir una mezcla creible de prioridades.

Historia: los SKU de mayor velocidad de demanda son los que quedan en riesgo
(stockout / critico), el resto sano. Esto evita el artefacto de combinaciones sin
registro de inventario (que aparecian como P1-STOCKOUT falsos).

Requiere que el pipeline ya haya corrido una vez (lee reorder_point de
mart_purchase_reco_2027). Append idempotente: borra cualquier snapshot previo
de SNAPSHOT_DATE antes de reescribir.

Uso: python data_gen/gen_inventory_topup.py
"""

import random
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

PROJECT = "latam-uniforms-portfolio"
DATASET = "latam_uniforms"
CSV_PATH = Path(__file__).parent / "inventory_snapshots.csv"
SNAPSHOT_DATE = "2025-12-31"

# Reparto objetivo de prioridades sobre las 213 combinaciones
N_STOCKOUT = 6    # P1 - sin stock
N_CRITICO = 12    # P2 - bajo reorder point
N_BAJO = 18       # P3 - entre rop y rop*1.5
# resto -> P4 OK

random.seed(2027)


def fetch_combos() -> pd.DataFrame:
    client = bigquery.Client(project=PROJECT)
    sql = f"""
        SELECT region_code, item_name AS item, size_code AS size,
               annual_demand_base, reorder_point
        FROM `{PROJECT}.{DATASET}.mart_purchase_reco_2027`
    """
    return client.query(sql).to_dataframe()


def assign_stock(df: pd.DataFrame) -> pd.DataFrame:
    # Mayor demanda primero -> los de mas velocidad caen en riesgo
    df = df.sort_values("annual_demand_base", ascending=False).reset_index(drop=True)

    def stock_for(rank: int, rp: float) -> int:
        jitter = random.uniform(0.9, 1.15)
        if rank < N_STOCKOUT:
            return 0
        if rank < N_STOCKOUT + N_CRITICO:
            return max(1, round(rp * 0.5 * jitter))           # < rop
        if rank < N_STOCKOUT + N_CRITICO + N_BAJO:
            return round(rp * 1.2 * jitter)                   # rop .. rop*1.5
        return round((rp * 2.0 + df.loc[rank, "annual_demand_base"] * 0.15) * jitter)

    df["stock_qty"] = [stock_for(i, df.loc[i, "reorder_point"]) for i in range(len(df))]
    return df


def main() -> None:
    combos = assign_stock(fetch_combos())

    existing = pd.read_csv(CSV_PATH, dtype=str)
    existing = existing[existing["snapshot_date"] != SNAPSHOT_DATE]
    start_n = len(existing)

    new_rows = pd.DataFrame({
        "snapshot_id": [f"SNP9{i:05d}" for i in range(len(combos))],
        "snapshot_date": SNAPSHOT_DATE,
        "region_code": combos["region_code"],
        "item": combos["item"],
        "size": combos["size"],
        "stock_qty": combos["stock_qty"].astype(int),
    })

    out = pd.concat([existing, new_rows], ignore_index=True)
    out.to_csv(CSV_PATH, index=False)

    mix = combos.assign(
        priority=combos.apply(
            lambda r: "P1" if r.stock_qty == 0
            else "P2" if r.stock_qty < r.reorder_point
            else "P3" if r.stock_qty < r.reorder_point * 1.5
            else "P4", axis=1)
    )["priority"].value_counts().sort_index()

    print(f"CSV: {start_n} filas previas + {len(new_rows)} snapshot {SNAPSHOT_DATE} = {len(out)}")
    print(f"Mezcla esperada de prioridades:\n{mix.to_string()}")


if __name__ == "__main__":
    main()
