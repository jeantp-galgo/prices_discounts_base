## 1. Constante de keywords y detección en reader.py

- [x] 1.1 Agregar constante `PROMO_KEYWORDS = ["buen fin", "hot sale", "arrancan promos"]` en `main.py`
- [x] 1.2 Agregar función `detect_promo_sheet(spreadsheet, keywords)` en `reader.py` que itere las hojas del spreadsheet y retorne el nombre de la primera hoja cuyo nombre (lowercase) contenga algún keyword, o `None` si no hay ninguna
- [x] 1.3 Agregar log informativo cuando se detecta una hoja de promo (nombre detectado) y advertencia si se detectan varias

## 2. Lectura de la hoja de promoción

- [x] 2.1 Agregar función `read_promo_sheet(spreadsheet, sheet_name)` en `reader.py` que lea la hoja y aplique alias de columnas antes de la normalización estándar: `Bono Galgo` → `Desc. Galgo`, captura de `Desc. adicional` → `promo_discount`
- [x] 2.2 Si `Desc. adicional` no existe en la hoja, agregar la columna `promo_discount` con valor 0
- [x] 2.3 Agregar columna `is_promo = True` a todas las filas leídas desde la hoja de promo

## 3. Override en la consolidación (main.py)

- [x] 3.1 Después del `pd.concat` de hojas de marca, llamar `detect_promo_sheet` y, si retorna un nombre, llamar `read_promo_sheet`
- [x] 3.2 Aplicar el override: eliminar del DataFrame consolidado las filas cuyo `(brand, model)` aparezca en el DataFrame de promo, luego concatenar las filas de promo
- [x] 3.3 Para modelos sin promo, rellenar `promo_discount = 0` e `is_promo = False`

## 4. Nuevas columnas en el output

- [x] 4.1 Agregar `promo_discount` a la lista de columnas seleccionadas en `main.py`, en posición adyacente a `galgo_discount`
- [x] 4.2 Crear flag `has_promo_discount` con `np.where(df["promo_discount"] > 0, True, False)`, consistente con los flags existentes
- [x] 4.3 Incluir `is_promo` y `has_promo_discount` en las columnas finales del DataFrame de salida
- [x] 4.4 Verificar que el orden de columnas en el output quede: `code, brand, model, year, brand_discount, galgo_discount, promo_discount, total_discount, price_net, has_galgo_discount, has_brand_discount, has_brand_and_galgo_discount, is_promo, has_promo_discount`

## 5. Verificación

- [ ] 5.1 Ejecutar `main.py` con el sheet que contiene la hoja "Arrancan Promos" y confirmar que los modelos de promo aparecen con `is_promo = True` y `promo_discount > 0`
- [ ] 5.2 Confirmar que los modelos duplicados (en promo y en hoja de marca) aparecen una sola vez en el output
- [ ] 5.3 Ejecutar cuando ya no haya hoja de promo y confirmar que el pipeline termina sin errores y todas las filas tienen `is_promo = False`
