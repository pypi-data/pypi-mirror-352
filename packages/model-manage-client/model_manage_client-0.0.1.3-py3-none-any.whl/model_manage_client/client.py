import logging

import requests

logger = logging.getLogger(__name__)


class ModelManageClient:
    def __init__(self, base_url: str, client_token: str):
        self.base_url = base_url if base_url.endswith("/v1.0") else base_url + "/v1.0"
        self.client_token = client_token

    def _send_request(
        self,
        method,
        endpoint,
        headers=None,
        params=None,
        json=None,
        stream=False,
    ):
        new_headers = {
            "Authorization": f"Bearer {self.client_token}",
            "Content-Type": "application/json",
        }

        if headers:
            new_headers.update(headers)

        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, json=json, params=params, headers=new_headers, stream=stream)

        return response

    def register_agent(self, agent_name, agent_id, agent_url, **kargs):
        if not agent_name:
            raise ValueError("agent_name is required")
        if not agent_id:
            raise ValueError("agent_id is required")
        if not agent_url:
            raise ValueError("agent_url is required")

        args = {
            "agent_name": agent_name,
            "agent_id": agent_id,
            "agent_url": agent_url,
            **kargs,
        }
        response = self._send_request("POST", "/agents", json=args)
        if response.status_code != 200:
            raise ValueError(f"register agent failed: {response.text}")
        logger.info("register agent success......")

    def get_agent(self, agent_name):
        if not agent_name:
            raise ValueError("agent_name is required")

        response = self._send_request("GET", "/agents", params={"agent_name": agent_name})
        if response.status_code != 200 and response.status_code != 404:
            raise ValueError(f"get agent failed: {response.text}")
        if response.status_code == 404:
            return None
        return response.json()

    def delete_agent(self, agent_name):
        if not agent_name:
            raise ValueError("agent_name is required")

        response = self._send_request("DELETE", "/agents", params={"agent_name": agent_name})
        if response.status_code != 200:
            raise ValueError(f"delete agent failed: {response.text}")
        logging.info("delete agent success......")

    def get_model_credentials(
        self,
        agent_name: str,
        model: str,
        provider: str,
        model_type: str,
        tenent_id: str,
    ) -> dict:
        if not provider:
            raise ValueError("provider is required")
        if not model_type:
            raise ValueError("model_type is required")
        if not model:
            raise ValueError("model is required")
        if not agent_name:
            raise ValueError("agent_name is required")
        if not tenent_id:
            raise ValueError("tenent_id is required")

        params = {
            "agent_name": agent_name,
            "model": model,
            "model_type": model_type,
        }

        header = {
            "X-Ifp-Tenant-Id": tenent_id,
        }
        response = self._send_request(
            "GET",
            f"/agents/model-providers/{provider}/models/credentials",
            params=params,
            headers=header,
        )

        if response.status_code != 200:
            raise ValueError(f"get model credentials failed: {response.text}")
        return response.json()

    def get_provider_credential(
        self,
        agent_name: str,
        provider: str,
        tenent_id: str,
    ) -> dict:
        if not agent_name:
            raise ValueError("agent_name is required")
        if not provider:
            raise ValueError("provider is required")
        if not tenent_id:
            raise ValueError("tenent_id is required")
        header = {
            "X-Ifp-Tenant-Id": tenent_id,
        }
        response = self._send_request(
            method="GET",
            endpoint=f"/agents/model-providers/{provider}/credentials",
            headers=header,
            params={"agent_name": agent_name},
        )
        if response.status_code != 200:
            raise ValueError(f"get provider credential failed: {response.text}")
        return response.json()
