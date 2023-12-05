from elevenlabs import clone, generate, set_api_key
from config import db_config, origins, TTS_key
from datetime import datetime
from fastapi import FastAPI, HTTPException, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from pydantic import BaseModel
import random
from typing import Dict
from fastapi.responses import FileResponse
import os

app = FastAPI()

# CORS 미들웨어 활성화
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

set_api_key(TTS_key)


def get_actor_by_user_id(user_id, cursor):
    # MySQL에서 user_id에 해당하는 튜플의 actor를 검색합니다.
    sql_select = "SELECT actor FROM voice_config WHERE user_id = %s"
    cursor.execute(sql_select, (user_id,))
    result = cursor.fetchone()
    if result and result[0] is not None:
        return result[0]
    else:
        return "Grace"


# actor 목록 : "Dorothy" "Grace" "Matilda"   "Michael"   "James" "🎅 Santa Claus"
def elevenLabs(contents, model, cursor, userId):
    # voice_config에서 user_id에 해당하는 actor를 가져옵니다.
    user_id_actor = get_actor_by_user_id(userId, cursor)

    # 가져온 actor 값을 이용하여 elevenLabs를 호출합니다.
    audio = generate(text=contents, voice=user_id_actor, model=model)

    file_path = f"{int(datetime.now().timestamp())}{random.randint(1000, 9999)}.mp3"
    with open(file_path, "wb") as file:
        file.write(audio)
    return file_path


class TTSRequest(BaseModel):
    contents: str
    userId: int


@app.post("/api/tts")
async def generate_text(contents: TTSRequest):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        response = elevenLabs(
            contents=contents.contents,
            model="eleven_multilingual_v2",
            cursor=cursor,
            userId=contents.userId,
        )

        # 응답을 MySQL 테이블에 저장
        sql = "UPDATE post SET voice_file = %s WHERE contents = %s"
        val = (response, contents.contents)
        cursor.execute(sql, val)

        connection.commit()
        return response
    except Exception as error:
        print(error)
        return {"error": f"An error occurred: {str(error)}"}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


@app.get("/api/tts/{post_id}")
def play_voice(post_id: int):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # MySQL에서 post_id에 해당하는 튜플을 찾습니다.
        sql_select = "SELECT voice_file FROM post WHERE post_id = %s"
        cursor.execute(sql_select, (post_id,))
        result = cursor.fetchone()

        if result:
            voice_file_path = result[0]

            if os.path.exists(voice_file_path):
                # 파일이 존재하면 클라이언트에게 파일을 전송합니다.
                return FileResponse(voice_file_path, media_type="audio/mp3")
            else:
                raise HTTPException(status_code=404, detail="MP3 file not found")
        else:
            raise HTTPException(status_code=404, detail="Post not found")

    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(error)}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


@app.post("/api/tts/clone")
async def voiceClone(file: UploadFile = File(...), userId: int = Form(...)):
    try:
        # 저장할 경로 및 파일 이름 설정
        file_path = f"./source/source{userId}.mp3"

        # 받아온 mp3 파일을 저장
        with open(file_path, "wb") as file_local:
            file_local.write(file.file.read())

        # voice_config 테이블 업데이트
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # voice_config 테이블 업데이트
            sql_update = "UPDATE voice_config SET actor = %s WHERE user_id = %s"
            actor_name = f"Custom{userId}"
            cursor.execute(sql_update, (actor_name, userId))

            connection.commit()
        except Exception as error:
            print(f"An error occurred while updating voice_config: {str(error)}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

        voice = clone(
            name=f"Custom{userId}",
            description="Perfect for news",
            files=[file_path],
        )

        return {"message": "File saved successfully", "file_path": file_path}
    except Exception as error:
        return {"error": f"An error occurred: {str(error)}"}