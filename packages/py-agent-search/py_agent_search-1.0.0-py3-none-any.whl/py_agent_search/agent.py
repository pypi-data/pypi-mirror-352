import uuid

from typing import Any, AsyncGenerator
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langmem.short_term import SummarizationNode
from langchain_core.messages.utils import count_tokens_approximately
from langchain.agents import Tool
from langgraph.graph.graph import CompiledGraph
from langchain_core.runnables import RunnableConfig
from langmem import (
    # Lets agent create, update, and delete memories 
    create_manage_memory_tool,
)
from .tools import search_tool, wikipedia_tool, youtube_tool
from .memory import AsyncRedisSaver, store
from .state import State
from .log import send_log
from .stream import StreamingCallbackHandler
from .prompt import prompt

class AgentSearch:
    
    model_name: str = "gpt-4.1-mini"
    handler = StreamingCallbackHandler()
    model : Any = None
    streaming : bool = True
    verbose : bool = True
    temperature : float = 0
    max_iterations: int = 10
    recursion_limit: int = 21  # 2 * max_iterations + 1
    agent : CompiledGraph
    redis_persistence_config: dict = {
        "host": "localhost",
        "port": 6379,
        "db": 0
    }
    debug : bool = False
    
    def __init__(self, model_name: str = "gpt-4.1-mini", **kwargs):
        """
        Initializes the AgentSearch with a specified model name and configuration options.
        Args:
            model_name (str): The name of the language model to use.
            **kwargs: Additional configuration options for the agent, such as streaming, verbose, temperature:
                - model (Any): The language model to use (Default ChatOpenAI with specified parameters).
                - model_name (str): The name of the model to use (Default "gpt-4.1-mini").
                - streaming (bool): Whether to stream responses from the model (Default True).
                - verbose (bool): Whether to enable verbose logging (Default True).
                - temperature (float): The temperature setting for the model's responses (Default 0).
                - max_completion_tokens (int): The maximum number of tokens for the model's completion (Default 2048).
                - max_iterations (int): The maximum number of iterations for the agent (Default 10).
                - redis_persistence_config (dict): Configuration for Redis persistence, including host, port, and db:
                    Example:
                    redis_persistence_config = {
                        "host": "localhost",
                        "port": 6379,
                        "db": 0
                    }
                - debug (bool): Whether to enable debugging mode (Default False).
        Raises:
            ValueError: If the model_name is not provided or is empty.
            TypeError: If the agent is not a CompiledGraph instance.
        """
        self.model_name = model_name
        self.streaming = kwargs.get("streaming", self.streaming)
        self.verbose = kwargs.get("verbose", self.verbose)
        self.temperature = kwargs.get("temperature", self.temperature)
        self.max_iterations = kwargs.get("max_iterations", self.max_iterations)
        self.recursion_limit = 2 * self.max_iterations + 1
        self.redis_persistence_config = kwargs.get("redis_persistence_config", self.redis_persistence_config)
        self.debug = kwargs.get("debug", self.debug)
    
        self.model = kwargs.get("model", ChatOpenAI(
            streaming=self.streaming, 
            verbose=self.verbose, 
            model=self.model_name, 
            callbacks=[self.handler],
            temperature=self.temperature
        ))
        
        self.agent = self._create_agent()
        
    def _summarization_node(self, model: Any) -> SummarizationNode:
        """
        Creates and returns a SummarizationNode configured with the specified model and token counting function.

        Args:
            model (Any): The language model to be used by the SummarizationNode.

        Returns:
            SummarizationNode: An instance of SummarizationNode initialized with the provided model, token counter,
            maximum token limits, and output messages key.
        """
        return SummarizationNode( 
            token_counter=count_tokens_approximately,
            model=self.model,
            max_tokens=384,
            max_summary_tokens=128,
            output_messages_key="llm_input_messages",
        )
        
    def _create_agent(self) -> CompiledGraph:
        """
        Creates and configures a CompiledGraph agent with specified model, tools, and settings.

        Returns:
            CompiledGraph: An agent instance initialized with the provided model, tools, state schema, checkpointer, store, and configuration options.

        The agent is set up with:
            - A list of tools (search, Wikipedia, YouTube).
            - A pre-model hook for summarization.
            - State schema, checkpointer, and store for state management.
            - Versioning and debugging options.
            - A recursion limit applied via configuration.
        """

        # Create the agent with the specified model and tools
        return create_react_agent(
            self.model,
            prompt=prompt,
            tools=[create_manage_memory_tool(namespace=("memories",)), 
                   search_tool, 
                   wikipedia_tool, 
                   youtube_tool],
            pre_model_hook=self._summarization_node,
            state_schema=State,
            version="v2",
            debug=self.debug,
            store=store
        )
        
    def get_graph(self) -> bytes:
        """
        Returns a PNG image of the agent's graph in Mermaid format.
        This method generates a visual representation of the agent's graph,
        which can be useful for debugging or understanding the agent's structure.
        :return: A PNG image of the agent's graph.
        """
        if not hasattr(self, 'agent'):
            self.agent = self._create_agent()
            
        if not isinstance(self.agent, CompiledGraph):
            raise TypeError("Agent must be a CompiledGraph instance.")
        
        return self.agent.get_graph().draw_mermaid_png()
        
    def _create_config(self, thread_id: str) -> RunnableConfig:
        """
        Create a configuration dictionary with the given thread ID.

        Args:
            thread_id (str): The unique identifier for the thread.

        Returns:
            dict: A dictionary containing the configuration with the thread ID.
            :param thread_id:
            :param recursion_limit:  
            :param tools: 
            :param headers: 
            :param metadata:  
        """
        
        if not thread_id:
            raise ValueError("Thread ID is required.")
        
        if not isinstance(thread_id, str):
            raise ValueError("Thread ID must be a string.")
        
        config : RunnableConfig = {
            "configurable": {
                "thread_id": thread_id
            },
            "recursion_limit": self.recursion_limit,
        }
        
        return config
    
    async def stream(self, input: str, thread_id: str = str(uuid.uuid4())) -> AsyncGenerator[str, None]:
        """
        Streams the response from the agent based on the provided input.
        This method allows for real-time interaction with the agent, streaming tokens as they are generated.

        :param input: The input string to process.
        :return: An async generator yielding responses from the agent.
        """
        if not hasattr(self, 'agent'):
            self.agent = self._create_agent()

        if not isinstance(self.agent, CompiledGraph):
            raise TypeError("Agent must be a CompiledGraph instance.")

        async with AsyncRedisSaver.from_conn_info(
            host=self.redis_persistence_config["host"],
            port=self.redis_persistence_config["port"],
            db=self.redis_persistence_config["db"]
        ) as checkpointer:
            
            self.agent.checkpointer = checkpointer

            input_message = {
                "messages": [{"role": "user", "content": input}]
            } 

            async for chunk in self.agent.astream(
                input=input_message,
                stream_mode="updates",
                interrupt_before=["tool"],
                config=self._create_config(thread_id=thread_id),
            ):
                
                response = None

                if "agent" in chunk and "messages" in chunk["agent"]:
                    response = chunk["agent"]["messages"][-1].content

                if response:
                    send_log(message=input, metadata=chunk)
                    yield response
        
        