import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

_raw = os.getenv("GSHEETS_CREDENTIALS")
if not _raw:
    raise EnvironmentError(
        "La variable de entorno GSHEETS_CREDENTIALS no está definida. "
        "Copia env_example a .env y completa el valor."
    )

GOOGLE_SHEET_CREDENTIALS = json.loads(base64.b64decode(_raw).decode("utf-8"))
