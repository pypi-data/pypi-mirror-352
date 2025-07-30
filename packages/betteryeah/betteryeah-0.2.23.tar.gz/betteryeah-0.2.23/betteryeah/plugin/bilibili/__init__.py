from typing import List

from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.plugin.bilibili.response import BiliBiliHotTopicItem, BiliBiliSearchVideoItem, BiliBiliVideoCommentsItem


class BiliBiliClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def get_hot_topics(self) -> ApiResponse[List[BiliBiliHotTopicItem]]:
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {},
                "code": "get_bilibili_trending_topics"
            }
        }
        api_res = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        output_data = api_res.get('data', {}).get('output', {})
        res = [BiliBiliHotTopicItem(**item) for item in output_data]
        return ApiResponse(
            code=api_res['code'],
            message=api_res['message'],
            now_time=api_res['now_time'],
            success=api_res['success'],
            usage=api_res.get('data', {}).get('usage', {}),
            data=res,
            request_id=api_res.get('request_id', '')
        )

    async def get_comments(self, count: int, urls: List[str]) -> ApiResponse[List[BiliBiliVideoCommentsItem]]:
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"count": count, "urls": urls},
                "code": "get_bilibili_video_comments"
            }
        }

        api_res = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        output_data = api_res.get('data', {}).get('output', {})
        res = [BiliBiliVideoCommentsItem(**item) for item in output_data]
        return ApiResponse(
            code=api_res['code'],
            message=api_res['message'],
            now_time=api_res['now_time'],
            success=api_res['success'],
            usage=api_res.get('data', {}).get('usage', {}),
            data=res,
            request_id=api_res.get('request_id', '')
        )

    async def search_videos(self, keyword: str, page: int, page_size: int) -> ApiResponse[
        List[BiliBiliSearchVideoItem]]:
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"keyword": keyword, "page": page, "pageSize": page_size},
                "code": "search_bilibili_videos"
            }
        }
        api_res = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        output_data = api_res.get('data', {}).get('output', {})
        res = [BiliBiliSearchVideoItem(**item) for item in output_data]
        return ApiResponse(
            code=api_res['code'],
            message=api_res['message'],
            now_time=api_res['now_time'],
            success=api_res['success'],
            usage=api_res.get('data', {}).get('usage', {}),
            data=res,
            request_id=api_res.get('request_id', '')
        )
