import os
import json
from jsonschema import validate, RefResolver
from jsonschema.exceptions import ValidationError
import importlib.resources

# Configure logging
import logging
logger = logging.getLogger("cccAPI")

class cccAPIApplication:
    def __init__(self, connection):
        """Handles CCC Application API endpoints."""
        self.connection = connection

    def list_application_entry_points(self):
        """
        List application entry points.

        :return: API response containing application entry points.
        :raises ValueError: If the response does not conform to the ApplicationDescriptionDTO.json schema.
        """
        # Send the GET request to the root endpoint
        response = self.connection.get("")

        # Load the ApplicationDescriptionDTO.json schema using importlib.resources
        try:
            with importlib.resources.open_text("cccAPI.definitions", "ApplicationDescriptionDTO.json") as schema_file:
                schema = json.load(schema_file)
        except FileNotFoundError as e:
            raise RuntimeError("Schema file ApplicationDescriptionDTO.json not found in package.") from e

        # Validate the response against the schema
        try:
            validate(instance=response, schema=schema)
            logger.debug("Validation successful")
        except ValidationError as e:
            raise ValueError(f"Response validation failed: {e.message}")

        return response

    def list_application_settings(self):
        """
        List application current settings.

        :return: API response containing application settings.
        """
        # Send the GET request to the /settings endpoint
        response = self.connection.get("settings")

        # Return the response as-is
        return response