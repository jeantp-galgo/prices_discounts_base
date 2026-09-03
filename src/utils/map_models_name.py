"""
Mapeo de nombres de modelo contra la hoja "Mapeos" del Google Sheets de precios.

Misma lógica usada en Marketplace/update_marketplace_prices: la hoja "Mapeos"
permite corregir, por marca, un nombre de modelo tal como llega en el listado
(nombre_limpio) por el nombre que sí matchea con el catálogo de inventario
(nombre_reemplazar). Cubre los casos donde el modelo no obtiene "code" por un
espacio de más o por diferencias de mayúsculas/minúsculas frente a Galgo.
"""

from typing import Any, Dict, Union

import pandas as pd


def normalize_brand_name(marca: Any) -> str:
    """Normaliza el nombre de marca para comparar entre listado de precios y Mapeos."""
    if marca is None or pd.isna(marca):
        return ""
    s = str(marca).strip().lower()
    if s in ("cf moto", "cf_moto"):
        return "cf_moto"
    elif s in ("qj motor", "qj_motor"):
        return "qj_motor"
    return s


def load_mapeos_por_marca(
    gsheets_client, sheet_name: str, worksheet: str = "Mapeos"
) -> Dict[str, Dict[str, str]]:
    """
    Lee la hoja "Mapeos" y arma un dict {marca_normalizada: {nombre_limpio: nombre_reemplazar}}.

    Ignora filas con nombre_reemplazar vacío (todavía sin resolver).
    """
    df = gsheets_client.read_sheet({"sheet_name": sheet_name, "worksheet": worksheet})
    df = df.reset_index(drop=True).dropna(how="all").dropna(axis=1, how="all")

    columnas_requeridas = {"marca", "nombre_limpio", "nombre_reemplazar"}
    faltantes = columnas_requeridas - set(df.columns)
    if faltantes:
        raise ValueError(
            f"La hoja '{worksheet}' no tiene las columnas requeridas: {sorted(faltantes)}. "
            f"Columnas encontradas: {list(df.columns)!r}"
        )

    df = df[df["nombre_reemplazar"].notna() & (df["nombre_reemplazar"].astype(str).str.strip() != "")]
    df["marca"] = df["marca"].astype(str).apply(normalize_brand_name)

    mapeos: Dict[str, Dict[str, str]] = {}
    for marca, grupo in df.groupby("marca"):
        mapeos[marca] = dict(
            zip(
                grupo["nombre_limpio"].astype(str).str.strip(),
                grupo["nombre_reemplazar"].astype(str).str.strip(),
            )
        )
    return mapeos


def map_model_name(modelo: Union[str, float, Any], mapeo_nombres: Dict[str, str]) -> Any:
    """Reemplaza el nombre de modelo si está en el mapeo; si no, lo deja igual."""
    if pd.isna(modelo):
        return modelo
    modelo_limpio = str(modelo).strip()
    return mapeo_nombres.get(modelo_limpio, modelo_limpio)
