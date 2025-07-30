# Configure logging
import logging
logger = logging.getLogger("cccAPI")

class cccAPIImageCaptureDeployment:
    def __init__(self, connection):
        """Handles CCC Image Capture Deployment API endpoints."""
        self.connection = connection