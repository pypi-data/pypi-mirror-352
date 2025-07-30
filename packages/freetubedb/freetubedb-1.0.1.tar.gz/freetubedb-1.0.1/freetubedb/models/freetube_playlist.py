"""
Module containing the FreetubePlaylist class.
"""

from dataclasses import dataclass, field

from freetubedb.models import FreetubeVideo


__all__ = ["FreetubePlaylist"]


@dataclass(frozen=True)
class FreetubePlaylist:
    """
    FreetubePlaylist class. Contains all the information stored about a playlist.
    """

    id: str
    name: str
    description: str
    protected: bool
    videos: list[FreetubeVideo] = field(default_factory=list[FreetubeVideo])
