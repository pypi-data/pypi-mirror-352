from betteryeah.api_client import ApiClient
from betteryeah.plugin.bilibili import BiliBiliClient
from betteryeah.plugin.douyin import DouyinClient
from betteryeah.plugin.generic import GenericClient
from betteryeah.plugin.image import ImageClient
from betteryeah.plugin.parsing import ParsingClient
from betteryeah.plugin.search import SearchClient
from betteryeah.plugin.toutiao import ToutiaoClient
from betteryeah.plugin.weibo import WeiboClient
from betteryeah.plugin.xiaohongshu import XiaohongshuClient
from betteryeah.plugin.zhihu import ZhihuClient
from betteryeah.plugin.knowledgeqa import KnowledgeQAClient

class PluginClient:
    def __init__(self, api_client: ApiClient):
        self.image = ImageClient(api_client)
        self.parsing = ParsingClient(api_client)
        self.search = SearchClient(api_client)
        self.xiaohongshu = XiaohongshuClient(api_client)
        self.zhihu = ZhihuClient(api_client)
        self.weibo = WeiboClient(api_client)
        self.bilibili = BiliBiliClient(api_client)
        self.toutiao = ToutiaoClient(api_client)
        self.douyin = DouyinClient(api_client)
        self.generic = GenericClient(api_client)
        self.knowledgeqa = KnowledgeQAClient(api_client)