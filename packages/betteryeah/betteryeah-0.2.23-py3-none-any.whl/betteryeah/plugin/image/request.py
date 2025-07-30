from enum import Enum


class GenerateImageModel(Enum):
    gpt_4o = "gpt-4o"
    gpt_4_vision_preview = "gpt-4-vision-preview"
    anthropic_claude_3_sonnet = "anthropic.claude-3-sonnet"
    anthropic_claude_3_haiku = "anthropic.claude-3-haiku"
    gemini_1_5_Pro = "Gemini 1.5 Pro"
    gemini_1_5_Flash = "Gemini 1.5 Flash"
    gemini_1_0_Pro_Vision = "Gemini 1.0 Pro Vision"


class ImageGenerateModelType(Enum):
    DALL_E_3 = 'dall-e-3'
    Doubao_TextToImageModel_IntelligentDrawing = '豆包-文生图模型-智能绘图'
    CogView = 'CogView'


class AIImageToImageModelType(Enum):
    Doubao_ImageToImageModel_Seaweed = '豆包-图生图模型-智能绘图'

class ImageGenerateVideoModelType(Enum):
    Doubao_VideoGeneration_Seaweed = '豆包-视频生成-Seaweed'

class VideoRatio(Enum):
    """视频比例枚举类"""
    RATIO_1_1 = "1:1"
    RATIO_3_4 = "3:4"
    RATIO_9_16 = "9:16"
    RATIO_21_9 = "21:9"
    RATIO_4_3 = "4:3"
    RATIO_16_9 = "16:9"
