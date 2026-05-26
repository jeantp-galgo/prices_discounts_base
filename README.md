# Reporte de bonos Galgo — México

Herramienta Python que actualiza automáticamente la hoja **[MKP - MX] Bonos en modelos** en Google Sheets con los precios y descuentos vigentes de cada marca, cruzando la lista de precios del mes con el inventario disponible en el marketplace.

## Requisitos previos

- Python 3.11 o superior
- Acceso a las Google Sheets de origen y destino
- Credenciales de una **Service Account** de Google con permisos de lectura y escritura sobre los sheets involucrados

## Instalación y configuración

### 1. Clonar y crear el entorno virtual

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar (Windows PowerShell)
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```powershell
# Copiar la plantilla
Copy-Item env_example .env
```

Editar `.env` y completar el valor de `GSHEETS_CREDENTIALS` con las credenciales de la Service Account en formato base64.

**Cómo generar el valor base64 desde `credentials.json`:**

```powershell
# PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json"))
```

```bash
# Linux / Mac
base64 -w 0 credentials.json
```

El resultado se pega directamente en `.env`:

```
GSHEETS_CREDENTIALS=eyJ0eXBlIjoic2Vydm...
```

## Estructura del proyecto

```
bonos_galgo/
├── main.py                        # Punto de entrada — orquesta todo el proceso
├── requirements.txt               # Dependencias Python
├── env_example                    # Plantilla de variables de entorno
├── .env                           # Variables de entorno (NO se commitea)
├── .gitignore
├── src/
│   ├── config/
│   │   └── settings.py            # Carga y decodifica GSHEETS_CREDENTIALS
│   └── sources/
│       └── sheets/
│           ├── client.py          # Autenticación con Google Sheets API
│           └── reader.py          # Lectura y escritura de hojas (GoogleSheetReader)
├── notebooks/
│   └── app.ipynb                  # Exploración y prototipado
├── scripts/                       # Scripts auxiliares o de mantenimiento
├── docs/                          # Documentación adicional del proyecto
└── outputs/                       # Resultados generados (NO se commitean)
```

## Cómo ejecutar

Con el entorno virtual activo y `.env` configurado:

```powershell
python main.py
```

El script imprime el progreso en consola:

```
Leyendo inventario...
  → 412 modelos en inventario

Leyendo hojas de precios desde 'Lista de Precios Mayo | 2026'...
[OK]   Bajaj → 'Bajaj' (columna 'Desc. Bajaj' → 'Desc. marca')
[OK]   TVS → 'TVS' (columna 'Desc. TVS' → 'Desc. marca')
...

  → 387 filas en el reporte final

Actualizando hoja destino...
  ✓ Actualizado: Bonos en modelos
```

## Entradas y salidas

### Fuentes de datos (lectura)

| Sheet | Pestaña | Contenido |
|---|---|---|
| `[MKP] Precios no duplicados` - Base de inventario | `price_data_mx` | Inventario: `code`, `brand`, `model`, `status` |
| `Lista de Precios [Mes] \| [Año]` | Una pestaña por marca | Precios y descuentos vigentes |

Las marcas procesadas actualmente son: Bajaj, TVS, Vento, Yamaha, Hero, Honda, Suzuki, Italika, Morbidelli, CF Moto & CF LITE.

### Destino (escritura)

| Sheet | Pestaña | Contenido escrito |
|---|---|---|
| `[MKP - MX] Bonos en modelos` | `mx` | Reporte final consolidado |

### Columnas del reporte de salida

| Columna | Descripción |
|---|---|
| `code` | Código único del modelo en el inventario MKP |
| `brand` | Marca |
| `model` | Nombre del modelo |
| `year` | Año del modelo |
| `brand_discount` | Descuento aportado por la marca |
| `galgo_discount` | Descuento aportado por Galgo |
| `total_discount` | Descuento total combinado |
| `price_net` | Precio Galgo con IVA |
| `has_galgo_discount` | `True` si Galgo aporta descuento |
| `has_brand_discount` | `True` si la marca aporta descuento |
| `has_brand_and_galgo_discount` | `True` si ambos aportan descuento |

## Cadencia de actualización

El proceso debe ejecutarse cada vez que cambie la información de precios o descuentos en cualquiera de las fuentes. La siguiente tabla resume las frecuencias recomendadas:

| Frecuencia | Disparador | Acción requerida |
|---|---|---|
| **Mensual** | Publicación de nueva lista de precios (inicio de mes) | Actualizar `SHEET_NAME` en `main.py` con el nombre del nuevo sheet y ejecutar |
| **Al recibir un bono especial** | Notificación de descuento puntual de una marca | Verificar que la pestaña correspondiente esté actualizada en el sheet de precios y ejecutar |
| **Antes de campañas** | Hot Sale, Buen Fin, lanzamientos, fechas comerciales clave | Ejecutar el día anterior para asegurar datos vigentes en el marketplace |
| **Después de cambios en inventario** | Alta o baja de modelos en `[MKP] Precios no duplicados` | Re-ejecutar para que el `code` de los nuevos modelos quede asignado en el reporte |
| **Bajo demanda** | Solicitud del equipo de Marketing o Pricing | Ejecutar con la lista de precios vigente |

> Regla práctica: si la lista de precios cambió, el reporte debe actualizarse antes de que ese cambio sea visible en el marketplace.

## Convenciones

- El nombre del sheet de lista de precios cambia cada mes. Antes de ejecutar, verificar que `SHEET_NAME` en `main.py` apunte al documento correcto.
- Los modelos con `status` distinto de `available` o `no_stock` se excluyen del inventario base.
- La columna de descuento por marca puede llamarse `Desc. Honda`, `Desc. Bajaj`, etc. El reader la normaliza automáticamente a `Desc. marca`.
- La marca `GOES` se normaliza a `CF Moto` durante el procesamiento.
- El reporte de salida se ordena por `has_galgo_discount` descendente (modelos con descuento Galgo primero).

## Seguridad y archivos excluidos de git

Los siguientes archivos nunca deben commitearse al repositorio:

| Archivo / patrón | Motivo |
|---|---|
| `.env` | Contiene credenciales de la Service Account |
| `*.csv`, `*.xlsx` | Archivos de datos con información de precios e inventario |
| `outputs/` | Resultados generados localmente |
| `venv/`, `.venv/` | Entorno virtual (se reconstruye desde `requirements.txt`) |

Si las credenciales de la Service Account quedan expuestas accidentalmente, revocarlas de inmediato en Google Cloud Console y generar nuevas.
