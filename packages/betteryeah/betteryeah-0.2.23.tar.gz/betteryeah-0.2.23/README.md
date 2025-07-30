# BetterYeah

⚡ 依托于 **[BetterYeah AI 应用开发平台](https://ai.betteryeah.com)** 快速构建 AI 应用的开发库 ⚡

## 🌊 为什么选择 BetterYeah?

尽管 **[BetterYeah AI 应用开发平台](https://ai.betteryeah.com)** 已经提供了相当友好的产品助力我们开发 AI 应用，**BetterYeah** 在此基础上将平台能力封装，可以让平台的 AI 能力更方便友好的集成到你的业务系统中。你可以通过编码的方式自由的组合各种逻辑，丝滑的与业务逻辑相结合。

与市面上同类产品的对比：

| 产品/对比维度 | BetterYeah                                                   | Langchain                                                    | Dify                                                         | Coze                                                         | 自研                                                         |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 上手难度      | ⭐️⭐️⭐️⭐️⭐️<br />无需了解的AI应用开发概念                          | ⭐️⭐️<br />需要了解Langchain中各种抽象概念，有一定的学习门槛    | ⭐️⭐️⭐️⭐️<br />需要了解基本的AI应用开发概念                       | ⭐️⭐️⭐️⭐️<br />需要了解基本的AI应用开发概念                       | ⭐️<br />需要了解AI应用开发上下文知识后纯Code编码实现，难度较大 |
| 开发方式      | ⭐️⭐️⭐️⭐️<br />1、提供标准产品化使用<br />2、支持在线CodeIDE编码、集成、部署，IDE内置 AI 应用开发SDK，可以调用<br />3、支持 AI 应用开发框架 | ⭐️⭐️⭐️<br />1、仅支持开发框架                                   | ⭐️⭐️<br />1、提供标准产品化使用<br />                          | ⭐️⭐️⭐️<br />1、提供标准产品化使用<br />2、支持在线CodeIDE编码、集成、部署<br /> | 项目研发                                                     |
| 易用性        | ⭐️⭐️⭐️⭐️⭐️<br />1、Agent Copilot辅助搭建Agent，从Prompt，知识库，Flow技能，插件，开场白，推荐问题等全方面辅助搭建，并且搭建效果可以随时测试和辅助修改<br /><br />2、Prompt编辑器 -- 辅助使用者写出更符合期望的Prompt<br />3、支持30+行业垂类模板Agent<br />4、支持30+，搜索、图像处理、解析、小红书、抖音、微博等涵盖国内各种应用场景的内置插件 | ⭐️<br />纯Code编码，易用性较差                                | ⭐️⭐️<br />1、仅支持辅助Prompt和开场白等简单的辅助搭建<br />2、支持31个Agent、工作流模板，主要针对通用场景和国外应用场景<br />3、支持40个内置工具，主要针对通用场景（比如绘画）和国外应用 | ⭐️⭐️<br />1、仅支持辅助Prompt和开场白等简单的辅助搭建，搭建效果不支持实时预览和调试在修改。<br />2、提供插件商店，提供非常多的公开插件，主要这对国外应用场景和通用类场景 | ⭐️<br />需要结合自研产品形态判断                              |
| 支持模块      | ⭐️⭐️⭐️⭐️<br />1、大模型（LLM）<br />2、Agent<br />3、工作流<br />4、插件<br />5、知识库<br />6、数据库 | ⭐️<br />需要了解开发框架抽象的Chain、Agents、Memory等概念后自研各种标准业务模块 | ⭐️⭐️⭐️<br />1、大模型（LLM）<br />2、Agent<br />3、工作流<br />4、插件<br />5、知识库 | ⭐️⭐️⭐️⭐️⭐️<br />1、大模型（LLM）<br />2、Agent<br />3、工作流<br />4、插件<br />5、知识库<br />6、数据库<br />7、自定义消息卡片 | ⭐️<br />需要自行研发各种模块                                  |
| 模型          | [内置40+ 常用大模型](#模型支持)，并且对模型能力做过评估，方便基于不同场景选择合适的模型<br />稳定性保障；✅<br />模型运行情况监控✅<br />统一集成协议✅<br />支持模型能力评估✅<br />多环境部署，平滑上下线✅<br />支持监督管理（安全）✅ | 需要手动接入模型,理论支持所有模型<br />稳定性保障；❌<br />模型运行情况监控❌<br />统一集成协议✅<br />支持模型能力评估❌<br />多环境部署，平滑上下线✅<br />支持监督管理（安全）❌ | 仅支持OpenAI和claude的模型❌                                  | 仅支持Gemini和OpenAI等6个模型❌                               | ⭐️<br />需要手动接入各个模型，需要花费大量资源处理模型之间的差异、资源代理、模型服务监控、部署等等 |
| 知识库        | ⭐️⭐️⭐️⭐️⭐️<br />1、针对Excel、Pdf、Docx等多种格式的问题提供相适配文档类型的分段规则<br />2、文档支持150MB超大杯导入<br />3、支持文档、问答、手动输入、网页、视频、浏览器插件抓取等多种添加文档的方式<br />4、支持重排以提高查询准确度<br />5、支持两种Embeding方式<br />6、支持语义、关键词、标签、QA等多种查询方式<br />7、支持在线命中测试和编辑器，随时调整知识库文档 | ⭐️<br />需要自行开发                                          | ⭐️⭐️⭐️<br />1、支持文档、Notion、网页三种导入方式<br />2、文档导入限制15MB<br />3、支持两种Embeding方式<br />4、支持重排以提高查询准确度<br >5、支持向量检索、全文检索、混合检索3中检索方式<br />6、支持命中测试 | ⭐️⭐️<br />1、支持文档、网页、Notion、Google Drive、手动输入等添加文档方式<br />2、文档限制最多300个文档/知识库，每个文档不超过20MB，PDF不超过250页 | ⭐️<br />1、需要花费大量精力处理文档解析（比如处理PDF，PDF中的表格，Word表格，复杂内容解析，复杂格式解析）<br />2、需要花费精力处理向量化，重排，混合检索，查询算法等等来保证查询准确性 |
| 数据库        | ⭐️⭐️⭐️⭐️⭐️<br />支持Excel、CSV数据导入<br />支持在线数据预览、编辑<br />支持一键集成到Agent、Workflow<br />提供增删改查的自由使用方式 | 需要自行开发                                                 | 不支持数据库                                                 | ⭐️<br />支持一键集成到Agent、Workflow<br />不支持数据导入<br />不支持数据预览、编辑 | 需要自行开发                                                 |
| 调试          | 1、Agent、Flow测试集支持，Prompt的自动化测试<br />2、支持基于日志联动测试集，更高效的调试<br />3、支持基于日志调试，场景重现 | ⭐️<br />开发者自行调试                                        | ⭐️⭐️<br />日志调试，效率低                                     | ⭐️⭐️<br />日志调试，效率低                                     | ⭐️<br />本地调试，时间长，排查困难                            |
| 部署,发布     | ⭐️⭐️⭐️⭐️⭐️<br />1、支持平台内发布，在线使用<br />2、支持发布到独立web<br />3、支持发布到生态系统的桌面应用<br />4、支持持发布到生态系统移动端H5<br />5、支持发布到IOS、Android生态系统App<br />6、支持通过ChatSDK集成到三方产品中使用<br />7、支持通过API暴露给三方产品使用<br />8、支持一键发布到钉钉、飞书、企业微信、微信公众号等国内平台 | ⭐️<br />需要自行打通各种发布渠道                              | ⭐️⭐️⭐️⭐️<br />1、支持作为独立web发布<br />2、支持通过API集成到三方产品<br />3、提供前端开发SDK二次开发 | ⭐️⭐️⭐️<br />1、支持发布到Cici、Discord、Telegram、Instagram、Messenger、Reddit、Slack、LINE、Lark等国外平台 | ⭐️<br />需要自行打通各种发布渠道                              |
| 维护          | 1、支持在线详细粒度日志系统<br />2、支持从日志跳转到对应业务功能进行错误定位 | 需要自行排查错误                                             | 支持在线日志                                                 | 支持在线日志                                                 | 需要自行排查错误                                             |
| 生态系统      | Agent Chat SDK（开发生态）<br />BetterYeah SDK（开发生态）<br />BetterYeah IOS、Android App（使用生态）<br />BetterYeah Chatbot 桌面App（使用生态） | LangSmith（开发生态）<br />LangGraph（开发生态）<br />LangServe（开发生态） | 无生态                                                       | Cici（使用生态）                                             | 生态需要自行开发                                             |

### 模型支持

| 渠道          | 模型                        |
| ------------- | --------------------------- |
| OpenAI        | gpt-3.5-turbo               |
|               | gpt-3.5-turbo-16K           |
|               | gpt-4-turbo                 |
|               | gpt-4o                      |
| Claude        | anthropic.claude-v2         |
|               | anthropic.claude-instant-v1 |
|               | anthropic.claude-3-sonnet   |
|               | anthropic.claude-3-haiku    |
| Google        | gemini 1.5 Pro              |
|               | Gemini 1.5 Flash            |
| Kimi          | moonshot-v1-32k             |
|               | moonshot-v1-8k              |
|               | moonshot-v1-128k            |
| 豆包          | Doubao-pro-128k             |
|               | Doubao-pro-32k              |
|               | Doubao-pro-4k               |
| 智普          | GLM-3-Turbo                 |
|               | GLM-4                       |
|               | GLM-4V                      |
| 通义千问      | qwen-turbo                  |
|               | qwen-plus                   |
|               | qwen-max-longcontext        |
|               | qwen-max                    |
|               | qwen-7b-chat                |
| 百度千帆      | ERNIE-4.0-8k                |
|               | ERNIE-3.5-128k              |
|               | ERNIE-3.5-8k                |
|               | ERNIE-Speed-8k              |
|               | ERNIE-Speed-128k            |
| Llama         | meta.llma3-8b-instruct      |
|               | meta.llma3-70b-instruct     |
| 深度求索      | deepseek-chat               |
| GLM           | glm-4-9b                    |
| BTY-NeuroText | BTY-NeuroText-Enhanced      |

## 🚀 BetterYeah 可以做什么？

BetterYeah 可以轻松打造业务专家级的AI工作助手，在下面场景均有沉淀丰富的解决方案：

**智能客服**

- [麦乐（Melody）女装客服](https://ai.betteryeah.com/chatbot/e2740ac6-5187-4ada-be10-14ef1a722145)
- [人人乐家电商城售后](https://ai.betteryeah.com/chatbot/7b293d4c-21fa-4f9e-bfa4-2fd8edb0ab5a)
- [小啄汽修铺](https://ai.betteryeah.com/chatbot/7b1578ae-f19d-4fad-acb1-9af9df137dcb)

**电商场景**

- [店铺数据分析师](https://ai.betteryeah.com/chatbot/0130788a-d9ca-43fb-9840-19123c4de56d)
- [电商客服小Y](https://ai.betteryeah.com/chatbot/9da70a59-3600-43ef-a33e-7c1ec32043e4)
- [店铺评论分析助手](https://ai.betteryeah.com/chatbot/10518030-87cf-4a73-b28a-3ead1cd8153e)

**销售场景**

- [StyleHup销售分析助理](https://ai.betteryeah.com/chatbot/73c4ed01-484e-42f4-a3a9-32f67b8ce6a1)
- [CloudWav客户挖掘助理](https://ai.betteryeah.com/chatbot/31dd7361-1679-421b-b3cf-13aacbaa6eb0)
- [手机导购助手](https://ai.betteryeah.com/chatbot/5146aa72-b3df-45ad-ad96-f1fb261e5c93)

**营销场景**

- [小红书爆款内容分析生成](https://ai.betteryeah.com/chatbot/0b0adfee-2bb8-43d0-822c-1cc8bcf17e7c)
- [广告文案AI工作助理](https://ai.betteryeah.com/chatbot/1be21199-01c4-4aad-b90e-bf510e6e07c8)

**HR场景**

- [JD生成大师](https://ai.betteryeah.com/chatbot/62c86e6e-8f70-441d-a048-daafa0655932)
- [【销售经理】初面官](https://ai.betteryeah.com/chatbot/f6ffa238-7663-456a-8655-afcb6ff247fa)

更多场景和解决方案可以进入[官网](https://www.betteryeah.com/)详细了解，产品体验地址：https://ai.betteryeah.com

你也可以扫码加入我们的产品讨论群咨询交流：

![产品交流群](https://ai.betteryeah.com/png/productDiscussionGroup-635024d6.png)

## 🔗 安装
python版本最低要求为3.10
```bash
# 使用pip
pip install betteryeah

# 使用conda
conda install langchain
```

## 🌴 BetterYeah 开发框架的介绍

**BetterYeah** 将 AI 应用开发过程抽象为 4 大模块 `大模型` `知识库` `数据库` `技能插件` 四个模块

模型模块，**BetterYeah** 内置了国内外，开源，非开源等 40+个 AI 模型，这些模型在 **[BetterYeah AI 应用开发平台](https://ai.betteryeah.com)** 云端统一代理，无需大家进行额外 KEY 的配置、Proxy 等操作，开箱即用，灵活切换。

知识库模块，**[BetterYeah AI 应用开发平台](https://ai.betteryeah.com)** 提供了非常成熟友好的产品功能，将繁琐的文件解析、文件拆分、向量化等操作在云端统一处理，用户侧无需关心复杂的文件处理过程，**BetterYeah** 中只需要一键调用即可使用完整完善的知识库能力。

数据库模块，**[BetterYeah AI 应用开发平台](https://ai.betteryeah.com)** 托管了一个在线的数据库，可以方便自由的数据存储，让你的 AI 更容易得具备持久化记忆的能力，得益于在线数据库的可视化操作，可以更直观的看到你的 AI “记住了什么”。

技能插件模块，**BetterYeah** 中内置了国内常用的 `数据解析` `网络搜索` `图像处理` `抖音` `小红书` `微博` 等几十个常用能力，助力你的业务飞速落地。

开发框架详细文档，请参考[帮助文档](https://xq5s55765m8.feishu.cn/wiki/YatVwh6EXid2Qyk0iGOcPQBHnwg?fromScene=spaceOverview#KKpddJBOroKIwxxIBHNcfqZInLb)

## 🌩 快速开始

**第一步：点击[https://ai.betteryeah.com](https://ai.betteryeah.com)注册BetterYeah AI 应用开发平台**

**第二步：获取 API_KEY**，登录 **[BetterYeah AI 应用开发平台](https://ai.betteryeah.com)**，按照用户指引新建工作空间后，在下图位置找到 API_KEY。

![获取密钥](https://resource.bantouyan.com/betteryeah/sdk/sdk_key.png)

**第三步：实例化**

可以直接在实例化的构造函数中传入 API_KEY。

```python
from betteryeah import BetterYeah

better_yeah = BetterYeah(api_key = "API_KEY")
```

也可以将 API_KEY 设置到环境变量中，此时构造函数就无需传入 API_KEY

如下：

```python
import os
from betteryeah import BetterYeah

os.environ['API_KEY'] = "xxx"
better_yeah = BetterYeah()  # 此时，SDK会从环境变量中获取相关KEY，但是需要你在运行时将.env文件加载到环境变量中(比如使用dotenv库)
print(better_yeah)
```

> **后续的示例代码默认以环境变量的方式实例化**

**第四步，使用**

通过使用一个 LLM 演示

```python
import asyncio
from betteryeah import BetterYeah, Model
better_yeah = BetterYeah(api_key="API_KEY")

result = asyncio.run(better_yeah.llm.chat(
    '中国的汉朝有几位皇帝',
    json_mode=False,
    model=Model.gpt_3_5_turbo,
    messages=[],
    temperature=0.0
))
print(result)
```

BetterYeah的完整功能，请参考[帮助文档](https://xq5s55765m8.feishu.cn/wiki/YatVwh6EXid2Qyk0iGOcPQBHnwg?fromScene=spaceOverview#KKpddJBOroKIwxxIBHNcfqZInLb)
