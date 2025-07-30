# ccc_client

This package provides a simple, modular SDK for the CCC REST API.

## Features

* Automatically handles authentication and renewal
* Graceful error management
* Logically organized modules
* Easily maintained

## Installation

**Requirements:**
* Python 3.8 or higher
* Required packages: requests>=2.26.0, jsonschema>=4.23.0

**Install using `pip`:**

```bash
pip install cccAPI 
```

**Install from source:**

```bash
git clone https://github.hpe.com/hpe/cccAPI.git
cd cccAPI
pip install -e .
```

## Quick Start

### Initialize the Client
```python
import json
from cccAPI import cccAPIClient
client = cccAPIClient("https://localhost:8000/cmu/v1", "root", "your-password")
```

### Example Usage

#### Get Nodes

```python
nodes = client.nodes.show_nodes()
print(json.dumps(nodes, indent=4))
```

#### Get specific Node

```python
#Specific node named Node1
node = client.nodes.show_node("Node1")
print(json.dumps(node, indent=4))
```

#### Get specific Node/fields 
- Allowed fields are: 

```python 
query_params = {"fields": "name,id,uuid,network.name,network.ipAddress,network.macAddress"}
specific_nodes=client.nodes.show_nodes(query_params)
print(json.dumps(specific_nodes, indent=4))
```

See `examples/test.py` for other test cases as implemented

## API Modules

| Module | Description | User Guide Section |
|---------|-------------|------------------|
| `nodes` | Node Operations: Create/Delete/Update/List Nodes, Add/Remove nodes in groups, Manage node features | Section 4.5 |
| `image_groups` | Image Group Operations | Section 4.3 |
| `network_groups` | Network Group Operations | Section 4.4 |
| `custom_groups` | Custom Group Operations | Section 4.2 |
| `resource_features` | Resource Features Management | Section 4.8 |
| `image_capture_deployment` | Image Capture and Deployment Operations | Section 4.9 |
| `power_operation` | Power Operations Management | Section 4.10 |
| `application` | Application Entrypoints and Settings | Section 4.1 |
| `architecture` | Architecture Management | Section 4.11 |
| `management_cards` | Network Devices, Interfaces, and Routes Management | Section 4.12 |
| `tasks` | Tasks Operations | Section 4.7 |
| `conn` | Sessions Operations | Section 4.6 |

## Building and Publishing

### Local Development

There are several ways to install the package for local development:

1. Direct pip install:
```bash
pip install .
```

2. Using pip-tools (recommended for development):
```bash
pip install pip-tools
pip-compile pyproject.toml  # Produces requirements.txt
pip install -r requirements.txt
```

3. Using uv (faster installation):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -e . --system
```

4. Building distribution packages:
```bash
pip install build
python -m build  # Creates dist/ with tar.gz and .whl
```

### Publishing to PyPI

1. Ensure you have the required tools:
```bash
pip install setuptools wheel twine
```

2. Build the distribution:
```bash
python -m build
# Or alternatively:
# python3 setup.py sdist bdist_wheel
```

3. Upload to PyPI (requires ~/.pypirc with PyPI token):
```bash
twine upload dist/*
```

You can verify the installation by downloading the published package:
```bash
pip install cccAPI=={version}  # Replace {version} with desired version
```
## License

This project is license under the [MIT license](LICENSE).
