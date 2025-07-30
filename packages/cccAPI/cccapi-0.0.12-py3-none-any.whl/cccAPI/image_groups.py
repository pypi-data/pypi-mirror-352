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

class cccAPIImageGroups:
    def __init__(self, connection):
        """Handles CCC Image Group API endpoints."""
        self.connection = connection
        # Load allowed fields from ImageGroup.json
        schema_path = os.path.join(os.path.dirname(__file__), "definitions", "ImageGroup.json")
        try:
            with open(schema_path, "r") as f:
                schema = json.load(f)
                # Initialize set with properties from the schema
                self.allowed_fields = set(schema.get("properties", {}).keys())
                # Add additional field paths
                self.allowed_fields.update({
                    "id", "uuid", "etag", "creationTime", "modificationTime", 
                    "deletionTime", "links", "links.actions", 
                    "nodes.name", "nodes.id", "nodes.uuid",
                    "candidates.name", "candidates.id", "candidates.uuid"
                })
        except Exception as e:
            logger.warning(f"Could not load ImageGroup.json schema: {e}")
            self.allowed_fields = set()

        self.default_fields = "name,id,type,backupImageDevice"

    # 4.3.2. Lists all groups
    def show_imagegroups(self, params=None):
        """
        Retrieve all image groups with optional query parameters.

        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response containing image groups.
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

        return self.connection.get("imagegroups", params=params)

    # 4.3.15. Gets one or more group(s)
    def show_imagegroup(self, identifier, params=None):
        """
        Retrieve details about specific image group with optional query parameters.

        :param identifier: The identifier of the image group to retrieve.
        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response for the specified image group.
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

        return self.connection.get(f"imagegroups/{identifier}", params=params)

    # 4.3.4. Creates one or multiple new image group(s)
    def create_imagegroups(self, groups):
        """
        Create one or multiple image groups on CCC Server.

        :param groups: A list of image group objects conforming to the ImageGroup.json schema.
                      Example:
                      [
                          {
                              "name": "ImageGroup1",
                              "type": "linux",
                              "backupImageDevice": "/dev/sda",
                              ...
                          },
                          {
                              "name": "ImageGroup2",
                              ...
                          }
                      ]
        :return: API response from the POST /imagegroups endpoint.
        """
        if not isinstance(groups, list):
            raise ValueError("The 'groups' parameter must be a list of image group objects.")
        
        # Validate each group against the schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "ImageGroup.json")
            with open(schema_path, "r") as schema_file:
                imagegroup_schema = json.load(schema_file)
            
            # Create a resolver for handling schema references
            resolver = get_schema_resolver(schema_dir)
            
            for group in groups:
                try:
                    validate(instance=group, schema=imagegroup_schema, resolver=resolver)
                    logger.debug("Validation successful")
                except ValidationError as e:
                    raise ValueError(f"Image group validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file ImageGroup.json not found at {schema_path}") from e

        # Send the POST request to the /imagegroups endpoint
        response = self.connection.post("imagegroups", data=groups)

        return response

    # 4.3.14. Updates an existing image group
    def update_imagegroup(self, identifier, body):
        """
        Update an existing image group.

        :param identifier: The identifier of the image group to update (String).
        :param body: The updated image group definition conforming to the ImageGroup.json schema.
        :return: API response indicating the result of the update.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")
        
        if not isinstance(body, dict):
            raise ValueError("The 'body' parameter must be a dictionary conforming to the ImageGroup.json schema.")

        # Validate the body against the ImageGroup.json schema with reference resolution
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "ImageGroup.json")
            with open(schema_path, "r") as schema_file:
                imagegroup_schema = json.load(schema_file)
            
            # Create a resolver for handling schema references
            resolver = get_schema_resolver(schema_dir)
            
            try:
                validate(instance=body, schema=imagegroup_schema, resolver=resolver)
                logger.debug("Validation successful")
            except ValidationError as e:
                raise ValueError(f"Image group validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file ImageGroup.json not found at {schema_path}") from e

        # Send the PUT request to the /imagegroups/{identifier} endpoint
        response = self.connection.put(f"imagegroups/{identifier}", data=body)

        return response

    # 4.3.16. Deletes an existing image group
    def delete_imagegroup(self, identifier):
        """
        Delete an existing image group.

        :param identifier: The identifier of the image group to delete (String).
        :return: API response indicating the result of the deletion.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        # Send the DELETE request to the /imagegroups/{identifier} endpoint
        response = self.connection.delete(f"imagegroups/{identifier}")

        return response

    # 4.3.3. Deletes a set of existing image groups
    def delete_imagegroups(self, identifiers):
        """
        Delete multiple image groups.

        :param identifiers: A list of image group identifiers to delete.
        :return: API response indicating the result of the deletion.
        """
        if not isinstance(identifiers, list):
            raise ValueError("The 'identifiers' parameter must be a list of image group identifiers.")

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

        # Send the DELETE request to the /imagegroups endpoint with the payload
        response = self.connection.delete("imagegroups", data=body)

        return response

    # 4.3.8. Lists all candidates of an existing image group
    def show_candidates_in_imagegroup(self, identifier, params=None):
        """
        Retrieve all candidate nodes of an image group with optional query parameters.

        :param identifier: The identifier of the image group.
        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid"}
        :return: API response containing candidate nodes.
        """
        if params is None:
            params = {}

        # Validate and process the 'fields' parameter if provided
        if "fields" in params:
            # For this endpoint, we need to validate against node fields, not image group fields
            # This is a simplified approach; in production, you might want to load Node.json schema
            params["fields"] = params["fields"]  # Just pass it through for now

        return self.connection.get(f"imagegroups/{identifier}/candidates", params=params)

    # 4.3.17. Gets all nodes of an existing group
    def show_nodes_in_imagegroup(self, identifier, params=None):
        """
        Retrieve all nodes of an image group with optional query parameters.

        :param identifier: The identifier of the image group.
        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid"}
        :return: API response containing nodes in the image group.
        """
        if params is None:
            params = {}

        # Validate and process the 'fields' parameter if provided
        if "fields" in params:
            # For this endpoint, we need to validate against node fields, not image group fields
            # This is a simplified approach; in production, you might want to load Node.json schema
            params["fields"] = params["fields"]  # Just pass it through for now

        return self.connection.get(f"imagegroups/{identifier}/nodes", params=params)

    # 4.3.10. Adds candidates to an existing image group
    def add_candidates_to_imagegroup(self, identifier, candidates_identifiers):
        """
        Add candidate nodes to an existing image group.

        :param identifier: The identifier of the image group.
        :param candidates_identifiers: A list of node identifiers to add as candidates.
        :return: API response indicating the result.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")
        
        if not isinstance(candidates_identifiers, list):
            raise ValueError("The 'candidates_identifiers' parameter must be a list of node identifiers.")

        # Create the body with identifiers
        body = {"identifiers": candidates_identifiers}

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

        # Send the POST request to add candidates
        response = self.connection.post(f"imagegroups/{identifier}/candidates", data=body)

        return response

    # 4.3.9. Removes some or all candidates from an existing image group
    def remove_candidates_from_imagegroup(self, identifier, candidates_identifiers=None):
        """
        Remove candidate nodes from an existing image group.

        :param identifier: The identifier of the image group.
        :param candidates_identifiers: A list of node identifiers to remove from candidates.
                                      If None, all candidates will be removed.
        :return: API response indicating the result.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        # If candidates_identifiers is provided, create a body with identifiers
        if candidates_identifiers:
            if not isinstance(candidates_identifiers, list):
                raise ValueError("The 'candidates_identifiers' parameter must be a list of node identifiers.")
            
            body = {"identifiers": candidates_identifiers}

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
            response = self.connection.delete(f"imagegroups/{identifier}/candidates", data=body)
        else:
            # If no candidates_identifiers provided, remove all candidates
            response = self.connection.delete(f"imagegroups/{identifier}/candidates")

        return response

    # 4.3.19. Adds nodes to an existing group
    def add_nodes_to_imagegroup(self, identifier, node_identifiers):
        """
        Add nodes to an existing image group.

        :param identifier: The identifier of the image group.
        :param node_identifiers: A list of node identifiers to add to the image group.
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
        response = self.connection.post(f"imagegroups/{identifier}/nodes", data=body)

        return response

    # 4.3.18. Removes some or all nodes from an existing group
    def remove_nodes_from_imagegroup(self, identifier, node_identifiers=None):
        """
        Remove nodes from an existing image group.

        :param identifier: The identifier of the image group.
        :param node_identifiers: A list of node identifiers to remove from the image group.
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
            response = self.connection.delete(f"imagegroups/{identifier}/nodes", data=body)
        else:
            # If no node_identifiers provided, remove all nodes
            response = self.connection.delete(f"imagegroups/{identifier}/nodes")

        return response

    # 4.3.5. Gets list of available actions on an existing group
    def show_imagegroup_actions(self, identifier):
        """
        Show available actions on an existing image group.

        :param identifier: The identifier of the image group (String).
        :return: API response containing available actions.
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        # Send the GET request to the /imagegroups/{identifier}/actions endpoint
        response = self.connection.get(f"imagegroups/{identifier}/actions")

        return response

    # 4.3.13. Runs an action on a set of existing groups
    def run_action_on_imagegroups(self, identifiers, action_name, action_params=None):
        """
        Run an action on a set of existing image groups.

        :param identifiers: A list of image group identifiers.
        :param action_name: The name of the action to run.
        :param action_params: Dictionary of parameters for the action (optional).
        :return: API response indicating the result.
        """
        if not isinstance(identifiers, list):
            raise ValueError("The 'identifiers' parameter must be a list of image group identifiers.")
        
        if not isinstance(action_name, str) or not action_name.strip():
            raise ValueError("The 'action_name' parameter must be a non-empty string.")

        # Create the body with identifiers and action
        body = {
            "resources": {"identifiers": identifiers},
            "parameters": action_params or {}
        }

        # Send the POST request to run the action
        response = self.connection.post(f"imagegroups/actions/{action_name}", data=body)

        return response