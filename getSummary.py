from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json

app = FastAPI()

# REST API 호출에 필요한 라이브러리

# [내 애플리케이션] > [앱 키] 에서 확인한 REST API 키 값 입력
REST_API_KEY = '3bb30f6d9eab61add4b056721668725f'

# KoGPT API 호출을 위한 메서드 선언
# 각 파라미터 기본값으로 설정
def kogpt_api(prompt, max_tokens, temperature, top_p, n=1):
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
@app.post("/post")
def generate_text(request: PromptRequest):
    # 전달된 문자열을 prompt로 사용하여 kogpt_api() 메서드 호출
    response = kogpt_api(
        prompt=request.prompt,
        max_tokens=100,
        temperature=0.1,
        top_p=0.1,
        n=1
    )
    return response