"""
Module containing the "playlists.db" file parser.
"""

import json
import platform
from pathlib import Path
from typing import Optional, Any, Union

from freetubedb import FreetubePlaylist, FreetubeVideo


__all__ = ["parse_playlists_file"]


def default_playlists_file_path() -> Path:
    # https://docs.freetubeapp.io/usage/data-location/

    match platform.system():
        case "Windows":
            import os

            return Path(str(os.getenv("APPDATA"))).joinpath("FreeTube", "playlists.db")
        case "Darwin":  # macOS
            return Path(
                "~/Library/Application Support/FreeTube/playlists.db"
            ).expanduser()
        case _:  # Linux/Unix
            return Path("~/.config/FreeTube/playlists.db").expanduser()


def parse_video_entry(video_entry: dict[str, Union[str, int]]) -> FreetubeVideo:
    return FreetubeVideo(
        id=str(video_entry["videoId"]),
        title=str(video_entry["title"]),
        author_id=str(video_entry["authorId"]),
        author_name=str(video_entry["author"]),
        length=int(video_entry["lengthSeconds"]),
        date_published=int(video_entry["published"]),
        date_added=int(video_entry["timeAdded"]),
        playlist_item_id=str(video_entry["playlistItemId"]),
    )


def parse_playlist_entries(
    playlist_entries: list[dict[str, Any]],
) -> list[FreetubePlaylist]:
    playlists: list[FreetubePlaylist] = []
    seen_playlist_ids: set[str] = set()
    deleted_playlist_ids: set[str] = set()

    for playlist_entry in reversed(playlist_entries):
        id: str = playlist_entry["_id"]

        if id in deleted_playlist_ids or id in seen_playlist_ids:
            continue

        deleted: bool = "$$deleted" in playlist_entry
        if deleted:
            deleted_playlist_ids.add(id)
            continue

        playlists.append(
            FreetubePlaylist(
                id=str(id),
                name=str(playlist_entry["playlistName"]),
                description=str(playlist_entry["description"]),
                protected=bool(playlist_entry["protected"]),
                videos=list(map(parse_video_entry, playlist_entry["videos"])),
            )
        )
        seen_playlist_ids.add(id)

    return playlists


def parse_playlists_file(
    playlists_file: Optional[Path] = None,
) -> list[FreetubePlaylist]:
    playlists_file = playlists_file or default_playlists_file_path()

    if not playlists_file.exists():
        raise FileNotFoundError(f"File does not exist: {playlists_file}")

    playlist_entries: list[dict[str, Any]] = []
    with playlists_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue  # skip blank lines

            playlist_entry: dict[str, Any] = json.loads(line)
            playlist_entries.append(playlist_entry)

    return parse_playlist_entries(playlist_entries)
