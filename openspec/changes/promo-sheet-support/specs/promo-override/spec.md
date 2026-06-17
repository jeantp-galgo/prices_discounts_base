## ADDED Requirements

### Requirement: Override de filas de marca por filas de promo
El sistema SHALL, después de consolidar todas las hojas de marca, reemplazar las filas de los modelos que aparecen en la hoja de promo con sus respectivas filas de promo. La clave de matching es `(brand, model)`.

#### Scenario: Modelo en promo y en hoja de marca
- **WHEN** un modelo aparece tanto en la hoja de su marca como en la hoja de promo
- **THEN** la fila de promo reemplaza a la de marca en el DataFrame consolidado, y el modelo aparece exactamente una vez

#### Scenario: Modelo solo en promo (no en ninguna hoja de marca)
- **WHEN** un modelo aparece en la hoja de promo pero no en ninguna hoja de marca
- **THEN** la fila de promo se incluye en la consolidación normalmente

#### Scenario: Modelo no participante en promo
- **WHEN** un modelo no aparece en la hoja de promo
- **THEN** conserva su fila original de la hoja de marca sin modificación

### Requirement: Columnas de descuento promocional en el output
El sistema SHALL incluir en el DataFrame final las columnas `promo_discount`, `is_promo` y `has_promo_discount`, consistentes en nombre y tipo con las columnas de descuento existentes.

#### Scenario: Modelo con promo activa
- **WHEN** el modelo proviene de la hoja de promo
- **THEN** `promo_discount` = valor de `Desc. adicional`, `is_promo` = True, `has_promo_discount` = True si `promo_discount > 0`

#### Scenario: Modelo sin promo
- **WHEN** el modelo no proviene de la hoja de promo
- **THEN** `promo_discount` = 0, `is_promo` = False, `has_promo_discount` = False

#### Scenario: Sin hoja de promo en el sheet
- **WHEN** no existe ninguna hoja de promo en el sheet de precios
- **THEN** todos los modelos tienen `promo_discount = 0`, `is_promo = False`, `has_promo_discount = False`
