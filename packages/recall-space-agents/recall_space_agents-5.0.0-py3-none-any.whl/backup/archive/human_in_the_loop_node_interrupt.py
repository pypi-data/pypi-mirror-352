import os
import uuid
from datetime import datetime
from typing import Literal

import pytz
from azure.identity import UsernamePasswordCredential
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.errors import NodeInterrupt
from langgraph.graph import (
    END,
    START,
    MessagesState,
    StateGraph,
)
from langgraph.types import Command
from langsmith import traceable
from psycopg_pool import AsyncConnectionPool

from recall_space_agents.hierarchical_agents.application_graph import (
    ApplicationGraph,
)
from recall_space_agents.hierarchical_agents.realized_workers.email_manager import (
    EmailManager,
)
from recall_space_agents.hierarchical_agents.realized_workers.todo_manager import (
    TodoManager,
)
from recall_space_agents.hierarchical_agents.realized_workers.site_manager import (
    SiteManager,
)
from recall_space_agents.hierarchical_agents.realized_workers.site_workbook_manager import (
    SiteWorkbookManager,
)
from recall_space_agents.hierarchical_agents.supervisor import Supervisor
from recall_space_agents.toolkits.chat_db.chat_db import ChatDbToolKit
from recall_space_agents.utils.get_authenticated_entra_id_connection_string import (
    get_authenticated_entra_id_connection_string,
)

# ========================== CONSTANT CONFIGURATION ==========================
load_dotenv()

# Authenticate using Azure UsernamePasswordCredential. This provides credentials
# required for interacting with protected user configured resources
# (e.g., TODO list, emails). This allows the system to interact with the user's
# system securely.
credentials = UsernamePasswordCredential(
    client_id=os.getenv("CLIENT_ID"),
    authority=os.getenv("MS_AUTHORITY"),
    tenant_id=os.getenv("TENANT_ID"),
    username=os.getenv("LISA_USER_NAME"),
    password=os.getenv("LISA_PASSWORD"),
)

# Initialize the language model interface with specified parameters.
# This model is used by workers for NLP tasks like understanding instructions
# or generating text.
llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
    temperature=0,  # Deterministic output.
)

# Get authenticated connection strings for chat database and checkpointers.
chat_db_connection_string = get_authenticated_entra_id_connection_string(
    os.getenv("CHAT_DB_ENTRA_ID_CONNECTION_STRING")
)
checkpointers_db_connection_string = get_authenticated_entra_id_connection_string(
    f"{os.getenv('CHAT_DB_ENTRA_ID_CONNECTION_STRING')}-checkpointers"
)

# ========================== WORKER SETUP ==========================
# Define workers here. Each worker encapsulates functionality for a specific task.
email_manager = EmailManager(llm=llm, credentials=credentials)
todo_manager = TodoManager(llm=llm, credentials=credentials)
site_manager = SiteManager(llm=llm, credentials=credentials)
site_workbook_manager = SiteWorkbookManager(llm=llm, credentials=credentials)

# Configure appropriate workers for the tasks.
workers = [
    email_manager,
    # Add other workers as needed.
]

# ========================== SUPERVISOR & APPLICATION GRAPH ==========================
# Supervisor orchestrates the workflow and plans tasks before execution.
supervisor = Supervisor(llm=llm, workers=workers, require_plan=False)

# ApplicationGraph defines the hierarchical execution logic for the workflow.
supervisor_app = ApplicationGraph(supervisor).get_compiled_graph()

# Initialize the chat database toolkit.
chat_db_tool_kit = ChatDbToolKit(chat_db_connection_string)


class SampleAppState(MessagesState):
    """
    Extends MessagesState to include additional state variables required
    for the application.

    Attributes:
        request_human_input_flag (bool): Flag to indicate if human input is required.
        user_name (str): Name of the user.
        thread_id (str): Identifier for the chat thread.
        accountable_user_id (str): User ID of the accountable user.
        reviewer_response (str): Response from the reviewer.
    """

    request_human_input_flag: bool = False
    user_name: str = ""
    # This key is always required. When user input is needed, the user
    # specified by this key will receive the request for input via chat session.
    thread_id: str = ""
    accountable_user_id: str = ""
    reviewer_response: str = ""


