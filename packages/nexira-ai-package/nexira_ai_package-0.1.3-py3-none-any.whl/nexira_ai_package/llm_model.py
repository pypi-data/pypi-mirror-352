from nexira_ai_package.app_config import app_config
from langchain_openai import ChatOpenAI
import os

class Model:
    def __init__(self, prompt):
        os.environ["OPENAI_API_KEY"] = app_config.OPENAI_API_KEY or "none"
        self.llm_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    async def invoke(self, input: dict) -> str:
        return await self.content_creator.ainvoke(input)
