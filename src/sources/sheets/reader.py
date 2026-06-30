from src.sources.sheets.client import GoogleSheetClient
from gspread_dataframe import get_as_dataframe, set_with_dataframe

class GoogleSheetReader:
    def __init__(self, credentials: dict):
        self.client = GoogleSheetClient(credentials).get_client()

    def read_sheet(self, google_sheet_info: dict):
        """
        Lee una hoja de Google Sheets y devuelve un DataFrame.
        Args:
            google_sheet_info: dict
                sheet_name: str
                worksheet: str
        """
        try:
            sheet = self.client.open(google_sheet_info["sheet_name"])
            worksheet = sheet.worksheet(google_sheet_info["worksheet"])
            return get_as_dataframe(worksheet, evaluate_formulas=True)
        except Exception as e:
            sheet_name = google_sheet_info.get("sheet_name", "NOMBRE_DESCONOCIDO")
            print(f"Error al leer la hoja: '{sheet_name}'. Detalle: {e}")
            raise
   

    def read_sheets_by_brands(self, sheet_name: str, marcas: list, percentage_brands: set = None) -> dict:
        """
        Abre el Sheets y devuelve un dict {marca: DataFrame} para cada
        marca que tenga una pestaña coincidente (búsqueda case-insensitive).

        Args:
            sheet_name: nombre del documento en Google Sheets.
            marcas:     lista de strings con los nombres de marca a buscar.
                        Ej. ["Honda", "Yamaha", "KTM"]

        Returns:
            dict con clave = nombre de marca (tal como viene en `marcas`)
            y valor = DataFrame con el contenido de esa pestaña.

        Raises:
            ValueError: si no se detecta ninguna pestaña válida para
                        ninguna de las marcas de la lista.
        """
        spreadsheet = self.client.open(sheet_name)
        all_tabs = [
            ws.title
            for ws in spreadsheet.worksheets()
            if not ws._properties.get("hidden", False)
        ]

        resultado = {}
        for marca in marcas:
            match = next(
                (tab for tab in all_tabs if marca.lower() in tab.lower()),
                None
            )
            if match:
                ws = spreadsheet.worksheet(match)
                df = get_as_dataframe(ws, evaluate_formulas=True)

                # Normalizar columna "Desc. {marca}" → "Desc. marca"
                # Cubre casos como "Desc. Bajaj", "Desc. Honda", "Desc. CF", etc.
                desc_col = next(
                    (col for col in df.columns if str(col).strip().startswith("Desc.")),
                    None,
                )
                if desc_col:
                    df = df.rename(columns={desc_col: "Desc. marca"})
                    if percentage_brands and marca in percentage_brands:
                        price_col = next(
                            (c for c in df.columns if c.strip() in ("Precio Lista", "Precio", "Price")),
                            None,
                        )
                        if price_col:
                            def _pct_to_float(x):
                                s = str(x).strip().rstrip('%').strip()
                                try:
                                    return float(s)
                                except ValueError:
                                    return float('nan')
                            df["Desc. marca"] = (
                                df["Desc. marca"].apply(_pct_to_float) / 100 * df[price_col]
                            )
                            print(f"[OK]   {marca} → '{match}' (columna '{desc_col}' convertida de % a valor absoluto usando '{price_col}')")
                        else:
                            print(f"[WARN] {marca} → '{match}' (columna '{desc_col}' es % pero no se encontró columna de precio para convertir)")
                    else:
                        print(f"[OK]   {marca} → '{match}' (columna '{desc_col}' → 'Desc. marca')")
                else:
                    print(f"[OK]   {marca} → '{match}' (sin columna 'Desc. marca' detectada)")

                resultado[marca] = df
            else:
                print(f"[WARN] Marca '{marca}' no encontrada en ninguna pestaña.")

        if not resultado:
            raise ValueError(
                f"No se encontró ninguna hoja válida para las marcas: {marcas}"
            )

        return resultado

    def detect_promo_sheet(self, sheet_name: str, keywords: list):
        """
        Retorna el nombre de la primera hoja cuyo título (lowercase) contenga
        alguno de los keywords de promoción. Retorna None si no hay coincidencia.
        """
        spreadsheet = self.client.open(sheet_name)
        all_tabs = [
            ws.title
            for ws in spreadsheet.worksheets()
            if not ws._properties.get("hidden", False)
        ]
        matches = [tab for tab in all_tabs if any(kw in tab.lower() for kw in keywords)]

        if len(matches) > 1:
            print(f"[WARN] Se detectaron {len(matches)} hojas de promo: {matches}. Se usará: '{matches[0]}'")
        elif len(matches) == 1:
            print(f"[OK]   Hoja de promo detectada: '{matches[0]}'")
        else:
            print("[INFO] Sin hoja de promo activa.")

        return matches[0] if matches else None

    def read_promo_sheet(self, sheet_name: str, tab_name: str):
        """
        Lee la hoja de promo y normaliza columnas variables:
          - "Bono Galgo" → "Desc. Galgo"  (variante del nombre de Galgo)
          - "Desc. adicional" → "promo_discount"  (descuento extra de la promo)
        Agrega is_promo=True a todas las filas.
        """
        spreadsheet = self.client.open(sheet_name)
        ws = spreadsheet.worksheet(tab_name)
        df = get_as_dataframe(ws, evaluate_formulas=True)

        # Alias de columna Galgo: "Bono Galgo" → "Desc. Galgo"
        if "Bono Galgo" in df.columns and "Desc. Galgo" not in df.columns:
            df = df.rename(columns={"Bono Galgo": "Desc. Galgo"})

        # Capturar descuento adicional de promo
        if "Desc. adicional" in df.columns:
            df = df.rename(columns={"Desc. adicional": "promo_discount"})
        else:
            df["promo_discount"] = 0

        # Normalizar columna de descuento de marca si aún no es "Desc. marca"
        KNOWN_COLS = {"Desc. Galgo", "Desc. marca", "promo_discount"}
        if "Desc. marca" not in df.columns:
            desc_col = next(
                (col for col in df.columns
                 if str(col).strip().startswith("Desc.") and col not in KNOWN_COLS),
                None,
            )
            if desc_col:
                df = df.rename(columns={desc_col: "Desc. marca"})

        df["is_promo"] = True
        n = df["Marca"].notna().sum()
        print(f"[OK]   Promo '{tab_name}' → {n} modelos")
        return df

    def update_sheet(self, google_sheet_info: dict, clear_data: bool = False):
        """
        Actualiza una hoja de Google Sheets con los datos de un DataFrame.
        Args:
            google_sheet_info: dict
                sheet_name: str
                worksheet: str
                df: pd.DataFrame
            clear_data: bool = False
                Si es True, se limpian los datos de la hoja antes de escribir los nuevos.
                Si es False, se escriben los datos desde la ultima fila disponible.
        """
        sheet = self.client.open(google_sheet_info["sheet_name"])
        worksheet = sheet.worksheet(google_sheet_info["worksheet"])
        df = google_sheet_info["df"]

        start_row = self.start_row(worksheet, clear_data)

        if clear_data:
            worksheet.clear()
            set_with_dataframe(worksheet, df, row=start_row, col=1) # Se escribe la data desde cero
        else:
            set_with_dataframe(worksheet, df, row=start_row, col=1, include_column_header=False) # Se escribe la data desde la ultima fila sin incluir la columna
        print(f"Updated sheet: {google_sheet_info['sheet_name']}")

    def start_row(self, worksheet, clear_data: bool = False):
        """ """
        if clear_data:
            return 1
        else:
            last_row = len(worksheet.get_all_values())
            return last_row + 1 if last_row > 0 else 2