from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from config import db_config, KOGPT_KEY, origins

app = FastAPI()

# CORS 미들웨어 활성화
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# REST API 호출 함수
def kogpt_api(prompt, max_tokens, temperature, top_p, n):
    r = requests.post(
        "https://api.kakaobrain.com/v1/inference/kogpt/generation",
        json={
            "prompt": prompt + "\n한줄 요약:",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
        },
        headers={
            "Authorization": "KakaoAK " + KOGPT_KEY,
            "Content-Type": "application/json",
        },
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
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        response = kogpt_api(
            prompt=request.prompt, max_tokens=100, temperature=0.1, top_p=0.1, n=1
        )

        # 응답을 MySQL 테이블에 저장
        sql = "UPDATE post SET summary = %s WHERE contents = %s"
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
