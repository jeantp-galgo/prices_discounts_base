# bonos_galgo — Contexto del Proyecto

## Que es

Herramienta Python que actualiza automáticamente la hoja **[MKP - MX] Bonos en modelos** en Google Sheets con los precios y descuentos vigentes de cada marca, cruzando la lista de precios del mes con el inventario disponible en el marketplace (México).

## Problema que resuelve

Mantener al día los bonos/descuentos por modelo en el sheet que consume el equipo comercial requería cruces manuales entre la lista de precios mensual y el inventario del marketplace.

## Que cubre este proyecto

- Conexión a Google Sheets vía Service Account (épica 01)
- Extracción y cruce de bonos por marca (épica 02)
- Escritura del reporte en la hoja destino (épica 03)

Ver `docs/prds/00_vision.md` y las épicas para el detalle funcional.

## Lo que NO cubre

- La gestión de la lista de precios de origen (la mantiene el equipo comercial)
- Países distintos a México
