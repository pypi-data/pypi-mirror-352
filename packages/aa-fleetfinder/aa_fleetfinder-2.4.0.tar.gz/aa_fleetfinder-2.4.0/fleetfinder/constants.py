"""
Constants used in this app
"""

# Standard Library
import os

# Alliance Auth
from esi import __version__ as esi_version

# AA Fleet Finder
from fleetfinder import __version__

APP_NAME = "aa-fleetfinder"
APP_NAME_VERBOSE = "AA Fleet Finder"
APP_NAME_VERBOSE_USERAGENT = "AA-Fleet-Finder"
PACKAGE_NAME = "fleetfinder"
GITHUB_URL = f"https://github.com/ppfeufer/{APP_NAME}"
USER_AGENT = f"{APP_NAME_VERBOSE_USERAGENT}/{__version__} (+{GITHUB_URL}) Django-ESI/{esi_version}"

APP_BASE_DIR = os.path.join(os.path.dirname(__file__))
APP_STATIC_DIR = os.path.join(APP_BASE_DIR, "static", PACKAGE_NAME)
