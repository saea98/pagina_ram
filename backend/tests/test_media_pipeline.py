import json
import math
import struct
import wave
from io import BytesIO
from pathlib import Path

import pytest
from app.core.db import SessionMaker
from app.core.storage import LocalStorage
from app.models.enums import MediaStatus, MediaVisibility
from app.models.media import MediaAsset
from app.services.media import ingest_upload
from app.workers.loop import run_once


def _wav_5s() -> bytes:
    rate = 44100
    buffer = BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        frames = bytearray()
        for index in range(rate * 5):
            sample = int(16000 * math.sin(2 * math.pi * 440 * index / rate))
            frames += struct.pack("<h", sample)
        handle.writeframes(frames)
    return buffer.getvalue()


async def test_wav_upload_is_ready_with_lufs_and_peaks(tmp_path: Path) -> None:
    storage = LocalStorage(tmp_path)
    async with SessionMaker() as session:
        asset = await ingest_upload(
            session,
            storage,
            BytesIO(_wav_5s()),
            filename="toma.wav",
            visibility=MediaVisibility.PUBLIC,
            max_bytes=30 * 1024 * 1024,
        )
        asset_id = asset.id

    for _ in range(40):
        await run_once(storage)
        async with SessionMaker() as session:
            current = await session.get(MediaAsset, asset_id)
        if current is not None and current.status is MediaStatus.READY:
            break

    async with SessionMaker() as session:
        stored = await session.get(MediaAsset, asset_id)
        assert stored is not None
        assert stored.status is MediaStatus.READY
        assert stored.lufs_integrated is not None
        assert stored.duration_s is not None
        assert float(stored.duration_s) == pytest.approx(5.0, abs=0.2)
        assert stored.peaks_key is not None
        peaks_key = stored.peaks_key

    peaks = json.loads(storage.path(peaks_key).read_text(encoding="utf-8"))
    assert len(peaks) == 800
    assert max(peaks) == 1.0
