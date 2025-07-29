"""
Module for handling inquiries about master data on ERP using a workflow script.

This module initializes the necessary components such as the LLM,
workers, supervisor, and workflow graph to process user inquiries
about master data in an ERP system.

It defines an asynchronous main function that takes user data
and returns an appropriate response after processing the workflow.
"""

import os
from recall_space_agents.hierarchical_agents.realized_workers.master_data_erp_manager import (
    MasterDataERPManager,
)
from langsmith import traceable
from recall_space_agents.hierarchical_agents.supervisor import Supervisor
from recall_space_agents.hierarchical_agents.application_graph import ApplicationGraph
from langchain_openai import AzureChatOpenAI
from recall_space_agents.utils.azure_quere_handler import AzureQueueHandler
from recall_space_agents.utils.workflow_execution_management import (
    WorkflowExecutionManagement,
)
from dotenv import load_dotenv

load_dotenv()

workflow_flow_name = "Erp Master Data Inquiries"


BASE_URL = "https://erp.greenwave-c759a37d.northeurope.azurecontainerapps.io"
USER_NAME = "Lisa"
PASSWORD = "GoLisa2025"

# Enqueuer for node step execution messages to Azure Functions queue
azure_functions_enqueuer = AzureQueueHandler(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="azure-functions-queue",
)

# Initialize LLM (Large Language Model)
llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
)

# Initialize the MasterDataERPManager worker
master_data_erp_manager = MasterDataERPManager(
    llm=llm,
    base_url=BASE_URL,
    username=USER_NAME,
    password=PASSWORD,
)

# Workers
workers = [master_data_erp_manager]

# Supervisor
supervisor = Supervisor(llm=llm, workers=workers, require_plan=False)

# Application graph
workflow_graph = ApplicationGraph(supervisor).get_compiled_graph()


@traceable(
    name="Erp Master Data Inquiries",
    project_name="Erp Master Data Inquiries",
)
async def main(data: dict):
    """
    Asynchronously handle an inquiry about master data on ERP.

    Args:
        data (dict): A dictionary containing the user's inquiry with key "inquiry".

    Returns:
        user_response:  "answer".
    """
    input_state = {
        "messages": [("user", data["inquiry"])],
    }
    response = await WorkflowExecutionManagement.astream_with_queue_workflow(
        message_enqueuer=azure_functions_enqueuer,
        compile_graph=workflow_graph,
        state=input_state,
        stream_mode="values",
    )

    user_response = response[-1]["messages"][-1].content

    return user_response