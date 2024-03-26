import os

import fastapi
import suno
from fastapi import responses

VERSION = "v1"
COOKIE = os.getenv("SUNO_COOKIE")
HOST = "0.0.0.0"
PORT = 8000


# Suno API client
client = suno.Suno(cookie=COOKIE)


# FastAPI app
app = fastapi.FastAPI()


@app.post(f"/{VERSION}/songs")
def generate(params: suno.SongGenerateParams) -> responses.JSONResponse:
    songs = client.songs.generate(**params.model_dump())
    return responses.JSONResponse(content=[song.model_dump() for song in songs])


@app.get(f"/{VERSION}/songs")
def list() -> responses.JSONResponse:
    songs = client.get_songs()
    return responses.JSONResponse(content=[song.model_dump() for song in songs])


@app.get(f"/{VERSION}/song/{id}")
def get(id: str) -> responses.JSONResponse:
    song = client.get_song(id)
    return responses.JSONResponse(content=song.model_dump())


@app.get(f"/{VERSION}/credits")
def credits() -> responses.JSONResponse:
    credits = client.get_credits()
    return responses.JSONResponse(content={"total_credits_left": credits})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
