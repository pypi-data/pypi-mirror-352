from typing import List, Optional, Union

from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.plugin.search.request import TimeFreshness
from betteryeah.plugin.search.response import SearchItem, FeloSearchResponse, AiSearchResponse


class SearchClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def google(
            self, question: str, parse_web_count: int = 2, domain_name: str = None
    ) -> ApiResponse[List[SearchItem]]:
        """
        搜索google并返回信息
        :param question: 要搜索的内容
        :param parse_web_count: 解析链接数量,默认为2
        :param domain_name: 指定域名搜索
        :return: ApiResponse对象
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "question": question,
                    "parse_web_count": parse_web_count,
                    "domain_name": domain_name,
                },
                "code": "search_by_google"
            },
        }
        api_response = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )

        search_items = [
            SearchItem(**item)
            for item in api_response.get("data", {}).get("output", [])
        ]

        return ApiResponse(
            code=api_response["code"],
            message=api_response["message"],
            now_time=api_response["now_time"],
            success=api_response["success"],
            usage=api_response.get("data", {}).get("usage", {}),
            data=search_items,
            request_id=api_response.get("request_id", ""),
        )

    async def bing(
            self, question: str, parse_web_count: int = 2, domain_name: str = None
    ) -> ApiResponse[List[SearchItem]]:
        """
        搜索bing并返回信息
        :param question: 要搜索的内容
        :param parse_web_count: 解析链接数量,默认为2
        :param domain_name: 指定域名搜索
        :return: ApiResponse对象
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "question": question,
                    "parse_web_count": parse_web_count,
                    "domain_name": domain_name,
                },
                "code": "search_by_bing"
            },
        }
        api_response = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )

        search_items = [
            SearchItem(**item)
            for item in api_response.get("data", {}).get("output", [])
        ]

        return ApiResponse(
            code=api_response["code"],
            message=api_response["message"],
            now_time=api_response["now_time"],
            success=api_response["success"],
            usage=api_response.get("data", {}).get("usage", {}),
            data=search_items,
            request_id=api_response.get("request_id", ""),
        )

    async def felo_search(
            self, 
            query: str, 
            summary: Optional[bool] = False, 
            freshness: Union[str, TimeFreshness] = TimeFreshness.NO_LIMIT,
            parse_web_count: int = 5
    ) -> ApiResponse[FeloSearchResponse]:
        freshness = freshness.value if isinstance(freshness, TimeFreshness) else freshness
        """
        搜索felo并返回信息
        :param question: 要搜索的内容
        :param summary: 是否返回摘要
        :param freshness: 时间筛选条件，控制搜索结果的时间范围
        :param parse_web_count: 解析链接数量,默认为5
        :return: ApiResponse对象
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "query": query,
                    "summary": summary,
                    "freshness": freshness,
                    "parse_web_count": parse_web_count,
                },
                "code": "web_search"
            },
        }
        api_response = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )

        output = api_response.get("data", {}).get("output", {})
        if output:
            search_items = FeloSearchResponse(**output)
        else:
            search_items = None

        return ApiResponse(
            code=api_response["code"],
            message=api_response["message"],
            now_time=api_response["now_time"],
            success=api_response["success"],
            usage=api_response.get("data", {}).get("usage", {}),
            data=search_items,
            request_id=api_response.get("request_id", ""),
        )
        
    async def ai_search(    
            self, query: str, 
            freshness: Union[str, TimeFreshness] = TimeFreshness.NO_LIMIT
    ) -> ApiResponse[AiSearchResponse]:
        freshness = freshness.value if isinstance(freshness, TimeFreshness) else freshness
        """
        搜索ai并返回信息
        :param query: 要搜索的内容
        :param freshness: 时间筛选条件，控制搜索结果的时间范围
        :return: ApiResponse对象
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "query": query,
                    "freshness": freshness,
                },
                "code": "ai_search"
            },
        }
        api_response = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )

        search_items = AiSearchResponse(**api_response.get("data", {}).get("output", {}))

        return ApiResponse(
            code=api_response["code"],
            message=api_response["message"],
            now_time=api_response["now_time"],
            success=api_response["success"],
            usage=api_response.get("data", {}).get("usage", {}),
            data=search_items,
            request_id=api_response.get("request_id", ""),
        )
