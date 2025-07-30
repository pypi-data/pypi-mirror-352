from typing import List, Dict

from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.plugin.douyin.response import DouyinTrendingTopicItem, DouyinVideoAnalysisItem, \
    DouyinVideoAnalysisItemDetail


class DouyinClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def get_comments(self, url: str) -> ApiResponse[List[Dict[str, str]]]:
        """
        通过抖音链接，获取相关评论
        :param url: 抖音视频的URL地址
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"url": url},
                "code": "get_douyin_comments"
            }
        }
        api_res = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        return ApiResponse(
            code=api_res['code'],
            message=api_res['message'],
            now_time=api_res['now_time'],
            success=api_res['success'],
            usage=api_res.get('data', {}).get('usage', {}),
            data=api_res.get('data', {}).get('output', []),
            request_id=api_res.get('request_id', '')
        )

    async def analyze_video(self, url: str) -> ApiResponse[DouyinVideoAnalysisItem]:
        """
        通过抖音链接，获取视频文案和相关截图
        :param url: 抖音视频的URL地址
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"url": url},
                "code": "analyze_douyin_video"
            }
        }
        api_res = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        output_data = api_res.get('data', {}).get('output', {})
        res = DouyinVideoAnalysisItem(
            title=output_data.get('title'),
            tags=output_data.get('tags'),
            data=[DouyinVideoAnalysisItemDetail(**item) for item in output_data.get('data', [])]
        )
        return ApiResponse(
            code=api_res['code'],
            message=api_res['message'],
            now_time=api_res['now_time'],
            success=api_res['success'],
            usage=api_res.get('data', {}).get('usage', {}),
            data=res,
            request_id=api_res.get('request_id', '')
        )

    async def get_hot_topics(self, type: str = "热榜") -> ApiResponse[List[DouyinTrendingTopicItem]]:
        """
        获取抖音热门话题
        :param type: 热榜类型，可选值为 "热榜"、"娱乐榜"、"社会榜"、"挑战榜"，默认为 "热榜"
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"type": type},
                "code": "get_douyin_trending_topics"
            }
        }
        api_res = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        output_data = api_res.get('data', {}).get('output', [])
        res = [DouyinTrendingTopicItem(**item) for item in output_data]
        return ApiResponse(
            code=api_res['code'],
            message=api_res['message'],
            now_time=api_res['now_time'],
            success=api_res['success'],
            usage=api_res.get('data', {}).get('usage', {}),
            data=res,
            request_id=api_res.get('request_id', '')
        )
