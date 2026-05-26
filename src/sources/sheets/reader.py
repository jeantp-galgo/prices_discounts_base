from src.sources.sheets.client import GoogleSheetClient
from gspread_dataframe import get_as_dataframe, set_with_dataframe

class GoogleSheetReader:
    def __init__(self):
        self.client = GoogleSheetClient().get_client()

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
   

    def read_sheets_by_brands(self, sheet_name: str, marcas: list) -> dict:
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