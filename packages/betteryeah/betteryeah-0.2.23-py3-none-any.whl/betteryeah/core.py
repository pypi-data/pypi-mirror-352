from typing import Optional
from betteryeah.api_client import ApiClient
from betteryeah.database import DatabaseClient
from betteryeah.knowledge import KnowledgeClient
from betteryeah.llm import LLMClient
from betteryeah.plugin import PluginClient
from betteryeah.sub_flow import FlowClient, SubFlowClient
from betteryeah.plugin.knowledgeqa import KnowledgeQAClient

class BetterYeah:
    def __init__(self, api_key: Optional[str] = None, workspace_id: Optional[str] = None):
        self.api_client = ApiClient(api_key, workspace_id)
        self.database = DatabaseClient(self.api_client)
        self.knowledge = KnowledgeClient(self.api_client)
        self.llm = LLMClient(self.api_client)
        self.plugin = PluginClient(self.api_client)
        self.sub_flow = SubFlowClient(self.api_client)
        self.flow = FlowClient(self.api_client)
        self.knowledgeqa = KnowledgeQAClient(self.api_client)