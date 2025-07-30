from langgraph.prebuilt.chat_agent_executor import AgentState
from typing import Any

class State(AgentState):
    # NOTE: we're adding this key to keep track of previous summary information
    # to make sure we're not summarizing on every LLM call
    context: dict[str, Any]