def request_human_input(
    state,
) -> Command[Literal["delegate_to_supervisor_app", "delegate_to_email_manager_directly"]]:
    """
    Node function to request human input when required.

    Parameters:
        state (dict): The current state of the application.

    Returns:
        Command: Next command to execute, along with updates to the state.

    Raises:
        NodeInterrupt: If human input is required and not yet provided.
    """
    next_node = "delegate_to_email_manager_directly"
    messages = [
        (
            "user",
            f"""
            Check if there are unread emails from '{state['user_name']}'.
            If there are:
                - Summarize its content.
            Else:
                - Do nothing.
            """,
        )
    ]
    if state["request_human_input_flag"] is True:
        if state["reviewer_response"] == "":
            raise NodeInterrupt(
                "Reviewer, who should perform the job? Supervisor or the email manager"
            )

    if "supervisor" in state["reviewer_response"].lower():
        next_node = "delegate_to_supervisor_app"
    return Command(
        goto=next_node,
        update={"messages": messages},
    )


# Build the state graph for the application workflow.
builder = StateGraph(SampleAppState)
builder.add_edge(START, "request_human_input")
builder.add_node("request_human_input", request_human_input)
builder.add_node("delegate_to_supervisor_app", supervisor_app)
builder.add_node("delegate_to_email_manager_directly", email_manager.agent)
builder.add_edge("delegate_to_supervisor_app", END)
builder.add_edge("delegate_to_email_manager_directly", END)

# Connection configuration for the database.
connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

workflow_graph = builder.compile()

# ========================== WORKFLOW EXECUTION TEMPLATE ==========================
@traceable(name="human_in_the_loop_node_interrupt", project_name="human_in_the_loop_node_interrupt")
async def main(data: dict):
    """
    Main entry point for executing the workflow.

    Parameters:
        data (dict): Input parameters needed to drive the workflow.

    Returns:
        Response from the workflow execution.
    """
    # Extract state variables from input data.
    request_human_input_flag = data.get("request_human_input_flag") or False
    user_name = data.get("user_name") or ""
    thread_id = data.get("thread_id") or ""
    accountable_user_id = data.get("accountable_user_id") or ""
    reviewer_response = data.get("reviewer_response") or ""

    # Initialize state with extracted variables.
    messages = []
    state = {
        "request_human_input_flag": request_human_input_flag,
        "user_name": user_name,
        "thread_id": thread_id,
        "accountable_user_id": accountable_user_id,
        "reviewer_response": reviewer_response,
        "messages": messages,
    }

    # Create a connection pool for the database.
    async with AsyncConnectionPool(
        conninfo=checkpointers_db_connection_string,
        max_size=5,
        kwargs=connection_kwargs,
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        # Note: Uncomment the line below if running for the first time to setup the checkpointer.
        # await checkpointer.setup()

        if thread_id == "" and state["request_human_input_flag"] is True:
            # New execution requiring human input. Assign a new thread ID.
            workflow_graph = builder.compile(checkpointer=checkpointer)
            thread_id = f"human_in_the_loop_node_interrupt:{str(uuid.uuid4())}"
            config = {"configurable": {"thread_id": thread_id}}
            response = await workflow_graph.ainvoke(input=state, config=config)

            # Emit a message to alert the accountable user that input is required.
            german_timezone = pytz.timezone("Europe/Berlin")
            now_in_germany = datetime.now(german_timezone)
            now_in_germany_str = now_in_germany.strftime("%Y-%m-%d %H:%M:%S %Z%z")

            new_chat_id = await chat_db_tool_kit.asave_chat(
                user_id=state["accountable_user_id"],
                title=f"Call to action {now_in_germany_str}",
            )
            await chat_db_tool_kit.asave_message(
                chat_id=new_chat_id,
                role="assistant",
                content=f"""
                Hi, who should continue the workflow—the Supervisor or the
                email manager? Please note that the Supervisor can generate
                an execution plan. To resume the execution use
                thread_id: {thread_id}
                """,
            )

        elif thread_id != "":
            # Existing execution resuming after human input.
            workflow_graph = builder.compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": thread_id}}
            await workflow_graph.aupdate_state(
                config=config, values={"reviewer_response": reviewer_response}
            )
            response = await workflow_graph.ainvoke(None, config=config)

            # Clean up execution data from the checkpoint tables.
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "DELETE FROM public.checkpoint_blobs WHERE thread_id = %s;",
                        (thread_id,),
                    )
                    await cur.execute(
                        "DELETE FROM public.checkpoint_writes WHERE thread_id = %s;",
                        (thread_id,),
                    )
                    await cur.execute(
                        "DELETE FROM public.checkpoints WHERE thread_id = %s;",
                        (thread_id,),
                    )
        else:
            # Standard execution without human input required.
            workflow_graph = builder.compile()
            response = await workflow_graph.ainvoke(input=state)

        # Return the response for logging or further processing.
        return response