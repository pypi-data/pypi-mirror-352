from _typeshed import Incomplete
from gllm_agents.a2a.server.base_langchain_executor import BaseLangChainExecutor as BaseLangChainExecutor
from gllm_agents.agent.langgraph_agent import LangGraphAgent as LangGraphAgent
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete

class LangGraphA2AExecutor(BaseLangChainExecutor):
    """A2A Executor for serving a `LangGraphAgent`.

    This executor bridges the A2A server protocol with a `gllm_agents.agent.LangGraphAgent`.
    It handles incoming requests by invoking the agent's `arun_a2a_stream` method,
    processes the streamed dictionary chunks, and formats them into A2A compliant events.
    It leverages common functionality from `BaseA2AExecutor` for task management,
    initial request checks, and cancellation.

    Attributes:
        agent (LangGraphAgent): The instance of `LangGraphAgent` to be executed.
    """
    agent: LangGraphAgent
    def __init__(self, langgraph_agent_instance: LangGraphAgent) -> None:
        """Initializes the LangGraphA2AExecutor.

        Args:
            langgraph_agent_instance (LangGraphAgent): A fully initialized instance
                of `LangGraphAgent`.

        Raises:
            TypeError: If `langgraph_agent_instance` is not an instance of `LangGraphAgent`.
        """
