from typing import Any, List, Optional, Union, Dict

from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.plugin.parsing.request import AnalysisModeType, ArticleParsingModel, ExcelOutputType, ResultType
from betteryeah.plugin.parsing.response import VideoParsingItem, WebParsingItem


class ParsingClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def web(self, url_list: List[str]) -> ApiResponse[List[WebParsingItem]]:
        """
        解析给定的URL列表。

        :param url_list: 要解析的url地址列表
        :return: 包含解析结果的ApiResponse对象
        """
        if not url_list:
            return ApiResponse(code=200, success=True, message="SUCCESS", data=[])

        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "url": ",".join(url_list),
                },
                "code": "parse_web_pages"
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
                WebParsingItem(**item)
                for item in api_response.get("data", {}).get("output", [])
            ],
            request_id=api_response.get("request_id", ""),
        )

    async def excel(
            self, excel_url: str, output_format: ExcelOutputType = ExcelOutputType.JSON
    ) -> ApiResponse[Any]:
        """
        解析给定的Excel URL。

        :param excel_url: 要解析的excel url地址
        :param output_format: 输出格式
        :return: 包含解析结果的ApiResponse对象
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"excel_url": excel_url, "output_format": output_format.value},
                "code": "vision_excel"
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
            data=api_response.get("data", {}).get("output", ""),
            request_id=api_response.get("request_id", ""),
        )

    async def audio(
            self, audio_url: str, auto_split: bool = True
    ) -> ApiResponse[Union[str, List[Dict]]]:
        """
        解析给定的音频 URL。

        :param audio_url: 要解析的音频 url地址
        :param auto_split: 是否进行智能分轨,默认为True
        :return: 包含解析结果的ApiResponse对象
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"audio_url": audio_url, "auto_split": auto_split},
                "code": "vision_audio"
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
            data=api_response.get("data", {}).get("output"),
            request_id=api_response.get("request_id", ""),
        )

    async def article(
            self,
            long_text_list: List[str],
            analysis_description: str = "请解析",
            model: ArticleParsingModel = ArticleParsingModel.Claude,
    ) -> ApiResponse[Optional[str]]:
        """
        解析给定的长文本列表。

        :param long_text_list: 长文本的文件url地址,该数组的长度最大为2
        :param analysis_description: 解析要求
        :param model: 选择的模型类型
        :return: 包含解析结果的ApiResponse对象
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "long_text_list": [{"value": item} for item in long_text_list],
                    "analysis_description": analysis_description,
                    "model_type": model.value,
                },
                "code": "vision_article"
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
            data=api_response.get("data", {}).get("output"),
            request_id=api_response.get("request_id", ""),
        )

    async def video(
            self,
            video_url: str,
            analysis_mode: AnalysisModeType = AnalysisModeType.ScreenshotAndAudio,
    ) -> ApiResponse[Union[str, List[VideoParsingItem]]]:
        """
        解析给定的视频 URL。

        :param video_url: 要解析的视频url
        :param analysis_mode: 分析模式
        :return: 包含解析结果的ApiResponse对象
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"video_url": video_url, "analysis_mode": analysis_mode.value},
                "code": "vision_video"
            },
        }
        api_response = await self.api_client.send_request(
            "POST", "/oapi/action/execute", data
        )

        output = api_response.get("data", {}).get("output")
        if isinstance(output, list):
            parsed_output = [VideoParsingItem(**item) for item in output]
        else:
            parsed_output = output

        return ApiResponse(
            code=api_response["code"],
            message=api_response["message"],
            now_time=api_response["now_time"],
            success=api_response["success"],
            usage=api_response.get("data", {}).get("usage", {}),
            data=parsed_output,
            request_id=api_response.get("request_id", ""),
        )

    async def pdf(self, pdf_url: str, result_type: ResultType = ResultType.TEXT) -> ApiResponse[str]:
        """
        PPT、PDF转Word/文本

        :param pdf_url: 要解析的文本url
        :param result_type: 输出格式 text/word
        :return: 包含解析结果的ApiResponse对象
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"pdf_url": pdf_url, "result_type": result_type.value},
                "code": "vision_pdf"
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
            data=api_response.get("data", {}).get("output"),
            request_id=api_response.get("request_id", ""),
        )

    async def parse_document(self, file_url: str) -> ApiResponse[str]:
        """
        通用文档解析

        :param file_url: 要解析的文档 url地址
        :return: 包含解析结果的ApiResponse对象
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {"file_url": file_url},
                "code": "parse_generic_file"
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
            data=api_response.get("data", {}).get("output"),
            request_id=api_response.get("request_id", ""),
        )
