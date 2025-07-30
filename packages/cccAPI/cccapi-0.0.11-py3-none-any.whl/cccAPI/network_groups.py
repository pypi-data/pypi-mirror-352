# Configure logging
import logging
import os
import json
from jsonschema import validate, RefResolver
from jsonschema.exceptions import ValidationError
import urllib.parse

logger = logging.getLogger("cccAPI")

def get_schema_resolver(schema_dir):
    """Create a schema resolver that can resolve references within the schema directory"""
    schema_base_uri = urllib.parse.urljoin('file:', os.path.abspath(schema_dir) + '/')
    
    def custom_uri_handler(uri):
        # Handle file: URI scheme for schema references
        if uri.startswith('file:'):
            schema_path = os.path.join(schema_dir, os.path.basename(uri[5:]))
            with open(schema_path, 'r') as f:
                return json.load(f)
        return RefResolver._default_handlers[uri.split(':')[0]](uri)
    
    handlers = {'file': custom_uri_handler}
    return RefResolver(schema_base_uri, {}, handlers=handlers)

class cccAPINetworkGroups:
    def __init__(self, connection):
        """Handles CCC Network Groups Deployment API endpoints."""
        self.connection = connection
        # Load allowed fields from NetworkGroup.json
        schema_path = os.path.join(os.path.dirname(__file__), "definitions", "NetworkGroup.json")
        try:
            with open(schema_path, "r") as f:
                schema = json.load(f)
                # Initialize set with properties from the schema
                self.allowed_fields = set(schema.get("properties", {}).keys())
                # Add additional field paths
                self.allowed_fields.update({
                    "id", "uuid", "etag", "creationTime", "modificationTime", 
                    "deletionTime", "links", "links.actions", 
                    "nodes.name", "nodes.id", "nodes.uuid"
                })
        except Exception as e:
            logger.warning(f"Could not load NetworkGroup.json schema: {e}")
            self.allowed_fields = set()

        self.default_fields = "name,id"

    # Lists all network groups
    def show_networkgroups(self, params=None):
        """
        Retrieve all network groups with optional query parameters.

        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response containing network groups.
        """
        if params is None:
            params = {}

        # Validate and process the 'fields' parameter
        if "fields" in params:
            requested_fields = set(params["fields"].split(","))
            invalid_fields = requested_fields - self.allowed_fields
            if invalid_fields:
                raise ValueError(f"Invalid fields requested: {', '.join(invalid_fields)}. Allowed fields are: {', '.join(self.allowed_fields)}")
            # Use only the valid fields
            params["fields"] = ",".join(requested_fields)
        else:
            # Use default fields if 'fields' is not specified
            params["fields"] = self.default_fields

        return self.connection.get("networkgroups", params=params)

    # Gets one or more group(s)
    def show_networkgroup(self, identifier, params=None):
        """
        Retrieve details about specific network group with optional query parameters.

        :param identifier: The identifier of the network group to retrieve.
        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response for the specified network group.
        """
        if params is None:
            params = {}

        # Validate and process the 'fields' parameter
        if "fields" in params:
            requested_fields = set(params["fields"].split(","))
            invalid_fields = requested_fields - self.allowed_fields
            if invalid_fields:
                raise ValueError(f"Invalid fields requested: {', '.join(invalid_fields)}. Allowed fields are: {', '.join(self.allowed_fields)}")
            # Use only the valid fields
            params["fields"] = ",".join(requested_fields)
        else:
            # Use default fields if 'fields' is not specified
            params["fields"] = None

        return self.connection.get(f"networkgroups/{identifier}", params=params)

    # Creates one or multiple new network group(s)
    def create_networkgroups(self, groups):
        """
        Create one or multiple network groups on CCC Server.

        :param groups: A list of network group objects conforming to the NetworkGroup.json schema.
                      Example:
                      [
                          {
                              "name": "NetworkGroup1",
                              "features": {},
                              ...
                          },
                          {
                              "name": "NetworkGroup2",
                              ...
                          }
                      ]
        :return: API response from the POST /networkgroups endpoint.
        """
        if not isinstance(groups, list):
            raise ValueError("The 'groups' parameter must be a list of network group objects.")
        
        # Validate each group against the schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "NetworkGroup.json")
            with open(schema_path, "r") as schema_file:
                networkgroup_schema = json.load(schema_file)
            
            # Create a resolver for handling schema references
            resolver = get_schema_resolver(schema_dir)
            
            for group in groups:
                try:
                    validate(instance=group, schema=networkgroup_schema, resolver=resolver)
                    logger.debug("Validation successful")
                except ValidationError as e:
                    raise ValueError(f"Network group validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file NetworkGroup.json not found at {schema_path}") from e

        # Send the POST request to the /networkgroups endpoint
        response = self.connection.post("networkgroups", data=groups)

        return response

    # Updates a existing network group
    def update_networkgroup(self, identifier, body):
        """
        Update an existing network group.

        :param identifier: The identifier of the network group to update (String).
        :param body: The updated network group definition conforming to the NetworkGroup.json schema.
        :return: API response indicating the result of the update.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")
        
        if not isinstance(body, dict):
            raise ValueError("The 'body' parameter must be a dictionary conforming to the NetworkGroup.json schema.")

        # Validate the body against the NetworkGroup.json schema with reference resolution
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "NetworkGroup.json")
            with open(schema_path, "r") as schema_file:
                networkgroup_schema = json.load(schema_file)
            
            # Create a resolver for handling schema references
            resolver = get_schema_resolver(schema_dir)
            
            try:
                validate(instance=body, schema=networkgroup_schema, resolver=resolver)
                logger.debug("Validation successful")
            except ValidationError as e:
                raise ValueError(f"Network group validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file NetworkGroup.json not found at {schema_path}") from e

        # Send the PUT request to the /networkgroups/{identifier} endpoint
        response = self.connection.put(f"networkgroups/{identifier}", data=body)

        return response

    # Updates a set of existing network groups
    def update_networkgroups(self, groups, nameAsId=False):
        """
        Update multiple existing network groups.

        :param groups: A list of network group objects conforming to the NetworkGroup.json schema.
        :param nameAsId: Boolean to indicate if name should be used instead of UUID as identifier (default: False).
        :return: API response indicating the result of the update.
        """
        if not isinstance(groups, list):
            raise ValueError("The 'groups' parameter must be a list of network group objects.")

        # Validate each group against the schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "NetworkGroup.json")
            with open(schema_path, "r") as schema_file:
                networkgroup_schema = json.load(schema_file)
            
            # Create a resolver for handling schema references
            resolver = get_schema_resolver(schema_dir)
            
            for group in groups:
                try:
                    validate(instance=group, schema=networkgroup_schema, resolver=resolver)
                    logger.debug("Validation successful")
                except ValidationError as e:
                    raise ValueError(f"Network group validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file NetworkGroup.json not found at {schema_path}") from e

        # Prepare query parameters if nameAsId is True
        params = {"nameAsId": "true"} if nameAsId else None

        # Send the PUT request to update all network groups
        response = self.connection.put("networkgroups", data=groups, params=params)

        return response

    # Deletes a network group
    def delete_networkgroup(self, identifier):
        """
        Delete an existing network group.

        :param identifier: The identifier of the network group to delete (String).
        :return: API response indicating the result of the deletion.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        # Send the DELETE request to the /networkgroups/{identifier} endpoint
        response = self.connection.delete(f"networkgroups/{identifier}")

        return response

    # Deletes a set of existing network groups
    def delete_networkgroups(self, identifiers):
        """
        Delete multiple network groups.

        :param identifiers: A list of network group identifiers to delete.
        :return: API response indicating the result of the deletion.
        """
        if not isinstance(identifiers, list):
            raise ValueError("The 'identifiers' parameter must be a list of network group identifiers.")

        # Create the payload with identifiers
        body = {"identifiers": identifiers}

        # Validate the body against the MultipleIdentifierDto.json schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "MultipleIdentifierDto.json")
            with open(schema_path, "r") as schema_file:
                multiple_identifier_schema = json.load(schema_file)
            
            try:
                validate(instance=body, schema=multiple_identifier_schema)
                logger.debug("Validation of body with MultipleIdentifierDto schema successful")
            except ValidationError as e:
                raise ValueError(f"Request body validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file MultipleIdentifierDto.json not found at {schema_path}") from e

        # Send the DELETE request to the /networkgroups endpoint with the payload
        response = self.connection.delete("networkgroups", data=body)

        return response

    # Gets all features of a single group
    def show_features_in_networkgroup(self, identifier):
        """
        Retrieve all features of a network group.

        :param identifier: The identifier of the network group.
        :return: API response containing features of the network group.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        return self.connection.get(f"networkgroups/{identifier}/features")

    # Adds or modifies features of an existing group
    def add_or_modify_features_in_networkgroup(self, identifier, features):
        """
        Add or modify features of an existing network group.

        :param identifier: The identifier of the network group.
        :param features: Dictionary of features to add or modify.
        :return: API response indicating the result.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        # Create the body with features
        body = {"features": features}

        # Validate the body against the FeaturesDto.json schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "FeaturesDto.json")
            
            # Check if schema exists
            if os.path.exists(schema_path):
                with open(schema_path, "r") as schema_file:
                    features_schema = json.load(schema_file)
                
                try:
                    validate(instance=body, schema=features_schema)
                    logger.debug("Validation of body with FeaturesDto schema successful")
                except ValidationError as e:
                    raise ValueError(f"Request body validation failed: {e.message}")
        except FileNotFoundError:
            # If schema doesn't exist, just log a warning and continue
            logger.warning(f"Schema file FeaturesDto.json not found at {schema_path}, skipping validation")

        # Send the PUT request to add or modify features
        response = self.connection.put(f"networkgroups/{identifier}/features", data=body)

        return response

    # Remove all features of an existing group
    def remove_all_features_from_networkgroup(self, identifier):
        """
        Remove all features from an existing network group.

        :param identifier: The identifier of the network group.
        :return: API response indicating the result.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        # Send the DELETE request to remove all features
        response = self.connection.delete(f"networkgroups/{identifier}/features")

        return response

    # Gets all nodes of an existing group
    def show_nodes_in_networkgroup(self, identifier, params=None):
        """
        Retrieve all nodes of a network group with optional query parameters.

        :param identifier: The identifier of the network group.
        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid"}
        :return: API response containing nodes in the network group.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        if params is None:
            params = {}

        # Send the GET request to retrieve nodes
        response = self.connection.get(f"networkgroups/{identifier}/nodes", params=params)

        return response

    # Adds nodes to an existing group
    def add_nodes_to_networkgroup(self, identifier, node_identifiers):
        """
        Add nodes to an existing network group.

        :param identifier: The identifier of the network group.
        :param node_identifiers: A list of node identifiers to add to the network group.
        :return: API response indicating the result.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")
        
        if not isinstance(node_identifiers, list):
            raise ValueError("The 'node_identifiers' parameter must be a list of node identifiers.")

        # Create the body with identifiers
        body = {"identifiers": node_identifiers}

        # Validate the body against the MultipleIdentifierDto.json schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "MultipleIdentifierDto.json")
            with open(schema_path, "r") as schema_file:
                multiple_identifier_schema = json.load(schema_file)
            
            try:
                validate(instance=body, schema=multiple_identifier_schema)
                logger.debug("Validation of body with MultipleIdentifierDto schema successful")
            except ValidationError as e:
                raise ValueError(f"Request body validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file MultipleIdentifierDto.json not found at {schema_path}") from e

        # Send the POST request to add nodes
        response = self.connection.post(f"networkgroups/{identifier}/nodes", data=body)

        return response

    # Removes some or all nodes from an existing group
    def remove_nodes_from_networkgroup(self, identifier, node_identifiers=None):
        """
        Remove nodes from an existing network group.

        :param identifier: The identifier of the network group.
        :param node_identifiers: A list of node identifiers to remove from the network group.
                               If None, all nodes will be removed.
        :return: API response indicating the result.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        # If node_identifiers is provided, create a body with identifiers
        if node_identifiers:
            if not isinstance(node_identifiers, list):
                raise ValueError("The 'node_identifiers' parameter must be a list of node identifiers.")
            
            body = {"identifiers": node_identifiers}

            # Validate the body against the MultipleIdentifierDto.json schema
            try:
                schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
                schema_path = os.path.join(schema_dir, "MultipleIdentifierDto.json")
                with open(schema_path, "r") as schema_file:
                    multiple_identifier_schema = json.load(schema_file)
                
                try:
                    validate(instance=body, schema=multiple_identifier_schema)
                    logger.debug("Validation of body with MultipleIdentifierDto schema successful")
                except ValidationError as e:
                    raise ValueError(f"Request body validation failed: {e.message}")
            except FileNotFoundError as e:
                raise RuntimeError(f"Schema file MultipleIdentifierDto.json not found at {schema_path}") from e

            # Send the DELETE request with the body
            response = self.connection.delete(f"networkgroups/{identifier}/nodes", data=body)
        else:
            # If no node_identifiers provided, remove all nodes
            response = self.connection.delete(f"networkgroups/{identifier}/nodes")

        return response

    # Gets list of available actions on an existing group
    def show_networkgroup_actions(self, identifier):
        """
        Show available actions on an existing network group.

        :param identifier: The identifier of the network group (String).
        :return: API response containing available actions.
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        # Send the GET request to the /networkgroups/{identifier}/actions endpoint
        response = self.connection.get(f"networkgroups/{identifier}/actions")

        return response

    # Runs an action on an existing group
    def run_action_on_networkgroup(self, identifier, action, action_params=None):
        """
        Run an action on an existing network group.

        :param identifier: The identifier of the network group.
        :param action: The name of the action to run.
        :param action_params: Dictionary of parameters for the action (optional).
        :return: API response indicating the result.
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        if not isinstance(action, str) or not action.strip():
            raise ValueError("The 'action' parameter must be a non-empty string.")

        # Create the body with parameters
        body = action_params or {}

        # Send the POST request to run the action
        response = self.connection.post(f"networkgroups/{identifier}/actions/{action}", data=body)

        return response