import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetClient:
    def __init__(self, credentials: dict):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = gspread.authorize(
            ServiceAccountCredentials.from_json_keyfile_dict(credentials, self.scope)
        )

    def get_client(self):
        return self.client
