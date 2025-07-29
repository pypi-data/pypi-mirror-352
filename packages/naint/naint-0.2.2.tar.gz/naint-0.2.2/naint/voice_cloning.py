import os
from typing import Any, Dict

from httpx import AsyncClient, Client


class VoiceCloningClient:
    def __init__(self, client: Client):
        self._client = client

    def clone(self, origin_audio: str | os.PathLike, reference_audio: str | os.PathLike) -> Dict[str, Any]:
        with (
            open(origin_audio, "rb") as origin_file,
            open(reference_audio, "rb") as reference_file,
        ):
            files_to_send = [
                ("origin_audio", ("origin.wav", origin_file.read(), "audio/wav")),
                ("reference_audio", ("reference.wav", reference_file.read(), "audio/wav")),
            ]

        response = self._client.post("/voice_cloning", files=files_to_send)
        response.raise_for_status()
        return response.json()

    def clone_to_file(
        self, origin_audio: str | os.PathLike, reference_audio: str | os.PathLike, save_file: str | os.PathLike
    ) -> None:
        data = self.clone(origin_audio=origin_audio, reference_audio=reference_audio)

        with open(save_file, "wb") as file:
            file.write(data["content"])


class AsyncVoiceCloningClient:
    def __init__(self, client: AsyncClient):
        self._client = client

    async def clone(self, origin_audio: str | os.PathLike, reference_audio: str | os.PathLike) -> Dict[str, Any]:
        with (
            open(origin_audio, "rb") as origin_file,
            open(reference_audio, "rb") as reference_file,
        ):
            files_to_send = [
                ("origin_audio", ("origin.wav", origin_file.read(), "audio/wav")),
                ("reference_audio", ("reference.wav", reference_file.read(), "audio/wav")),
            ]

        response = await self._client.post("/voice_cloning", files=files_to_send)
        response.raise_for_status()
        return response.json()

    async def clone_to_file(
        self, origin_audio: str | os.PathLike, reference_audio: str | os.PathLike, save_file: str | os.PathLike
    ) -> None:
        data = await self.clone(origin_audio=origin_audio, reference_audio=reference_audio)

        with open(save_file, "wb") as file:
            file.write(data["content"])
