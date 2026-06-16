# PRD: Conexión y detección de hojas

## Épica: E01 — conexion-sheets

## Sobre este documento
- **Para quién es**: PMs e IAs que van a implementar esta épica.
- **Qué incluye**: el QUÉ y el PARA QUÉ de la autenticación con Google Sheets y la detección de hojas válidas.
- **Qué NO incluye**: implementación técnica → ver `/docs/specs/T01_conexion_sheets.md` (por definir).
- **PRD padre**: `/docs/prds/00_vision.md`

## 1. Objetivo

Esta épica establece la base del pipeline: la capacidad de conectarse a Google Sheets con credenciales de servicio y de identificar, dentro del Sheets de precios, cuáles pestañas corresponden a marcas válidas del listado de configuración.

La detección no puede depender del nombre exacto de la pestaña porque los nombres incluyen la vigencia del período (ej. "Honda Ene-Mar 2026"). En su lugar, el sistema usa el listado de marcas conocidas para hacer una búsqueda flexible sobre los nombres de las pestañas disponibles.

## 2. Alcance

### Incluye
- Autenticación con Google Sheets API usando una service account.
- Lectura del listado de todas las pestañas del Sheets de precios.
- Detección de hojas válidas: para cada pestaña, verificar si el nombre contiene el nombre de alguna marca del listado (búsqueda case-insensitive, tolerante a variaciones menores).
- Log de marcas encontradas y marcas no encontradas en el Sheets.
- Manejo de error explícito cuando no se encuentra ninguna hoja válida.

### No incluye
- Lectura del contenido de las hojas (eso es E02).
- Escritura de ningún dato (eso es E03).
- Detección de hojas por contenido interno de la celda (solo por nombre de pestaña en esta épica).

## 3. Estrategia de detección de hojas válidas

El nombre de una pestaña puede ser "Toyota Feb-Abr 2026" o "NISSAN Enero 2026". El listado de marcas en el archivo de config podría contener "Toyota" y "Nissan". La regla es:

- Para cada pestaña del Sheets, buscar si el nombre contiene alguna marca del listado (comparación case-insensitive).
- Si hay match, la pestaña se considera hoja válida para esa marca.
- Si una marca del listado no tiene match en ninguna pestaña, se registra como advertencia en el log (no es error fatal, a menos que sean todas).
- Si dos pestañas hacen match con la misma marca, se toma la primera y se registra una advertencia.

El listado de marcas se provee como archivo de configuración externo (no hardcodeado en el código).

## 4. User stories

### 4.1. Autenticación con Google Sheets
- **ID**: E01-001
- **Descripción**: Como pipeline automatizado, quiero autenticarme con Google Sheets usando una service account, para poder leer el Sheets de precios sin intervención humana.
- **Criterios de aceptación**:
  - El pipeline se autentica correctamente usando credenciales JSON de service account almacenadas como variable de entorno o secret.
  - Si las credenciales son inválidas o están ausentes, el pipeline falla con un error descriptivo antes de intentar cualquier lectura.
  - La autenticación no requiere ningún paso manual (flujo OAuth interactivo está fuera del alcance).

### 4.2. Lectura del listado de pestañas
- **ID**: E01-002
- **Descripción**: Como pipeline automatizado, quiero obtener la lista de todas las pestañas del Sheets de precios, para poder evaluar cuáles corresponden a marcas válidas.
- **Criterios de aceptación**:
  - El pipeline accede al Sheets de precios identificado por su URL o ID (configurado externamente).
  - El pipeline obtiene los nombres de todas las pestañas disponibles.
  - Si el Sheets no existe o no es accesible con las credenciales dadas, el error es explícito y detiene la ejecución.

### 4.3. Detección de hojas válidas por marca
- **ID**: E01-003
- **Descripción**: Como pipeline automatizado, quiero identificar qué pestaña corresponde a cada marca del listado, para poder procesarlas en la épica E02.
- **Criterios de aceptación**:
  - Para cada marca en el listado de config, el pipeline determina si existe una pestaña cuyo nombre la contiene (case-insensitive).
  - El resultado es un mapeo `marca → nombre_de_pestaña` para todas las marcas detectadas.
  - Las marcas sin pestaña correspondiente se registran como advertencia en el log, no como error fatal.
  - Si no se detecta ninguna hoja válida, el pipeline falla con error explícito.
  - El proceso es reproducible: misma entrada, mismo resultado.

### 4.4. Carga del listado de marcas desde config
- **ID**: E01-004
- **Descripción**: Como operador técnico, quiero que el listado de marcas válidas se cargue desde un archivo de configuración externo, para poder actualizarlo sin modificar el código.
- **Criterios de aceptación**:
  - El archivo de config con marcas se carga al inicio del pipeline.
  - Si el archivo no existe o está vacío, el pipeline falla con error descriptivo.
  - Agregar o quitar una marca del listado no requiere cambios en el código Python.

## 5. Criterios de aceptación de la épica

- [ ] El pipeline se autentica con Google Sheets sin intervención humana usando credenciales de service account.
- [ ] El pipeline produce un mapeo `marca → pestaña` para todas las marcas detectadas en el Sheets.
- [ ] Las marcas del listado sin pestaña correspondiente se loguean como advertencia (no error silencioso).
- [ ] Si no se encuentra ninguna hoja válida, el pipeline falla de forma explícita con mensaje descriptivo.
- [ ] El listado de marcas es configurable externamente sin tocar el código.

## 6. Riesgos y supuestos

- Se asume que el Sheets de precios es un único documento (no múltiples Sheets).
- Se asume que cada marca tiene como máximo una pestaña vigente en el Sheets en un momento dado.
- Riesgo: si los nombres de pestaña cambian drásticamente (ej. usan abreviaturas no estándar), la detección flexible puede fallar. Mitigación: el operador actualiza el listado de marcas en el config.
- Se asume que las credenciales de service account están disponibles como secret en GitHub Actions.

## 7. Épicas relacionadas

- E02 (`02_epic_extraccion_bonos.md`) consume el mapeo `marca → pestaña` producido por esta épica.
- E03 (`03_epic_output_reporte.md`) no depende directamente de esta épica, pero E02 sí.

## 8. Specs técnicos asociados

- `/docs/specs/T01_conexion_sheets.md` (por definir — responsabilidad de documentation-expert)

## 9. Decisiones relacionadas

- (Ninguna registrada aún. Si se decide un mecanismo específico de detección o un formato de config, crear el ADR correspondiente en `/docs/decisions/`.)
