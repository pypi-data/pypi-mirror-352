"""
Module that defines the AzureBlobManager class, a worker agent to manage Azure Blob Storage tasks.

This module provides the AzureBlobManager class, which extends the Worker class.
AzureBlobManager uses a language model and the AzureBlobToolkit to perform file storage tasks
(listing blobs, reading file contents, reading pickled objects) as part of a hierarchical
or agent-based system.
"""

from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from recall_space_agents.hierarchical_agents.worker import Worker
from recall_space_agents.toolkits.azure_blob.azure_blob_toolkit import (
    AzureBlobToolkit,
)
from typing import Literal


class AzureBlobManager(Worker):
    """
    AzureBlobManager class that handles Azure Blob Storage-related tasks.

    The AzureBlobManager is a worker agent that uses an LLM and Azure Blob tools
    to perform tasks such as listing blobs, reading file contents, reading pickled objects, etc.
    It interacts with a supervisor agent in a hierarchical agent system.
    """

    def __init__(self, llm, connection_string: str, container_name: str):
        """
        Initialize the AzureBlobManager with an LLM, Azure Blob Storage connection string,
        and a container name.

        Args:
            llm: The language model to use for processing messages.
            connection_string: The Azure Storage account connection string.
            container_name: Name of the container to operate on.
        """
        self.llm = llm
        self.tools = AzureBlobToolkit(
            connection_string=connection_string, container_name=container_name
        ).get_tools()
        self._agent_name = "azure_blob_manager"
        self.system_prompt = f"You are a worker agent named {self._agent_name}."
        self.extracted_tool_description = "\n + ".join(
            [tool.description for tool in self.tools]
        )
        self.agent = create_react_agent(
            self.llm, tools=self.tools, state_modifier=self.system_prompt
        )

    @property
    def agent_name(self):
        """
        Get the name of the agent.

        Returns:
            str: The agent's name.
        """
        return self._agent_name

    async def get_worker_node(
        self, state: MessagesState
    ) -> Command[Literal["supervisor"]]:
        """
        Process the worker node in the conversation graph.

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
                        f"""
                Execution failed due to the following error:
                {str(error)}
                Hint: Try to reformulate the task. Sometimes, due to LLM provider or API policies,
                specific data formats or credentials may not be accepted.
                Try again using slightly different input or check permissions.
            """
                    )
                ]
            }
        return Command(
            goto="supervisor",
            update={
                "messages": [
                    AIMessage(
                        content=response["messages"][-1].content, name=self.agent_name
                    )
                ]
            },
        )
