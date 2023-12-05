# config.py

# MySQL 연결 설정
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1q2w3e4r",
    "database": "spring_social"
}

# REST API 호출에 필요한 정보
KOGPT_KEY = '3bb30f6d9eab61add4b056721668725f'

# CORS 정책 활성화
origins = [
    "http://localhost:3000",  # React 프론트엔드 주소
    "http://localhost:8000",  # 백엔드 주소
]

# TTS api key
TTS_key = '9cc7d235ea9b96e8f150d5f164fd4631'