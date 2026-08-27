import time
from functools import wraps

import gspread
import requests

# Códigos HTTP transitorios: la API de Google puede devolverlos bajo carga
# momentánea; reintentar con backoff suele resolverlos sin intervención.
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def retry_on_transient_error(max_attempts: int = 5, initial_delay: float = 2, backoff_factor: float = 2):
    """
    Reintenta la función decorada ante errores transitorios de la API de
    Google Sheets (APIError con status 429/5xx) o de red (requests).
    Backoff exponencial: initial_delay, initial_delay*backoff_factor, ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except gspread.exceptions.APIError as e:
                    status_code = getattr(getattr(e, "response", None), "status_code", None)
                    if status_code not in RETRYABLE_STATUS_CODES or attempt == max_attempts:
                        raise
                except requests.exceptions.RequestException:
                    if attempt == max_attempts:
                        raise

                print(f"[WARN] Error transitorio en '{func.__name__}', intento {attempt}/{max_attempts}. Reintentando en {delay:.0f}s...")
                time.sleep(delay)
                delay *= backoff_factor
        return wrapper
    return decorator
