# Suno AI API

[![GitHub][github_badge]][github_link] [![PyPI][pypi_badge]][pypi_link]

**Suno AI API** is

* An unofficial Python library for [Suno AI](https://www.suno.ai/) API

**Suno AI API** supports to

- [x] Create a Python client for Suno AI
- [x] Utilize Chirp v3 model to make a song by default
- [ ] Continue from a song
- [x] Make a song using CLI
- [x] Deploy a REST API available at [http://http://127.0.0.1/:8000](http://localhost:8000/)
- [ ] Deploy with Docker
- [ ] Deploy on Vercel



## Installation

```bash
pip install suno-api
```

or 

```bash
git clone git@github.com:imyizhang/suno-api.git
cd suno-api
poetry install --only main
```



## Quickstart

### Sign in to Suno AI at https://app.suno.ai/, and get your cookie

You can find your cookie from the browser's **Developer Tools** -> **Network** tab

![Screenshot](Screenshot.png)



### Create a client for Suno AI with your cookie

```python
import suno

client = suno.Suno(cookie="your-cookie-here")
```



### Create your clips

```python
clips = client.songs.generate(
    "your-song-description-here", 
    instrumental=False,
)
```

or start with **custom mode**


```python
clips = client.songs.generate(
    "your-lyrics-here", 
    cutomized=True,
    tags="your-music-style-here",
    instrumental=False,
)
```



### Review your newly created clip

```python
clip = client.songs.get("your-clip-id-here")
```



### Review all your created clips in the library

```python
clips = client.songs.list()
```



### Check your remaining credits

```python
credits = client.get_credits()
```



### Download a clip on Suno AI

```python
suno.download("your-clip-id-here")
```



## Documentation

### Python Library

#### `suno.Song`

##### `suno.Song(*args, **kwargs)`

An object representing a song.

**Properties:**

**id** (`str`): Unique ID for the song.

**video_url** (`str`): Video URL for the song.

**audio_url** (`str`): Audio URL for the song.

**image_url** (`str | None`): Image URL for the song.

**image_large_url** (`str | None`): Large image URL for the song.

**major_model_version** (`str`): Major model version used to create the song.

**model_name** (`str`): Model name used to create the song.

**metadata** (`dict`): Metadata of the song.

**is_liked** (`bool`): The song is liked or not.

**user_id** (`str`): Unique ID for a user who created the song.

**is_trashed** (`bool`): The song is trashed or not.

**reaction** (`dict | None`): Reaction to the song.

**created** (`str`): When the song was created.

**status** (`str`): Status for the song.

**title** (`str`): Title for the song.

**play_count** (`int`): Play count for the song.

**upvote_count** (`int`): Upvote count for song.

**is_public** (`bool`): The song is public or not.



#### `suno.Suno`

##### `suno.Suno(cookie: str)`

A object representing a client for Suno AI.

**Parameters:**

- **cookie** (`str`): Cookie stored for the cookie-based authentication.

**Properties:**

**headers** (`dict`): Request headers.



##### `songs.generate(prompt: str, custom: bool, tags: str, instrumental: bool)`

Create songs.

> Each song generation consumes 5 credits, thus a total of 10 credits is necessary for each successful call.

**Parameters:**

- **prompt** (`str`): Prompt used to create the song, song, description, lyrics, or style of music.
- **custom** (`bool`, optional): Whether to create the song in custom mode. Defaults to `False`.
- **tags** (`str`, optional): Tags indicating musical style of the song to be created. Defaults to `""`.
- **instrumental** (`bool`, optional): Whether to create the song without lyrics. Defaults to `False`.

**Returns:**

(`List[suno.Song]`): A list of `suno.Song` objects representing the created songs.



##### `get_songs()`

List all songs (equivalent to `songs.list()`).

**Returns:**

(`List[suno.Song]`): A list of `suno.Song` objects representing the songs in the library of the logged-in account.



##### `get_song(id: str)`

Get a song by its ID (equivalent to `songs.get(id: str)`).

**Parameters:**

- **id** (`str`): ID of the song.

**Returns:**

(`suno.Song`): A `suno.Song` object representing the song.



##### `get_credits()`

Get all credits left.

**Returns:**

(`int`): Remaining credits in the logged-in account.



#### `suno.download`

##### `suno.download(song: str | suno.Song, root: str)`

Download a song.

**Parameters:**

- **song** (`str | suno.Song`): ID indicating a song, URL linked to a song or an `suno.Song` object.
- **root** (`str`): Root directory to store the downloaded songs.



### REST API

#### Set environment variable `SUNO_COOKIE`

##### Check the value of the environment variable `SUNO_COOKIE` on macOS

```bash
echo $SUNO_COOKIE
```

##### Add the environment variable `SUNO_COOKIE` permanently on macOS

Find your current shell.

```bash
echo $0
```

In `zsh`, a environment variable can be permanently added to the configuration file  `~/.zshrc`. In `bash`, the configuration file is `~/.bash_profile`.

```bash
vim ~/.zshrc
```

In the configuration file, add the environment variable `SUNO_COOKIE`.

```bash
export SUNO_COOKIE="your-cookie-here"
```

Save the changes to the configuration file and execute it.

```bash
source ~/.zshrc
```



#### Deployment

```bash
git clone git@github.com:imyizhang/suno-api.git
cd suno-api/suno
uvicorn api:app --reload
```

or

```bash
git clone git@github.com:imyizhang/suno-api.git
cd suno-api
poetry run python suno/api.py
```



#### POST `/v1/songs`

Create songs.

##### Request example

**cURL**

```bash
curl -X POST "http://localhost:8000/v1/songs" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Make a song about the moon"}'
```

**Suno AI CLI**

```bash
suno songs generate "Make a song about the moon"
```

**Python**

```python
import json

import requests

data = json.dumps({
    "prompt": "Make a song about the moon",
})

response = requests.post("http://localhost:8000/v1/songs", data=data)
response.json()
```



#### GET `v1/songs`

List all songs.

##### Request example

**cURL**

```bash
curl -X GET "http://localhost:8000/v1/songs" \
     -H "Accept: application/json"
```

**Suno AI CLI**

```bash
suno songs list
```

**Python**

```python
import requests

response = requests.get('http://localhost:8000/v1/songs')
response.json()
```



#### GET `v1/song/{id}`

Get a song by its ID.

##### Request example

**cURL**

```bash
curl -X GET "http://localhost:8000/v1/songs/{id}" \
     -H "Accept: application/json"
```

**Suno AI CLI**

```bash
suno songs get ID
```

**Python**

```python
import requests

response = requests.get('http://localhost:8000/v1/songs/{id}')
response.json()
```



##### Response Example

```json
{
  "id":"0e42f167-17ab-4004-941b-d549b24dce76",
  "video_url":"https://cdn1.suno.ai/0e42f167-17ab-4004-941b-d549b24dce76.mp4",
  "audio_url":"https://cdn1.suno.ai/0e42f167-17ab-4004-941b-d549b24dce76.mp3",
  "image_url":"https://cdn1.suno.ai/image_75b03116-0aa2-4367-bdf6-8556dde4df9f.png",
  "image_large_url":"https://cdn1.suno.ai/image_large_75b03116-0aa2-4367-bdf6-8556dde4df9f.png",
  "major_model_version":"v3",
  "model_name":"chirp-v3",
  "metadata":{
    "tags":"Rap\nJapanese rock\nPop\nVocaloid style\nEnergetic\nUpbeat\nCatchy\nCulinary\nCooking\nRecipe-focused",
    "prompt":"[Chorus]\nIn der Weihnachtsbäckerei\nGibt es manche Leckerei\nZwischen Mehl und Milch\nMacht so mancher Knilch\nEine riesengroße Kleckerei\nIn der Weihnachtsbäckerei\nIn der Weihnachtsbäckerei\n\n[Verse 1]\nWo ist das Rezept geblieben\nVon den Plätzchen, die wir lieben?\nWer hat das Rezept verschleppt?\n\"Ich nicht\"\n\"Du vielleicht?\"\n\"Ich auch nicht\"\n\nNa, dann müssen wir es packen\nEinfach frei nach Schnauze backen\nSchmeißt den Ofen an (oh ja)\nUnd ran\n\n[Chorus]\nIn der Weihnachtsbäckerei\nGibt es manche Leckerei\nZwischen Mehl und Milch\nMacht so mancher Knilch\nEine riesengroße Kleckerei\nIn der Weihnachtsbäckerei\nIn der Weihnachtsbäckerei\n\n[Verse 2]\nBrauchen wir nicht Schokolade\nHonig, Nüsse und Succade\nUnd ein bischen Zimt?\nDas stimmt\n\nButter, Mehl und Milch verrühren\nZwischendurch einmal probieren\nUnd dann kommt das Ei (pass auf)\nVorbei\n\n[Chorus]\nIn der Weihnachtsbäckerei\nGibt es manche Leckerei\nZwischen Mehl und Milch\nMacht so mancher Knilch\nEine riesengroße Kleckerei\nIn der Weihnachtsbäckerei\nIn der Weihnachtsbäckerei\n\n[Verse 3]\nBitte mal zur Seite treten\nDenn wir brauchen Platz zum kneten\nSind die Finger rein?\nDu Schwein\n\n\nSind die Plätzchen, die wir stechen\nErstmal auf den Ofenblechen\nWarten wir gespannt\nVerbrannt\n\n[Chorus]\nIn der Weihnachtsbäckerei\nGibt es manche Leckerei\nZwischen Mehl und Milch\nMacht so mancher Knilch\nEine riesengroße Kleckerei\nIn der Weihnachtsbäckerei\nIn der Weihnachtsbäckerei\n\n[Outro]",
    "gpt_description_prompt":"None",
    "audio_prompt_id":"None",
    "history":"None",
    "concat_history":[
      {
        "id":"7b9cfa43-d231-44e8-b69a-d9c0627b016d",
        "continue_at":107.0
      },
      {
        "id":"75b03116-0aa2-4367-bdf6-8556dde4df9f",
        "continue_at":"None"
      }
    ],
    "type":"concat",
    "duration":158.83997916666667,
    "refund_credits":"None",
    "stream":"None",
    "error_type":"None",
    "error_message":"None"
  },
  "is_liked":false,
  "user_id":"cb7486d0-238e-409e-9ff9-e69db325fa84",
  "is_trashed":false,
  "reaction":"None",
  "created_at":"2024-03-24T13:46:25.916Z",
  "status":"complete",
  "title":"In der Weihnachtsbäckerei ",
  "play_count":0,
  "upvote_count":724,
  "is_public":true
}
```



#### GET `v1/credits`

Get all credits left.

##### Request example

**cURL**

```bash
curl -X GET "http://localhost:8000/v1/credits" \
     -H "Accept: application/json"
```

**Suno AI CLI**

```bash
suno credits display
```

**Python**

```python
import requests

response = requests.get('http://localhost:8000/v1/credits')
response.json()
```



##### Response Example

```json
{
  "total_credits_left": 50
}
```



## License

**Suno AI API** has a BSD-3-Clause license, as found in the [LICENSE](https://github.com/imyizhang/suno-api/blob/main/LICENSE) file.



## Contributing

Thanks for your interest in contributing to **Suno AI API**! Please feel free to create a pull request.



## Changelog

**Suno AI API 0.1.2**

* Add a function to download any song on Suno AI
* Fix bugs for song generation



**Suno AI API 0.1.1**

* Introduce `suno.Song` to structure `suno.Suno` methods' outputs
* Support environment variable `SUNO_COOKIE`
* Support CLI for Suno AI API
* Allow to deploy REST API for Suno AI API



**Suno AI API 0.1.0**

* Quickly generate a song with a description
* Create songs with lyrics and music style in custom mode
* Review songs using their ID
* List all songs in the library




[github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label
[github_link]: https://github.com/imyizhang/suno-api



[pypi_badge]: https://badgen.net/pypi/v/suno-api?icon=pypi&color=black&label
[pypi_link]: https://www.pypi.org/project/suno-api