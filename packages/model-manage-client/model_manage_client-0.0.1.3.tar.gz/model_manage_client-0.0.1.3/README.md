# model-manage-client

A model-manage App Service-API Client, using for build a webapp by request Service-API

## Usage

First, install `model-manage-client` python sdk package:

```
pip install model-manage-client
```

Write your code with sdk:

- completion generate with `blocking` response_mode

```python
from model-manage-client import ModelManageClient

base_url = "model-manage service api url"
client_token = "your_client_token"

# Initialize CompletionClient
m_client = ModelManageClient(base_url, client_token)

# Create Completion Message using CompletionClient
extra_params = {
    "agent_description": "agent_description",
    "agent_icon_url": "agent_icon_url",
    "agent_api_version": "agent_api_version",
    "agent_features":{}
}
m_client.register_agent("agent_name","agent_id","agent_url", **extra_params)

```