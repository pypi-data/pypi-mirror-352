from .conn import cccAPIConnection
from .image_groups  import cccAPIImageGroups
from .custom_groups import  cccAPICustomGroups
from .network_groups import  cccAPINetworkGroups
from .resource_features import  cccAPIResource
from .image_capture_deployment import  cccAPIImageCaptureDeployment
from .power_operation import  cccAPIPowerOperations
from .application import  cccAPIApplication
from .architecture import  cccAPIArchitecture
from .management_cards import  cccAPIManagementCards
from .tasks import cccAPITasks
from .nodes import cccAPINodes


import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log message format
    handlers=[
        logging.StreamHandler(),  # Log to console
        #logging.FileHandler("ccc_client.log", mode="a")  # Log to a file (append mode)
    ]
)

class cccAPIClient:
    def __init__(self, base_url, username, password):
        """
        Initialize the cccAPI client wrapper.

        :param base_url: CCC API base URL
        :param username: CCC username 
        :param password: CCC password
        """
        # Initialize the connection
        if not base_url or not username or not password:
            raise ValueError("Base URL, username, and password must be provided.")
        self.connection = cccAPIConnection(base_url, username, password)

        # Attach API Modules
        self.nodes = cccAPINodes(self.connection)
        self.image_groups  = cccAPIImageGroups(self.connection)
        self.custom_groups = cccAPICustomGroups(self.connection)
        self.network_groups = cccAPINetworkGroups(self.connection)
        self.resource_features = cccAPIResource(self.connection)
        self.image_capture_deployment = cccAPIImageCaptureDeployment(self.connection)
        self.power_operation = cccAPIPowerOperations(self.connection)
        self.application = cccAPIApplication(self.connection)
        self.architecture = cccAPIArchitecture(self.connection)
        self.management_cards = cccAPIManagementCards(self.connection)
        self.tasks = cccAPITasks(self.connection)
    
    def close_session(self):
        """Close the cccAPI client session by calling the exit method in the connection."""
        return self.connection.exit()
    
    def get_session(self, token):
        """
        Retrieve session details for a given token.

        :param token: The session token (String).
        :return: API response containing session details.
        :raises ValueError: If the token is not a valid string.
        """
        if not isinstance(token, str) or not token.strip():
            raise ValueError("The 'token' parameter must be a non-empty string.")

        # Send the GET request to the /sessions/{token} endpoint
        response = self.connection.get(f"sessions/{token}")

        # Return the response as-is
        return response

    def delete_session(self, token):
        """
        Delete a session for a given token.

        :param token: The session token (String).
        :return: API response indicating the result of the deletion.
        :raises ValueError: If the token is not a valid string.
        """
        if not isinstance(token, str) or not token.strip():
            raise ValueError("The 'token' parameter must be a non-empty string.")

        # Send the DELETE request to the /sessions/{token} endpoint
        response = self.connection.delete(f"sessions/{token}")

        # Return the response as-is
        return response
    
    def list_sessions(self):
        """
        List all active sessions.

        :return: API response containing all active sessions.
        """
        # Send the GET request to the /sessions endpoint
        response = self.connection.get("sessions")

        # Return the response as-is
        return response