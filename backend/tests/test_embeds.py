from app.models.enums import PortfolioKind
from app.services.embeds import detect


def test_youtube_start_and_spotify_id() -> None:
    kind, external_id, start = detect("https://youtu.be/pLuaWY0WsTI?t=137")
    assert kind is PortfolioKind.YOUTUBE
    assert external_id == "pLuaWY0WsTI"
    assert start == 137
    spotify, track, _start = detect("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
    assert spotify is PortfolioKind.SPOTIFY
    assert track == "6rqhFgbbKwnb9MLmUQDhG6"
