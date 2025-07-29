"""
App Store Icon Hunter

A powerful command-line tool and REST API for searching apps and downloading 
their icons from App Store and Google Play Store in multiple sizes.
"""

__version__ = "2.0.0"
__author__ = "SU-KO KUO"
__email__ = "su@okuso.uk"
__description__ = "Search apps and download icons from App Store and Google Play"

try:
    from .core.app_store import AppStoreAPI
    from .core.google_play import GooglePlayAPI
    from .core.downloader import IconDownloader
    __all__ = ["AppStoreAPI", "GooglePlayAPI", "IconDownloader"]
except ImportError:
    # Handle import errors gracefully during development
    __all__ = []
