from typing import AsyncGenerator, List, Optional, Union

from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.llm.request import Model
from betteryeah.llm.response import LLMAvailableModel


class LLMClient:

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def chat(
            self,
            system_prompt: str,
            model: Model | str = Model.gpt_3_5_turbo,
            json_mode: bool = False,
            messages: Optional[List[dict]] = None,
            temperature: float = 0.7,
            stream: bool = False,
    ) -> Union[ApiResponse[Union[str, dict]], AsyncGenerator[str, None]]:
        """
        :param system_prompt: 用户输入的prompt
        :param model: 选择的对应模型
        :param json_mode: 输出的文本类型是否是json格式,注意,若为True,请在system_prompt中明确声明返回json的key
        的形式,否则模型会随机返回json的key
        :param messages: 上下文历史信息,例如:[{"role": "user","content": "你好"},{"role": "assistant","content": "你好，有什么可以帮助您？"}]
        :param temperature: 模型对应的temperature参数
        :param stream: 是否使用流式输出
        :param time_out: 请求超时时间
        :return:例如:{'code': 200, 'success': True, 'message': 'SUCCESS', 'data': '汉朝一共有26位皇帝。', 'now_time': 1715395402}
        """
        data = {
            "type": "LLM",
            "parameters": {
                "inputs": {
                    "model": model if isinstance(model, str) else model.value,
                    "plugin": {"json_mode": json_mode},
                    "stream": stream,
                    "messages": [] if not messages else messages,
                    "temperature": temperature,
                    "context_type": "messageList",
                    "system_content": system_prompt,
                }
            }
        }

        if stream:
            return self.api_client.send_stream_request("POST", "/oapi/action/execute", data)
        else:
            api_res = await self.api_client.send_request("POST", "/oapi/action/execute", data)
            return ApiResponse(
                code=api_res["code"],
                message=api_res["message"],
                now_time=api_res["now_time"],
                success=api_res["success"],
                usage=api_res.get("data", {}).get("usage", {}),
                data=api_res.get("data", {}).get("output", {}),
                request_id=api_res.get("request_id", "")
            )

    async def get_available_models(self) -> ApiResponse[LLMAvailableModel]:
        """
        获取当前可用的模型列表
        :return: ApiResponse包装的LLMAvailableModelsResponse，其中包含可用模型列表
        """
        api_res = await self.api_client.send_request(
            "GET", "/oapi/active_channels", json_data={}
        )
        models = [
            LLMAvailableModel(**item)
            for item in api_res.get("data", {})
        ]
        return ApiResponse(
            code=api_res["code"],
            message=api_res["message"],
            now_time=api_res["now_time"],
            success=api_res["success"],
            data=models,
            request_id=api_res.get("request_id", "")
        )
