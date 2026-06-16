# PRD: Consolidación y escritura del reporte

## Épica: E03 — output-reporte

## Sobre este documento
- **Para quién es**: PMs e IAs que van a implementar esta épica.
- **Qué incluye**: el QUÉ y el PARA QUÉ de la construcción de la tabla final, los cálculos derivados, la escritura en Google Sheets y la automatización vía GitHub Actions.
- **Qué NO incluye**: implementación técnica → ver `/docs/specs/T03-output-reporte.md` (por definir).
- **PRD padre**: `/docs/prds/00_vision.md`

## 1. Objetivo

Una vez que E02 entrega el conjunto de filas filtradas (modelos con al menos un descuento activo), esta épica construye la tabla consolidada final, calcula los campos derivados (Total Desc. y Precio Final) y escribe el resultado en una hoja nueva de Google Sheets. Todo esto ocurre de forma automática cada día a las 6 AM hora México, orquestado por GitHub Actions.

El reporte resultante es el artefacto que consume el pipeline downstream. Su schema debe ser consistente, predecible y estar siempre disponible en el mismo Sheets de destino.

## 2. Alcance

### Incluye
- Construcción de la tabla consolidada a partir de las filas de E02.
- Cálculo de Total Desc. = Desc. Marca + Desc. Galgo.
- Cálculo de Precio Final = Precio - Total Desc.
- Escritura del reporte en una hoja nueva del Google Sheets de destino (puede ser el mismo Sheets de origen u otro, configurado externamente).
- Encabezado de hoja con la fecha de generación del reporte.
- Automatización completa vía GitHub Actions con cron `0 12 * * *` (6 AM UTC-6 / hora México).
- Manejo de errores en la escritura: reintentos o fallo explícito con log.

### No incluye
- Formateo visual avanzado del Sheets (colores, bordes, anchos de columna).
- Envío de notificaciones o alertas (puede ser una épica futura).
- Archivado histórico de reportes anteriores (la hoja se sobreescribe o se crea nueva cada día).
- Validación del reporte contra umbrales de negocio.

## 3. Schema del reporte de salida

La tabla escrita en Sheets tiene exactamente las siguientes columnas, en este orden:

| # | Columna | Origen | Tipo |
|---|---|---|---|
| 1 | Marca | Campo de origen de E02 | Texto |
| 2 | Modelo | Campo "Modelo MKP" de E02 | Texto |
| 3 | Año | Campo "Año" de E02 | Entero |
| 4 | Precio | Campo "Precio" de E02 | Numérico |
| 5 | Desc. Marca | Campo "Desc. Marca" de E02 | Numérico |
| 6 | Desc. Galgo | Campo "Desc. Galgo" de E02 | Numérico |
| 7 | Total Desc. | Calculado: Desc. Marca + Desc. Galgo | Numérico |
| 8 | Precio Final | Calculado: Precio - Total Desc. | Numérico |

La primera fila de la hoja es el encabezado con estos nombres de columna exactos. La segunda fila puede incluir la fecha de generación como metadato, o incorporarse en el nombre de la hoja (ver sección 4).

## 4. Hoja de destino

- El reporte se escribe en una hoja nueva dentro del Google Sheets de destino.
- El nombre de la hoja incluye la fecha de ejecución (ej. "Bonos 2026-05-26") para facilitar la trazabilidad.
- Si ya existe una hoja con ese nombre del mismo día, se sobreescribe.
- El Sheets de destino se identifica por URL o ID en el archivo de config (puede ser el mismo Sheets de origen o uno separado).

## 5. Automatización vía GitHub Actions

El pipeline se ejecuta automáticamente cada día con el siguiente schedule:

```yaml
on:
  schedule:
    - cron: '0 12 * * *'   # 6:00 AM UTC-6 (hora México)
  workflow_dispatch:         # permite ejecución manual para pruebas
```

Las credenciales de Google Service Account se almacenan como secrets en el repositorio de GitHub y se inyectan como variables de entorno al job.

## 6. User stories

### 6.1. Construcción de la tabla consolidada
- **ID**: E03-001
- **Descripción**: Como pipeline automatizado, quiero unificar todas las filas filtradas de E02 en una sola tabla con schema consistente, para tener un único artefacto de salida estructurado.
- **Criterios de aceptación**:
  - La tabla final contiene exactamente las columnas definidas en la sección 3, en ese orden.
  - Todas las filas provienen del resultado de E02 (ninguna fila sin descuento activo aparece en el reporte).
  - Si E02 produce cero filas (ningún modelo con descuento en ninguna marca), el reporte se escribe igualmente con solo el encabezado, y se registra advertencia en el log.

