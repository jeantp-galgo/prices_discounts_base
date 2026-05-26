# Bonos Galgo — Reporte diario de descuentos

## Sobre este documento
- **Para quién es**: PMs, IAs que ayudan a construir o mantener el producto, y pipelines automatizados que consumen el reporte.
- **Qué incluye**: visión, problema, usuarios, épicas, métricas de éxito y stack tecnológico.
- **Qué NO incluye**: arquitectura técnica, código, decisiones de implementación. Eso vive en `/docs/specs/` y `/docs/decisions/`.

## Arquitectura de documentación

```
/docs
  /prds
    00-vision.md                  ← Este documento
    01-epic-conexion-sheets.md    ← E01: Conexión y detección de hojas
    02-epic-extraccion-bonos.md   ← E02: Extracción y filtrado de bonos
    03-epic-output-reporte.md     ← E03: Consolidación y escritura del reporte
  /specs
    (por definir — responsabilidad de documentation-expert)
  /decisions
    (por definir)
```

## 1. Visión del producto

Bonos Galgo es un pipeline automatizado que lee diariamente una hoja de cálculo de precios en Google Sheets, detecta todos los modelos de vehículos con descuentos activos (de la marca o de Galgo), y escribe un reporte consolidado en otra hoja de Google Sheets lista para ser consumida por sistemas externos.

El objetivo es eliminar el trabajo manual de revisar múltiples pestañas de precios, asegurar que los descuentos vigentes sean visibles cada mañana antes de que el negocio opere, y proveer una fuente de datos confiable y consistente para los pipelines de decisión de Galgo.

## 2. Problema que resuelve

El listado de precios de los distribuidores llega en un Google Sheets con múltiples pestañas, una por marca. Cada pestaña puede tener un nombre diferente (porque incluye la vigencia del período), y las columnas de descuento varían según la marca. Hoy no existe ningún proceso automatizado que consolide todos los descuentos activos en un único lugar estructurado; eso se hace de forma manual, con riesgo de error y sin reproducibilidad.

## 3. Usuarios del sistema

| Usuario | Descripción |
|---|---|
| Pipeline automatizado | Sistema o proceso externo que consume el reporte de bonos para tomar decisiones (pricing, disponibilidad, promociones). No es un usuario humano directo. |
| Operador técnico | Persona que configura, monitorea o depura el pipeline (DevOps / analista). Interactúa con GitHub Actions y los logs. |

## 4. Propuesta de valor

**Para el pipeline automatizado**
- Reporte disponible cada día a las 6 AM hora México, antes de que el negocio arranque.
- Datos normalizados: schema consistente sin importar cuántas marcas tenga el Sheets de origen.
- Sin intervención humana: el proceso corre y escribe solo.

**Para el operador técnico**
- Código reproducible y documentado.
- Fácil de depurar: errores explícitos cuando una hoja no tiene el formato esperado.
- Configuración externalizada: el listado de marcas válidas se provee vía config, no está hardcodeado.

## 5. Jobs to be Done

### JTBD 1: Consolidar bonos activos
Cuando el negocio necesita saber qué modelos tienen descuento hoy, el pipeline quiere leer el Sheets de precios automáticamente y producir una tabla limpia con todos los modelos con descuento activo, para que los sistemas downstream puedan actuar sobre esa información sin trabajo manual.

### JTBD 2: Detectar hojas válidas de forma flexible
Cuando el Sheets de precios tiene pestañas con nombres que cambian por período (ej. "Toyota Ene-Mar 2026"), el pipeline quiere identificar la hoja correcta para cada marca usando un listado de marcas conocidas, para no depender de nombres exactos de pestaña.

### JTBD 3: Escribir el reporte en Sheets sin intervención
Cuando el pipeline termina de procesar, quiere escribir el resultado directamente en Google Sheets (hoja nueva), para que los consumidores downstream tengan siempre la versión más reciente disponible.

## 6. Épicas

| # | Épica | Descripción | Link | Estado |
|---|---|---|---|---|
| E01 | Conexión y detección de hojas | Autenticación con Google Sheets API y detección flexible de hojas válidas por marca | `01-epic-conexion-sheets.md` | Pendiente |
| E02 | Extracción y filtrado de bonos | Lectura de columnas clave y filtrado de modelos con al menos un descuento activo | `02-epic-extraccion-bonos.md` | Pendiente |
| E03 | Consolidación y escritura del reporte | Construcción de tabla final, cálculos derivados y escritura en Google Sheets vía GitHub Actions | `03-epic-output-reporte.md` | Pendiente |

## 7. Métricas de éxito

### North Star Metric
El reporte de bonos está disponible en Google Sheets antes de las 6:05 AM hora México todos los días hábiles, sin intervención manual.

### Métricas secundarias

| Métrica | Objetivo | Por qué importa |
|---|---|---|
| Tasa de éxito del pipeline | >= 95% de ejecuciones exitosas por mes | Indica confiabilidad del proceso automatizado |
| Cobertura de marcas | 100% de marcas del listado procesadas (o error explícito por marca faltante) | Garantiza que no se omite ninguna marca silenciosamente |
| Latencia de escritura | Reporte escrito en Sheets en menos de 5 minutos desde el inicio del job | El pipeline downstream no debe esperar |
| Modelos con descuento detectados | Variación < 50% día a día sin alerta | Cambios bruscos pueden indicar error de lectura |

## 8. Stack tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.x |
| Lectura/escritura Sheets | gspread |
| Procesamiento de datos | pandas |
| Automatización | GitHub Actions (cron `0 12 * * *` → 6 AM UTC-6) |
| Autenticación | Google Service Account (credenciales en secrets de GitHub) |
| Configuración | Archivo de config con listado de marcas válidas |

## 9. Glosario

| Término | Definición |
|---|---|
| Bono | Descuento aplicado sobre el precio de un modelo de vehículo; puede ser de la marca (fabricante) o de Galgo (distribuidor/financiera). |
| Desc. Marca | Descuento ofrecido por el fabricante del vehículo para un modelo y período dados. |
| Desc. Galgo | Descuento adicional ofrecido por Galgo sobre el precio del modelo. |
| Total Desc. | Suma de Desc. Marca + Desc. Galgo. |
| Precio Final | Precio del modelo menos el Total Desc. |
| Hoja válida | Pestaña del Sheets de precios que corresponde a una marca del listado de marcas conocidas. |
| Listado de marcas | Archivo de configuración con las marcas que el pipeline debe buscar y procesar. |
| Pipeline downstream | Sistema externo que consume el reporte de bonos generado por este proyecto. |
