# AMP Agent

A Python library for building and deploying AMP agents with ease. This library provides the functionality needed to create, manage, and run AMP agents.

## Features

- Easy agent creation with base classes and interfaces
- Built-in HTTP server with Flask integration
- Token-based authentication and validation
- Configuration management
- Database integration with AsyncPG
- Async/sync support
- Logging and error handling
- Semantic interest matching
- Event subscription and listening
- Agent setup and registration utilities
- Swarm-based agent components

## Modules

- `amp_agent`: Core functionality for building and running agents
- `amp_setup`: Configuration and setup utilities
- `semantic`: Semantic interest matching and processing
- `subscription`: Event subscription and listening
- `swarm_cell`: Swarm-based agent components

## Installation

You can install the package using pip:

```bash
pip install amp-agent
```

For development installation:

```bash
pip install -e ".[dev]"
```

For testing:

```bash
pip install -e ".[test]"
```

For documentation:

```bash
pip install -e ".[docs]"
```

For machine learning features (advanced semantic matching):

```bash
pip install -e ".[ml]"
```

You can combine multiple extras like this:

```bash
pip install -e ".[dev,ml]"
```

## Quick Start

Here's a simple example of creating an AMP agent:

```python
from amp_agent import AgentInterface
from amp_agent.amp_setup import ConfigManager

class MyAgent(AgentInterface):
    async def process_message(self, content: str, metadata: dict = None) -> str:
        return f"Processed: {content}"

# Setup configuration
config_manager = ConfigManager()
config = config_manager.load_config()

# Create and run server
from amp_agent.server import create_app
app = create_app()
app.run()
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/theswarmhub/amp-agent.git
cd amp-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Run tests:
```bash
pytest
```

## Configuration

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
JWT_SECRET_KEY=your-secret-key
DEBUG=True
```

## Module Usage Examples

### Core Features

```python
from amp_agent import AgentInterface
from amp_agent.amp_setup import ConfigManager

# Create an agent
class MyAgent(AgentInterface):
    async def process_message(self, content: str, metadata: dict = None) -> str:
        return f"Processed: {content}"

# Load configuration
config_manager = ConfigManager()
config = config_manager.load_config()
```

### Semantic Processing

```python
from amp_agent.semantic import interest

# Define interests
@interest("code_review")
async def handle_code_review(content: str) -> str:
    return "Code review processed"
```

### Event Subscription (Optional)

```python
# Import the optional subscription module when needed
from amp_agent.subscription import AMPListener

# Create and start a listener
listener = AMPListener(config)
listener.start()
```

### Swarm Components (Optional)

```python
# Import the optional swarm_cell module when needed
from amp_agent.swarm_cell import SwarmCell

# Create a swarm cell
cell = SwarmCell(config)
cell.initialize()
```

## Documentation

For detailed documentation, visit [https://amp-agent.readthedocs.io/](https://amp-agent.readthedocs.io/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 