### 6.2. Cálculo de campos derivados
- **ID**: E03-002
- **Descripción**: Como pipeline automatizado, quiero que Total Desc. y Precio Final se calculen automáticamente, para que el pipeline downstream reciba valores listos para usar.
- **Criterios de aceptación**:
  - Total Desc. = Desc. Marca + Desc. Galgo para cada fila.
  - Precio Final = Precio - Total Desc. para cada fila.
  - Los valores calculados son numéricos; si Precio es nulo o cero, Precio Final es nulo y se registra advertencia.
  - No se usan fórmulas de Sheets; los valores se escriben como números estáticos.

### 6.3. Escritura del reporte en Google Sheets
- **ID**: E03-003
- **Descripción**: Como pipeline automatizado, quiero escribir la tabla consolidada en una hoja nueva del Sheets de destino, para que el pipeline downstream siempre encuentre el reporte en una ubicación consistente.
- **Criterios de aceptación**:
  - El reporte se escribe en una hoja nueva cuyo nombre incluye la fecha de ejecución (formato YYYY-MM-DD).
  - Si ya existe una hoja con ese nombre, se sobreescribe.
  - La primera fila de la hoja contiene los nombres de columna exactos del schema definido.
  - Si la escritura falla (error de API, permisos, etc.), el pipeline falla con error explícito y no produce una hoja parcial.

### 6.4. Ejecución automática vía GitHub Actions
- **ID**: E03-004
- **Descripción**: Como operador técnico, quiero que el pipeline corra automáticamente cada día a las 6 AM hora México sin intervención manual, para garantizar que el reporte esté disponible al inicio del día hábil.
- **Criterios de aceptación**:
  - El workflow de GitHub Actions tiene el cron `0 12 * * *` configurado.
  - El workflow también puede ejecutarse manualmente vía `workflow_dispatch` para pruebas.
  - Las credenciales de Google Service Account se leen desde los secrets de GitHub, no están en el código ni en archivos commiteados.
  - El log del job en GitHub Actions permite determinar si el pipeline tuvo éxito o falló, y por qué.

### 6.5. Trazabilidad del reporte
- **ID**: E03-005
- **Descripción**: Como operador técnico, quiero saber cuándo fue generado cada reporte y cuántos modelos incluye, para poder diagnosticar diferencias entre ejecuciones.
- **Criterios de aceptación**:
  - El nombre de la hoja de destino incluye la fecha de ejecución.
  - El log del pipeline incluye: fecha/hora de inicio, número de marcas procesadas, número de filas en el reporte final, y resultado (éxito/fallo).
  - En caso de fallo parcial (algunas marcas omitidas), el log especifica cuáles marcas fueron omitidas y por qué.

## 7. Criterios de aceptación de la épica

- [ ] La tabla consolidada tiene exactamente las 8 columnas del schema, en el orden definido.
- [ ] Total Desc. y Precio Final se calculan correctamente como valores estáticos numéricos.
- [ ] El reporte se escribe en una hoja nueva del Sheets de destino con nombre que incluye la fecha.
- [ ] Si ya existe una hoja del mismo día, se sobreescribe sin error.
- [ ] El pipeline corre automáticamente a las 6 AM hora México vía GitHub Actions (cron `0 12 * * *`).
- [ ] Las credenciales no están en el código; se inyectan desde secrets de GitHub.
- [ ] El log de cada ejecución permite diagnosticar éxito o fallo.

## 8. Riesgos y supuestos

- Se asume que la service account tiene permisos de escritura sobre el Sheets de destino.
- Riesgo: diferencia horaria en GitHub Actions. El cron `0 12 * * *` corresponde a 12:00 UTC, que es 6:00 AM UTC-6. Verificar que esto coincide con la hora México durante todo el año (México no usa horario de verano en todos los estados desde 2023). Mitigación: validar en la primera ejecución real.
- Riesgo: si el Sheets de destino es el mismo que el de origen, una falla de escritura podría interferir con lecturas de E01/E02 en futuras ejecuciones. Mitigación: evaluar si conviene un Sheets de destino separado.
- Se asume que el repositorio de GitHub tiene secrets configurados antes del primer despliegue.
- Riesgo: el pipeline puede producir cero filas si ninguna marca tiene descuentos ese día. Esto es válido pero debe distinguirse de un error. El log lo indica explícitamente.

## 9. Épicas relacionadas

- Depende de E02 (`02_epic_extraccion_bonos.md`): requiere el conjunto de filas filtradas como entrada.
- Depende indirectamente de E01 (`01_epic_conexion_sheets.md`): la conexión establecida en E01 se reutiliza para la escritura del reporte.

## 10. Specs técnicos asociados

- `/docs/specs/T03-output-reporte.md` (por definir — responsabilidad de documentation-expert)

## 11. Decisiones relacionadas

- (Si se decide si el Sheets de destino es el mismo que el de origen, o si se elige una estrategia específica de sobreescritura vs. append, registrar en `/docs/decisions/`.)
