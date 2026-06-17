## Context

El pipeline actual lee las hojas de marca del sheet de precios mensual y las consolida en un solo DataFrame. El reader (`src/sources/sheets/reader.py`) ya normaliza columnas variables (ej. `Desc. Bajaj` → `Desc. marca`) y `main.py` genera flags booleanos a partir de los descuentos.

El problema: durante promociones, el sheet puede tener una hoja adicional (ej. "Arrancan Promos - Junio 2026") con la misma estructura de marca pero con una columna extra `Desc. adicional` y nombres de columna ligeramente distintos (`Bono Galgo` en vez de `Desc. Galgo`). Los modelos en esa hoja tienen el precio final correcto; si se ignoran, el reporte muestra el descuento de marca sin el adicional de promo.

## Goals / Non-Goals

**Goals:**
- Detectar la hoja de promo si existe, sin romper el pipeline si no existe
- Leer la hoja de promo con el mismo mecanismo que las de marca, tolerando variantes de nombre
- Hacer override en el DataFrame consolidado para los modelos de promo
- Exponer `promo_discount`, `is_promo`, `has_promo_discount` en el output

**Non-Goals:**
- Soportar múltiples hojas de promo simultáneas (se toma la primera que coincida)
- Modificar la lógica de escritura al sheet destino más allá de agregar las nuevas columnas
- Crear configuración dinámica para los keywords (se hardcodean por ahora)

## Decisions

### 1. Detección por keyword substring, case-insensitive

La hoja de promo se identifica si su nombre **contiene** alguno de los keywords definidos en una constante en `main.py`:

```python
PROMO_KEYWORDS = ["buen fin", "hot sale", "arrancan promos"]
```

Se usa `any(kw in sheet_name.lower() for kw in PROMO_KEYWORDS)` contra la lista de hojas del spreadsheet.

**Alternativas consideradas:** Prefijo fijo (ej. "PROMO:") — descartado porque requeriría cambiar la convención de nombres en el equipo de pricing.

### 2. Reutilizar `read_brand_sheet` con parámetro de alias de columnas

En lugar de una función nueva, se extiende `reader.py` con una función `read_promo_sheet` que internamente llama la misma lógica de lectura pero con un mapa de alias para columnas variables:

- `Bono Galgo` → `Desc. Galgo` (antes de la normalización estándar)
- `Desc. adicional` → capturada como columna extra `promo_discount`

Esto evita duplicar lógica de lectura de Google Sheets.

### 3. Override en `main.py` post-consolidación, antes de los flags

Después de `pd.concat` de todas las hojas de marca, si hay DataFrame de promo:

```
df_all = pd.concat(brand_dfs)
if df_promo is not None:
    # drop filas de marca para modelos que están en promo
    key = ["brand", "model"]
    df_all = df_all[~df_all.set_index(key).index.isin(df_promo.set_index(key).index)]
    df_all = pd.concat([df_all, df_promo], ignore_index=True)
```

Este approach es simple, sin dependencias extra, y mantiene el orden (modelos de promo al final antes del sort).

### 4. Columnas nuevas con valor por defecto

Para modelos sin promo, `promo_discount = 0`. Los flags se crean con el mismo patrón `np.where` ya usado en `main.py`:

```python
df["promo_discount"] = df["promo_discount"].fillna(0)
df["is_promo"] = np.where(df["is_promo"].fillna(False), True, False)
df["has_promo_discount"] = np.where(df["promo_discount"] > 0, True, False)
```

## Risks / Trade-offs

- **Matching por (brand, model) puede tener falsos positivos** si el mismo modelo tiene variaciones de nombre entre hojas → Mitigation: el equipo de pricing ya normaliza `Modelo MKP` antes de publicar el sheet; no se requiere lógica adicional.
- **Si el equipo agrega una promo con keyword no listado**, no se detectará → Mitigation: lista de keywords centralizada en constante, fácil de ampliar; se documenta en `CLAUDE.md`.
- **Múltiples hojas de promo**: se toma la primera coincidencia → Mitigation: escenario no ocurre actualmente; se agrega log de advertencia si se detectan varias.

## Open Questions

_(ninguna — diseño acordado con el usuario en sesión de exploración)_
