"""
Reporte de bonos Galgo — México
Actualiza la hoja '[MKP - MX] Bonos en modelos' con los precios y descuentos
vigentes extraídos del sheet de lista de precios.

Ejecución:
    python main.py
"""

import pandas as pd
import numpy as np
from src.sources.sheets.reader import GoogleSheetReader
from src.config.settings import MONITOR_CREDENTIALS, PRICE_SHEETS_CREDENTIALS


def main():
    monitor_reader = GoogleSheetReader(MONITOR_CREDENTIALS)
    price_reader   = GoogleSheetReader(PRICE_SHEETS_CREDENTIALS)

    # ── 1. Inventario ────────────────────────────────────────────────────────
    print("Leyendo inventario...")
    google_sheet_info = {
        "sheet_name": "[MKP] Precios no duplicados",
        "worksheet": "Base MX Moto",
    }
    df_inventory = monitor_reader.read_sheet(google_sheet_info)
    df_inventory = df_inventory[["code", "brand", "model", "status"]]

    df_inventory = (
        df_inventory[df_inventory["status"].isin(["available", "no_stock"])]
        .drop_duplicates(subset=["code"], keep="first")
        .reset_index(drop=True)
    )
    print(f"  → {len(df_inventory)} modelos en inventario")

    # ── 2. Lista de precios por marca ─────────────────────────────────────────
    SHEET_NAME = "🌎🏆⚽ Lista de Precios Junio | 2026"
    marcas = [
        "Bajaj",
        "TVS",
        "Vento",
        "Yamaha",
        "Hero",
        "Honda",
        "Suzuki",
        "Italika",
        "Morbidelli",
        "CF Moto & CF LITE",
    ]

    print(f"\nLeyendo hojas de precios desde '{SHEET_NAME}'...")
    hojas = price_reader.read_sheets_by_brands(SHEET_NAME, marcas)

    # ── 3. Consolidar ─────────────────────────────────────────────────────────
    df_all = pd.concat(hojas.values(), ignore_index=True)

    df_columns_selected = df_all[
        [
            "Marca",
            "Modelo MKP",
            "Año",
            "Desc. marca",
            "Desc. Galgo",
            "Total desc.",
            "Precio Galgo (c/IVA)",
        ]
    ]

    # ── 4. Flags de descuento ─────────────────────────────────────────────────
    df_columns_selected = df_columns_selected.copy()
    df_columns_selected["has_galgo_discount"] = np.where(
        df_columns_selected["Desc. Galgo"] > 0, True, False
    )
    df_columns_selected["has_brand_discount"] = np.where(
        df_columns_selected["Desc. marca"] > 0, True, False
    )
    df_columns_selected["has_brand_and_galgo_discount"] = np.where(
        (df_columns_selected["has_galgo_discount"] > 0)
        & (df_columns_selected["has_brand_discount"] > 0),
        True,
        False,
    )

    # ── 5. Limpieza ───────────────────────────────────────────────────────────
    df_columns_selected = df_columns_selected[df_columns_selected["Marca"].notna()]
    df_columns_selected["Marca"] = df_columns_selected["Marca"].replace(
        "GOES", "CF Moto"
    )

    df_columns_selected.rename(
        columns={
            "Marca": "brand",
            "Modelo MKP": "model",
            "Año": "year",
            "Desc. marca": "brand_discount",
            "Desc. Galgo": "galgo_discount",
            "Total desc.": "total_discount",
            "Precio Galgo (c/IVA)": "price_net",
        },
        inplace=True,
    )

    # ── 6. Join con inventario ────────────────────────────────────────────────
    df_merged = pd.merge(
        df_columns_selected,
        df_inventory[["code", "brand", "model"]],
        on=["brand", "model"],
        how="left",
    )

    df_final = (
        df_merged[
            [
                "code",
                "brand",
                "model",
                "year",
                "brand_discount",
                "galgo_discount",
                "total_discount",
                "price_net",
                "has_galgo_discount",
                "has_brand_discount",
                "has_brand_and_galgo_discount",
            ]
        ]
        .sort_values(by="has_galgo_discount", ascending=False)
        .reset_index(drop=True)
    )

    print(f"\n  → {len(df_final)} filas en el reporte final")

    # ── 7. Escribir resultado ─────────────────────────────────────────────────
    print("\nActualizando hoja destino...")
    google_sheet_info_out = {
        "sheet_name": "[MKP - MX] Bonos en modelos",
        "worksheet": "Base MX Moto",
        "df": df_final,
    }
    monitor_reader.update_sheet(google_sheet_info_out, clear_data=True)
    print("  ✓ Actualizado: Bonos en modelos")


if __name__ == "__main__":
    main()
