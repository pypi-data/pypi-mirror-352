from typing import List, Optional, Union, Dict

from betteryeah.api_client import ApiClient
from betteryeah.api_response import ApiResponse
from betteryeah.plugin.image.request import GenerateImageModel, ImageGenerateModelType, ImageGenerateVideoModelType, VideoRatio, AIImageToImageModelType


class ImageClient:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    async def vision(self,
                     image_path: List[str],
                     prompt: str = None,
                     model: Union[GenerateImageModel, str] = GenerateImageModel.gpt_4o) -> ApiResponse[Optional[str]]:
        """
        AI识图
        :param image_path: 图像的链接地址
        :param prompt: 图像的提示词
        :param model: AI识图使用的模型，可以是GenerateImageModel枚举或字符串
        """
        image_paths = [{"value": img} for img in image_path] if isinstance(image_path, list) else image_path

        model_value = model.value if isinstance(model, GenerateImageModel) else model

        request_data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "question": prompt,
                    "image_path": image_paths,
                    "model": model_value
                },
                "code": "vision_image"
            }
        }
        api_response = await self.api_client.send_request('POST', '/oapi/action/execute', request_data)
        return ApiResponse(
            code=api_response['code'],
            message=api_response['message'],
            now_time=api_response['now_time'],
            success=api_response['success'],
            usage=api_response.get('data', {}).get('usage', {}),
            data=api_response.get('data', {}).get('output'),
            request_id=api_response.get('request_id', '')
        )

    async def generate(self,
                       prompt: str = None,
                       model: Union[ImageGenerateModelType, str] = ImageGenerateModelType.DALL_E_3) -> ApiResponse[str]:
        """
        AI生图,如果成功,返回GenerateImageResponse实例的一个对象,这个对象的data属性中包含一个message对象.该对象
        存储生成的图片的url地址
        :param prompt: 图像的提示词
        :param model: 生成图像的模型，可以是ImageGenerateModelType枚举或字符串
        :return:GenerateImageResponse的一个对象
        """
        model_value = model.value if isinstance(model, ImageGenerateModelType) else model
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "prompt": prompt,
                    "model_type": model_value
                },
                "code": "generate_image"
            }
        }
        api_response = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        return ApiResponse(
            code=api_response['code'],
            message=api_response['message'],
            now_time=api_response['now_time'],
            success=api_response['success'],
            usage=api_response.get('data', {}).get('usage', {}),
            data=api_response.get('data', {}).get('output'),
            request_id=api_response.get('request_id', '')
        )

    async def ocr(self, image_url: str) -> ApiResponse[str]:
        """
        OCR识图
        :param image_url: 要解析的ocr url地址数组
        """
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "image_url": image_url
                },
                "code": "ocr_image"
            }
        }
        api_response = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        return ApiResponse(
            code=api_response['code'],
            message=api_response['message'],
            now_time=api_response['now_time'],
            success=api_response['success'],
            usage=api_response.get('data', {}).get('usage', {}),
            data=api_response.get('data', {}).get('output'),
            request_id=api_response.get('request_id', '')
        )

    async def ai_image_to_image(self,
                                prompt: str,
                                model: Union[AIImageToImageModelType, str] = AIImageToImageModelType.Doubao_ImageToImageModel_Seaweed,
                                logo_enable: bool = False,
                                logo_content: str = None,
                                logo_opacity: float = None,
                                logo_position: int = None,
                                output_format: str = "markdown",
                                controlnet_args: Optional[List[Dict]] = None,
                                style_reference_args: Optional[Dict] = None) -> ApiResponse[str]:
        """
        图片转图片
        :param prompt: 图片的提示词
        :param model: 图片生成图片的模型
        :param logo_enable: 是否启用logo，可选
        :param logo_content: logo的内容，可选
        :param logo_opacity: logo的透明度，可选
        :param logo_position: logo的位置，可选
        :param output_format: 输出的格式，可选值为markdown、json
        :param controlnet_args: 数组类型，可传入多个。类似ControlNet 保持构图的方案，可选，包含以下字段：
            - imageUrl: 参考图片的URL地址，字符串类型
            - pose: 人物姿态参数，包含两个子字段：
                - enable: 是否启用人物姿态，布尔值类型（True/False）
                - strength: 相似度参数，数值越大越相似；数值为0时不参考，数值范围0.0-1.0。
            - canny: 画面轮廓边缘参数，包含两个子字段：
                - enable: 是否启用轮廓边缘，布尔值类型（True/False）
                - strength: 相似度参数，数值越大越相似；数值为0时不参考，数值范围0.0-1.0。
            - depth: 画面景深参数，包含两个子字段：
                - enable: 是否启用景深，布尔值类型（True/False）
                - strength: 相似度参数，数值越大越相似；数值为0时不参考，数值范围0.0-1.0。
            注意：pose、canny、depth三种方案只能选择一种启用
        :param style_reference_args: 风格参考图，可选，包含以下字段：
            - imageUrl: 风格参考图片的URL地址，字符串类型，可选
            - styleWeight: 风格保持权重参数，包含两个子字段：
                - enable: 是否启用风格权重，布尔值类型（True/False）
                - strength: 数值越大越相似；数值为0时不参考，数值范围0.0-1.0。
            - idWeight: 人脸权重参数，包含两个子字段：
                - enable: 是否启用人脸权重，布尔值类型（True/False）
                - strength: 数值越大越相似；数值为0时不参考，数值范围0.0-1.0。      
        """
        model_value = model.value if isinstance(model, AIImageToImageModelType) else model
        controlnet_args = controlnet_args if controlnet_args else [
                {
                    "imageUrl": "",
                    "pose": {"enable": False, "strength": 0.4},
                    "canny": {"enable": False, "strength": 0.4},
                    "depth": {"enable": False, "strength": 0.4},
                }
            ]
        style_reference_args = style_reference_args if style_reference_args else {
            "imageUrl": "",
            "idWeight": {"enable": False, "strength": 0.4},
            "styleWeight": {"enable": False, "strength": 0.4}
        }
        
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "type":"image_to_image",
                    "prompt": prompt,
                    "image_to_image_model_type": model_value,
                    "logo_enable": logo_enable,
                    "logo_content": logo_content,
                    "logo_opacity": logo_opacity,
                    "logo_position": logo_position,
                    "output_format": output_format,
                    "controInetArgs": controlnet_args,
                    "StyleReferenceArgs": style_reference_args
                },
                "code": "generate_image"
            }
        }
        api_response = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        return ApiResponse(
            code=api_response['code'],
            message=api_response['message'],
            now_time=api_response['now_time'],
            success=api_response['success'],
            usage=api_response.get('data', {}).get('usage', {}),
            data=api_response.get('data', {}).get('output'),
            request_id=api_response.get('request_id', '')
        )

    async def ai_image_to_video(self, 
                                prompt: str,
                                image_url: str,
                                model: Union[ImageGenerateVideoModelType, str] = ImageGenerateVideoModelType.Doubao_VideoGeneration_Seaweed,
                                video_ratio: VideoRatio = VideoRatio.RATIO_16_9,
                                webhook_url: str = ""
                                ) -> ApiResponse[str]:
        """
        图片转视频
        :param prompt: 图片的提示词
        :param image_url: 图片的url地址
        :param model: 视频生成的模型
        :param video_ratio: 视频的宽高比
        :param webhook_url: 回调的url地址
        """
        model_value = model.value if isinstance(model, ImageGenerateVideoModelType) else model
        data = {
            "type": "PLUGIN",
            "parameters": {
                "inputs": {
                    "prompt": prompt,
                    "image_to_video_model_type": model_value,
                    "ratio": video_ratio.value,
                    "image_url": image_url,
                    "webhook_url": webhook_url
                },
                "code": "generate_video"
            }
        }
        api_response = await self.api_client.send_request('POST', '/oapi/action/execute', data)
        return ApiResponse(
            code=api_response['code'],
            message=api_response['message'],
            now_time=api_response['now_time'],
            success=api_response['success'],
            usage=api_response.get('data', {}).get('usage', {}),
            data=api_response.get('data', {}).get('output'),
            request_id=api_response.get('request_id', '')
        )
