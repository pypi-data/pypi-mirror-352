# ========================== CONSTANT IMPORTS ==========================
import os
from dotenv import load_dotenv
from azure.identity import UsernamePasswordCredential
from recall_space_agents.hierarchical_agents.realized_workers.email_manager import (
    EmailManager,
)
from recall_space_agents.hierarchical_agents.realized_workers.todo_manager import (
    TodoManager,
)
from recall_space_agents.hierarchical_agents.realized_workers.site_manager import SiteManager
from recall_space_agents.hierarchical_agents.realized_workers.site_workbook_manager import SiteWorkbookManager
from recall_space_agents.hierarchical_agents.supervisor import Supervisor
from recall_space_agents.hierarchical_agents.application_graph import ApplicationGraph
from langchain_openai import AzureChatOpenAI
from zoneinfo import ZoneInfo
from datetime import datetime
from langsmith import traceable
from langgraph.graph import MessagesState
from langgraph.types import Command, interrupt
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


# ========================== CONSTANT CONFIGURATION ==========================
load_dotenv()

# Authenticate using Azure UsernamePasswordCredential. This provides credentials
# required for interacting with protected user configured resources (e.g., TODO list, emails).
# This allows the system to already interact with the user's system
credentials = UsernamePasswordCredential(
    client_id=os.getenv("CLIENT_ID"),
    authority=os.getenv("MS_AUTHORITY"),
    tenant_id=os.getenv("TENANT_ID"),
    username=os.getenv("LISA_USER_NAME"),
    password=os.getenv("LISA_PASSWORD"),
)

# Initialize the language model interface with specified parameters.
# This model is used by workers for NLP tasks like understanding instructions or generating text.
llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
    temperature=0,  # Deterministic output.
)

# ========================== WORKER SETUP ==========================
# Define workers here. Each worker encapsulates functionality for a specific task.
email_manager = EmailManager(llm=llm, credentials=credentials)
todo_manager = TodoManager(llm=llm, credentials=credentials)
site_manager = SiteManager(llm=llm, credentials=credentials)
site_workbook_manager = SiteWorkbookManager(llm=llm, credentials=credentials)

# Configure appropriate workers for the tasks
workers = [ email_manager, ]

# ========================== SUPERVISOR & APPLICATION GRAPH ==========================
# Supervisor orchestrates the workflow and plans tasks before execution.
supervisor = Supervisor(llm=llm, workers=workers, require_plan=True)

# ApplicationGraph defines the hierarchical execution logic for the workflow.
application_graph = ApplicationGraph(supervisor)

# Compile the application graph into an executable workflow.
hierarchical_application = application_graph.get_compiled_graph()

class SampleAppState(MessagesState):
    request_human_input: bool
    user_name: str



# ========================== WORKFLOW EXECUTION TEMPLATE ==========================
@traceable(name="<trace-project-name>", project_name="<trace-project-name>")
# NOTE: data is only included when the trigger is Http Type.
# The data would consist of input params defined by input_signature.
async def main(data: dict):
    """
    Main entry point for executing the workflow.

    Parameters:
        data (dict): Input parameters needed to drive the workflow.
    """


    # ========================== INPUT LOGIC ==========================
    # Extract the required input fields from data (For Http Trigger Workflows)
    # Define the state and instructions.
    # Modify `messages` for supervisor to include the specific steps or instructions for the workflow.
    # The `Supervisor` utilizes the workers to achieve the workflow objective.
    state = {
        "messages": [
            """
            Instructions:
            
            1. Task 1 description.
            2. Task 2 description.
            3. Task 3 description.

            Add additional instructions as required.
            """,
        ],
    }
    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
    }
    async with AsyncConnectionPool(
        # Example configuration
        conninfo=os.getenv('CHAT_DB_ENTRA_ID_CONNECTION_STRING'),
        max_size=10,
        kwargs=connection_kwargs,
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        application = application_graph.get_compiled_graph()


    # CHAT_DB_ENTRA_ID_CONNECTION_STRING
    # ========================== EXECUTE WORKFLOW ==========================
    response = await workflow_graph.ainvoke(state)

    # Return the response for logging or further processing.
    return response
