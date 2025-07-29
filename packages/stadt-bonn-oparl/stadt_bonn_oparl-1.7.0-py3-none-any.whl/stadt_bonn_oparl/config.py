from pathlib import Path

from . import __version__

# OParl API configuration
OPARL_BASE_URL = "http://localhost:8000"
UPSTREAM_API_URL = "https://www.bonn.sitzung-online.de/public/oparl"

OPARL_PAPERS_ENDPOINT = "/papers?body=1"
OPARL_MAX_PAGES = 5  # Limit number of pages to fetch (20 items per page)

# Application settings
USER_AGENT = f"stadt-bonn-ratsinfo/{__version__} (https://machdenstaat.de)"

CACHE_DIR = Path(".") / ".cache" / "oparl_responses"
DEFAULT_DATA_PATH = Path("./data")
