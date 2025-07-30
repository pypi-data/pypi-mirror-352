from typing import Optional

from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse


class GenericClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def chart_plotting(self,
                             requirement: str,
                             data_desc: str,
                             data: Optional[str] = None,
                             excel_file: Optional[str] = None) -> ApiResponse[Optional[str]]:
        """
        图表插件绘制
        :param requirement: 图表绘制要求，包含图表类型（折线、柱状等）、数据维度、工具栏等等图表细节信息
        :param data_desc: 数据描述，即针对数据的解释，包含数据含义整体描述、字段含义、数据间逻辑关系等等信息
        :param data: 用于生成图表的自定义数据源，可以是任意格式的json数据。
        :param excel_file: excel文件链接，如果用户输入中没有文件链接，默认值为None
        :return: 返回markdown格式的字符串
        :raises ValueError: 当data和excel_file同时为None时抛出
        """
        if data is None and excel_file is None:
            raise ValueError("data 与 excel_file 不能同时为空")

        data = {
            "type": "PLUGIN",
            "parameters": {
                "code": "generate_chart",
                "inputs": {
                    "requirment": requirement,
                    "dataDesc": data_desc,
                    "data": data,
                    "excelFile": excel_file
                }
            }
        }
        api_res = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        return ApiResponse(
            code=api_res['code'],
            message=api_res['message'],
            now_time=api_res['now_time'],
            success=api_res['success'],
            usage=api_res.get('data', {}).get('usage', {}),
            data=api_res.get('data', {}).get('output'),
            request_id=api_res.get('request_id', '')
        )
