# SOP — bonos_galgo

## Qué hace

Actualiza la hoja **[MKP - MX] Bonos en modelos** en Google Sheets con precios y descuentos vigentes por marca.

## Requisitos

- Python 3.11+ y `venv` con `requirements.txt` instalado
- `.env` con `GSHEETS_CREDENTIALS` (Service Account de Google en base64) — ver README para generarlo
- Permisos de lectura/escritura sobre los sheets de origen y destino

## Pasos de ejecución

1. Activar el entorno virtual.
2. Verificar `.env` (copiar de `env_example` si no existe).
3. Ejecutar `python main.py`.
4. Verificar la hoja **[MKP - MX] Bonos en modelos** actualizada.

Para instalación desde cero, seguir el `README.md`.

## Inputs / Outputs

- **Inputs**: lista de precios del mes e inventario del marketplace (Google Sheets de origen)
- **Output**: hoja **[MKP - MX] Bonos en modelos** actualizada

## Errores comunes

- Credenciales mal codificadas en base64 → regenerar `GSHEETS_CREDENTIALS` según README
- <!-- TODO: completar -->
