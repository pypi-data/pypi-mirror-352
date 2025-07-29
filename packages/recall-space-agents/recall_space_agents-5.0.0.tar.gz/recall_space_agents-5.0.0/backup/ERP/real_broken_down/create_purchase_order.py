"""Place Purchase Order Skill.

This module defines a skill that takes a single PurchaseOrder,
requires manager approval, and finally places the PurchaseOrder.
"""

import json
import aiohttp
import logging
import os
from textwrap import dedent
from typing import Literal, TypedDict

from azure.identity import UsernamePasswordCredential
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langgraph.errors import NodeInterrupt
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from langsmith import traceable

from recall_space_agents.toolkits.ms_bot.ms_bot import MSBotToolKit
from recall_space_agents.utils.workflow_execution_management import (
    WorkflowExecutionManagement,
)
from recall_space_utils.connectors.lisa.lisa_connector import LisaConnector
from recall_space_agents.utils.azure_quere_handler import AzureQueueHandler
from recall_space_agents.hierarchical_agents.realized_workers.master_data_erp_manager import MasterDataERPManager
from recall_space_utils.recall_space_erp.inventory_overview import InventoryOverview

# ========================== CONSTANT CONFIGURATION ==========================
load_dotenv()

# ERP Credentials Recall Space App
BASE_URL = "https://erp.greenwave-c759a37d.northeurope.azurecontainerapps.io"
USER_NAME = "Lisa"
PASSWORD = "GoLisa2025"
LISA_API = os.getenv("LISA_API")
API_KEY = os.getenv("API_KEY")
# Manager's Info (Replace with the actual manager's name)
#MANAGER_NAME = "Titus Lottig"
MANAGER_NAME = "Gari Jose Ciodaro Guerra"

workflow_flow_name = "Create Purchase Order"


class WorkflowState(TypedDict):
    supplierId: int
    materialId: int
    quantity: float
    unitOfMeasure: str
    shipToLocationId: int
    orderDate: str
    status: str
    requestedDeliveryDate: str
    confirmedDeliveryDate: str
    metadata:dict
    thread_id: str
    reviewer_response: str

# Enqueuer for human-in-the-loop pending workflows
pending_workflows_enqueuer = AzureQueueHandler(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="pending-workflows",
)

# Enqueuer for node step execution messages to Azure Functions queue
azure_functions_enqueuer = AzureQueueHandler(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="azure-functions-queue",
)

# Workflow execution management with message enqueuer
workflow_execution_management = WorkflowExecutionManagement(
    db_connection_string=os.getenv("CHECKPOINTERS_DB_URL"),
    message_enqueuer=azure_functions_enqueuer,
)

credentials = UsernamePasswordCredential(
    client_id=os.getenv("CLIENT_ID"),
    authority=os.getenv("MS_AUTHORITY"),
    tenant_id=os.getenv("TENANT_ID"),
    username=os.getenv("LISA_USER_NAME"),
    password=os.getenv("LISA_PASSWORD"),
)

workflow_llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
)

# Initialize the MSBotToolkit
bot_toolkit = MSBotToolKit(
    credentials=credentials,
    bot_id=os.getenv("BOT_ID"),
    direct_line_secret=os.getenv("DIRECT_LINE_SECRET"),
)

# Workaround retry caused by node interrupt
# flag_notification_sent = False


async def get_purchase_order_metadata(state):
    logging.error("in get_purchase_order_metadata")
    async with InventoryOverview(BASE_URL, USER_NAME, PASSWORD) as inventory_overview:
        logging.error("Fetching data")
        await inventory_overview.fetch_data()

    supplier_object = inventory_overview.get_supplier_by_id(state["supplierId"])
    material_object = inventory_overview.get_material_by_id(state["materialId"])
    location_object = inventory_overview.get_location_by_id(state["shipToLocationId"])
    if supplier_object == "object not found":
        raise NodeInterrupt("supplierId is invalid or was not found.")
    if material_object == "object not found":
        raise NodeInterrupt("materialId is invalid or was not found.")
    if location_object == "object not found":
        raise NodeInterrupt("shipToLocationId is invalid or was not found.")
    
    state["metadata"] = {
        "supplier_email":supplier_object["contactInfo"].split(",")[0],
        "supplier_name":supplier_object["name"],
        "material_name":material_object["name"],
        "location_name":location_object["name"]
        }
    return state



