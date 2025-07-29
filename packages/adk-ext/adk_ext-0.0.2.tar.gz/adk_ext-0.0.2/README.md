# adk-ext

[![Python Unit Tests](https://github.com/nandlabs/adk-ext-python/actions/workflows/unittest.yml/badge.svg)](https://github.com/nandlabs/adk-ext-python/actions/workflows/unittest.yml)
[![Python Versions](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.0.1-green)](https://github.com/nandlabs/adk-ext-python)

A comprehensive Python extension library for Google's Agent Development Kit (ADK).

## Overview

adk-ext provides a set of tools, utilities, and wrapper functions that extend the functionality of the standard ADK for Python developers. This library aims to simplify common ADK operations, improve development workflow, and offer additional features not available in the core ADK implementation.

## Features

- **Agent Extensions**:
  - SkippableSequentialAgent: A sequential agent that allows skipping remaining agents at any point
- **Session Service**:  
   Session Service Implementations including:
  - Firestore: Persistent storage of sessions and events in Google Cloud Firestore
  - Redis: High-performance in-memory session storage with Google Cloud Memorystore
  - MongoDB (coming soon): Document-oriented session storage

## Installation

Install the base package:

```bash
pip install adk-ext
```

For optional dependencies:

```bash
# For Firestore session storage
pip install 'adk-ext[firestore]'

# For Redis/Memorystore session storage
pip install 'adk-ext[redis]'

# For all optional dependencies
pip install 'adk-ext[all]'
```

## Quick Start

### Using FirestoreSessionService

```python
from adk.ext.sessions import FirestoreSessionService

# Initialize the service (requires google-cloud-firestore package)
try:
    session_service = FirestoreSessionService(
        project_id="your-gcp-project-id",  # Optional, uses default if None
        collection_name="adk_sessions",    # Optional, defaults to "adk_sessions"
    )
except ImportError:
    print("You need to install Firestore dependencies: pip install 'adk-ext[firestore]'")

# Use with your ADK agent
async def create_session(app_name, user_id):
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state={"initial_data": "value"}
    )
    return session
```

### Using RedisSessionService

```python
from adk.ext.sessions import RedisSessionService

# Initialize the service (requires redis package)
try:
    session_service = RedisSessionService(
        host="your-redis-host",         # For Cloud Memorystore, use the instance IP
        port=6379,                      # Optional, defaults to 6379
        ssl=True,                       # Optional, set to True for secure connections
        password="your-redis-password", # Optional, for authenticated instances
        session_ttl=3600                # Optional, session expiration in seconds
    )
except ImportError:
    print("You need to install Redis dependencies: pip install 'adk-ext[redis]'")

# Use with your ADK agent
async def retrieve_session(app_name, user_id, session_id):
    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    return session
```

### Handling Missing Dependencies

If you try to use a class that requires dependencies you haven't installed, the library will raise an informative ImportError:

```python
try:
    from adk.ext.sessions import FirestoreSessionService
    # Code that uses FirestoreSessionService
except ImportError as e:
    print(f"Missing dependency: {e}")
    # Handle the missing dependency or install it
```

```python
from adk.ext.sessions import FirestoreSessionService
from google.adk.runners import Runner
from google.adk.agents import LlmAgent

# Initialize the session service
session_service = FirestoreSessionService(project_id="your-gcp-project-id")

# Create Runner and execute the request
....
```

### Prerequisites for Firestore

- Set up a Google Cloud project with Firestore enabled
- Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your service account key file
- Install dependencies: `pip install google-cloud-firestore`

### Using SkippableSequentialAgent

```python
from adk.ext.agents import SkippableSequentialAgent
from google.adk.agents import LlmAgent

# Create sub-agents
agent1 = LlmAgent(...)
agent2 = LlmAgent(...)
agent3 = LlmAgent(...)

# Create a skippable sequential agent
sequential_agent = SkippableSequentialAgent([agent1, agent2, agent3])

# In your models, you can skip remaining agents by calling the skip_remaining_agents function
# Example in a custom agent:
if condition_to_skip:
    self.parent.skip_remaining_agents()

# For LLM agents, you can use the skip_remaining function in your prompts
# The function will be automatically added to LlmAgents
```

### Using RedisSessionService with Google Cloud Memorystore

```python
from adk.ext.sessions import RedisSessionService
from google.adk.runners import Runner
from google.adk.agents import LlmAgent

# Initialize the session service with your Memorystore instance details
session_service = RedisSessionService(
    host="10.0.0.1",  # Your Memorystore IP address
    port=6379,        # Default Redis port
    ssl=True,         # Use SSL if enabled on your instance
    password="your-auth-string"  # If auth is enabled
)

# Create Runner and execute the request
....
```

### Prerequisites for Redis/Memorystore

- Set up a Google Cloud Memorystore for Redis instance
- Configure networking to allow access from your application
- Install dependencies: `pip install redis`

## Testing

### Unit Tests

To run the unit tests:

```bash
pytest -xvs tests/unittests/
```

### Integration Tests

To run the integration tests for Firestore:

1. Set up your Google Cloud credentials:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
```

2. Specify the Google Cloud project ID:

```bash
export FIRESTORE_PROJECT_ID=your-test-project-id
```

3. Run the integration tests:

```bash
pytest -xvs tests/integration/
```

Note: Integration tests will create temporary collections in your Firestore database with random prefixes to avoid conflicts.

## Documentation

For detailed documentation, examples and API reference, please visit the [documentation site](https://adk-ext.readthedocs.io).

## Requirements

- Python 3.8+
- ADK core library

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Releasing

This project uses GitHub Actions to automatically publish to PyPI when a new release is tagged with a semantic version number.

1. Update the version in `pyproject.toml`
2. Commit and push the changes
3. Create and push a new tag with a semantic version format:

```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

4. The GitHub Action will automatically build and publish the package to PyPI

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- ADK core developers
- Contributors to this extension library
- All users providing valuable feedback and feature requests
