import array
import base64
import json
import re
import subprocess
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from uuid import UUID

import pillow_avif  # noqa: F401
from PIL import Image, ImageOps
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import LocalStorage
from app.models.enums import MediaStatus
from app.models.media import MediaAsset

_IMAGE_WIDTHS = (480, 960, 1600)
_LUFS = re.compile(r"\bI:\s*(-?\d+(?:\.\d+)?)")


@dataclass(frozen=True)
class AudioRender:
    variants: dict[str, object]
    duration_s: float
    lufs: float
    peaks_key: str


def render_image(
    source: Path,
    sha: str,
    storage: LocalStorage,
) -> tuple[dict[str, object], int, int, str]:
    with Image.open(source) as raw:
        image = ImageOps.exif_transpose(raw)
        if image is None:
            image = raw
        has_alpha = image.mode in {"RGBA", "LA"} or (
            image.mode == "P" and "transparency" in image.info
        )
        image = image.convert("RGBA" if has_alpha else "RGB")
        width, height = image.size
        variants: dict[str, object] = {"webp": {}, "avif": {}}
        webp: dict[str, str] = {}
        avif: dict[str, str] = {}
        for target_width in _IMAGE_WIDTHS:
            target_height = max(1, round(height * (target_width / width)))
            resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            webp_key = f"public/img/{sha[:2]}/{sha}-{target_width}.webp"
            avif_key = f"public/img/{sha[:2]}/{sha}-{target_width}.avif"
            _save(storage, resized, webp_key, "WEBP", quality=78)
            _save(storage, resized, avif_key, "AVIF", quality=50)
            webp[str(target_width)] = webp_key
            avif[str(target_width)] = avif_key
        variants["webp"] = webp
        variants["avif"] = avif
        thumb = image.copy()
        thumb.thumbnail((16, 16))
        encoded = BytesIO()
        thumb.save(encoded, format="WEBP", quality=20)
        lqip = "data:image/webp;base64," + base64.b64encode(encoded.getvalue()).decode()
    return variants, width, height, lqip


def render_audio(source: Path, sha: str, storage: LocalStorage) -> AudioRender:
    m4a_key = f"public/audio/{sha}.m4a"
    mp3_key = f"public/audio/{sha}.mp3"
    peaks_key = f"public/audio/{sha}.peaks.json"
    m4a_path = storage.path(m4a_key)
    mp3_path = storage.path(mp3_key)
    m4a_path.parent.mkdir(parents=True, exist_ok=True)
    _ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            str(m4a_path),
        ]
    )
    _ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "320k",
            str(mp3_path),
        ]
    )
    duration = float(
        _capture(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(source),
            ]
        ).strip()
    )
    loudness = _capture(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(source),
            "-af",
            "ebur128=framelog=quiet",
            "-f",
            "null",
            "-",
        ]
    )
    match = _LUFS.search(loudness)
    if match is None:
        raise RuntimeError("ffmpeg no devolvió LUFS.")
    peaks = _peaks(source)
    peaks_path = storage.path(peaks_key)
    peaks_path.parent.mkdir(parents=True, exist_ok=True)
    peaks_path.write_text(json.dumps(peaks), encoding="utf-8")
    return AudioRender(
        variants={"m4a": m4a_key, "mp3": mp3_key},
        duration_s=duration,
        lufs=float(match.group(1)),
        peaks_key=peaks_key,
    )


async def apply_image_result(
    session: AsyncSession,
    media_id: UUID,
    variants: dict[str, object],
    width: int,
    height: int,
    lqip: str,
) -> None:
    asset = await _asset(session, media_id)
    asset.variants = variants
    asset.width = width
    asset.height = height
    asset.lqip = lqip
    asset.status = MediaStatus.READY


async def apply_audio_result(session: AsyncSession, media_id: UUID, rendered: AudioRender) -> None:
    asset = await _asset(session, media_id)
    asset.variants = rendered.variants
    asset.duration_s = rendered.duration_s
    asset.lufs_integrated = rendered.lufs
    asset.peaks_key = rendered.peaks_key
    asset.status = MediaStatus.READY


def _save(storage: LocalStorage, image: Image.Image, key: str, fmt: str, *, quality: int) -> None:
    buffer = BytesIO()
    image.save(buffer, format=fmt, quality=quality)
    buffer.seek(0)
    storage.save(buffer, key)


def _peaks(source: Path) -> list[float]:
    raw = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(source),
            "-ac",
            "1",
            "-ar",
            "8000",
            "-f",
            "s16le",
            "-",
        ],
        check=True,
        capture_output=True,
    ).stdout
    samples = array.array("h")
    samples.frombytes(raw)
    total = len(samples)
    peaks: list[float] = []
    for index in range(800):
        start = index * total // 800
        end = (index + 1) * total // 800
        window = samples[start:end] or array.array("h", [0])
        peaks.append(float(max(abs(sample) for sample in window)))
    top = max(peaks) or 1.0
    return [round(value / top, 4) for value in peaks]


def _ffmpeg(args: list[str]) -> None:
    subprocess.run(args, check=True, capture_output=True)


def _capture(args: list[str]) -> str:
    completed = subprocess.run(args, check=False, capture_output=True, text=True)
    output = completed.stdout + completed.stderr
    if completed.returncode != 0 and "I:" not in output:
        raise subprocess.CalledProcessError(completed.returncode, args, output)
    return output


async def _asset(session: AsyncSession, media_id: UUID) -> MediaAsset:
    asset = await session.get(MediaAsset, media_id)
    if asset is None:
        raise LookupError(media_id)
    return asset
