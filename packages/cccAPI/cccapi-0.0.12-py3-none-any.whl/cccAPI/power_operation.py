# Configure logging
import logging
logger = logging.getLogger("cccAPI")

class cccAPIPowerOperations:
    def __init__(self, connection):
        """Handles CCC Power Operations API endpoints."""
        self.connection = connection