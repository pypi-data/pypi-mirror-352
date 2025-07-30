import asyncio
import json
import os
import time
from typing import AsyncGenerator

import aiohttp
import requests

BASE_URL = (
    os.environ.get("GEMINI_SERVER_HOST") + "/v1"
    if os.environ.get("GEMINI_SERVER_HOST")
    else "https://ai-api.betteryeah.com/v1"
)

RETRY_STATUS_CODES = [499, 502, 504]
MAX_RETRIES = 3


class RetryableError(Exception):
    pass


class ApiClient:

    def __init__(self, api_key: str, workspace_id: str = None):
        self.api_key = api_key or os.environ.get("API_KEY")
        self.run_env = os.environ.get("RUN_ENV") or "BETTERYEAH_SDK"
        self.traceparent = os.environ.get("TRACEPARENT") or ""
        self.workspace_id = workspace_id or os.environ.get("WORKSPACE_ID") or self.get_workspace_id()

    async def _prepare_request(self, method: str, endpoint: str, json_data=None):
        headers = {
            "Access-Key": f"{self.api_key}",
            "Content-Type": "application/json",
            "Workspace-Id": self.workspace_id,
        }
        if self.traceparent:
            headers["Traceparent"] = self.traceparent

        url = f"{BASE_URL}{endpoint}"

        run_args = json.loads(os.environ.get("RUN_ARGS", "{}"))
        base_info = {
            "workspace_id": self.workspace_id,
            "flow_id": run_args.get("flow_id", ""),
            "node_id": run_args.get("node_id", ""),
            "node_name": run_args.get("node_name", ""),
        }

        json_data = (
            {**json_data, **{"run_env": self.run_env, **base_info}}
            if json_data
            else {"run_env": self.run_env, **base_info}
        )
        await self.build_curl_command(url, method, headers, json_data)

        return url, headers, json_data

    async def send_request(self, method: str, endpoint: str, json_data=None):
        url, headers, json_data = await self._prepare_request(
            method, endpoint, json_data
        )

        timeout = aiohttp.ClientTimeout(total=600)

        async def _make_request() -> dict:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(method, url, json=json_data, headers=headers) as response:
                    if response.status in RETRY_STATUS_CODES:
                        raise RetryableError(f"Received status code {response.status}")

                    response_data = await response.json()
                    if 'usage' in response_data.get("data", {}):
                        await self.update_usage(response_data.get("data", {}).get("usage", {}), json_data)
                    return response_data

        for retry in range(MAX_RETRIES):
            try:
                return await _make_request()
            except (RetryableError, aiohttp.ClientError) as e:
                if retry == 2:
                    raise
                await asyncio.sleep(1 ** retry)

    async def send_stream_request(self, method: str, endpoint: str, json_data=None):
        url, headers, json_data = await self._prepare_request(
            method, endpoint, json_data
        )

        timeout = aiohttp.ClientTimeout(total=600)

        async def _make_stream_request() -> AsyncGenerator[str, None]:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(method, url, json=json_data, headers=headers) as response:
                    if response.status in RETRY_STATUS_CODES:
                        raise RetryableError(f"Received status code {response.status}")
                    try:
                        async for res in response.content:
                            decoded_line = res.decode("utf-8").strip()
                            if decoded_line.startswith("data:"):
                                yield decoded_line[5:].strip()
                    finally:
                        await self.update_usage({}, json_data)

        for retry in range(MAX_RETRIES):
            try:
                async for data in _make_stream_request():
                    yield data
                break
            except (RetryableError, aiohttp.ClientError) as e:
                if retry == 2:
                    raise
                await asyncio.sleep(1 ** retry)

    def get_workspace_id(self):
        endpoint = "/oapi/integration/get_workspace_id"
        for retry in range(MAX_RETRIES):
            try:
                response = requests.post(
                    f"{BASE_URL}{endpoint}", json={"Authorization": f"{self.api_key}"}
                )
                if response.status_code in RETRY_STATUS_CODES:
                    raise RetryableError(f"Received status code {response.status_code}")
                result = response.json()
                if result.get("code") == 200 and result.get("data"):
                    self.workspace_id = result.get("data").get("workspace_id")
                    return self.workspace_id
                else:
                    raise Exception(
                        f"Failed to get workspace_id. Response: {result}. Please verify if the API key is correct."
                    )
            except (RetryableError, requests.RequestException) as e:
                if retry == 2:
                    raise Exception(f"Failed to get workspace_id after {MAX_RETRIES} attempts: {str(e)}")
                time.sleep(2 ** retry)

    async def build_curl_command(self, url: str, method: str, headers: dict, json_data=None):
        curl_command = f'curl -X {method} "{url}"'
        for key, value in headers.items():
            curl_command += f' -H "{key}: {value}"'
        if json_data:
            curl_command += f" -d '{json.dumps(json_data, ensure_ascii=False)}'"
        # print(curl_command)

    async def update_usage(self, new_usage, parameters):
        current_usage = json.loads(os.environ.get('USAGE', '{"points": 0}'))

        if parameters.get("type") == "LLM":
            inputs = parameters.get("parameters", {}).get("inputs", {})
            stream = inputs.get("stream", False)
            if stream:
                model = inputs.get("model", "gpt-4o")
                model_config = await self.get_workspace_model_config()
                model_consume_points = model_config.get(model, {}).get("llm_consume_points", 0)
                new_usage["points"] = new_usage.get("points", 0) + model_consume_points

        current_usage.update({key: current_usage.get(key, 0) + value for key, value in new_usage.items()})

        os.environ['USAGE'] = json.dumps(current_usage)

    async def get_workspace_model_config(self):
        endpoint = "/oapi/workspace/model_config"
        response = await self.send_request("GET", endpoint)
        return response.get("data", {})
