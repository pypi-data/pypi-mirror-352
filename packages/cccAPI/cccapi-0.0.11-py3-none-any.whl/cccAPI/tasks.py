# Configure logging
import logging
import os
import json
from jsonschema import validate, ValidationError

logger = logging.getLogger("cccAPI")

class cccAPITasks:
    def __init__(self, connection):
        """Handles CCC Tasks API endpoints."""
        self.connection = connection
        
    def get_all_tasks(self):
        """
        Lists all tasks.
        
        :return: List of Task objects
        """
        return self.connection.get("tasks")

    def get_task(self, identifier):
        """
        Gets one or more task(s).

        :param identifier: The task identifier (String)
        :return: Task object(s)
        :raises ValueError: If the identifier is invalid
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        return self.connection.get(f"tasks/{identifier}")

    def delete_task(self, identifier):
        """
        Deletes a single task.

        :param identifier: The task identifier (String)
        :return: API response indicating success
        :raises ValueError: If the identifier is invalid
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        return self.connection.delete(f"tasks/{identifier}")

    def delete_tasks(self, identifiers):
        """
        Deletes multiple tasks.

        :param identifiers: List of task identifiers
        :return: API response indicating success
        :raises ValueError: If identifiers is not a list of strings
        """
        if not isinstance(identifiers, list) or not all(isinstance(x, str) for x in identifiers):
            raise ValueError("The 'identifiers' parameter must be a list of strings.")

        return self.connection.delete("tasks", data={"identifiers": identifiers})

    def get_task_features(self, identifier):
        """
        Gets all features of a single task.

        :param identifier: The task identifier (String)
        :return: Dictionary of task features
        :raises ValueError: If the identifier is invalid
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        return self.connection.get(f"tasks/{identifier}/features")

    def update_task_features(self, identifier, features):
        """
        Adds or modifies features of an existing task.

        :param identifier: The task identifier (String)
        :param features: Dictionary conforming to FeaturesDto.json schema
        :return: API response indicating the result of the update
        :raises ValueError: If the identifier or features are invalid
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        if not isinstance(features, dict):
            raise ValueError("The 'features' parameter must be a dictionary conforming to the FeaturesDto.json schema.")

        # Validate features against FeaturesDto schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "FeaturesDto.json")
            with open(schema_path, "r") as schema_file:
                schema = json.load(schema_file)
            resolver = self._get_schema_resolver(schema_dir)
            
            try:
                validate(instance=features, schema=schema, resolver=resolver)
                logger.debug("Features validation successful")
            except ValidationError as e:
                raise ValueError(f"Features validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file FeaturesDto.json not found at {schema_path}") from e

        return self.connection.put(f"tasks/{identifier}/features", data=features)

    def delete_task_features(self, identifier):
        """
        Removes all features of an existing task.

        :param identifier: The task identifier (String)
        :return: API response indicating success
        :raises ValueError: If the identifier is invalid
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        return self.connection.delete(f"tasks/{identifier}/features")

    def _get_schema_resolver(self, schema_dir):
        """Helper method to create a schema resolver for JSON validation."""
        from jsonschema.validators import RefResolver
        from pathlib import Path
        from urllib.parse import urljoin

        base_path = f"file://{Path(schema_dir).as_posix()}/"
        resolver = RefResolver(base_path, None)
        return resolver
