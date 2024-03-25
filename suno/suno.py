import json
from typing import List

from curl_cffi import requests


class Client:

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }

    def __init__(self, cookie: str) -> None:
        self.headers["cookie"] = cookie
        self._session = requests.Session(headers=self.headers)
        self._sid = None

    def request(self, *args, **kwargs):
        kwargs["impersonate"] = kwargs.get("impersonate", "chrome")
        return self._session.request(*args, **kwargs)


class Suno(Client):

    def __init__(self, cookie: str) -> None:
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

    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)
        while response.status_code == 401:
            self._renew()
            response = super().request(*args, **kwargs)
        return response

    def get_credits(self) -> int:
        url = "https://studio-api.suno.ai/api/billing/info"
        response = self.request("GET", url)
        if not response.ok:
            raise Exception(f"failed to get credits: {response.status_code}")
        data = response.json()
        return data.get("total_credits_left")


class APIResource:

    def __init__(self, client: Suno) -> None:
        self._client = client

    def request(self, *args, **kwargs):
        return self._client.request(*args, **kwargs)


class Songs(APIResource):

    def generate(
        self,
        prompt: str,
        instrumental: bool = False,
        custom: bool = False,
        tags: str = "",
    ) -> List:
        url = "https://studio-api.suno.ai/api/generate/v2/"
        if custom:
            payload = {
                "mv": "chirp-v3-0",
                "tags": tags,
                "prompt": prompt,
                "gpt_description_prompt": "",
                "make_instrumental": instrumental,
            }
        else:
            payload = {
                "mv": "chirp-v3-0",
                "gpt_description_prompt": prompt,
                "prompt": "",
                "make_instrumental": instrumental,
            }
        response = self.request("POST", url, data=json.dumps(payload))
        if not response.ok:
            raise Exception(f"failed to generate songs: {response.status_code}")
        data = response.json()
        songs = data["clips"]
        ids = [song["id"] for song in songs]
        for id in ids:
            print(f"song link: https://app.suno.ai/song/{id}")
        return songs

    def list(self) -> List:
        url = f"https://studio-api.suno.ai/api/feed"
        response = self.request("GET", url)
        if not response.ok:
            raise Exception(f"failed to get songs: {response.status_code}")
        data = response.json()
        return data

    def get(self, id: str) -> dict:
        url = f"https://studio-api.suno.ai/api/feed/?ids={id}"
        response = self.request("GET", url)
        if not response.ok:
            raise Exception(f"failed to get song: {response.status_code}")
        data = response.json()
        return data[0]
