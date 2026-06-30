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

PROMO_KEYWORDS = ["buen fin", "hot sale", "arrancan promos"]


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
    SHEET_NAME = "🏟️⚽🔥 Lista de Precios Julio | 2026"
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
        "Sharmax"
    ]
    PERCENTAGE_BRANDS = {"CF Moto & CF LITE", "Sharmax"}

    print(f"\nLeyendo hojas de precios desde '{SHEET_NAME}'...")
    hojas = price_reader.read_sheets_by_brands(SHEET_NAME, marcas, percentage_brands=PERCENTAGE_BRANDS)

    # ── 3. Consolidar ─────────────────────────────────────────────────────────
    df_all = pd.concat(hojas.values(), ignore_index=True)

    # ── 3b. Override con hoja de promo (si existe) ───────────────────────────
    print("\nBuscando hoja de promo...")
    promo_tab = price_reader.detect_promo_sheet(SHEET_NAME, PROMO_KEYWORDS)
    if promo_tab:
        df_promo = price_reader.read_promo_sheet(SHEET_NAME, promo_tab)
        df_promo_clean = (
            df_promo[df_promo["Marca"].notna()]
            .drop_duplicates(subset=["Marca", "Modelo MKP"], keep="first")
            .copy()
        )
        promo_key = pd.MultiIndex.from_arrays([df_promo_clean["Marca"], df_promo_clean["Modelo MKP"]])
        brand_key = pd.MultiIndex.from_arrays([df_all["Marca"], df_all["Modelo MKP"]])
        df_all = pd.concat([df_all[~brand_key.isin(promo_key)], df_promo_clean], ignore_index=True)
        print(f"  → {len(df_promo_clean)} modelos con promo activa")

    # Rellenar columnas de promo para modelos sin promo
    if "promo_discount" not in df_all.columns:
        df_all["promo_discount"] = 0
    else:
        df_all["promo_discount"] = df_all["promo_discount"].fillna(0)
    if "is_promo" not in df_all.columns:
        df_all["is_promo"] = False
    else:
        df_all["is_promo"] = df_all["is_promo"].fillna(False)

    df_columns_selected = df_all[
        [
            "Marca",
            "Modelo MKP",
            "Año",
            "Desc. marca",
            "Desc. Galgo",
            "Total desc.",
            "Precio Galgo (c/IVA)",
            "promo_discount",
            "is_promo",
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
    df_columns_selected["has_promo_discount"] = np.where(
        df_columns_selected["promo_discount"] > 0, True, False
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
            # promo_discount e is_promo ya están en inglés
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
                "promo_discount",
                "total_discount",
                "price_net",
                "has_galgo_discount",
                "has_brand_discount",
                "has_brand_and_galgo_discount",
                "is_promo",
                "has_promo_discount",
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
