import asyncio
import io
import os
from typing import Any, Dict, List, Self

import numpy as np
import pytest
import soundfile

from naint import NAINT, AsyncNAINT


@pytest.fixture(scope="module")
def fake_input_files(test_data_directory: str) -> List[str]:
    def _create_fake_audio() -> (np.ndarray, int):
        channels = np.random.randint(1, 5)
        length = np.random.randint(10_000, 500_000)
        sample_rate = np.random.choice([16000, 22050, 44100, 48000])

        audio = np.random.random(size=(channels, length))
        return audio, sample_rate

    result_paths = []

    for file_name in ["reference.wav", "origin.wav"]:
        waveform, sample_rate = _create_fake_audio()
        soundfile.write(f"{test_data_directory}/{file_name}", data=waveform.T, samplerate=sample_rate)
        result_paths.append(f"{test_data_directory}/{file_name}")

    return result_paths


@pytest.fixture(scope="module")
def fake_output_file(test_data_directory) -> str:
    output_path = f"{test_data_directory}/fake_output.wav"

    sample_rate = 22050
    channels = 1
    length = np.random.randint(10_000, 500_000)

    audio = np.random.random(size=(channels, length))

    soundfile.write(output_path, data=audio.T, samplerate=sample_rate)

    return output_path


class MockResponse:
    def __init__(self, audio_path: str):
        with open(audio_path, "rb") as file:
            self._content = file.read()

    def __call__(self, route, files) -> Self:
        assert route == "/v1/voice_cloning"
        assert files
        return self

    def raise_for_status(self) -> bool:
        return True

    def json(self) -> Dict[str, Any]:
        return {"content": self._content}


class AcyncMockResponse(MockResponse):
    def __init__(self, audio_path: str):
        super().__init__(audio_path)

    async def __call__(self, route, files) -> Self:
        await asyncio.sleep(0.1)
        assert route == "/v1/voice_cloning"
        assert files
        return self


def test_sync_clone(fake_input_files: List[str], fake_output_file: str, mocker):
    mocked_response = MockResponse(fake_output_file)
    mocker.patch("naint.voice_cloning.Client.post", new=mocked_response)

    reference_path, origin_path = fake_input_files

    voice_cloning_client = NAINT(api_key="SOME_KEY", base_url="SOME_URL").voice_cloning
    data = voice_cloning_client.clone(origin_audio=origin_path, reference_audio=reference_path)

    # Soundfile return waveform as [frames x channels]
    assert "content" in data.keys()
    waveform, sample_rate = soundfile.read(io.BytesIO(data["content"]), always_2d=True)
    assert sample_rate == 22050
    assert waveform.shape[1] == 1
    assert waveform.shape[0] > 0


def test_sync_clone_to_file(fake_input_files: List[str], fake_output_file: str, test_data_directory, mocker):
    mocked_response = MockResponse(fake_output_file)
    mocker.patch("naint.voice_cloning.Client.post", new=mocked_response)

    reference_path, origin_path = fake_input_files
    save_path = f"{test_data_directory}/output.wav"

    voice_cloning_client = NAINT(api_key="SOME_KEY", base_url="SOME_URL").voice_cloning
    voice_cloning_client.clone_to_file(origin_audio=origin_path, reference_audio=reference_path, save_file=save_path)

    assert os.path.isfile(save_path)
    waveform, sample_rate = soundfile.read(save_path, always_2d=True)
    assert sample_rate == 22050
    assert waveform.shape[1] == 1
    assert waveform.shape[0] > 0


@pytest.mark.asyncio
async def test_async_clone(fake_input_files: List[str], fake_output_file: str, mocker):
    mocked_response = AcyncMockResponse(fake_output_file)
    mocker.patch("naint.voice_cloning.AsyncClient.post", new=mocked_response)

    reference_path, origin_path = fake_input_files

    voice_cloning_client = AsyncNAINT(api_key="SOME_KEY", base_url="SOME_URL").voice_cloning
    data = await voice_cloning_client.clone(origin_audio=origin_path, reference_audio=reference_path)

    # Soundfile return waveform as [frames x channels]
    assert "content" in data.keys()
    waveform, sample_rate = soundfile.read(io.BytesIO(data["content"]), always_2d=True)
    assert sample_rate == 22050
    assert waveform.shape[1] == 1
    assert waveform.shape[0] > 0


@pytest.mark.asyncio
async def test_async_clone_to_file(fake_input_files: List[str], fake_output_file: str, test_data_directory, mocker):
    mocked_response = AcyncMockResponse(fake_output_file)
    mocker.patch("naint.voice_cloning.AsyncClient.post", new=mocked_response)

    reference_path, origin_path = fake_input_files
    save_path = f"{test_data_directory}/output.wav"

    voice_cloning_client = AsyncNAINT(api_key="SOME_KEY", base_url="SOME_URL").voice_cloning
    await voice_cloning_client.clone_to_file(
        origin_audio=origin_path, reference_audio=reference_path, save_file=save_path
    )

    assert os.path.isfile(save_path)
    waveform, sample_rate = soundfile.read(save_path, always_2d=True)
    assert sample_rate == 22050
    assert waveform.shape[1] == 1
    assert waveform.shape[0] > 0
