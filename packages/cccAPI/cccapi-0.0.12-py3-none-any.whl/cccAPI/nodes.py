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

class cccAPINodes:
    def __init__(self, connection):
        """Handles CCC Nodes API endpoints."""
        self.connection = connection
        self.allowed_fields = {"name", "id", "uuid", "etag", "creationTime", "modificationTime",
                               "deletionTime", "primaryId", "secondaryId", "biosBootMode", "iscsiRoot",
                               "links", "links.actions", "links.imagegroup", "links.networkgroup",
                               "network", "network.name", "network.ipAddress", "network.subnetMask",
                               "network.macAddress", "network.mgmtServerIp", "network.defaultGateway",
                               "image", "image.name", "image.cloningBlockDevice", "image.cloningDate",
                               "platform", "platform.name", "platform.architecture", "platform.serialPort",
                               "platform.serialPortSpeed", "platform.vendorsArgs",
                               "management", "management.cardType", "management.cardIpAddress",
                               "features", "features.BIOS", "features.CPU model", "features.Cluster dns domain name",
                               "features.Disk size", "features.Disk type", "features.Logical CPU number",
                               "features.Memory size", "features.Native CPU speed", "features.System model"
        } # Define allowed fields

        self.default_fields = "name,id,network.name,network.ipAddress,management.cardType,management.cardIpAddress"  # Default fields if none are specified

    def show_nodes(self, params=None):
        """
        Retrieve currently registered nodes with optional query parameters.

        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response containing currently registered nodes.
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

        return self.connection.get("nodes", params=params)

    def show_node(self, name, params=None):
        """
        Retrieve details about specific node "name" with optional query parameters.

        :param name: The name of the node to retrieve.
        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response for the node "name".
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

        return self.connection.get(f"nodes/{name}", params=params)

    def create_nodes(self, nodes):
        """
        Create one or multiple nodes= on CCC Server

        :param nodes: A list of node objects conforming to the Node.json schema.
                      Example:
                      [
                          {
                              "name": "Node1",
                              "network": {...},
                              "image": {...},
                              ...
                          },
                          {
                              "name": "Node2",
                              "network": {...},
                              "image": {...},
                              ...
                          }
                      ]
        :return: API response from the POST /nodes endpoint.
        """


        if not isinstance(nodes, list):
            raise ValueError("The 'nodes' parameter must be a list of node objects.")
        
         # Restricted fields in the 'image' object
        restricted_image_fields = {"name", "cloningBlockDevice", "cloningDate"}

        # Validate each node
        for node in nodes:
            # Check for restricted fields in the 'image' object
            if "image" in node:
                restricted_fields_in_image = restricted_image_fields.intersection(node["image"].keys())
                if restricted_fields_in_image:
                    raise ValueError(
                        f"The following fields are not allowed in the 'image' object: {', '.join(restricted_fields_in_image)}"
                    )

        # Check for readonly field 'network.name'
        if "network" in node and "name" in node["network"]:
            raise ValueError("The 'network.name' field is readonly and cannot be set.")

        # Validate each node against the schema
        # Load the Node.json schema using direct file path
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "Node.json")
            with open(schema_path, "r") as schema_file:
                node_schema = json.load(schema_file)
            
            # Create a resolver for handling schema references
            resolver = get_schema_resolver(schema_dir)
            
            for node in nodes:
                try:
                    validate(instance=node, schema=node_schema, resolver=resolver)
                    logger.debug("Validation successful")
                except ValidationError as e:
                    raise ValueError(f"Node validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file Node.json not found at {schema_path}") from e
        
        # for node in nodes:
        #     if not isinstance(node, dict):
        #         raise ValueError("Each node must be a dictionary conforming to the Node.json schema.")

        VALID_BIOS_BOOT_MODES = {"UEFI", "PXE", "AUTO"}
        for node in nodes:
            if "biosBootMode" in node and node["biosBootMode"] not in VALID_BIOS_BOOT_MODES:
                raise ValueError(f"Invalid biosBootMode value: {node['biosBootMode']}. Allowed values are: {', '.join(VALID_BIOS_BOOT_MODES)}")

        # Send the POST request to the /nodes endpoint
        response = self.connection.post("nodes", data=nodes)

        return response

    def delete_node(self, identifier):
        """
        Delete an existing node.

        :param identifier: The identifier of the node to delete (String).
        :return: API response indicating the result of the deletion.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")

        # Send the DELETE request to the /nodes/{identifier} endpoint
        response = self.connection.delete(f"nodes/{identifier}")

        return response
    

    def update_node(self, identifier, body):
        """
        Update an existing node.

        :param identifier: The identifier of the node to update (String).
        :param body: The updated node definition conforming to the Node.json schema.
        :return: API response indicating the result of the update.
        """
        if not isinstance(identifier, str):
            raise ValueError("The 'identifier' parameter must be a string.")
        
        if not isinstance(body, dict):
            raise ValueError("The 'body' parameter must be a dictionary conforming to the Node.json schema.")

        # Validate the body against the Node.json schema with reference resolution
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "Node.json")
            with open(schema_path, "r") as schema_file:
                node_schema = json.load(schema_file)
            
            # Create a resolver for handling schema references
            resolver = get_schema_resolver(schema_dir)
            
            try:
                validate(instance=body, schema=node_schema, resolver=resolver)
                logger.debug("Validation successful")
            except ValidationError as e:
                raise ValueError(f"Node validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file Node.json not found at {schema_path}") from e

        # Send the PUT request to the /nodes/{identifier} endpoint
        response = self.connection.put(f"nodes/{identifier}", data=body)

        return response
    

    def show_node_noimggroup(self, params=None):
        """
        Retrieve nodes that are not in any image group with optional query parameters.

        :param params: Dictionary of query parameters to include in the request.
                    Example: {"fields": "name,id,uuid,etag"}
        :return: API response containing nodes not in any image group.
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

        # Send the GET request to the /nodes/no_image endpoint
        return self.connection.get("nodes/no_image", params=params)

    def remove_nodes_from_image_group(self, body):
        """
        Remove a set of nodes from their current image group.

        :param body: A dictionary conforming to the MultipleIdentifierDto.json schema.
        :return: API response. If the response status is 200, it returns a response conforming to Node.json schema.
        :raises ValueError: If the body does not conform to the MultipleIdentifierDto.json schema.
        """
        if not isinstance(body, dict):
            raise ValueError("The 'body' parameter must be a dictionary conforming to the MultipleIdentifierDto.json schema.")

        # Validate the body against the MultipleIdentifierDto.json schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "MultipleIdentifierDto.json")
            with open(schema_path, "r") as schema_file:
                multiple_identifier_schema = json.load(schema_file)
            
            # Create a resolver for handling schema references
            resolver = get_schema_resolver(schema_dir)
            
            try:
                validate(instance=body, schema=multiple_identifier_schema, resolver=resolver)
                logger.debug("Validation of body with MultipleIdentifierDto schema successful")
            except ValidationError as e:
                raise ValueError(f"Request body validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file MultipleIdentifierDto.json not found at {schema_path}") from e

        # Send the POST request to the /nodes/no_image endpoint
        response = self.connection.post("nodes/no_image", data=body)

        # If the response status is 200, validate it against the Node.json schema
        if response.status_code == 200:
            # Load the Node.json schema using direct file path
            try:
                schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
                schema_path = os.path.join(schema_dir, "Node.json")
                with open(schema_path, "r") as schema_file:
                    node_schema = json.load(schema_file)
                
                # Create a resolver for handling schema references
                resolver = get_schema_resolver(schema_dir)
                
                try:
                    validate(instance=response.json(), schema=node_schema, resolver=resolver)
                    logger.debug("Validation of response with Node schema successful")
                except ValidationError as e:
                    raise ValueError(f"Response validation failed: {e.message}")
            except FileNotFoundError as e:
                raise RuntimeError(f"Schema file Node.json not found at {schema_path}") from e

            return response.json()

        # Return the response as-is for other status codes
        return response
    
    #Section 4.5.11
    def show_node_noNetworkGroup(self, params=None):
        """
        Retrieve nodes that are not in any network group with optional query parameters.
    
        :param params: Dictionary of query parameters to include in the request.
                       Example: {"fields": "name,id,uuid,etag"}
        :return: API response containing nodes not in any network group.
        :raises ValueError: If the response does not conform to the Node.json schema.
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
    
        # Send the GET request to the /nodes/no_network endpoint
        response = self.connection.get("nodes/no_network", params=params)
    
        # If the response status is 200, validate it against the Node.json schema
        if response.status_code == 200:
            # Validate the body against the Node.json schema
            import importlib.resources
            import json
            from jsonschema import validate, RefResolver
            from jsonschema.exceptions import ValidationError
        
            # Load the Node.json schema using direct file path
            try:
                schema_path = os.path.join(os.path.dirname(__file__), "definitions", "Node.json")
                with open(schema_path, "r") as schema_file:
                    node_schema = json.load(schema_file)
            except FileNotFoundError as e:
                raise RuntimeError(f"Schema file Node.json not found at {schema_path}") from e
            except FileNotFoundError as e:
                raise RuntimeError("Schema file Node.json not found in package.") from e

            try:
                validate(instance=response.json(), schema=node_schema)
                logger.debug("Validation of response with Node schema successful")
            except ValidationError as e:
                raise ValueError(f"Response validation failed: {e.message}")
            
            return response.json()
    
        # Return the response as-is for other status codes
        return response
    
    #section 4.5.12 
    def remove_nodes_noNetworkGroup(self, body):
        """
        Remove a set of nodes from their current network group.
    
        :param body: A dictionary conforming to the MultipleIdentifierDto.json schema.
        :return: API response. If the response status is 200, it returns a response conforming to Node.json schema.
        :raises ValueError: If the body does not conform to the MultipleIdentifierDto.json schema.
        """
        if not isinstance(body, dict):
            raise ValueError("The 'body' parameter must be a dictionary conforming to the MultipleIdentifierDto.json schema.")
    
        # Validate the body against the MultipleIdentifierDto.json schema
        import importlib.resources
        import json
        from jsonschema import validate, RefResolver
        from jsonschema.exceptions import ValidationError
        
        try:
            with importlib.resources.open_text("cccAPI.definitions", "MultipleIdentifierDto.json") as schema_file:
                multiple_identifier_schema = json.load(schema_file)
        except FileNotFoundError as e:
            raise RuntimeError("Schema file MultipleIdentifierDto.json not found in package.") from e

        try:
            validate(instance=body, schema=multiple_identifier_schema)
            logger.debug("Validation of body with MultipleIdentifierDto schema successful")
        except ValidationError as e:
            raise ValueError(f"Request body validation failed: {e.message}")
    
        # Send the POST request to the /nodes/no_network endpoint
        response = self.connection.post("nodes/no_network", data=body)
    
        # If the response status is 200, validate it against the Node.json schema
        if response.status_code == 200:
            # Validate the response against the Node.json schema
            import importlib.resources
            import json
            from jsonschema import validate, RefResolver
            from jsonschema.exceptions import ValidationError
        
            # Load the Node.json schema using importlib.resources
            try:
                with importlib.resources.open_text("cccAPI.definitions", "Node.json") as schema_file:
                    node_schema = json.load(schema_file)
            except FileNotFoundError as e:
                raise RuntimeError("Schema file Node.json not found in package.") from e

            try:
                validate(instance=response.json(), schema=node_schema)
                logger.debug("Validation of response with Node schema successful")
            except ValidationError as e:
                raise ValueError(f"Response validation failed: {e.message}")
    
            return response.json()
    
        # Return the response as-is for other status codes
        return response
    
    #Section 4.5.13 
    def show_node_actions(self, identifier):
        """
        Show available actions on an existing node.

        :param identifier: The identifier of the node (String).
        :return: API response containing available actions if status code is 200.
        :raises ValueError: If the identifier is not a valid string or if the response does not conform to the Action.json schema.
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        # Send the GET request to the /nodes/{identifier}/actions endpoint
        response = self.connection.get(f"nodes/{identifier}/actions")

        return response
        #CMU Rest API documentation does not have Actionable Array schema defined. (Actionable)
        #Hence the section below is commented out

        # If the response status is 200, validate it against the Node.json schema
        # if response.status_code == 200:
        #     import importlib.resources
        #     import json
        #     from jsonschema import validate, RefResolver
        #     from jsonschema.exceptions import ValidationError
        
        #     # Load the Action.json schema using importlib.resources
        #     try:
        #         with importlib.resources.open_text("cccAPI.definitions", "Action.json") as schema_file:
        #             action_schema = json.load(schema_file)
        #     except FileNotFoundError as e:
        #         raise RuntimeError("Schema file Node.json not found in package.") from e

        #     try:
        #         validate(instance=response.json(), schema=action_schema)
        #         logger.debug("Validation of response with Node schema successful")
        #     except ValidationError as e:
        #         raise ValueError(f"Response validation failed: {e.message}")
            
        #     return response.json()

        # # Return the response as-is for other status codes
        # return response

    def update_nodes(self, nodes, name_as_id=False):
        """
        Updates a set of existing nodes.

        :param nodes: List of node objects conforming to the Node.json schema
        :param name_as_id: Use name instead of UUID as identifier (default: False)
        :return: API response containing updated nodes if successful
        :raises ValueError: If the nodes parameter is invalid or validation fails
        """
        if not isinstance(nodes, list):
            raise ValueError("The 'nodes' parameter must be a list of node objects.")

        # Validate each node against the Node.json schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "Node.json")
            with open(schema_path, "r") as schema_file:
                node_schema = json.load(schema_file)
            
            resolver = get_schema_resolver(schema_dir)
            
            for node in nodes:
                try:
                    validate(instance=node, schema=node_schema, resolver=resolver)
                    logger.debug("Validation successful")
                except ValidationError as e:
                    raise ValueError(f"Node validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file Node.json not found at {schema_path}") from e

        params = {"nameAsId": name_as_id} if name_as_id else None
        return self.connection.put("nodes", data=nodes, params=params)

    def delete_nodes(self, identifiers):
        """
        Deletes a set of existing nodes.

        :param identifiers: Dictionary conforming to MultipleIdentifierDto.json schema containing node identifiers to delete
        :return: API response indicating the result of the deletion
        :raises ValueError: If the identifiers parameter is invalid or validation fails
        """
        if not isinstance(identifiers, dict):
            raise ValueError("The 'identifiers' parameter must be a dictionary conforming to the MultipleIdentifierDto.json schema.")

        # Validate the identifiers against MultipleIdentifierDto schema
        try:
            schema_dir = os.path.join(os.path.dirname(__file__), "definitions")
            schema_path = os.path.join(schema_dir, "MultipleIdentifierDto.json")
            with open(schema_path, "r") as schema_file:
                schema = json.load(schema_file)
            
            resolver = get_schema_resolver(schema_dir)
            
            try:
                validate(instance=identifiers, schema=schema, resolver=resolver)
                logger.debug("Validation successful")
            except ValidationError as e:
                raise ValueError(f"Identifiers validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file MultipleIdentifierDto.json not found at {schema_path}") from e

        return self.connection.delete("nodes", data=identifiers)

    def execute_node_action(self, identifier, action, parameters=None):
        """
        Runs an action on an existing node.

        :param identifier: The identifier of the node (String)
        :param action: The name of the action to execute (String)
        :param parameters: Optional parameters for the action (Dictionary)
        :return: API response indicating the result of the action
        :raises ValueError: If the identifier, action or parameters are invalid
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")
        
        if not isinstance(action, str) or not action.strip():
            raise ValueError("The 'action' parameter must be a non-empty string.")

        # Get available actions first to validate
        available_actions = self.show_node_actions(identifier)
        
        # Find the requested action
        action_info = next((a for a in available_actions if a["name"] == action), None)
        if not action_info:
            raise ValueError(f"Action '{action}' is not available for node '{identifier}'")
            
        # Validate parameters if provided
        if parameters:
            if not isinstance(parameters, dict):
                raise ValueError("The 'parameters' must be a dictionary")
                
            # Validate required parameters are present
            required_params = [p["name"] for p in action_info.get("parameters", []) 
                             if p.get("required", False)]
            missing_params = [p for p in required_params if p not in parameters]
            if missing_params:
                raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
                
            # Validate parameter values against allowed values
            for param_name, param_value in parameters.items():
                param_info = next((p for p in action_info.get("parameters", [])
                                 if p["name"] == param_name), None)
                if param_info and "allowableValues" in param_info:
                    if param_value not in param_info["allowableValues"]:
                        raise ValueError(
                            f"Invalid value for parameter '{param_name}'. "
                            f"Allowed values: {', '.join(param_info['allowableValues'])}")

        return self.connection.post(f"nodes/{identifier}/actions/{action}", data=parameters)

    def get_node_features(self, identifier):
        """
        Gets all features of a single node.

        :param identifier: The identifier of the node (String)
        :return: API response containing the node's features
        :raises ValueError: If the identifier is invalid
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        return self.connection.get(f"nodes/{identifier}/features")

    def update_node_features(self, identifier, features):
        """
        Updates features of an existing node.

        :param identifier: The identifier of the node (String)
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
            
            resolver = get_schema_resolver(schema_dir)
            
            try:
                validate(instance=features, schema=schema, resolver=resolver)
                logger.debug("Validation successful")
            except ValidationError as e:
                raise ValueError(f"Features validation failed: {e.message}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Schema file FeaturesDto.json not found at {schema_path}") from e

        return self.connection.put(f"nodes/{identifier}/features", data=features)

    def delete_node_features(self, identifier):
        """
        Deletes all features of an existing node.

        :param identifier: The identifier of the node (String)
        :return: API response indicating the result of the deletion
        :raises ValueError: If the identifier is invalid
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("The 'identifier' parameter must be a non-empty string.")

        return self.connection.delete(f"nodes/{identifier}/features")

