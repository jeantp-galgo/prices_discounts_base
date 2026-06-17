## Why

Durante eventos promocionales (Buen Fin, Hot Sale, Arrancan Promos), el sheet de precios incluye una hoja especial con descuentos adicionales por modelo. Actualmente el pipeline no detecta ni lee estas hojas, perdiendo la información del descuento promocional y reportando precios incorrectos para los modelos que participan en la promo.

## What Changes

- El reader detecta automáticamente si existe una hoja con nombre de promoción en el sheet de precios (keywords: "buen fin", "hot sale", "arrancan promos")
- Si existe, la lee como fuente alternativa para los modelos participantes, tolerando variantes de nombre en la columna de Galgo (`Desc. Galgo` o `Bono Galgo`)
- Los modelos de la promo **reemplazan** (override) sus filas de la hoja de marca correspondiente en la consolidación
- Se agrega la columna `promo_discount` al output (valor de `Desc. adicional`, 0 si no hay promo)
- Se agregan dos flags nuevos: `is_promo` y `has_promo_discount`, consistentes con los flags existentes

## Capabilities

### New Capabilities

- `promo-sheet-detection`: Detectar si existe una hoja de promoción en el sheet de precios activo y leerla con la estructura correcta
- `promo-override`: Reemplazar filas de marca con filas de promo para los modelos participantes y exponer los descuentos adicionales en el output

### Modified Capabilities

_(ninguna — no cambia el comportamiento para modelos sin promo)_

## Impact

- `src/sources/sheets/reader.py`: agregar lógica de detección y lectura de hoja de promo
- `main.py`: agregar paso de override post-consolidación y nuevas columnas en el output final
- Google Sheets destino `[MKP - MX] Bonos en modelos`: dos columnas y dos flags nuevos en el schema de salida
