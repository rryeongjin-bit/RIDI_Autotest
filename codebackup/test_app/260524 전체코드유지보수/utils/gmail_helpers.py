import re
import base64
import time
from html import unescape
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from utils.google_auth import get_google_token, clear_token, force_refresh_token


class TokenRefreshFailedError(Exception):
    pass


def _query_gmail_for_verification_url(after_timestamp=None, sender_email=None, sign_up_email=None):
    creds   = get_google_token()
    service = build('gmail', 'v1', credentials=creds)

    parts = ['subject:"[리디] 회원가입 이메일 주소 인증"']
    if sender_email:
        parts = [f'from:{sender_email}']
    if sign_up_email:
        parts.append(f'to:{sign_up_email}')
    if after_timestamp:
        parts.append(f'after:{after_timestamp}')
    query = ' '.join(parts)

    results  = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
    messages = results.get('messages', [])

    if not messages:
        return None

    msg       = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
    payload   = msg['payload']
    parts     = payload.get('parts', [])
    body_data = None

    for part in parts:
        if part.get('mimeType', '').startswith('text') and 'data' in part.get('body', {}):
            body_data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            break

    if not body_data and 'data' in payload.get('body', {}):
        body_data = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    if not body_data:
        return None

    match = re.search(r'https://ridibooks\.com/account/email/verify[^\s"<]+', body_data)
    return unescape(match.group(0)) if match else None


def _retry_with_force_refresh(after_timestamp=None, sender_email=None, sign_up_email=None):
    print("🔄 토큰 강제 재갱신 시도...")
    clear_token()
    if force_refresh_token():
        print("✅ 토큰 강제 재갱신 성공. Gmail API 재시도합니다.")
        try:
            return _query_gmail_for_verification_url(after_timestamp, sender_email, sign_up_email)
        except Exception as retry_e:
            raise TokenRefreshFailedError(f"토큰 재갱신 후 Gmail API 실패: {retry_e}")
    else:
        raise TokenRefreshFailedError("토큰 강제 재갱신 실패")


def get_latest_verification_url(after_timestamp=None, sender_email=None, sign_up_email=None):
    try:
        return _query_gmail_for_verification_url(after_timestamp, sender_email, sign_up_email)
    except RefreshError as e:
        print(f"⚠️ 토큰 갱신 실패: {e}")
        return _retry_with_force_refresh(after_timestamp, sender_email, sign_up_email)
    except HttpError as e:
        if e.resp.status in (401, 403):
            print(f"⚠️ Gmail API 인증 오류 (HTTP {e.resp.status}): {e}")
            return _retry_with_force_refresh(after_timestamp, sender_email, sign_up_email)
        print(f"⚠️ Gmail API HTTP 오류: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Gmail API 예외 발생: {e}")
        return None