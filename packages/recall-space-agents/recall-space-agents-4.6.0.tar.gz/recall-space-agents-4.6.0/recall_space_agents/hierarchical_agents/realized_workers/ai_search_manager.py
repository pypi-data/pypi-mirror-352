"""
Module that defines the AiSearchManager class, a worker that manages AI Search tasks.

This module provides the AiSearchManager class, which extends the Worker class.
AiSearchManager uses a language model and MSAISearchToolKit to perform search-related tasks
as part of a hierarchical agent system.
"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from recall_space_agents.hierarchical_agents.worker import Worker
from recall_space_agents.toolkits.ms_ai_search.ms_ai_search_toolkit import MSAISearchToolKit
from typing import Literal
from textwrap import dedent




class AiSearchManager(Worker):
    """AiSearchManager class that handles AI Search-related tasks.

    The AiSearchManager is a worker agent that uses a language model and search tools
    to perform tasks like indexing documents, searching content, etc. 
    It interacts with a supervisor agent in a hierarchical agent system.
    """

    def __init__(self, llm, ai_search_base_url: str, ai_search_api_key: str, index_name: str, embeddings_url: str, embeddings_api_key:str):
        """Initialize the AiSearchManager with an LLM and search-related credentials.
        """
        self.llm = llm
        self.tools = MSAISearchToolKit(
            ai_search_base_url=ai_search_base_url,
            ai_search_api_key=ai_search_api_key,
            index_name=index_name,
            embeddings_url=embeddings_url,
            embeddings_api_key=embeddings_api_key
        ).get_tools()
        self._agent_name = "ai_search_manager"

        # Updated system_prompt to include MEMORY_MANAGER_AGENT_PROMPT
        self.system_prompt = dedent(f"""
        As the worker agent named {self._agent_name}, you are also responsible for:
        - Storing, retrieving, and deleting important information (memories) so the system can learn, adapt, and improve.
        - Performing vector-based and text-based searches on these memories for conceptual or keyword matches.
        - Providing thorough and precise responses about search operations and memory management.
        - Ensuring that all indexing, document manipulation, and memory operations are seamlessly integrated to support continuous learning.

        Always returned a summary of what you have learnt.
        """)

        self.extracted_tool_description = "\n + ".join(
            [tool.description for tool in self.tools]
        )
        self.agent = create_react_agent(
            self.llm,
            tools=self.tools,
            state_modifier=self.system_prompt,
        )

    @property
    def agent_name(self):
        """Get the name of the agent.

        Returns:
            str: The agent's name.
        """
        return self._agent_name

    async def get_worker_node(self, state: MessagesState) -> Command[Literal["supervisor"]]:
        """Process the worker node in the conversation graph.

        The worker processes the last message from the supervisor and responds accordingly.
        It is only aware of the supervisor's command, not the full state of messages.

        Args:
            state (MessagesState): The current state of the conversation messages.

        Returns:
            Command[str]: The command indicating the next agent (usually the supervisor)
            and any updates to the messages.
        """
        try:
            response = await self.agent.ainvoke(
                {"messages": [("user", state["messages"][-1].content)]}
            )
        except Exception as error:
            response = {
                "messages": [
                    AIMessage(
                        content=(
                            f"Execution failed due to the following error:\n"
                            f"{str(error)}\n"
                            "Hint: Try to reformulate the task or check the request parameters."
                        )
                    )
                ]
            }
        return Command(
            goto="supervisor",
            update={
                "messages": [
                    AIMessage(
                        content=response["messages"][-1].content,
                        name=self.agent_name
                    )
                ]
            },
        )