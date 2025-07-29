from nexira_ai_package.vector_db.main_agent import ReactAgent
from fastapi import HTTPException, status
from typing import Dict

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, ReactAgent] = {}
        self.current_agent: str = None

    def add_agent(self, name: str, agent: ReactAgent):
        self.agents[name] = agent
        self.current_agent = name

    def get_agent(self, name: str = None) -> ReactAgent:        
        agent = self.agents.get(name)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Agent '{name}' not found. Please verify the agent name."
            )
        return agent

    def remove_agent(self, name: str):
        if name in self.agents:
            if name == self.current_agent:
                self.current_agent = None
            del self.agents[name]
            return True
        return False

    def set_current_agent(self, name: str):
        if name not in self.agents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{name}' not found"
            )
        self.current_agent = name
