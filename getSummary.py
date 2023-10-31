from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

app = FastAPI()

# CORS 정책 활성화
origins = [
    "http://localhost:3000",  # React 프론트엔드 주소
    "http://localhost:8081",  # 백엔드 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

# MySQL 연결 설정
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1q2w3e4r",
    "database": "spring_social"
}

# REST API 호출에 필요한 라이브러리
REST_API_KEY = '3bb30f6d9eab61add4b056721668725f'

def kogpt_api(prompt, max_tokens, temperature, top_p, n):
    r = requests.post(
        'https://api.kakaobrain.com/v1/inference/kogpt/generation',
        json={
            'prompt': prompt,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'top_p': top_p,
            'n': n
        },
        headers={
            'Authorization': 'KakaoAK ' + REST_API_KEY,
            'Content-Type': 'application/json'
        }
    )
    # 응답 JSON 형식으로 변환
    response = json.loads(r.content)
    return response

# POST 요청을 처리하는 모델 정의
class PromptRequest(BaseModel):
    prompt: str

# POST 요청을 처리하는 핸들러 함수
@app.post("/api/post")
def generate_text(request: PromptRequest):
    # 전달된 문자열을 prompt로 사용하여 kogpt_api() 메서드 호출
    response = kogpt_api(
        prompt=request.prompt,
        max_tokens=100,
        temperature=0.1,
        top_p=0.1,
        n=1
    )
    
    # MySQL 데이터베이스에 응답을 저장
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # 응답을 MySQL 테이블에 저장
        sql = "UPDATE post SET summary = %s WHERE contents = %s)"
        val = (json.dumps(response), request.prompt)
        cursor.execute(sql, val)

        connection.commit()
        return response
    except Exception as error:
        return {"error": str(error)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    
