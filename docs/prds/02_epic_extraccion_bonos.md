# PRD: Extracción y filtrado de bonos

## Épica: E02 — extraccion-bonos

## Sobre este documento
- **Para quién es**: PMs e IAs que van a implementar esta épica.
- **Qué incluye**: el QUÉ y el PARA QUÉ de la lectura de columnas clave y el filtrado de modelos con descuento activo.
- **Qué NO incluye**: implementación técnica → ver `/docs/specs/T02-extraccion-bonos.md` (por definir).
- **PRD padre**: `/docs/prds/00_vision.md`

## 1. Objetivo

Una vez que E01 provee el mapeo `marca → pestaña`, esta épica se encarga de leer cada hoja válida, identificar las columnas relevantes, y filtrar únicamente los modelos que tienen al menos un descuento activo (Desc. Marca > 0 o Desc. Galgo > 0).

El foco principal del reporte son los bonos de Galgo, pero se incluyen también los bonos de la marca cuando existen, porque ambos afectan el precio final que el pipeline downstream usa para tomar decisiones.

## 2. Alcance

### Incluye
- Lectura del contenido de cada hoja válida identificada en E01.
- Identificación de las columnas clave por nombre (no por posición), con fallback a columna F para Desc. Marca cuando el nombre de columna varía por marca.
- Filtrado: solo filas donde Desc. Marca > 0 o Desc. Galgo > 0.
- Manejo de hojas sin datos, sin filas de datos (solo encabezado), o sin las columnas esperadas.
- Asociación de cada fila filtrada con su marca de origen.

### No incluye
- Cálculo de totales o precios finales (eso es E03).
- Escritura de ningún dato (eso es E03).
- Validación de precios contra fuentes externas.

## 3. Columnas clave y estrategia de identificación

Las hojas de precios no tienen un schema completamente uniforme entre marcas. Las columnas esperadas son:

| Columna lógica | Nombre esperado en la hoja | Notas |
|---|---|---|
| Marca | "Marca" | Puede estar presente o inferirse del nombre de la pestaña |
| Modelo MKP | "Modelo MKP" o similar | El nombre de modelo tal como aparece en el marketplace |
| Año | "Año" o "Year" | Año del modelo del vehículo |
| Precio | "Precio" o "Precio Lista" | Precio base sin descuentos |
| Desc. Marca | "Desc. {nombre_marca}" (varía por marca) | Si no se encuentra por nombre, usar columna F como fallback |
| Desc. Galgo | "Desc. Galgo" | Consistente entre hojas |

La búsqueda de columnas es case-insensitive y tolerante a espacios adicionales. Cuando la columna de Desc. Marca no puede identificarse por nombre, se usa la columna F como fallback y se registra en el log.

## 4. Regla de filtrado

Un modelo se incluye en el reporte si cumple **al menos una** de las siguientes condiciones:
- Desc. Marca > 0
- Desc. Galgo > 0

Modelos con ambos descuentos en cero (o vacíos) se descartan silenciosamente. No son error; simplemente no tienen bono activo.

## 5. User stories

### 5.1. Lectura de contenido de hoja por marca
- **ID**: E02-001
- **Descripción**: Como pipeline automatizado, quiero leer el contenido de cada hoja válida identificada en E01, para poder extraer los datos de modelos y descuentos.
- **Criterios de aceptación**:
  - Para cada entrada del mapeo `marca → pestaña` de E01, el pipeline lee el contenido completo de esa pestaña.
  - Si una pestaña está vacía o solo tiene encabezado sin filas de datos, se registra advertencia y se continúa con la siguiente marca (no error fatal).
  - El pipeline no asume una estructura fija de filas de encabezado; detecta el encabezado por presencia de columnas clave.

