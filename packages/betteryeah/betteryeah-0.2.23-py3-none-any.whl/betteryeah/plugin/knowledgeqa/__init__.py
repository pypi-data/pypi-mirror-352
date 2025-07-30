from typing import Optional

from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse


class KnowledgeQAClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def multi_sense_qa(self, question: str, url_link: str, background_info: Optional[str] = None) -> ApiResponse[str]:
        """
        视频/图片问答
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"question": question, "url_link": url_link, "background_info": background_info},
                "code": "multi_sense_qa"
            },
        }
        api_response = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )

        return ApiResponse(
            code=api_response["code"],
            message=api_response["message"],
            now_time=api_response["now_time"],
            success=api_response["success"],
            usage=api_response.get("data", {}).get("usage", {}),
            data=api_response.get("data", {}).get("output"),
            request_id=api_response.get("request_id", ""),
        )
        
    async def longtext_qa(self, question: str, url_link: str, answer_rule: Optional[str] = None) -> ApiResponse[str]:
        """
        长文本问答
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"question": question, "url_link": url_link, "answer_rule": answer_rule},
                "code": "extensive_qa"
            },
        }
        
        api_response = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )

        return ApiResponse(
            code=api_response["code"],
            message=api_response["message"],
            now_time=api_response["now_time"],
            success=api_response["success"],
            usage=api_response.get("data", {}).get("usage", {}),
            data=api_response.get("data", {}).get("output"),
            request_id=api_response.get("request_id", ""),
        )