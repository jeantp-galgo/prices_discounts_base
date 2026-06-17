## ADDED Requirements

### Requirement: Detección de hoja de promoción
El sistema SHALL inspeccionar los nombres de todas las hojas del sheet de precios activo y determinar si alguna corresponde a una promoción, usando coincidencia case-insensitive contra la lista de keywords conocidos: `["buen fin", "hot sale", "arrancan promos"]`.

#### Scenario: Hoja de promo presente
- **WHEN** el sheet de precios contiene una hoja cuyo nombre incluye alguno de los keywords de promoción
- **THEN** el sistema la identifica como hoja de promo y la retorna para lectura

#### Scenario: Sin hoja de promo
- **WHEN** ninguna hoja del sheet tiene nombre que coincida con los keywords
- **THEN** el sistema continúa normalmente sin leer hoja de promo y sin error

#### Scenario: Coincidencia es case-insensitive
- **WHEN** el nombre de la hoja es "Arrancan Promos - Junio 2026" (con mayúsculas y texto adicional)
- **THEN** el sistema la detecta correctamente como hoja de promo

### Requirement: Lectura de hoja de promoción con columnas variables
El sistema SHALL leer la hoja de promo mapeando sus columnas al schema interno, tolerando variantes de nombre en la columna de descuento Galgo.

#### Scenario: Columna Galgo con nombre estándar
- **WHEN** la hoja de promo tiene columna `Desc. Galgo`
- **THEN** se mapea a `galgo_discount`

#### Scenario: Columna Galgo con nombre alternativo
- **WHEN** la hoja de promo tiene columna `Bono Galgo`
- **THEN** se mapea igualmente a `galgo_discount`

#### Scenario: Columna de descuento adicional presente
- **WHEN** la hoja de promo tiene columna `Desc. adicional`
- **THEN** se mapea a `promo_discount`

#### Scenario: Columna de descuento adicional ausente
- **WHEN** la hoja de promo no tiene columna `Desc. adicional`
- **THEN** `promo_discount` toma valor 0 y el sistema no falla
