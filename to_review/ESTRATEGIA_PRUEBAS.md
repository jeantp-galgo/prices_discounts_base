# Estrategia de pruebas — bonos_galgo

> Documento de referencia para implementar la suite de pruebas más adelante.
> Estado: **recomendación aprobada**, pendiente de implementar.

## Contexto

`bonos_galgo` es un pipeline diario (GitHub Actions, 4 AM UTC) que:
1. Lee inventario y hojas de precios por marca desde **Google Sheets**.
2. **Transforma** los datos (conversión de % a pesos, deduplicación, flags de descuento, override de promos, merge con inventario, reordenamiento de columnas).
3. Reescribe el resultado en la hoja `[MKP - MX] Bonos en modelos`.

Hoy **no existe ninguna prueba** (`tests/` no existe). El riesgo real: la lógica de negocio corre sin red de seguridad y se ejecuta desatendida cada día contra Sheets de producción. Un cambio en nombres de columnas/pestañas o en el formato de un descuento puede romper el reporte silenciosamente.

Un obstáculo estructural: **la lógica de transformación vive inline dentro de `main()`** ([main.py](main.py)) y mezclada con I/O en [reader.py](src/sources/sheets/reader.py). Además `_pct_to_float` es un closure anidado ([reader.py:75-80](src/sources/sheets/reader.py#L75-L80)), no importable. Para probar bien hay que separar *transformación pura* de *I/O*.

---

## Tipos de prueba aplicables (pirámide)

### 1. Unit tests — lógica pura de transformación (máxima prioridad)
Prueban funciones que reciben un DataFrame y devuelven otro, **sin tocar Sheets**. Rápidos, deterministas, alto valor.

Candidatos (algunos requieren extraerse primero, ver "Refactor previo"):
- **Conversión % → pesos** (`_pct_to_float` + multiplicación por precio). Casos: `"20%"`, `"20"`, `20`, `""`, `"abc"` → NaN, negativos, celda vacía. [reader.py:75-83](src/sources/sheets/reader.py#L75-L83)
- **Filtrado de inventario + dedup por `code`** (`status ∈ {available, no_stock}`, `keep="first"`). [main.py:31-35](main.py#L31-L35)
- **Flags booleanos** (`has_galgo_discount`, `has_brand_discount`, `has_brand_and_galgo_discount`, `has_promo_discount`), incluyendo bordes (0, negativos, NaN). [main.py:102-116](main.py#L102-L116)
- **Override de promo**: reemplazo de filas por clave `(Marca, Modelo MKP)` y dedup de promo. [main.py:64-74](main.py#L64-L74)
- **Normalización de columnas**: `Desc. {marca}` → `Desc. marca`, `Bono Galgo` → `Desc. Galgo`, `Desc. adicional` → `promo_discount`. [reader.py:61-90](src/sources/sheets/reader.py#L61-L90) y [reader.py:136-157](src/sources/sheets/reader.py#L136-L157)
- **Merge con inventario** (left join, asignación de `code`, modelos sin match → `code` NaN). [main.py:139-144](main.py#L139-L144)
- **Reemplazo `GOES` → `CF Moto`** y renombrado final de columnas. [main.py:120-136](main.py#L120-L136)
- **`start_row`** (única función pura ya aislada). [reader.py:187-193](src/sources/sheets/reader.py#L187-L193)

### 2. Integration tests — con Google Sheets mockeado
Prueban `GoogleSheetReader` y el flujo de `main()` **sin red**, sustituyendo el cliente gspread por un doble (mock/fake). Verifican el pegamento entre lectura, transformación y escritura.
- `detect_promo_sheet`: 0 matches → `None`; 1 match; >1 matches → usa el primero + warn; case-insensitive; ignora pestañas ocultas. [reader.py:103-123](src/sources/sheets/reader.py#L103-L123)
- `read_sheets_by_brands`: marca sin pestaña → warn y se omite; ninguna marca encontrada → `ValueError`. [reader.py:93-99](src/sources/sheets/reader.py#L93-L99)
- `update_sheet`: `clear_data=True` limpia y escribe desde fila 1; `clear_data=False` anexa sin header. [reader.py:162-193](src/sources/sheets/reader.py#L162-L193)
- Flujo `main()` end-to-end con Sheets falsos: dado un set de hojas de entrada, el DataFrame final tiene las columnas esperadas, en el orden esperado, ordenado por `has_galgo_discount`.

Herramientas: `unittest.mock` / `monkeypatch` de pytest, o `pytest-mock`. Se mockea `GoogleSheetClient.get_client()` para devolver un spreadsheet falso; los DataFrames de entrada se cargan desde fixtures.

### 3. Smoke / contrato de datos (schema tests)
Barato y muy efectivo contra "se movió una columna":
- El output final tiene **exactamente** las 14 columnas esperadas y en orden. [main.py:146-167](main.py#L146-L167)
- Tipos correctos: flags son `bool`, descuentos y `price_net` son numéricos.
- Invariantes: `code` único donde no es NaN; sin filas con `Marca` nula; `total_discount` ≈ `brand_discount + galgo_discount (+ promo)` si esa relación aplica.
- Validación opcional con **pandera** o **great_expectations** para declarar el esquema del output.

### 4. Regression / golden-file tests
Congelar un input representativo (fixtures CSV/Parquet) y comparar el output contra un "golden" aprobado. Detecta cualquier cambio no intencional en la transformación completa. Usar `pandas.testing.assert_frame_equal`.

### 5. (Fuera de alcance por ahora) Pruebas contra Sheets reales
Un test manual/on-demand que corra contra una copia de staging del Sheet. Útil pero lento y con credenciales; mantener separado de la suite rápida y **no** en cada push.

---

## Refactor previo recomendado (habilitador)

Para que los unit tests sean posibles sin mocks pesados, extraer la lógica pura de `main()` a un módulo nuevo, p. ej. `src/transform/bonos.py`, con funciones sin I/O:
- `filter_inventory(df) -> df`
- `pct_to_float(x) -> float` (subir el closure a función de módulo)
- `convert_percentage_discount(df, price_col) -> df`
- `add_discount_flags(df) -> df`
- `apply_promo_override(df_all, df_promo) -> df`
- `rename_and_select_output(df) -> df`
- `merge_inventory(df, df_inventory) -> df`

`main()` queda como orquestador: leer (I/O) → llamar funciones puras → escribir (I/O). Este refactor NO cambia comportamiento; conviene blindarlo primero con un golden-file test del output actual.

---

## Punto de partida sugerido (orden de implementación)

1. **Scaffolding**: `pip install pytest pytest-mock pandas`; crear `tests/`, `pytest.ini` (o `[tool.pytest]`), `tests/fixtures/` con CSVs pequeños de entrada.
2. **Golden-file test** del `main()` actual (con Sheets mockeado) para blindar el refactor.
3. **Refactor** de la lógica pura a `src/transform/bonos.py`.
4. **Unit tests** de las funciones puras (empezar por `pct_to_float` y flags — máximo valor / mínimo esfuerzo).
5. **Integration tests** de `reader.py` con cliente mock (`detect_promo_sheet`, `read_sheets_by_brands`, `update_sheet`).
6. **Schema/contrato** del output (14 columnas, tipos, invariantes).

---

## CI

Agregar workflow `.github/workflows/tests.yml`:
- Trigger: `push` y `pull_request`.
- Pasos: checkout → setup-python → `pip install -r requirements.txt pytest pytest-mock` → `pytest -q`.
- Corre solo unit + integration (con mocks); **no** requiere credenciales de Google, así que es seguro en PRs.
- Independiente del cron existente [daily_bonos.yml](.github/workflows/daily_bonos.yml).

---

## Verificación

- `pytest -q` en verde localmente y en el workflow de CI.
- Cobertura opcional con `pytest --cov=src` para confirmar que las transformaciones críticas quedan cubiertas.
- El golden-file test debe seguir pasando después del refactor (prueba de que no cambió el comportamiento).
