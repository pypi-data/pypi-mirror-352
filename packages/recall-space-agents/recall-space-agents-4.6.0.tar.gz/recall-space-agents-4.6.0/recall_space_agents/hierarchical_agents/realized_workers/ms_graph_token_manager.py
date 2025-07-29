"""
Module that defines the MsGraphTokenManager class, a worker that manages MS Graph token tasks.

This module provides the MsGraphTokenManager class, which extends the Worker class.
MsGraphTokenManager uses a language model and MsGraphTokenToolkit to perform token-related tasks
as part of a hierarchical agent system.
"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from recall_space_agents.hierarchical_agents.worker import Worker
from recall_space_agents.toolkits.ms_graph_token.ms_graph_token_toolkit import MsGraphTokenToolkit
from typing import Literal, Optional, List

class MsGraphTokenManager(Worker):
    """MsGraphTokenManager class that handles MS Graph token-related tasks.

    The MsGraphTokenManager is a worker agent that uses a language model and token tools
    to perform tasks like storing, retrieving, and generating tokens. It interacts with
    a supervisor agent in a hierarchical agent system.
    """

    def __init__(
        self, 
        llm, 
        keyvault_url: str,
        client_id: str,
        tenant_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: Optional[List[str]] = None
    ):
        """Initialize the MsGraphTokenManager with an LLM and Azure credentials.
        
        Args:
            llm: The language model to use
            keyvault_url (str): Azure Key Vault URL for storing tokens
            client_id (str): Azure Entra ID application client ID
            tenant_id (str): Azure Entra ID tenant ID
            client_secret (str): Azure Entra ID application client secret
            redirect_uri (str): OAuth2 redirect URI
            scope (list, optional): List of Microsoft Graph API scopes. Defaults to ["User.Read"]
        """
        self.llm = llm
        self.tools = MsGraphTokenToolkit(
            keyvault_url=keyvault_url,
            client_id=client_id,
            tenant_id=tenant_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        ).get_tools()
        self._agent_name = 'ms_graph_token_manager'
        self.system_prompt = f"You are a worker agent named {self._agent_name}. You manage MS Graph tokens."
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
        try:
            response = await self.agent.ainvoke(
                {"messages": [("user", state["messages"][-1].content)]}
            )
        except Exception as error:
            response = {"messages": [AIMessage(
                content=(
                    f"Execution failed due to the following error:\n"
                    f"{str(error)}\n"
                    "Hint: Try to reformulate the task or check the request parameters."
                )
            )]}
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
