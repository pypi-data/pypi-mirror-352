from _typeshed import Incomplete
from gllm_agents.a2a.server.base_langchain_executor import BaseLangChainExecutor as BaseLangChainExecutor
from gllm_agents.agent.langchain_agent import LangChainAgent as LangChainAgent
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete

class LangChainA2AExecutor(BaseLangChainExecutor):
    """A2A Executor for serving a LangChainAgent.

    This executor bridges the A2A server protocol with a gllm_agents `LangChainAgent`.
    It handles incoming requests, invokes the agent's streaming capabilities,
    and formats the agent's output into A2A compliant events.
    """
    agent: LangChainAgent
    def __init__(self, langchain_agent_instance: LangChainAgent) -> None:
        """Initializes the LangChainA2AExecutor.

        Args:
            langchain_agent_instance: A fully initialized instance of LangChainAgent.
        """
