import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

_monitor_raw = os.getenv("MKP_MONITOR_BASE64")
if not _monitor_raw:
    raise EnvironmentError(
        "La variable de entorno MKP_MONITOR_BASE64 no está definida. "
        "Copia env_example a .env y completa el valor."
    )

_price_raw = os.getenv("MKP_PRICE_SHEETS_BASE64")
if not _price_raw:
    raise EnvironmentError(
        "La variable de entorno MKP_PRICE_SHEETS_BASE64 no está definida. "
        "Copia env_example a .env y completa el valor."
    )

MONITOR_CREDENTIALS      = json.loads(base64.b64decode(_monitor_raw).decode("utf-8"))
PRICE_SHEETS_CREDENTIALS = json.loads(base64.b64decode(_price_raw).decode("utf-8"))
