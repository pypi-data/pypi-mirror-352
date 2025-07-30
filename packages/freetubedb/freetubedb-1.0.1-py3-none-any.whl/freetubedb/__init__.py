__productname__ = "freetubedb"
__version__ = "1.0.1"
__description__ = "Python library for interacting with FreeTube's playlists.db file"
__url__ = "https://github.com/FawkesOficial/python-freetubedb"
__author__ = "FawkesOficial"
__author_email__ = "mario.lourenco.morte@gmail.com"
__license__ = "GNU General Public License v3 (GPLv3)"
__bugtracker__ = "https://github.com/FawkesOficial/python-freetubedb/issues"
__ci__ = "https://github.com/FawkesOficial/python-freetubedb/actions"
__changelog__ = "https://github.com/FawkesOficial/python-freetubedb/releases"
__cake__ = "lie"


from freetubedb.models import FreetubePlaylist, FreetubeVideo
from freetubedb.parser import parse_playlists_file


__all__ = ["FreetubePlaylist", "FreetubeVideo", "parse_playlists_file"]
