from typing import List
from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.plugin.zhihu.response import ZhiHuContentSearchItem, ZhihuRealtimeHotspotsItem


class ZhihuClient:
    
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def get_hot_topics(self) -> ApiResponse[List[ZhihuRealtimeHotspotsItem]]:
        """
        获取知乎实时热搜榜
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {},
                "code": "get_zhihu_trending_topics"
            }
        }
        api_response = await self.api_client.send_request("POST", '/oapi/action/execute', data)
        hotspots = [ZhihuRealtimeHotspotsItem(**item) for item in api_response.get('data', {}).get('output', [])]
        return ApiResponse(
            code=api_response['code'],
            message=api_response['message'],
            now_time=api_response['now_time'],
            success=api_response['success'],
            usage=api_response.get('data', {}).get('usage', {}),
            data=hotspots,
            request_id=api_response.get('request_id', '')
        )

    async def content_search(self, keyword: str) -> ApiResponse[List[ZhiHuContentSearchItem]]:
        """
        搜索知乎内容
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"keyword": keyword},
                "code": "search_zhihu_content"
            }
        }
        api_response = await self.api_client.send_request("POST", '/oapi/action/execute', data)
        search_results = [ZhiHuContentSearchItem(**item) for item in api_response.get('data', {}).get('output', [])]
        return ApiResponse(
            code=api_response['code'],
            message=api_response['message'],
            now_time=api_response['now_time'],
            success=api_response['success'],
            usage=api_response.get('data', {}).get('usage', {}),
            data=search_results,
            request_id=api_response.get('request_id', '')
        )
    