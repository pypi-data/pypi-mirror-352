from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.database.response import ExecuteDatabaseResponse
from betteryeah.utils import type_check


class DatabaseClient:

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    @type_check
    async def execute_database(
            self, base_id: str, executable_sql: str
    ) -> ApiResponse[ExecuteDatabaseResponse]:
        """
        执行数据库操作
        :param base_id: 数据库的ID
        :param executable_sql: 要执行的SQL语句
        :return: 包含执行结果的ApiResponse对象
        """
        data = {
            "type": "DATABASE",
            "parameters": {
                "inputs": {
                    "baseId": base_id,
                    "executableSQL": executable_sql}
            },
            "run_env": "BETTERYEAH_SDK",
        }

        api_res = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )
        return ApiResponse(
            code=api_res["code"],
            message=api_res["message"],
            now_time=api_res["now_time"],
            success=api_res["success"],
            usage=api_res.get("data", {}).get("usage", {}),
            data=ExecuteDatabaseResponse(**api_res.get("data", {}).get("output", {})),
            request_id=api_res.get("request_id", ""),
        )
