"""
Module that defines the DocumentIntelligenceManager class, a worker that manages
Azure Document Intelligence (OCR, document extraction) tasks.

Extends the Worker class for hierarchical agent workflows.
"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from recall_space_agents.hierarchical_agents.worker import Worker
from recall_space_agents.toolkits.ms_document_intelligence.ms_document_intelligence_toolkit import (
    AzureDocumentIntelligenceToolkit,
)
from typing import Literal
from textwrap import dedent


class DocumentIntelligenceManager(Worker):
    """Handles Azure Document Intelligence tasks within a hierarchical agent structure."""

    def __init__(self, llm, endpoint: str, key: str, return_raw: bool = False):
        """
        Initialize with LLM, Azure Document Intelligence endpoint/key, and output control.
        """
        self.llm = llm
        self.tools = AzureDocumentIntelligenceToolkit(
            endpoint=endpoint, key=key, return_raw=return_raw
        ).get_tools()
        self._agent_name = "document_intelligence_manager"

        self.system_prompt = dedent(
            f"""
        As the worker agent named {self._agent_name}, your responsibilities include:
        - Extracting text and reliable information from documents using OCR.
        - Providing content that is useful for downstream reasoning and summarization.
        - If multiple extraction methods (like invoice/receipt) are available, use the most relevant one.
        - Clearly summarize and report the detailed extracted content without leaking unnecessary technical details.
        """
        )

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
        return self._agent_name

    async def get_worker_node(
        self, state: MessagesState
    ) -> Command[Literal["supervisor"]]:
        """
        Handles the conversation node for the worker.
        Args:
            state (MessagesState): Conversation state/messages.
        Returns:
            Command: Next agent and updated message set.
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
                        content=response["messages"][-1].content, name=self.agent_name
                    )
                ]
            },
        )
