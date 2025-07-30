# Configure logging
import logging
logger = logging.getLogger("cccAPI")

class cccAPIManagementCards:
    def __init__(self, connection):
        """Handles CCC Management Card API endpoints."""
        self.connection = connection