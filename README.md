# ODO-Server2

This is Server for Post Summary and TTS.

Create your own config.py in the root directory

```
# config.py

# MySQL 연결 설정
db_config = {
    "host": "(YourHostName)",
    "user": "(YourUserName)",
    "password": "(Password)",
    "database": "(YourDBName)"
}

# REST API 호출에 필요한 정보
KOGPT_KEY = '(YourKoGPTKey)'

# CORS 정책 활성화
origins = [
    "(IP Address)",  # React 프론트엔드 주소
    "(IP Address)",  # 백엔드 주소
]

# TTS api key
TTS_key = '(ElevenLabsAPIKe)'
```
