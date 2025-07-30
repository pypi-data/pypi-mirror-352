from typing import Optional, Dict, Any
from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.sub_flow.response import SubFlowExecuteOutput


class BaseFlowClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def execute(
            self, flow_id: str, parameter: Optional[Dict[str, Any]] = None
    ) -> ApiResponse[SubFlowExecuteOutput]:
        """
        执行flow并返回flow的结果
        :param flow_id: 要执行flow的id
        :param parameter: 执行的参数
        :return: ApiResponse containing SubFlowExecuteOutput
        """
        data = {
            "type": "SUB_FLOW",
            "parameters": {
                "inputs": parameter or {},
                "flow_id": flow_id
            }
        }

        api_response = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )

        output_data = api_response.get("data", {}).get("output", {})
        return ApiResponse(
            code=api_response["code"],
            message=api_response["message"],
            now_time=api_response["now_time"],
            success=api_response["success"],
            usage=api_response.get("data", {}).get("usage", {}),
            data=SubFlowExecuteOutput(
                flow_id='',
                task_id='',
                run_result=output_data,
                durationTime=0.0,
                message='',
                status=''
            ),
            request_id=api_response.get("request_id", ""),
        )


class SubFlowClient(BaseFlowClient):
    pass


class FlowClient(BaseFlowClient):
    pass
