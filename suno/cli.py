# import json
import os

# import requests
import suno
import typer
from rich import print

VERSION = "0.1.1"
COOKIE = os.getenv("SUNO_COOKIE")
# HOST = "127.0.0.1"
# PORT = 8000


# Suno API client
client = suno.Suno(cookie=COOKIE)


def version_callback(value: bool):
    if value:
        print(f"Suno {VERSION}: make a song with Suno using v3 🥳")
        raise typer.Exit()


# Typer app
app = typer.Typer()
app_songs = typer.Typer()
app.add_typer(
    app_songs,
    name="songs",
    help="Make your songs with Suno.",
)
app_credits = typer.Typer()
app.add_typer(
    app_credits,
    name="credits",
    help="Check your remaining credits on Suno.",
)


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
    )
) -> None:
    pass


@app_songs.command(help="Generate your songs.")
def generate(
    prompt: str,
    custom: bool = typer.Option(
        prompt="Are you sure you want to create a song in custom mode?",
        help="Create a song in custom mode.",
    ),
    tags: str = "",
    instrumental: bool = typer.Option(
        prompt="Are you sure you want to create a song without lyrics?",
        help="Create a song without lyrics.",
    ),
) -> None:
    songs = client.songs.generate(
        prompt,
        custom=custom,
        tags=tags,
        instrumental=instrumental,
    )
    data = [song.model_dump() for song in songs]
    # data = json.dumps(
    #     {
    #         "prompt": prompt,
    #         "custom": custom,
    #         "tags": tags,
    #         "instrumental": instrumental,
    #     }
    # )
    # response = requests.post(f"http://{HOST}:{PORT}/v1/songs", data=data)
    # if not response.ok:
    #     raise Exception(f"failed to generate songs: {response.status_code}")
    # data = response.json()
    print(data)


@app_songs.command(help="List all your created songs in the library.")
def list() -> None:
    songs = client.get_songs()
    data = [song.model_dump() for song in songs]
    # response = requests.get(f"http://{HOST}:{PORT}/v1/songs")
    # if not response.ok:
    #     raise Exception(f"failed to get songs: {response.status_code}")
    # data = response.json()
    print(data)


@app_songs.command(help="Get a song by its ID.")
def get(id: str) -> None:
    song = client.get_song(id)
    data = song.model_dump()
    # response = requests.get(f"http://{HOST}:{PORT}/v1/song/{id}")
    # if not response.ok:
    #     raise Exception(f"failed to get song: {response.status_code}")
    # data = response.json()
    print(data)


@app_songs.command(help="Download a song on Suno.")
def download(song: str, root: str = ".") -> None:
    suno.download(song, root=root)


@app_credits.command(help="Display your remaining credits.")
def display() -> None:
    credits = client.get_credits()
    data = {"total_credits_left": credits}
    # response = requests.get(f"http://{HOST}:{PORT}/v1/credits")
    # if not response.ok:
    #    raise Exception(f"failed to get credits: {response.status_code}")
    # data = response.json()
    print(data)


if __name__ == "__main__":
    app(prog_name="suno")
