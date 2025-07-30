from typing import Any, Dict, List

from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.plugin.xiaohongshu.response import (
    XiaoHongShuAccountNoteItem,
    XiaoHongShuPopularNotesSearchItem,
    XiaoHongShuSearchNotesItem,
    XiaoHongShuVogueNoteItem,
)


class XiaohongshuClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def search_covers(self, urls: List[str]) -> ApiResponse[any]:
        """
        小红书笔记封面批量查询
        :param urls: 笔记链接列表
        """
        data = {
            "type": "PLUGIN",
            "parameters": {"inputs": {"urls": urls}, "code": "batch_get_xhs_note_covers"},
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
            data=api_response.get("data", {}).get("output", []),
            request_id=api_response.get("request_id", ""),
        )

    async def search_comments(
            self, urls: List[str], count: int
    ) -> ApiResponse[List[str]]:
        """
        小红书评论批量查询
        :param urls: 笔记链接列表
        :param count: 返回的评论数目
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"urls": urls, "count": count},
                "code": "batch_get_xhs_note_comments",
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
            data=api_response.get("data", {}).get("output", []),
            request_id=api_response.get("request_id", ""),
        )

    async def get_hot_topic_comments(self, keyword: str) -> ApiResponse[List[str]]:
        """
        评论洞察
        搜索关键词，得到多篇热门笔记的热评
        :param keyword: 搜索关键字
        """
        data = {
            "type": "PLUGIN",
            "parameters": {"inputs": {"keyword": keyword}, "code": "analyze_xhs_trending_comments"},
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
            data=api_response.get("data", {}).get("output", []),
            request_id=api_response.get("request_id", ""),
        )

    async def get_comments(self, url: str) -> ApiResponse[List[Dict[str, Any]]]:
        """
        通过小红书链接，获取笔记评论数据
        :param url: 笔记的URL地址
        :return: ApiResponse containing a list of comment dictionaries
        """
        data = {
            "type": "PLUGIN",
            "parameters": {"inputs": {"url": url}, "code": "get_xsh_note_comments"},
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
            data=api_response.get("data", {}).get("output", []),
            request_id=api_response.get("request_id", ""),
        )

    async def get_note_details(self, url: str) -> ApiResponse[Dict[str, Any]]:
        """
        通过小红书笔记链接，获取标题、正文、封面图、轮播图、视频、点赞量、评论量、收藏量、分享量、标签信息
        :param url: 笔记的URL地址
        :return: ApiResponse containing note details
        """
        data = {
            "type": "PLUGIN",
            "parameters": {"inputs": {"url": url}, "code": "get_xhs_note_details"},
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
            data=api_response.get("data", {}).get("output", {}),
            request_id=api_response.get("request_id", ""),
        )

    async def search_notes(
            self, question: str
    ) -> ApiResponse[List[XiaoHongShuSearchNotesItem]]:
        """
        根据关键词搜索笔记，返回指定数量的笔记详情
        :param question: 搜索的问题
        :return: ApiResponse containing a list of XiaoHongShuSearchNotesItem
        """
        data = {
            "type": "PLUGIN",
            "parameters": {"inputs": {"question": question}, "code": "search_xhs_notes"},
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
            data=[
                XiaoHongShuSearchNotesItem(**item)
                for item in api_response.get("data", {}).get("output", [])
            ],
            request_id=api_response.get("request_id", ""),
        )

    async def search_popular_notes(
            self, keyword: str, count: int = 10
    ) -> ApiResponse[List[XiaoHongShuVogueNoteItem]]:
        """
        根据搜索关键词获取小红书上的爆款（最热门）笔记，可以配置要获取的笔记数目
        :param keyword: 搜索的关键词
        :param count: 要获取的笔记数量，默认为10篇
        :return: ApiResponse containing a list of XiaoHongShuVogueNoteItem
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"keyword": keyword, "count": count},
                "code": "search_xhs_popular_notes",
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
            data=[
                XiaoHongShuVogueNoteItem(**item)
                for item in api_response.get("data", {}).get("output", [])
            ],
            request_id=api_response.get("request_id", ""),
        )

    async def search_low_follower_popular_notes(
            self, keyword: str, count: int
    ) -> ApiResponse[List[XiaoHongShuPopularNotesSearchItem]]:
        """
        搜索关键词，获取小红书上的低粉爆款笔记�����粉丝量的作者发布的爆款笔记）
        :param keyword: 搜索的关键词
        :param count: 要获取的笔记数量
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"keyword": keyword, "count": count},
                "code": "search_xhs_low_follower_popular_notes",
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
            data=[
                XiaoHongShuPopularNotesSearchItem(**item)
                for item in api_response.get("data", {}).get("output", [])
            ],
            request_id=api_response.get("request_id", ""),
        )

    async def search_account_notes(
            self, author_id: str, count: int
    ) -> ApiResponse[List[XiaoHongShuAccountNoteItem]]:
        """
        根据小红书账号ID查询该账号下最热门笔记
        :param author_id: 小红书账号ID
        :param count: 要获取的笔记数量
        :return: ApiResponse containing a list of XiaoHongShuAccountNoteItem
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"authorId": author_id, "count": count},
                "code": "get_xhs_account_popular_notes",
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
            data=[
                XiaoHongShuAccountNoteItem(**item)
                for item in api_response.get("data", {}).get("output", [])
            ],
            request_id=api_response.get("request_id", ""),
        )

    async def get_hot_topics(self) -> ApiResponse[List[str]]:
        """
        获取小红书实时热点及相关热贴和评论
        """
        data = {
            "type": "PLUGIN",
            "parameters": {"inputs": {}, "code": "get_xhs_trending_topics"},
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
            data=api_response.get("data", {}).get("output", []),
        )
