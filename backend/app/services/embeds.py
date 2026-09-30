import re
from urllib.parse import parse_qs, urlparse

import httpx
from app.models.enums import PortfolioKind
from app.schemas.admin import InspectOut

_SPOTIFY = re.compile(r"open\.spotify\.com/(track|album)/([A-Za-z0-9]+)")
_YOUTUBE_SHORT = re.compile(r"youtu\.be/([A-Za-z0-9_-]{6,})")
_YOUTUBE_ID = re.compile(r"(?:v=|embed/|shorts/)([A-Za-z0-9_-]{6,})")
_SOUNDCLOUD = re.compile(r"soundcloud\.com/.+")
_APPLE = re.compile(r"music\.apple\.com/.+")
_BANDCAMP = re.compile(r"([a-z0-9-]+\.)?bandcamp\.com/.+")


def _youtube_start(url: str) -> int | None:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    raw = None
    if "t" in query:
        raw = query["t"][0]
    elif "start" in query:
        raw = query["start"][0]
    if raw is None and parsed.fragment.startswith("t="):
        raw = parsed.fragment.removeprefix("t=")
    if raw is None:
        return None
    digits = re.sub(r"[^0-9]", "", raw)
    return int(digits) if digits else None


def detect(url: str) -> tuple[PortfolioKind | None, str | None, int | None]:
    if match := _SPOTIFY.search(url):
        return PortfolioKind.SPOTIFY, match.group(2), None
    if match := _YOUTUBE_SHORT.search(url):
        return PortfolioKind.YOUTUBE, match.group(1), _youtube_start(url)
    if match := _YOUTUBE_ID.search(url):
        return PortfolioKind.YOUTUBE, match.group(1), _youtube_start(url)
    if _SOUNDCLOUD.search(url):
        return PortfolioKind.SOUNDCLOUD, None, None
    if _APPLE.search(url):
        return PortfolioKind.APPLE_MUSIC, None, None
    if _BANDCAMP.search(url):
        return PortfolioKind.BANDCAMP, None, None
    return None, None, None


async def inspect_url(url: str) -> InspectOut:
    kind, external_id, start = detect(url)
    title = None
    artist = None
    endpoint = None
    if kind is PortfolioKind.SPOTIFY:
        endpoint = "https://open.spotify.com/oembed"
    elif kind is PortfolioKind.YOUTUBE:
        endpoint = "https://www.youtube.com/oembed"
    if endpoint is not None:
        try:
            async with httpx.AsyncClient(timeout=4) as client:
                response = await client.get(endpoint, params={"url": url, "format": "json"})
                response.raise_for_status()
                payload = response.json()
            if isinstance(payload, dict):
                raw_title = payload.get("title")
                raw_author = payload.get("author_name")
                title = raw_title if isinstance(raw_title, str) else None
                artist = raw_author if isinstance(raw_author, str) else None
        except httpx.HTTPError:
            title = None
    return InspectOut(
        kind=kind,
        external_id=external_id,
        youtube_start_s=start,
        title=title,
        artist_name=artist,
    )