### 5.2. Identificación de columnas clave
- **ID**: E02-002
- **Descripción**: Como pipeline automatizado, quiero identificar las columnas de Marca, Modelo, Año, Precio, Desc. Marca y Desc. Galgo en cada hoja, para poder extraer los valores correctos sin depender de posiciones fijas.
- **Criterios de aceptación**:
  - La identificación de columnas se hace por nombre (case-insensitive), no por índice.
  - Para Desc. Marca: si no se encuentra columna cuyo nombre contenga "Desc." y el nombre de la marca, se usa la columna F como fallback.
  - El uso de fallback a columna F se registra en el log con el nombre de la marca afectada.
  - Si las columnas de Modelo, Precio o Desc. Galgo no se encuentran en una hoja, esa hoja se omite con advertencia explícita en el log.

### 5.3. Filtrado de modelos con descuento activo
- **ID**: E02-003
- **Descripción**: Como pipeline automatizado, quiero filtrar solo los modelos que tienen al menos un descuento activo, para que el reporte no incluya modelos sin bono.
- **Criterios de aceptación**:
  - Se incluyen filas donde Desc. Marca > 0 o Desc. Galgo > 0.
  - Valores nulos, vacíos o cero en ambas columnas de descuento resultan en exclusión silenciosa de la fila.
  - El número de filas incluidas y excluidas por hoja se registra en el log.

### 5.4. Asociación de filas con su marca de origen
- **ID**: E02-004
- **Descripción**: Como pipeline automatizado, quiero que cada fila extraída tenga asociada su marca de origen, para poder consolidar correctamente en E03.
- **Criterios de aceptación**:
  - Cada fila del resultado lleva un campo "Marca" con el nombre normalizado de la marca (del listado de config, no el nombre exacto de la pestaña).
  - Si la hoja tiene una columna "Marca" propia, se usa ese valor; si no, se usa el nombre de la marca del listado.

### 5.5. Manejo de hojas con formato inesperado
- **ID**: E02-005
- **Descripción**: Como operador técnico, quiero que el pipeline continúe procesando las demás marcas cuando una hoja tiene un formato inesperado, para que un error en una marca no bloquee todo el reporte.
- **Criterios de aceptación**:
  - Una hoja con columnas faltantes o sin datos produce una advertencia en el log y se omite.
  - El pipeline termina de procesar todas las demás marcas antes de reportar cuántas hojas fueron omitidas.
  - El reporte final puede generarse con cero filas de una marca si esa marca fue omitida por error de formato.

## 6. Criterios de aceptación de la épica

- [ ] Para cada marca en el mapeo de E01, el pipeline lee el contenido de la pestaña correspondiente.
- [ ] Las columnas clave se identifican por nombre (case-insensitive) con fallback a columna F para Desc. Marca.
- [ ] Solo las filas con Desc. Marca > 0 o Desc. Galgo > 0 se incluyen en el resultado.
- [ ] Cada fila del resultado tiene su marca de origen asignada correctamente.
- [ ] Hojas con formato inesperado producen advertencia en log y no detienen el pipeline.
- [ ] El log incluye el conteo de filas incluidas/excluidas por marca.

## 7. Riesgos y supuestos

- Se asume que la primera fila de la hoja con contenido reconocible es el encabezado.
- Riesgo: si el nombre de la columna de Desc. Marca no sigue el patrón "Desc. {marca}" ni está en columna F, el valor puede ser incorrecto. Mitigación: el fallback a columna F cubre el caso más común; se documenta en el log para revisión.
- Se asume que los valores de precio y descuento son numéricos o convertibles a numérico; valores de texto no numéricos se tratan como cero.
- Riesgo: cambios estructurales grandes en el Sheets de origen (ej. fusión de columnas, filas de subtotal) pueden romper la extracción. No hay mitigación automática; requiere intervención del operador.

## 8. Épicas relacionadas

- Depende de E01 (`01_epic_conexion_sheets.md`): requiere el mapeo `marca → pestaña` como entrada.
- E03 (`03_epic_output_reporte.md`) consume el conjunto de filas filtradas producido por esta épica.

## 9. Specs técnicos asociados

- `/docs/specs/T02-extraccion-bonos.md` (por definir — responsabilidad de documentation-expert)

## 10. Decisiones relacionadas

- (Si se decide la estrategia exacta de fallback de columnas o el tratamiento de valores no numéricos, registrar en `/docs/decisions/`.)
