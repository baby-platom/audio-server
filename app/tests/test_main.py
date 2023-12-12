import math
import random
import string
from pathlib import Path
from tempfile import NamedTemporaryFile

import aiofiles
import pytest
from config.settings import settings
from fastapi import status
from httpx import AsyncClient
from main import app
from pydub import AudioSegment


def get_random_api_key() -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(random.randint(10, 50)))


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health-check/")
    assert response.status_code == status.HTTP_200_OK


audio_dbfs_url = "/api/v1/audio/dbfs/"
auth_headers = {"access_token": settings.API_KEY}

audio_wav_file_path = Path(Path(__file__).parent / "test_audio.wav")
audio_mp3_file_path = Path(Path(__file__).parent / "test_audio.mp3")
audio_ogg_file_path = Path(Path(__file__).parent / "test_audio.ogg")


@pytest.mark.anyio
async def test_dbfs_no_auth():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(audio_dbfs_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    headers = {"access_token": get_random_api_key()}
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(audio_dbfs_url, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_dbfs_wav():
    target_dbfs = -15
    data = {"target": target_dbfs}
    files = {"file": open(audio_wav_file_path, "rb")}

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(audio_dbfs_url, data=data, files=files, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    tmp_file = NamedTemporaryFile(suffix=".wav")
    tmp_file.write(response.content)
    final_dbfs = AudioSegment.from_wav(tmp_file, "wav").dBFS
    assert math.isclose(target_dbfs, final_dbfs, rel_tol=0.5)
    tmp_file.close()


@pytest.mark.anyio
async def test_dbfs_mp3():
    target_dbfs = -15
    data = {"target": target_dbfs}
    files = {"file": open(audio_mp3_file_path, "rb")}

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(audio_dbfs_url, data=data, files=files, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    tmp_file_path = Path("result_audio.mp3")  # bug of pydub module, can not correctly read mp3 from a TemporaryFile
    try:
        async with aiofiles.open(tmp_file_path, "wb") as f:
            await f.write(response.content)
        final_dbfs = AudioSegment.from_mp3(tmp_file_path).dBFS
        assert math.isclose(target_dbfs, final_dbfs, rel_tol=0.5)
    finally:
        tmp_file_path.unlink()


@pytest.mark.anyio
async def test_positive_dbfs_value():
    data = {"target": 10}
    files = {"file": open(audio_mp3_file_path, "rb")}

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(audio_dbfs_url, data=data, files=files, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_dbfs_unsupported_format():
    data = {"target": -10}
    files = {"file": open(audio_ogg_file_path, "rb")}

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(audio_dbfs_url, data=data, files=files, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
