"""
Module containing the FreetubeVideo class.
"""

from dataclasses import dataclass


__all__ = ["FreetubeVideo"]


@dataclass(frozen=True)
class FreetubeVideo:
    """
    FreetubeVideo class. Contains all the information stored about a video in a FreetubePlaylist.
    """

    id: str
    title: str

    author_id: str
    author_name: str

    length: int  # seconds
    date_published: int  # unix timestamp
    date_added: int  # unix timestamp

    playlist_item_id: str
