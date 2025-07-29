import os
import logging
from rich.logging import RichHandler


# Get debug level from environment variable
debug_level = int(os.environ.get("QIMCHI_DEBUG_LEVEL", logging.INFO))

logging.basicConfig(
    level=debug_level,
    format="%(message)s",
    handlers=[RichHandler()],
)

# Qimchi Logger
logger = logging.getLogger(__name__)
