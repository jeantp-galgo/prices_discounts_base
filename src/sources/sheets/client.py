import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.config.settings import GOOGLE_SHEET_CREDENTIALS

class GoogleSheetClient:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = gspread.authorize(
            ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEET_CREDENTIALS, self.scope)
        )

    def get_client(self):
        return self.client