import os

COOKIE = os.getenv("SUNO_COOKIE", "")

import json
import pathlib
import random
import re
import time
from typing import List, Optional

from curl_cffi import requests
from pydantic import BaseModel, ConfigDict
from rich import print


class Song(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: str
    video_url: str
    audio_url: str
    image_url: str | None
    image_large_url: str | None
    major_model_version: str
    model_name: str
    metadata: dict
    is_liked: bool
    user_id: str
    is_trashed: bool
    reaction: dict | None
    created_at: str
    status: str
    title: str
    play_count: int
    upvote_count: int
    is_public: bool


class SongGenerateParams(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    prompt: str
    custom: bool = False
    tags: str = ""
    instrumental: bool = False


class Client:

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }

    def __init__(self, cookie: str) -> None:
        self.headers["cookie"] = cookie
        self._session = requests.Session(headers=self.headers)
        self._sid = None

    def request(self, *args, **kwargs) -> requests.Response:
        kwargs["impersonate"] = kwargs.get("impersonate", "chrome")
        return self._session.request(*args, **kwargs)

    def sleep(self, seconds: Optional[float] = None) -> None:
        if seconds is None:
            seconds = random.randint(1, 6)
        time.sleep(seconds)


class Suno(Client):

    def __init__(self, cookie: Optional[str] = None) -> None:
        if cookie is None:
            cookie = COOKIE
        if cookie == "":
            raise Exception("environment variable SUNO_COOKIE is not set")
        super().__init__(cookie)
        self._sid = self._get_sid()
        self.songs = Songs(self)

    def _get_sid(self) -> str:
        url = "https://clerk.suno.ai/v1/client?_clerk_js_version=4.70.5"
        response = super().request("GET", url)
        if not response.ok:
            raise Exception(f"failed to get SID: {response.status_code}")
        data = response.json()
        return data.get("response").get("last_active_session_id")

    def _get_jwt(self) -> str:
        url = f"https://clerk.suno.ai/v1/client/sessions/{self._sid}/tokens/api?_clerk_js_version=4.70.5"
        response = super().request("POST", url)
        if not response.ok:
            raise Exception(f"failed to get JWT: {response.status_code}")
        data = response.json()
        return data.get("jwt")

    def _renew(self) -> None:
        self._session.headers["Authorization"] = f"Bearer {self._get_jwt()}"

    def request(self, *args, **kwargs) -> requests.Response:
        response = super().request(*args, **kwargs)
        while response.status_code == 401:
            self._renew()
            response = super().request(*args, **kwargs)
        return response

    def get_songs(self) -> List[Song]:
        url = "https://studio-api.suno.ai/api/feed"
        response = self.request("GET", url)
        if not response.ok:
            raise Exception(f"failed to get songs: {response.status_code}")
        data = response.json()
        return [Song(**song) for song in data]

    def get_song(self, id: str) -> Song:
        url = f"https://studio-api.suno.ai/api/feed/?ids={id}"
        response = self.request("GET", url)
        if not response.ok:
            raise Exception(f"failed to get song: {response.status_code}")
        data = response.json()
        return Song(**data[0])

    def get_credits(self) -> int:
        url = "https://studio-api.suno.ai/api/billing/info"
        response = self.request("GET", url)
        if not response.ok:
            raise Exception(f"failed to get credits: {response.status_code}")
        data = response.json()
        return data.get("total_credits_left")


class APIResource:

    def __init__(self, client: Client) -> None:
        self._client = client

    def request(self, *args, **kwargs) -> requests.Response:
        return self._client.request(*args, **kwargs)

    def sleep(self, seconds: Optional[float] = None) -> None:
        return self._client.sleep(seconds)


class Songs(APIResource):

    def generate(
        self,
        prompt: str,
        custom: bool = False,
        tags: str = "",
        instrumental: bool = False,
    ) -> List[Song]:
        url = "https://studio-api.suno.ai/api/generate/v2/"
        timeout = 600
        # TODO: refactor this
        if custom:
            # create a song without lyrics
            if instrumental:
                payload = {
                    "mv": "chirp-v3-0",
                    "tags": prompt,  # style of music
                    "prompt": "",
                    "make_instrumental": instrumental,
                }
            # create a song with lyrics
            else:
                payload = {
                    "mv": "chirp-v3-0",
                    "tags": tags,  # style of music
                    "prompt": prompt,  # lyrics
                    "make_instrumental": instrumental,
                }
        else:
            payload = {
                "mv": "chirp-v3-0",
                "prompt": "",
                "gpt_description_prompt": prompt,
                "make_instrumental": instrumental,
            }
        data = json.dumps(payload)
        response = self.request("POST", url, data=data)
        if not response.ok:
            raise Exception(f"failed to generate songs: {response.status_code}")
        data = response.json()
        songs = data.get("clips")
        ids = [song.get("id") for song in songs]
        start = time.time()
        while True:
            if time.time() - start > timeout:
                raise Exception("failed to generate songs: TIMEOUT")
            if sum([self._is_ready(id) for id in ids]) == len(ids):
                print("")
                break
            else:
                print(".", end="", flush=True)
        for id in ids:
            print(f"song link: https://app.suno.ai/song/{id}")
        return [self._get(id) for id in ids]

    def _get(self, id: str) -> Song:
        song = self._client.get_song(id)
        self.sleep()
        return song

    def _is_ready(self, id: str) -> bool:
        song = self._get(id)
        return (song.audio_url != "") and (song.video_url != "")

    def list(self) -> List[Song]:
        return self._client.get_songs()

    def get(self, id: str) -> Song:
        return self._client.get_song(id)


def download(
    song: str | Song,
    root: str = ".",
) -> None:
    id = _get_id(song)
    print(f"id: {id}")
    url = _audio_url(id)
    print(f"audio url: {url}")
    response = requests.request("GET", url)
    if not response.ok:
        raise Exception(
            f"failed to download from audio url: {response.status_code}"
        )
    file = _audio_file(id, root)
    with open(file, "wb") as f:
        f.write(response.content)
    print(f"audio file: {file}")


def _get_id(song: str | Song) -> str:
    if isinstance(song, Song):
        return song.id
    if not isinstance(song, str):
        raise TypeError
    id_pattern = r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"
    match = re.search(id_pattern, song)
    if match:
        return match.group(0)
    raise ValueError


def _audio_url(id: str) -> str:
    return f"https://cdn1.suno.ai/{id}.mp3"


def _audio_file(id: str, root: str = ".") -> str:
    output_dir = pathlib.Path(root) / ".suno"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"suno-{id}.mp3"
