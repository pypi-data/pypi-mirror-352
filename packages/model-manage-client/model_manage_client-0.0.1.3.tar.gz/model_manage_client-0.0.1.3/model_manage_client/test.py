from client import ModelManageClient


def test_register():
    base_url = "http://localhost:5001"
    client_token = ""

    # Initialize CompletionClient
    m_client = ModelManageClient(base_url, client_token)

    agent_info = m_client.get_agent("test")
    if agent_info:
        print(agent_info)

    # Create Completion Message using CompletionClient
    extra_params = {
        "agent_description": "agent_description",
        "agent_icon_url": "agent_icon_url",
        "agent_api_version": "/v1.0",
        "agent_features": {},
    }
    m_client.register_agent("test", "license123", "test", **extra_params)

    # delete agent
    m_client.delete_agent("ppp")


def test_get_provider_credential():
    base_url = "http://localhost:5001"
    client_token = ""
    # Initialize CompletionClient
    m_client = ModelManageClient(base_url, client_token)

    try:
        credential = m_client.get_provider_credential(
            "test",
            "tongyi",
            "test",
        )
        print(credential)
    except Exception as e:
        print(e)


def test_get_model_credentials():
    base_url = "http://localhost:5001"
    client_token = ""
    # Initialize CompletionClient
    m_client = ModelManageClient(base_url, client_token)

    try:
        credential = m_client.get_model_credentials(
            "test",
            "gpt-4o-mini",
            "azure_openai",
            "llm",
            "test",
        )
        print(credential)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    test_get_model_credentials()
