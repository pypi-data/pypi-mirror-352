# Configure logging
import logging
logger = logging.getLogger("cccAPI")
import os
import json
from jsonschema import validate, RefResolver
from jsonschema.exceptions import ValidationError
import urllib.parse

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

class cccAPICustomGroups:
    def __init__(self, connection):
        """Handles CCC Custom Groups API endpoints."""
        self.connection = connection
        # Load allowed fields from CustomGroup.json
        schema_path = os.path.join(os.path.dirname(__file__), "definitions", "CustomGroup.json")
        try:
            with open(schema_path, "r") as f:
                schema = json.load(f)
                # Assume properties at the root level
                self.allowed_fields = set(schema.get("properties", {}).keys())
                # Add additional field paths
                self.allowed_fields.update({
                    "id", "uuid", "etag", "creationTime", "modificationTime", 
                    "deletionTime", "links", "links.actions", 
                    "nodes.name", "nodes.id", "nodes.uuid"
                })
        except Exception as e:
            logger.warning(f"Could not load CustomGroup.json schema: {e}")
            self.allowed_fields = set()
            
        self.default_fields = "name,id"
    
    # 4.2.9. Lists all groups
    def show_customgroups(self, params=None):
        """
        Retrieve current custom groups with optional query parameters.

        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response containing current custom groups.
        """
        if params is None:
            params = {}

        # Validate and process the 'fields' parameter
        if "fields" in params:
            requested_fields = set(params["fields"].split(","))
            invalid_fields = requested_fields - self.allowed_fields
            if invalid_fields:
                raise ValueError(
                    f"Invalid fields requested: {', '.join(invalid_fields)}. "
                    f"Allowed fields are: {', '.join(self.allowed_fields)}"
                )
            # Use only the valid fields
            params["fields"] = ",".join(requested_fields)
        else:
            # Use default fields if 'fields' is not specified
            params["fields"] = self.default_fields

        return self.connection.get("customgroups", params=params)
    
    # 4.2.14. Gets one or more group(s)
    def show_customgroup(self, identifier, params=None):
        """
        Retrieve details about specific custom group with optional query parameters.

        :param identifier: The identifier of the custom group to retrieve.
        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response containing custom group details.
        """
        if params is None:
            params = {}

        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

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

        return self.connection.get(f"customgroups/{identifier}", params=params)
    
    # 4.2.1. Gets all nodes of an existing group
    def show_nodes_in_customgroup(self, identifier, params=None):
        """
        Retrieve current set of nodes in {identifier} custom group with optional query parameters.

        :param identifier: The identifier of the custom group (UUID or name).
        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response containing current custom groups.
        """
        if params is None:
            params = {}

        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

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

        return self.connection.get(f"customgroups/{identifier}/nodes", params=params)
        
    # 4.2.4. Creates one or multiple new custom group(s)
    def create_customgroups(self, groups):
        """
        Create one or more new custom groups.

        :param groups: List of custom group definitions conforming to the CustomGroup.json schema.
                       Each group should contain at minimum a 'name' field.
                       Example: [{"name": "CustomGroup1"}, {"name": "CustomGroup2"}]
        :return: API response containing created custom group(s) information.
        """
        if not isinstance(groups, list):
            # If a single group is provided, convert it to a list
            groups = [groups]

        # Validate that each group has at least a name
        for i, group in enumerate(groups):
            if not isinstance(group, dict):
                raise ValueError(f"Group at index {i} is not a dictionary: {group}")
            if "name" not in group:
                raise ValueError(f"Group at index {i} is missing required 'name' field: {group}")

        # Validate against schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "CustomGroup.json")
            with open(schema_path, "r") as f:
                schema = json.load(f)
            
            resolver = get_schema_resolver(schema_dir)
            for i, group in enumerate(groups):
                try:
                    validate(instance=group, schema=schema, resolver=resolver)
                except ValidationError as e:
                    raise ValueError(f"Group at index {i} failed schema validation: {e.message}")
        except Exception as e:
            logger.warning(f"Schema validation error: {e}")
            # Continue with the operation even if validation fails

        return self.connection.post("customgroups", body=groups)
    
    # 4.2.13. Updates an existing custom group
    def update_customgroup(self, identifier, body):
        """
        Update an existing custom group.

        :param identifier: The identifier (name or UUID) of the custom group to update.
        :param body: The updated custom group definition conforming to the CustomGroup.json schema.
                     Must include a 'name' field.
                     Example: {"name": "CustomGroup1", "features": {"description": "Updated description"}}
        :return: API response containing the updated custom group information.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        # Validate that the body is a dictionary with required fields
        if not isinstance(body, dict):
            raise ValueError(f"Body must be a dictionary: {body}")
        if "name" not in body:
            raise ValueError(f"Body is missing required 'name' field: {body}")

        # Validate against schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "CustomGroup.json")
            with open(schema_path, "r") as f:
                schema = json.load(f)
            
            resolver = get_schema_resolver(schema_dir)
            validate(instance=body, schema=schema, resolver=resolver)
        except Exception as e:
            logger.warning(f"Schema validation error: {e}")
            # Continue with the operation even if validation fails

        return self.connection.put(f"customgroups/{identifier}", body=body)
    
    # 4.2.15. Deletes an existing custom group
    def delete_customgroup(self, identifier):
        """
        Delete an existing custom group.

        :param identifier: The identifier (name or UUID) of the custom group to delete.
        :return: API response indicating the result of the deletion operation.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        return self.connection.delete(f"customgroups/{identifier}")
    
    # 4.2.3. Deletes a set of existing custom groups
    def delete_customgroups(self, identifiers):
        """
        Delete multiple custom groups.

        :param identifiers: List of identifiers (names or UUIDs) of custom groups to delete.
                            Example: ["CustomGroup1", "CustomGroup2"]
        :return: API response indicating the result of the deletion operation.
        """
        if not isinstance(identifiers, list):
            # If a single identifier is provided, convert it to a list
            identifiers = [identifiers]

        # Validate that all identifiers are strings
        for i, identifier in enumerate(identifiers):
            if not isinstance(identifier, str):
                raise ValueError(f"Identifier at index {i} is not a string: {identifier}")

        # Prepare the body for the request
        body = {"identifiers": identifiers}

        # Validate against schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "MultipleIdentifierDto.json")
            with open(schema_path, "r") as f:
                schema = json.load(f)
            
            resolver = get_schema_resolver(schema_dir)
            validate(instance=body, schema=schema, resolver=resolver)
        except Exception as e:
            logger.warning(f"Schema validation error: {e}")
            # Continue with the operation even if validation fails

        return self.connection.delete("customgroups", data=body)
    
    # 4.2.19. Adds nodes to an existing group
    def add_nodes_to_customgroup(self, identifier, nodes):
        """
        Add nodes to an existing custom group.

        :param identifier: The identifier (name or UUID) of the custom group.
        :param nodes: List of node identifiers (names or UUIDs) to add to the custom group.
                      Example: ["Node1", "Node2"]
        :return: API response indicating the result of the operation.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        if not isinstance(nodes, list):
            # If a single node is provided, convert it to a list
            nodes = [nodes]

        # Validate that all node identifiers are strings
        for i, node in enumerate(nodes):
            if not isinstance(node, str):
                raise ValueError(f"Node identifier at index {i} is not a string: {node}")

        # Prepare the body for the request
        body = {"identifiers": nodes}

        return self.connection.post(f"customgroups/{identifier}/nodes", body=body)
    
    # 4.2.5. Removes some or all nodes from an existing group
    def remove_nodes_from_customgroup(self, identifier, nodes):
        """
        Remove nodes from an existing custom group.

        :param identifier: The identifier (name or UUID) of the custom group.
        :param nodes: List of node identifiers (names or UUIDs) to remove from the custom group.
                      Example: ["Node1", "Node2"]
        :return: API response indicating the result of the operation.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        if not isinstance(nodes, list):
            # If a single node is provided, convert it to a list
            nodes = [nodes]

        # Validate that all node identifiers are strings
        for i, node in enumerate(nodes):
            if not isinstance(node, str):
                raise ValueError(f"Node identifier at index {i} is not a string: {node}")

        # Prepare the body for the request
        body = {"identifiers": nodes}

        return self.connection.delete(f"customgroups/{identifier}/nodes", data=body)
    
    # 4.2.17. Removes one node from an existing group
    def remove_node_from_customgroup(self, identifier, node_id):
        """
        Remove a single node from an existing custom group.

        :param identifier: The identifier (name or UUID) of the custom group.
        :param node_id: The identifier (name or UUID) of the node to remove.
        :return: API response indicating the result of the operation.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")
        if not isinstance(node_id, str):
            raise ValueError("The 'node_id' parameter must be a string.")

        return self.connection.delete(f"customgroups/{identifier}/nodes/{node_id}")
    
    # 4.2.16. Gets one node of an existing group
    def show_node_in_customgroup(self, identifier, node_id, params=None):
        """
        Get details about a specific node in a custom group.

        :param identifier: The identifier (name or UUID) of the custom group.
        :param node_id: The identifier (name or UUID) of the node.
        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response containing node details.
        """
        if params is None:
            params = {}

        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")
        if not isinstance(node_id, str):
            raise ValueError("The 'node_id' parameter must be a string.")

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

        return self.connection.get(f"customgroups/{identifier}/nodes/{node_id}", params=params)
    
    # 4.2.12. Gets list of available actions on an existing group
    def show_customgroup_actions(self, identifier, params=None):
        """
        Get list of available actions for a custom group.

        :param identifier: The identifier (name or UUID) of the custom group.
        :param params: Dictionary of query parameters to include in the request.
        :return: API response containing available actions for the custom group.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        return self.connection.get(f"customgroups/{identifier}/actions", params=params)
    
    # 4.2.11. Runs an action on a set of existing groups
    def run_action_on_customgroup(self, identifier, action_name, params=None):
        """
        Run an action on a custom group.

        :param identifier: The identifier (name or UUID) of the custom group.
        :param action_name: The name of the action to run.
        :param params: Dictionary of parameters for the action.
        :return: API response containing the result of the action.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")
        if not isinstance(action_name, str):
            raise ValueError("The 'action_name' parameter must be a string.")

        return self.connection.post(f"customgroups/{identifier}/actions/{action_name}", body=params)
    
    # 4.2.8. Adds or modifies features of an existing group
    def add_or_modify_features_in_customgroup(self, identifier, features):
        """
        Add or modify features in a custom group.

        :param identifier: The identifier (name or UUID) of the custom group.
        :param features: Dictionary of features to add or modify.
                         Example: {"description": "New description", "priority": "high"}
        :return: API response indicating the result of the operation.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")
        if not isinstance(features, dict):
            raise ValueError("The 'features' parameter must be a dictionary.")

        return self.connection.put(f"customgroups/{identifier}/features", body=features)
    
    # 4.2.7. Gets all features of a single group
    def show_features_in_customgroup(self, identifier):
        """
        Get all features of a custom group.

        :param identifier: The identifier (name or UUID) of the custom group.
        :return: API response containing features of the custom group.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        return self.connection.get(f"customgroups/{identifier}/features")
    
    # 4.2.15. Remove all features of an existing group
    def remove_all_features_from_customgroup(self, identifier):
        """
        Remove all features from a custom group.

        :param identifier: The identifier (name or UUID) of the custom group.
        :return: API response indicating the result of the operation.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        return self.connection.delete(f"customgroups/{identifier}/features")