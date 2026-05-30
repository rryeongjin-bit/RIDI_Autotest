import os
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES           = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_PATH       = 'config/token.json'
CREDENTIALS_PATH = 'config/credentials.json'


def get_google_token() -> Credentials:
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds


def clear_token():
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)
        logging.info("🗑️ 토큰 삭제 완료")


def force_refresh_token() -> bool:
    try:
        clear_token()
        flow  = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
        logging.info("✅ 토큰 강제 재발급 완료")
        return True
    except Exception as e:
        logging.error(f"❌ 토큰 강제 재발급 실패: {e}")
        return False