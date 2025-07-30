from typing import List, Optional

from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.knowledge.request import HitStrategyType, OutPutType, MemoryType
from betteryeah.knowledge.response import (
    InsertKnowledgeResponse,
    KnowledgeMatchContent,
    SearchKnowledgeResponse,
)
from betteryeah.utils import type_check


class KnowledgeClient:

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    @type_check
    async def insert_knowledge(
            self, content: str, file_id: int, partition_id: Optional[int] = None
    ) -> ApiResponse[InsertKnowledgeResponse]:
        """
        插入知识库
        :param content: 要插入的知识库的内容
        :param file_id: 插入的知识库id
        :param partition_id: 知识库对应的partition_id
        """
        data = {
            "type": "KNOWLEDGE",
            "parameters": {
                "inputs": {
                    "content": content,
                    "file_id": file_id,
                    "memoryType": MemoryType.INSERT_MEMORY.value,
                    "partition_id": partition_id,
                },
            },
        }

        api_res = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )
        return ApiResponse(
            code=api_res.get("code", 0),
            message=api_res.get("message", ""),
            now_time=api_res.get("now_time", ""),
            success=api_res.get("success", False),
            usage=api_res.get("data", {}).get("usage", {}),
            data=InsertKnowledgeResponse(**api_res.get("data", {}).get("output", {})),
            request_id=api_res.get("request_id", ""),
        )

    async def search_knowledge(
            self,
            search_content: str,
            partition_id: int,
            file_ids: Optional[List[int]] = None,
            tags: List[str] = [],
            output_type: OutPutType = OutPutType.TEXT,
            hit_strategy: HitStrategyType = HitStrategyType.MIX,
            max_result_num: int = 3,
            ranking_strategy: bool = False,
            similarity: float = 0.4,
    ) -> ApiResponse[SearchKnowledgeResponse | str]:
        """
        查询知识库
        :param search_content: 查询的内容信息
        :param partition_id: 文件的 partition_id
        :param file_ids: 文件的id列表
        :param tags: 标签名称
        :param output_type: 选择输出类型
        :param hit_strategy: 查询策略，MIX表示混合查询，KEY表示关键字查询，SEMANTICS表示语义查询
        :param max_result_num: 最大结果数 1-10
        :param ranking_strategy: 是否启用指令重排，默认为False
        :param similarity: 最低相似度，默认0.4
        """
        if tags is None:
            tags = []
        if file_ids is None:
            file_ids = []
        data = {
            "type": "KNOWLEDGE",
            "parameters": {
                "inputs": {
                    "tags": tags,
                    "memory": partition_id,
                    "file_ids": file_ids,
                    "memoryType": MemoryType.SEARCH_MEMORY.value,
                    "outputType": output_type.value,
                    "hitStrategy": hit_strategy.value,
                    "maxResultNum": max_result_num,
                    "searchContent": search_content,
                    "rankingStrategy": 1 if ranking_strategy or ranking_strategy is None else 2,
                    "similarity": similarity if similarity else 0.4
                }
            },
        }
        api_res = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )

        output = api_res.get("data", {}).get("output", {})
        if isinstance(output, str):
            res_data = output
        else:
            match_contents = [KnowledgeMatchContent(**item) for item in output.get("match_contents", [])]
            res_data = SearchKnowledgeResponse(
                cost_time=output.get("cost_time"),
                match_contents=match_contents,
                usage=output.get("usage"),
                synonym_note=output.get("synonym_note")
            )

        return ApiResponse(
            code=api_res.get("code", 0),
            message=api_res.get("message", ""),
            now_time=api_res.get("now_time", ""),
            success=api_res.get("success", False),
            usage=api_res.get("data", {}).get("usage", {}),
            data=res_data,
            request_id=api_res.get("request_id", ""),
        )
