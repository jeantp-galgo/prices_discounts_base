# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Propósito del proyecto

Proyecto Python para la generación de reportes de bonos en Galgo. Procesa archivos de entrada (CSV/Excel) y produce resultados en la carpeta `outputs/`.

## Entorno y dependencias

```bash
# Crear y activar entorno virtual (Windows)
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias (cuando exista requirements.txt)
pip install -r requirements.txt
```

## Variables de entorno

Copiar `env_example` a `.env` y completar los valores requeridos antes de ejecutar.

## Estructura de datos

- **Entradas:** archivos `.csv` y `.xlsx` (excluidos de git).
- **Salidas:** se generan en `outputs/` (excluido de git).
- Los archivos de datos nunca deben commitearse al repositorio.

## Convenciones

- Lenguaje principal: **Python**.
- Archivos de reporte de salida van en `outputs/`.
- Variables de entorno sensibles van en `.env` (nunca en código).
