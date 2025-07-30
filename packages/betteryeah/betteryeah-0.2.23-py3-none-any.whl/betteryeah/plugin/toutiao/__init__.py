from typing import List
from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.plugin.toutiao.response import ToutiaoHotspotItem


class ToutiaoClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def get_hot_topics(self) -> ApiResponse[List[ToutiaoHotspotItem]]:
        """
        获取今日头条实时热搜榜
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {},
                "code": "get_toutiao_trending_topics"
            }
        }

        api_response = await self.api_client.send_request("POST", '/oapi/action/execute', data)
        
        hotspot_items = [
            ToutiaoHotspotItem(**item)
            for item in api_response.get('data', {}).get('output', [])
        ]

        return ApiResponse(
            code=api_response['code'],
            message=api_response['message'],
            now_time=api_response['now_time'],
            success=api_response['success'],
            usage=api_response.get('data', {}).get('usage', {}),
            data=hotspot_items,
            request_id=api_response.get('request_id', '')
        )
