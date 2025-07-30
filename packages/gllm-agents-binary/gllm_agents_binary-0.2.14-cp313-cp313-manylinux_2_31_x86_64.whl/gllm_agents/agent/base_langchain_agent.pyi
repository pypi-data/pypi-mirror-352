import abc
from _typeshed import Incomplete
from a2a.types import AgentCard as AgentCard
from gllm_agents.agent.base_agent import BaseAgent as BaseAgent
from gllm_agents.utils.a2a_connector import A2AConnector as A2AConnector
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from langchain_core.messages import BaseMessage as BaseMessage
from langchain_core.tools import BaseTool as BaseTool
from typing import Any, Callable

logger: Incomplete

class BaseLangChainAgent(BaseAgent, metaclass=abc.ABCMeta):
    """Base class for langchain-based agents, providing common functions for LangGraphAgent and LangChainAgent.

    This class extends BaseAgent and provides additional functionality specific to langchain-based agents.
    The common functionality includes:
    - Extracting output from various state formats (dict, list)
    - Handling LangChain message types (AIMessage, ToolMessage)
    - Common state management for LangChain agents
    - Delegation tool creation for coordinator agents
    - Shared logic for rebuilding tools and agent executor
    """
    agents: Incomplete
    model: Incomplete
    def __init__(self, name: str, instruction: str, description: str | None = None, agents: list[Any] | None = None, tools: list[BaseTool] | None = None, model: Any | None = None, **kwargs: Any) -> None:
        """Initialize the BaseLangChainAgent.

        Args:
            name: The name of the agent
            instruction: The system instruction/prompt for the agent
            description: Optional description of the agent
            agents: Optional; list of LangChain/LangGraph agents. Defaults to None (no agents).
            tools: Optional; list of LangChain tools. Defaults to None (no tools).
            model: A LangChain LLM (e.g., ChatOpenAI).
            **kwargs: Additional keyword arguments passed to BaseAgent
        """
    def create_a2a_tool(self, agent_card: AgentCard) -> Callable:
        """Creates a LangGraph tool for A2A communication."""
    def register_a2a_agents(self, agent_cards: list[AgentCard]) -> None:
        """Convert known A2A agents to LangChain tools.

        This method takes the agents from a2a_config.known_agents, creates A2AAgent
        instances for each one, and wraps them in LangChain tools.

        Returns:
            None: The tools are added to the existing tools list.
        """
