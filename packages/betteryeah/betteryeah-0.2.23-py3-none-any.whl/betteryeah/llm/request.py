from enum import Enum


class Model(Enum):
    # OpenAI
    gpt_3_5_turbo = "gpt-3.5-turbo"
    gpt_3_5_turbo_16k = "gpt-3.5-turbo-16k"
    gpt_4_turbo = "gpt-4-turbo"
    gpt_4o = "gpt-4o"
    gpt_4o_mini = "gpt-4o-mini"
    OPENAI_O1_PREVIEW = "o1-preview"
    OPENAI_O1_MINI = "o1-mini"
    
    # DeepSeek
    DEEPSEEK_DEEPSEEK_V3 = "DeepSeek-V3"
    DEEPSEEK_DEEPSEEK_R1 = "DeepSeek-R1"
    # 模型已废弃
    deepseek_chat = "deepseek-chat"

    # Anthropic
    anthropic_claude_3_sonnet = "anthropic.claude-3-sonnet"
    CLAUDE_ANTHROPIC_CLAUDE_35_SONNET = "anthropic.claude-3.5-sonnet"
    anthropic_claude_3_haiku = "anthropic.claude-3-haiku"
    ANTHROPIC_CLAUDE_35_HAIKU = "anthropic.claude-3.5-haiku-20241022-v1:0"
    ANTHROPIC_CLAUDE_35_SONNET_20241022 = "anthropic.claude-3.5-sonnet-20241022-v2:0"
    ANTHROPIC_CLAUDE_37_SONNET = "anthropic.claude-3.7-sonnet-20250219-v1:0"
    
    # 废弃
    anthropic_claude_v2 = "anthropic.claude-v2"
    anthropic_claude_instant_v1 = "anthropic.claude-instant-v1"
    anthropic_claude_3_opus = "anthropic.claude-3-opus"
    claude_3_opus = "claude-3-opus"
    
    
    # Google gemini
    gemini_1_5_pro = "Gemini 1.5 Pro"
    GOOGLE_GEMINI_15_FLASH = "Gemini 1.5 Flash"
    GOOGLE_GEMINI_20_FLASH = "Gemini 2.0 Flash"
    
    # 废弃废弃
    gemini = "gemini"
    
    #Moonshot Kimi 
    moonshot_v1_8k = "moonshot-v1-8k"
    moonshot_v1_32k = "moonshot-v1-32k"
    moonshot_v1_128k = "moonshot-v1-128k"
    
    
    # Doubao
    doubao_pro_128 = "Doubao-pro-128k"
    doubao_pro_32 = "Doubao-pro-32k"
    doubao_pro_4 = "Doubao-pro-4k"
    DOUBAO_15_PRO_256K = "Doubao-1.5-pro-256k"
    DOUBAO_15_PRO_32K = "Doubao-1.5-pro-32k"
    DOUBAO_15_LITE_32K = "Doubao-1.5-lite-32k"
    

    # 智普 (ChatGLM)
    GLM_3_Turbo = "GLM-3-Turbo"
    GLM_4 = "GLM-4"
    GLM_4V = "GLM-4V"
    GLM_4_AIRX = "GLM-4-AirX"
    GLM_4_AIR = "GLM-4-Air"
    GLM_4_LONG = "GLM-4-Long"
    GLM_4_FLASH = "GLM-4-Flash"
    GLM_4_PLUS = "GLM-4-Plus"
    GLM_4V_PLUS = "GLM-4V-Plus"
    GLM_4V_FLASH = "GLM-4V-Flash"
    
    # 废弃
    chatglm_lite = "chatglm_lite"
    chatglm_lite_32k = "chatglm_lite_32k"
    chatglm_pro = "chatglm_pro"
    chatglm_std = "chatglm_std"
    glm_4_9b = "glm-4-9b"
    ChatGLM2_6B_32K = "ChatGLM2_6B_32K"
    
    
    # Alibaba (Qwen)
    qwen_turbo = "qwen-turbo"
    qwen_plus = "qwen-plus"
    QWEN_MAX = "qwen-max"
    QWEN_7B_CHAT = "qwen-7b-chat"
    QWEN2_72B_INSTRUCT = "qwen2-72b-instruct"
    QWEN25_MAX = "Qwen2.5-Max"
    QWEN_CODER_PLUS = "qwen-coder-plus"
    QWEN_CODER_TURBO = "qwen-coder-turbo"
    QWQ_32B_PREVIEW = "qwq-32b-preview"


    # Baidu
    ERNIE_40_8K = "ERNIE-4.0-8K"
    ERNIE_35_128K = "ERNIE-3.5-128K"
    ERNIE_35_8K = "ERNIE-3.5-8K"
    ERNIE_SPEED_8K = "ERNIE-Speed-8K"
    ERNIE_SPEED_128K = "ERNIE-Speed-128K"
    ERNIE_40_TURBO_8K_PREVIEW = "ERNIE-4.0-Turbo-8K-Preview"
    
    # 废弃
    ERNIE_Bot = "ERNIE-Bot"
    ERNIE_Bot_turbo = "ERNIE-Bot-turbo"
    ERNIE_Bot_4 = "ERNIE-Bot-4"
    Qianfan_Chinese_Llama_2_7B = "Qianfan_Chinese_Llama_2_7B"
    
    # Meta Llama
    LLAMA3_1_8B_INSTRUCT = "llama3.1-8b-instruct"
    LLAMA3_1_70B_INSTRUCT = "llama3.1-70b-instruct"
    LLAMA3_1_405B_INSTRUCT = "llama3-1-405b-instruct"
    LLAMA3_8B_INSTRUCT = "meta.llama3-8b-instruct"
    LLAMA3_70B_INSTRUCT = "meta.llama3-70b-instruct"
    
    # 废弃
    Llama_2_7b_chat = "Llama-2-7b-chat"
    Llama_2_70b_chat = "Llama-2-70b-chat"
    

    # 百川
    BAICHUAN4 = "Baichuan4"
    BAICHUAN3_TURBO = "Baichuan3-Turbo"
    BAICHUAN2_TURBO_192K = "Baichuan2-Turbo-192k"
    
    # 废弃
    AquilaChat_7B = "AquilaChat_7B"
    
    # 阶跃星辰
    STEP_1V = "step-1v"
    STEP_1_32K = "step-1-32k"
    STEP_1_128K = "step-1-128k"
    STEP_1_256K = "step-1-256k"
    STEP_2_16K = "step-2-16k"
    STEP_1_FLASH = "step-1-flash"
    
    # 商汤日日新
    SENSECHAT_5 = "SenseChat-5"
    SENSECHAT_VISION = "SenseChat-Vision"
    
    # 腾讯混元模型
    HUNYUAN_VISION = "hunyuan-vision"
    HUNYUAN_PRO = "hunyuan-pro"
    HUNYUAN_TURBO = "hunyuan-turbo"
    HuanYuan = "HuanYuan"

    # 360
    generalv2 = "generalv2"
    general = "general"
    
    
    # 字节跳动
    skylark2_pro_32k = "skylark2-pro-32k"
    skylark2_pro_turbo_8k = "skylark2-pro-turbo-8k"
    BTY_NeuroText_Enhanced = "BTY-NeuroText-Enhanced"
    
    
    # BLOOMZ (BLOOM)
    BLOOMZ_7B = "BLOOMZ-7B"
    
    
