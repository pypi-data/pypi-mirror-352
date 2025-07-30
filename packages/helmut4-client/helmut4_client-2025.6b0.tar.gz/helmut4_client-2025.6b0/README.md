# Helmut4 Python Client

A Python client library for interacting with the Helmut4 API.

[![PyPI Version](https://img.shields.io/pypi/v/helmut4-client.svg)](https://pypi.org/project/helmut4-client/)
[![Python Versions](https://img.shields.io/pypi/pyversions/helmut4-client.svg)](https://pypi.org/project/helmut4-client/)
[![License](https://img.shields.io/pypi/l/helmut4-client.svg)](https://pypi.org/project/helmut4-client/)

## Overview

This library provides a convenient way to interact with the Helmut4 API
from Python. It covers all major components of the Helmut4 system:

- Users and Groups Management
- Projects Management
- Asset Management
- Job Management
- Workflow (Streams) Management
- Metadata Management
- Preferences Management
- Cronjobs
- Languages
- Licensing

## Installation

```bash
pip install helmut4-client
```

For development:

```bash
pip install -e ".[dev]"
```

## Basic Usage

```python
from helmut4.client import Helmut4Client, Helmut4Error

# Initialize the client with credentials
client = Helmut4Client(
    base_url="https://helmut.example.com",
    username="admin",
    password="password"
)

# Or with an existing token
client = Helmut4Client(
    base_url="https://helmut.example.com",
    token="your-jwt-token"
)

# Get all users
users = client.users.get_all()

# Create a project
new_project = client.projects.create({
    "name": "My Project",
    "group": "Documentary",
    "category": "Production",
    "template": "Default",
    # Other required fields...
})

# Search for assets in a project
assets = client.assets.search(
    search_filter={"name": "Interview"},
    project_id=new_project["id"]
)
```

## Module Overview

The client is organized into modules corresponding to the different
components of Helmut4:

- `client.users` - User management
- `client.groups` - Group management
- `client.projects` - Project management
- `client.assets` - Asset management
- `client.jobs` - Job management
- `client.streams` - Workflow stream management
- `client.metadata` - Metadata management
- `client.preferences` - System preferences
- `client.cronjobs` - Scheduled tasks
- `client.languages` - Language settings
- `client.licenses` - License management

Each module provides methods for interacting with the corresponding API
endpoints.

## Authentication

The client supports both username/password authentication and
token-based authentication:

```python
# With username/password (automatically handles token acquisition)
client = Helmut4Client(
    base_url="https://helmut.example.com",
    username="admin",
    password="password"
)

# With token (if you already have a valid JWT token)
client = Helmut4Client(
    base_url="https://helmut.example.com",
    token="your-jwt-token"
)
```

When using username/password, the client automatically handles token
acquisition and sets it in the session headers.

## Error Handling

All API errors are raised as `Helmut4Error` exceptions, which include
the status code and response data when available:

```python
from helmut4.client import Helmut4Error

try:
    client.users.get_by_id("non-existent-id")
except Helmut4Error as e:
    print(f"Error {e.status_code}: {e.message}")
    print(f"Response data: {e.response}")
```

## Example Use Cases

### Managing Users

```python
# List all users
all_users = client.users.get_all()

# Get a specific user
user = client.users.get_by_name("johndoe")

# Create a new user
new_user = client.users.create({
    "username": "janedoe",
    "password": "secure-password",
    "displayname": "Jane Doe",
    "role": "User"
})

# Add user to a group
client.users.add_to_group(new_user["id"], "group-id")

# Change password
client.users.change_password(new_user["id"], "old-password", "new-password")
```

### Managing Projects

```python
# Search for projects
projects = client.projects.search({"name": "Documentary"})

# Create a new project
new_project = client.projects.create({
    "name": "Summer Campaign",
    "group": "Marketing",
    "category": "Advertising",
    "template": "Commercial"
})

# Lock a project
client.projects.set_status(new_project["id"], "LOCKED")

# Download project file
project_file = client.projects.download(new_project["id"])
```

### Managing Assets

```python
# Get assets from a project
assets = client.assets.get_by_project_id("project-id")

# Create a new asset
new_asset = client.assets.create({
    "name": "Interview Footage",
    "projectId": "project-id",
    "type": "VIDEO",
    "path": "/path/to/footage.mp4"
})

# Add metadata to an asset
client.assets.set_metadata(new_asset["id"], [
    {
        "key": "location",
        "value": "New York"
    },
    {
        "key": "interviewer",
        "value": "John Smith"
    }
])
```

### Executing Workflows (Streams)

```python
# Execute a stream
result = client.streams.execute(
    stream_event="CREATE_PROJECT",
    endpoint="FX",
    content_package={
        "projectId": "project-id",
        "customData": {"key": "value"}
    }
)

# Execute a custom stream
result = client.streams.execute_custom("stream-id", "project-id")
```

## Development

### Setting up the Development Environment

```bash
# Clone the repository
git clone https://bitbucket.org/chesa/helmut4-client/
cd helmut4-client

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest -v tests/
```

### Code Formatting and Linting

```bash
# Optionally, remove unused import statements with pycln and/or alphabetically
# sort imports within logical sections using isort
pycln [--config pyproject.toml] src/
isort src/

# Format with black or yapf
black [--config pyproject.toml] src/
yapf --in-place --recursive [--print-modified] src/

# Lint with ruff and pylint
ruff [--config pyproject.toml] check [--fix] src/
pylint [--rcfile pyproject.toml] --recursive yes src/
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch
   (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
