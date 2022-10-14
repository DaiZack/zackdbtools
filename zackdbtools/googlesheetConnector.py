import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import importlib.resources as importlib_resources
import os

SERVICE_ACCOUNT_JSON_PATH = os.path.expandvars(os.environ.get("SERVICE_ACCOUNT_JSON_PATH", None))

def readgooglesheets(SAMPLE_SPREADSHEET_ID,SAMPLE_RANGE_NAME, service_account_json=None,dedupCol=None, skiprows = 0,valueRenderOption='UNFORMATTED_VALUE'):
  SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
  service_account_json = service_account_json or SERVICE_ACCOUNT_JSON_PATH
  credentials = service_account.Credentials.from_service_account_file(
          service_account_json, scopes=SCOPES)
  service = build('sheets', 'v4', credentials=credentials)
  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=SAMPLE_RANGE_NAME,valueRenderOption=valueRenderOption).execute()
  df = pd.DataFrame(result['values'][skiprows+1:], columns = result['values'][skiprows][:len(result['values'][skiprows+1])])
  if dedupCol and dedupCol in df.columns:
    df = df.dropna(subset=[dedupCol]).reset_index()
  return df