async def notify_manager(state) -> Command[Literal["Create Purchase Order", "__end__"]]:

    logging.error("Executing notify_manager node.")

    # Check if reviewer_response is empty
    if state["reviewer_response"] == "":
        # Enqueue message for human-in-the-loop
        enqueu_message_dict = {
            "thread_id": state["thread_id"],
            "workflow_flow_name": workflow_flow_name,
            "editable_state": {
                "reviewer_response": state["reviewer_response"],
                "supplierId": state["supplierId"],
                "materialId": state["materialId"],
                "shipToLocationId": state["shipToLocationId"],
                "orderDate": state["orderDate"],
                "unitOfMeasure": state["unitOfMeasure"]
            },
        }
        enqueu_message = json.dumps(enqueu_message_dict)

        # global flag_notification_sent
        # if flag_notification_sent is False:
        await pending_workflows_enqueuer.enqueue_message(
            enqueu_message, time_to_live=600, delay=0
        )
        message_markdown = dedent(
        f"""
        **Dear Manager,**

        You need to approve the placement of the following **purchase order**: 

        - **Supplier Name:** {state["metadata"]["supplier_name"]}
        - **Supplier Email:** {state["metadata"]["supplier_email"]}
        - **Material Name:** {state["metadata"]["material_name"]}
        - **location Name:** {state["metadata"]["location_name"]}
        - **Supplier ID:** {state["supplierId"]}
        - **Material ID:** {state["materialId"]}
        - **Quantity:** {state["quantity"]} - {state["unitOfMeasure"]}
        - **Ship To Location ID:** {state["shipToLocationId"]}
        - **Order Date:** {state["orderDate"]}
        - **Requested Delivery Date:** {state["requestedDeliveryDate"] or state["orderDate"]}
        - **Confirmed Delivery Date:** {state["confirmedDeliveryDate"] or state["requestedDeliveryDate"] or state["orderDate"]}
        - **Status:** {state["status"]}

        Request review for workflow run: {state["thread_id"]}
        """
        )
        logging.error(message_markdown)

        # Send the Teams message to the manager
        await bot_toolkit.asend_team_message_by_name(
            message=message_markdown,
            to_recipient_by_name=MANAGER_NAME,  # Manager's name
        )

        logging.error("Notification sent to the manager via Teams.")

        #flag_notification_sent = True

        # Pause the workflow
        raise NodeInterrupt("Waiting for manager's approval.")

    else:
        if "approve" in state["reviewer_response"]:
            response = {"decision":"CONTINUE"}
        else:
            class ProcessReviewerResponse(TypedDict):
                decision: Literal["END","CONTINUE"]

            input_prompt = f"""
            please review the following statement.
            ```
            {state["reviewer_response"]}
            ```
            This statement is a response from a reviewer regarding another process. 
            You need to analyze the semantic meaning of this statement in order to 
            determine the next steps: whether the process should continue, 
            or stop (if the reviewer denies).
            """

            response =  await workflow_llm.with_structured_output(
                ProcessReviewerResponse, strict=True).ainvoke(input_prompt)

        llm_decision = response.get("decision", "END")

        if "CONTINUE" in llm_decision:
            logging.error("Manager approved the purchase order.")
            return Command(goto="Create Purchase Order", update={})
        else:
            logging.error("Manager denied.")
            return Command(goto=END)
        



