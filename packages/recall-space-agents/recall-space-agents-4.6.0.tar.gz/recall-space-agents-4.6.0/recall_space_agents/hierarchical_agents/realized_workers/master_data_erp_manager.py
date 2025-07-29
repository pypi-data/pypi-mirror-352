"""
Module that defines the MasterDataERPManager class, a worker that manages master data ERP tasks.

This module provides the MasterDataERPManager class, which extends the Worker class.
MasterDataERPManager uses a language model and Master Data ERP Toolkit to perform ERP-related tasks
as part of a hierarchical agent system.
"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from recall_space_agents.hierarchical_agents.worker import Worker
from recall_space_agents.toolkits.master_data_erp.master_data_erp import MasterDataERPToolKit
from typing import Literal


class MasterDataERPManager(Worker):
    """MasterDataERPManager class that handles master data ERP-related tasks.

    The MasterDataERPManager is a worker agent that uses a language model and ERP tools
    to perform tasks like retrieving materials, locations, suppliers, etc.
    It interacts with a supervisor agent in a hierarchical agent system.
    """

    def __init__(self, llm, base_url, username, password, only_get_tools=False):
        """Initialize the MasterDataERPManager with an LLM and credentials.

        Args:
            llm: The language model to use for processing messages.
            base_url (str): The base URL of the ERP API.
            username (str): Username for authentication.
            password (str): Password for authentication.
            tool_set (str): fil
        """
        self.llm = llm
        self.credentials = {
            "base_url": base_url,
            "username": username,
            "password": password
        }
        self.toolkit = MasterDataERPToolKit(**self.credentials)
        if only_get_tools is True:
            get_tools = [each_tool for each_tool in self.toolkit.get_tools() if "aget" in each_tool.name]
            self.tools = get_tools
        else:
            self.tools = self.toolkit.get_tools() 
        self._agent_name = 'master_data_erp_manager'
        self.system_prompt = f"You are a worker agent named {self._agent_name}."
        self.extracted_tool_description = "\n + ".join(
            [tool.description for tool in self.tools]
        )
        self.agent = create_react_agent(
            self.llm,
            tools=self.tools,
            state_modifier=self.system_prompt
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
        # The worker is only aware of the supervisor command, not the full state of messages.
        try:
            response = await self.agent.ainvoke(
                {"messages": [("user", state["messages"][-1].content)]}
            )
        except Exception as error:
            response = {
                "messages": [AIMessage(content=f"""
                Execution failed due to the following error:
                {str(error)}
                Hint: Try to reformulate the task or check the input parameters.
                """)]}
        # Responds as a Human, so that its answer is taken as priority.
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