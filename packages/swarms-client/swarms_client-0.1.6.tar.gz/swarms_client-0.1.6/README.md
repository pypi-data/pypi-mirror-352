# Swarms SDK

[![PyPI version](https://badge.fury.io/py/swarms-client.svg)](https://badge.fury.io/py/swarms-client)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-grade Python SDK for the Swarms API, designed for enterprise applications requiring high reliability, scalability, and maintainability.

> 📚 For complete documentation, visit [Swarms API Python Client Documentation](https://docs.swarms.world/en/latest/swarms_cloud/python_client/)

## Enterprise Features

- 🚀 **High Performance**: Async-first design with connection pooling and advanced session management
- 🛡️ **Enterprise Security**: Secure API key management and comprehensive error handling
- 📊 **Observability**: Extensive logging with loguru and detailed telemetry
- 🔄 **Reliability**: Automatic retries with exponential backoff and circuit breaker pattern
- 🎯 **Type Safety**: Full type hints and validation with Pydantic
- 📚 **Documentation**: Comprehensive API reference and usage examples
- 🧪 **Testing**: Comprehensive test suite with detailed reporting
- 🔒 **Security**: Regular security audits and dependency updates

## Getting Started

### 1. Get Your API Key

First, obtain your API key from the [Swarms Platform](https://swarms.world/platform/api-keys). Keep your API key secure and never expose it in client-side code or version control.

### 2. Installation

```bash
pip install swarms-client
```

## API Resources

### Individual Agent Completions

```python
from swarms_client import SwarmsClient
from swarms_client.client import AgentSpec

client = SwarmsClient()

response = client.agent.create(
    agent_config=AgentSpec(
        agent_name="financial_analyst",
        model_name="gpt-4o-mini",
        temperature=0.5,  # Lower temperature for more precise financial analysis
        description="A specialized financial analyst who can analyze market trends, financial data, and provide investment insights",
        system_prompt="""You are an expert financial analyst with deep knowledge of:
- Financial markets and trading
- Company financial analysis and valuation
- Economic indicators and their impact
- Investment strategies and portfolio management
- Risk assessment and management

Provide detailed, data-driven analysis and insights while maintaining professional financial accuracy.""",
    ).model_dump(),
    task="Please analyze the recent performance of major market indices and provide key insights.",
)

print(response.model_dump_json(indent=4))

)

```

## Agent Batch Endpoint

This is the batch endpoint example, where you can create custom configurations of agents and they'll execute autonomously. 

```python
from swarms_client.client import SwarmsClient
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key with error handling
api_key = os.getenv("SWARMS_API_KEY")

# Initialize the client with explicit API key
client = SwarmsClient(api_key=api_key)


def run_agent_batch_example():
    """Example of running batch agent completions"""
    try:
        # Define multiple agent completion requests
        agent_completions = [
            {
                "agent_config": {
                    "agent_name": "Market Researcher",
                    "description": "Analyzes market trends and opportunities",
                    "model_name": "gpt-4o-mini",
                    "temperature": 0.7,
                },
                "task": "Analyze the current market trends in AI and ML",
            },
            {
                "agent_config": {
                    "agent_name": "Technical Writer",
                    "description": "Creates technical documentation and reports",
                    "model_name": "gpt-4o",
                    "temperature": 0.4,
                },
                "task": "Write a technical overview of transformer architecture",
            },
        ]

        # Execute batch agent completions
        responses = client.agent.create_batch(completions=agent_completions)

        # print(responses)
        print(responses.model_dump_json(indent=4))
        print(type(responses))

    except Exception as e:
        print(f"Error during batch processing: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print("Running Agent Batch Example...")
    run_agent_batch_example()
```


### Swarm Resource

```python
# Create a swarm
swarm = client.swarm.create(
    name="research-swarm",
    swarm_type="SequentialWorkflow",
    task="Research and analyze quantum computing",
    agents=[
        {
            "agent_name": "researcher",
            "model_name": "gpt-4",
            "role": "researcher"
        },
        {
            "agent_name": "analyst",
            "model_name": "gpt-4",
            "role": "analyst"
        }
    ]
)

# Create multiple swarms in batch
swarms = client.swarm.create_batch([
    {
        "name": "swarm-1",
        "task": "Task 1",
        "agents": [...]
    },
    {
        "name": "swarm-2",
        "task": "Task 2",
        "agents": [...]
    }
])

# List available swarm types
swarm_types = client.swarm.list_types()

# Async versions
async_swarm = await client.swarm.acreate(...)
async_swarms = await client.swarm.acreate_batch(...)
async_types = await client.swarm.alist_types()
```

### Models Resource

```python
# List available models
models = client.models.list()

# Async version
async_models = await client.models.alist()
```

### Logs Resource

```python
# List API request logs
logs = client.logs.list()

# Async version
async_logs = await client.logs.alist()
```

## Advanced Features

### Connection Pooling

```python
client = SwarmsClient(
    api_key="your-api-key",
    pool_connections=100,  # Number of connection pools
    pool_maxsize=100,      # Maximum connections in pool
    keep_alive_timeout=5   # Keep-alive timeout in seconds
)
```

### Circuit Breaker

```python
client = SwarmsClient(
    api_key="your-api-key",
    circuit_breaker_threshold=5,  # Failures before circuit opens
    circuit_breaker_timeout=60    # Seconds before retry
)
```

### Caching

```python
client = SwarmsClient(
    api_key="your-api-key",
    enable_cache=True  # Enable in-memory caching
)

# Clear cache manually
client.clear_cache()
```

## Error Handling

```python
from swarms_client import (
    SwarmsError,
    AuthenticationError,
    RateLimitError,
    APIError,
    InvalidRequestError,
    InsufficientCreditsError,
    TimeoutError,
    NetworkError
)

try:
    response = client.agent.create(...)
except AuthenticationError as e:
    print(f"Authentication error: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except APIError as e:
    print(f"API error: {e}")
except SwarmsError as e:
    print(f"Other error: {e}")
```

## Testing

The SDK includes a comprehensive test suite that validates all core functionality:

```bash
# Run the test suite
python test_client.py

# View the test report
cat test_report.md
```

## Contributing

We welcome contributions to make the SDK even more robust and feature-rich. Here's how you can help:

1. **Report Issues**
   - Use the GitHub issue tracker
   
   - Include detailed reproduction steps
   
   - Provide error logs and stack traces
   
   - Specify your environment details

2. **Submit Pull Requests**
   - Fork the repository
   
   - Create a feature branch
   
   - Write tests for new features
   
   - Update documentation
   
   - Submit a PR with a clear description

3. **Development Setup**
   ```bash
   # Clone the repository
   git clone https://github.com/The-Swarm-Corporation/swarms-sdk.git
   cd swarms-sdk

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows

   # Install dependencies
   pip install -e ".[dev]"
   ```

4. **Code Quality**
   - Follow PEP 8 style guide
   
   - Use type hints
   
   - Write docstrings
   
   - Run linters: `flake8`, `mypy`
   
   - Format code: `black`

## Enterprise Support

For enterprise customers, we offer:

- Priority support

- Custom feature development

- SLA guarantees

- Security audits

- Performance optimization

- Training and documentation

Contact our enterprise team at enterprise@swarms.world

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

For security concerns, please email security@swarms.world