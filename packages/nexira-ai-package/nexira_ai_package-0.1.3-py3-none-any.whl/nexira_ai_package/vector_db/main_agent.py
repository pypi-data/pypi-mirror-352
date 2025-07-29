from nexira_ai_package.llm_model import Model
from nexira_ai_package.vector_db.memory_handler import MemoryHandler
from langgraph.prebuilt import create_react_agent   

class ReactAgent():
    def __init__(self, name: str, memory_handler: MemoryHandler):
        self.memory_handler = memory_handler
        self.name = name
        self.all_agents = {
            "mini_mavia_agent": 0,
            "block_clans_agent": 1,
            "standard_agent": 2
        }
        self.agent = self.create_llm_agent()
        max_iterations = 3
        recursion_limit = 1 * max_iterations + 1
        self.recursion = {"recursion_limit": recursion_limit}

    # Agent type 0: Mini Mavia
    # Agent type 1: Block Clans
    # Agent type 2: Standard
    def create_llm_agent(self):
        agent_type = self.all_agents[self.name]
        all_tools = self.memory_handler.get_search_tool()
        if agent_type < len(all_tools):
            tools = [all_tools[agent_type]]
        else:
            tools = all_tools

        tool_names = "and".join([tool.name for tool in tools])
        system_prompt =f"""
        You are a helpful assistant who answers questions using relevant document content retrieved via tools.
        Use the {tool_names} to retrieve document chunks related to the query.
        Base your answer on the retrieved content, citing specific details where relevant.
        """

        llm_model = Model(system_prompt)
        agent = create_react_agent(
            llm_model.llm_model,
            tools=tools,
            prompt=system_prompt
        )
        return agent

    def get_agent(self):
        return self.agent

    async def process_question_stream(self, query: str) -> list[str]:
        messages = {"messages": [{"role": "user", "content": query}]}
        chunks = []
        async for chunk in self.agent.astream(messages, self.recursion, stream_mode="updates"):
            chunks.append(chunk)
        return chunks
        
    async def process_question(self, query: str) -> str:
        messages = {"messages": [{"role": "user", "content": query}]}
        response = await self.agent.ainvoke(messages, self.recursion)
        return response["messages"][-1].content
