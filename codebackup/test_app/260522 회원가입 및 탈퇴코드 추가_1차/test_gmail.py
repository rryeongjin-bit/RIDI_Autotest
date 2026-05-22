import time
from utils.gmail_helpers import get_latest_verification_url

url = get_latest_verification_url(
    after_timestamp=int(time.time()) - 3600,  # 1시간 전부터 조회
    sign_up_email="qa.part.test+260522153113@ridi.com"
)
print(f"URL: {url}")