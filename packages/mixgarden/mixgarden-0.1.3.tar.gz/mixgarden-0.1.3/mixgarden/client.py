import os
from typing import Any, Dict, Optional

import httpx


class MixgardenSDK:
    """Very small Python wrapper around the Mixgarden REST API."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.mixgarden.ai/api/v1") -> None:
        self.api_key = api_key or os.getenv("MIXGARDEN_API_KEY")
        if not self.api_key:
            raise ValueError("Mixgarden API key missing (set MIXGARDEN_API_KEY or pass api_key).")
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={ "Authorization": f"Bearer {self.api_key}" },
            timeout=30.0,
        )

    # ---- internal -------------------------------------------------------
    def _request(self, method: str, path: str, *, json: Optional[dict] = None, params: Optional[dict] = None):
        response = self._client.request(method.upper(), path, json=json, params=params)
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    # ---- public helpers -------------------------------------------------
    def get_models(self):
        return self._request("GET", "/models")

    def chat(self, content, model, conversation_id=None, plugin_id=None, plugin_settings=None,
            wait_for_response=True, poll_interval=1.5, timeout=30):
        # 1. Ensure conversation exists
        if not conversation_id:
            conv_res = self._request("POST", "/conversations", json={
                "title": "New Conversation",
                "model": model
            })
            conversation_id = conv_res.get("id")
            if not conversation_id:
                raise RuntimeError("Failed to create conversation")

        # 2. Add user message
        self._request("POST", f"/conversations/{conversation_id}/messages", json={
            "role": "user",
            "content": content,
            "pluginId": plugin_id,
            "pluginSettings": plugin_settings
        })

        # 3. Start AI/plugin job
        gen_res = self._request("POST", f"/conversations/{conversation_id}/generate", json={
            "model": model,
            "pluginId": plugin_id,
            "pluginSettings": plugin_settings
        })
        job_id = gen_res.get("jobId")
        if not job_id:
            raise RuntimeError("No jobId returned from backend")

        # 4. Optionally poll for result
        if wait_for_response:
            start = time.time()
            while time.time() - start < timeout:
                result = self._request("GET", f"/conversations/generate/status/{job_id}")
                if result and result.get("status") == "completed" and result.get("result"):
                    return result["result"]
                if result and result.get("status") == "failed":
                    raise RuntimeError(result.get("error", "AI/plugin job failed"))
                time.sleep(poll_interval)
            raise TimeoutError("Timed out waiting for AI/plugin response")
        else:
            return {"jobId": job_id}

    def get_completion(self, **params):
        return self._request("POST", "/chat/completions", json=params)

    def get_mg_completion(self, **params):
        return self._request("POST", "/mg-completion", json=params)

    def get_plugins(self, page: Optional[int] = 1, limit: Optional[int] = 10) -> Dict[str, Any]:
        """
        Fetches a single page of plugins.
        """
        return self._request("GET", "/plugins", params={"page": page, "limit": limit})

    def get_all_plugins(self, batch_size: int = 50) -> List[Dict[str, Any]]:
        """
        Fetches all plugins by handling pagination.
        """
        all_plugins: List[Dict[str, Any]] = []
        current_page = 1
        total_plugins = 0
        fetched_plugins = 0

        while True:
            response = self.get_plugins(page=current_page, limit=batch_size)
            if response and "plugins" in response:
                plugins_on_page = response["plugins"]
                all_plugins.extend(plugins_on_page)
                fetched_plugins = len(all_plugins)

                if current_page == 1: # Set total only on first successful fetch
                    total_plugins = response.get("total", 0)
                
                if not plugins_on_page or fetched_plugins >= total_plugins: # Break if no more plugins on page or all fetched
                    break
            else:
                # Should not happen if backend is consistent
                print("Warning: Failed to fetch a page of plugins or received invalid response.")
                break 
            
            current_page += 1
            if total_plugins == 0 and current_page > 1 : # Safety break if total was 0 but we somehow continued
                 break


        return all_plugins

    def get_conversations(self, **params):
        return self._request("GET", "/conversations", params=params)

    def get_conversation(self, conversation_id: str):
        return self._request("GET", f"/conversations/{conversation_id}")

    def close(self):
        self._client.close()