async def create_purchase_order(state):
    logging.info("Placing purchase orders.")


    async with aiohttp.ClientSession() as session:
        # Perform login
        login_url = f"{BASE_URL}/api/login"
        login_payload = {"username": USER_NAME, "password": PASSWORD}
        async with session.post(login_url, json=login_payload) as login_response:
            if login_response.status != 200:
                logging.error("Login failed.")
                return state
            else:
                logging.error("Login successful!")
                # Continue with placing purchase orders

        logging.info("Placing order...")
        logging.debug(f"Purchase order data: {state}")
        url = f"{BASE_URL}/api/purchase-orders"
        order_payload = {
            "supplierId": state["supplierId"],
            "materialId": state["materialId"],
            "quantity": state["quantity"],
            "unitOfMeasure": state["unitOfMeasure"],
            "shipToLocationId": state["shipToLocationId"],
            "orderDate": state["orderDate"],
            "status": state["status"],
            "requestedDeliveryDate": state["requestedDeliveryDate"] or state["orderDate"],
            "confirmedDeliveryDate": state["confirmedDeliveryDate"] or state["requestedDeliveryDate"] or state["orderDate"],
        }
        logging.error(f"Order payload: {order_payload}")
        async with session.post(url, json=order_payload) as response:
            if response.status == 201:
                logging.error("Purchase order placed successfully.")
                created_order = await response.json()
                order_id = created_order.get('id')
                logging.error(f"Purchase order placed successfully with ID: {order_id}")
                lisa_connector = LisaConnector(lisa_api=LISA_API,lisa_key=API_KEY)
                input_prompt = f"""
                Hi Lisa,

                Please send an email to the supplier ({state["metadata"]["supplier_email"]}) informing them 
                that the following purchase order needs to be fulfilled.

                Email template:

                ```
                <p>Dear <b>{state["metadata"]["supplier_name"]}</b>,</p>
                <p>I hope you are doing well. We have a purchase order for the following:</p>
                <ul>
                    <li><b>Order Id:</b> {order_id}</li>
                    <li><b>Material Name:</b> {state["metadata"]["material_name"]}</li>
                    <li><b>Ship-to:</b> {state["metadata"]["location_name"]}</li>
                    <li><b>Requested Delivery Date:</b> {state["requestedDeliveryDate"] or state["orderDate"]}</li>
                    <li><b>Quantity:</b> {state["quantity"]} - {state["unitOfMeasure"]}</li>
                </ul>
                <p>We kindly request that you fulfill this order on schedule. 
                If you need any further information or clarification, please feel free to let me know.</p>

                <p>Thank you for your cooperation.</p>

                <p>Best regards,</p>
                <b>Lisa AI</b>
                ```
                """
                logging.error(input_prompt)
                await lisa_connector.ask_question(input_prompt)
            else:
                error_text = await response.text()
                logging.error(
                    f"Failed to place purchase order. Status Code: {response.status}, "
                    f"Response: {error_text}"
                )
    return state


builder = StateGraph(WorkflowState)

builder.add_node("Get Purchase Order Metadata", get_purchase_order_metadata)
builder.add_node("Seek Manager's Approval", notify_manager)
builder.add_node("Create Purchase Order", create_purchase_order)

builder.add_edge(START, "Get Purchase Order Metadata")
builder.add_edge("Get Purchase Order Metadata", "Seek Manager's Approval")
builder.add_edge("Create Purchase Order", END)

workflow_graph = builder.compile()


@traceable(name="Create Purchase Order", project_name="Create Purchase Order")
async def main(data: dict):

    logging.error(f"Data received: {data}")
    input_state = {
        "supplierId": data.get("supplierId") or 0,
        "materialId": data.get("materialId") or 0,
        "quantity": data.get("quantity") or 0,
        "unitOfMeasure": data.get("unitOfMeasure") or "",
        "shipToLocationId": data.get("shipToLocationId") or 0,
        "orderDate": data.get("orderDate") or "",
        "status": data.get("status") or "In Progress",
        "requestedDeliveryDate": data.get("requestedDeliveryDate") or "",
        "confirmedDeliveryDate": data.get("confirmedDeliveryDate") or "",
        "metadata":data.get("metadata", {}),
        "thread_id": data.get("thread_id") or "",
        "reviewer_response": data.get("reviewer_response") or "",

    }

    # Normal execution
    if input_state["thread_id"] == "":
        logging.error("Starting new workflow execution.")

        run_response_in = await workflow_execution_management.run_workflow(
            graph_builder=builder,
            state=input_state,
            llm=workflow_llm,
            workflow_name=workflow_flow_name,
        )
        try:
            run_response = run_response_in[1]["__interrupt__"][0].value
        except:
            run_response = run_response_in

    # Resume execution, thread_id is required.
    elif input_state["thread_id"] != "" and input_state["reviewer_response"] != "":
        logging.error("Resuming workflow execution.")
        logging.error(f"Thread ID: {input_state['thread_id']}")
        logging.error(f"Resume input state: {input_state}")
        run_response = await workflow_execution_management.resume_workflow(
            thread_id=input_state["thread_id"],
            graph_builder=builder,
            resume_state={"reviewer_response": input_state["reviewer_response"]},
        )

    # Return the response for logging or further processing.
    return run_response