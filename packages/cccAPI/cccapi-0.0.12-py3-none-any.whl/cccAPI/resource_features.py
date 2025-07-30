# Configure logging
import logging
logger = logging.getLogger("cccAPI")

class cccAPIResource:
    def __init__(self, connection):
        """Handles CCC Resource Features API endpoints."""
        self.connection = connection