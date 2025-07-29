"""Modify Purchase Order Skill.

This module defines a skill that takes a purchase order ID and a request Modify message,
fetches the existing purchase order data, builds an Modify purchase order object,
requires manager approval, and finally Modify the purchase order.
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
MANAGER_NAME = "Gari Jose Ciodaro Guerra"  # Replace with the manager's name

workflow_flow_name = "Modify Purchase Order"

class WorkflowState(TypedDict):
    purchase_order_Id: int
    request_update_message: str
    purchase_order_object: dict
    updated_purchase_order_object: dict
    metadata: dict
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

async def get_purchase_order_data(state):
    logging.error("Fetching existing purchase order data.")
    async with InventoryOverview(BASE_URL, USER_NAME, PASSWORD) as inventory_overview:
        logging.error("Fetching data.")
        await inventory_overview.fetch_data()

    purchase_order_object = inventory_overview.get_purchase_order_by_id(state["purchase_order_Id"])
    if purchase_order_object == "object not found":
        raise NodeInterrupt("purchase_order_Id is invalid or was not found.")
    state["purchase_order_object"] = purchase_order_object
    return state

async def build_updated_purchase_order_object(state):
    logging.error("Building updated purchase order object using LLM.")

    class UpdatePurchaseOrder(TypedDict):
        supplierId: int
        materialId: int
        quantity: float
        unitOfMeasure: str
        shipToLocationId: int
        orderDate: str
        status: str
        requestedDeliveryDate: str
        confirmedDeliveryDate: str

    input_prompt = f"""
    Please transform the input message: "{state['request_update_message']}" and build the UpdatePurchaseOrder.

    Keep in mind the current purchase order details:
    {state['purchase_order_object']}

    Note that valid unitOfMeasure are: "Piece", "Each", "Kg", "Liter".
    """

    update_purchase_order_object = await workflow_llm.with_structured_output(
        UpdatePurchaseOrder, strict=True).ainvoke(input_prompt)


    state["updated_purchase_order_object"] = update_purchase_order_object
    return state

async def get_updated_purchase_order_metadata(state):
    logging.error("Fetching metadata for updated purchase order.")
    async with InventoryOverview(BASE_URL, USER_NAME, PASSWORD) as inventory_overview:
        logging.error("Fetching data.")
        await inventory_overview.fetch_data()

    supplier_object = inventory_overview.get_supplier_by_id(state["updated_purchase_order_object"]["supplierId"])
    material_object = inventory_overview.get_material_by_id(state["updated_purchase_order_object"]["materialId"])
    location_object = inventory_overview.get_location_by_id(state["updated_purchase_order_object"]["shipToLocationId"])
    if supplier_object == "object not found":
        raise NodeInterrupt("supplierId is invalid or was not found.")
    if material_object == "object not found":
        raise NodeInterrupt("materialId is invalid or was not found.")
    if location_object == "object not found":
        raise NodeInterrupt("shipToLocationId is invalid or was not found.")

    state["metadata"] = {
        "supplier_email": supplier_object["contactInfo"].split(",")[0],
        "supplier_name": supplier_object["name"],
        "material_name": material_object["name"],
        "location_name": location_object["name"]
    }
    return state

async def notify_manager(state) -> Command[Literal["Update Purchase Order", "__end__"]]:

    logging.error("Executing notify_manager node.")

    # Check if reviewer_response is empty
    if state["reviewer_response"] == "":
        # Enqueue message for human-in-the-loop
        enqueu_message_dict = {
            "thread_id": state["thread_id"],
            "workflow_flow_name": workflow_flow_name,
            "editable_state": {
                "reviewer_response": state["reviewer_response"],
                "purchase_order_Id": state["purchase_order_Id"]
            },
        }
        enqueu_message = json.dumps(enqueu_message_dict)

        # Enqueue message
        await pending_workflows_enqueuer.enqueue_message(
            enqueu_message, time_to_live=600, delay=0
        )
        message_markdown = dedent(
        f"""
        **Dear Manager,**

        You need to approve the update of the following purchase order:

        **Updated Purchase Order Details:**
        - **Purchase Order ID:** {state["purchase_order_Id"]}
        - **Supplier Name:** {state["metadata"]["supplier_name"]}
        - **Supplier Email:** {state["metadata"]["supplier_email"]}
        - **Material Name:** {state["metadata"]["material_name"]}
        - **Location Name:** {state["metadata"]["location_name"]}
        - **Supplier ID:** {state["updated_purchase_order_object"]["supplierId"]}
        - **Material ID:** {state["updated_purchase_order_object"]["materialId"]}
        - **Quantity:** {state["updated_purchase_order_object"]["quantity"]} - {state["updated_purchase_order_object"]["unitOfMeasure"]}
        - **Ship To Location ID:** {state["updated_purchase_order_object"]["shipToLocationId"]}
        - **Order Date:** {state["updated_purchase_order_object"]["orderDate"]}
        - **Requested Delivery Date:** {state["updated_purchase_order_object"]["requestedDeliveryDate"]}
        - **Confirmed Delivery Date:** {state["updated_purchase_order_object"]["confirmedDeliveryDate"]}
        - **Status:** {state["updated_purchase_order_object"]["status"]}

        **Original Purchase Order Details:**
        - **Quantity:** {state["purchase_order_object"]["quantity"]} - {state["purchase_order_object"]["unitOfMeasure"]}
        - **Order Date:** {state["purchase_order_object"]["orderDate"]}
        - **Requested Delivery Date:** {state["purchase_order_object"]["requestedDeliveryDate"]}
        - **Confirmed Delivery Date:** {state["purchase_order_object"]["confirmedDeliveryDate"]}

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

        # Pause the workflow
        raise NodeInterrupt("Waiting for manager's approval.")

    else:
        if "approve" in state["reviewer_response"].lower():
            response = {"decision": "CONTINUE"}
        else:
            class ProcessReviewerResponse(TypedDict):
                decision: Literal["END", "CONTINUE"]

            input_prompt = f"""
            Please review the following statement.
            ```
            {state["reviewer_response"]}
            ```
            This statement is a response from a reviewer regarding another process. 
            You need to analyze the semantic meaning of this statement in order to 
            determine the next steps: whether the process should continue, 
            or stop (if the reviewer denies).
            """

            response = await workflow_llm.with_structured_output(
                ProcessReviewerResponse, strict=True).ainvoke(input_prompt)

        llm_decision = response.get("decision", "END")

        if "CONTINUE" in llm_decision:
            logging.error("Manager approved the purchase order update.")
            return Command(goto="Update Purchase Order", update={})
        else:
            logging.error("Manager denied the purchase order update.")
            return Command(goto=END)

async def update_purchase_order(state):
    logging.info("Updating purchase order.")

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
                # Continue with updating purchase order

        logging.info("Updating order...")
        logging.debug(f"Updated purchase order data: {state['updated_purchase_order_object']}")
        url = f"{BASE_URL}/api/purchase-orders/{state['purchase_order_Id']}"
        order_payload = state["updated_purchase_order_object"]
        logging.error(f"Order payload: {order_payload}")
        async with session.patch(url, json=order_payload) as response:
            if response.status == 200:
                logging.error("Purchase order updated successfully.")
                updated_order = await response.json()
                logging.error(f"Purchase order updated successfully with ID: {updated_order.get('id')}")
                # Optionally notify supplier via Lisa
                lisa_connector = LisaConnector(lisa_api=LISA_API, lisa_key=API_KEY)
                input_prompt = f"""
                Hi Lisa,

                Please send an email to the supplier ({state["metadata"]["supplier_email"]}) informing them 
                that the purchase order (ID: {state['purchase_order_Id']}) has been updated as follows.

                Email template:

                ```
                <p>Dear <b>{state["metadata"]["supplier_name"]}</b>,</p>
                <p>We wanted to inform you that the purchase order with the following details has been updated:</p>
                <ul>
                    <li><b>Order Id:</b> {state['purchase_order_Id']}</li>
                    <li><b>Material Name:</b> {state["metadata"]["material_name"]}</li>
                    <li><b>Ship-to:</b> {state["metadata"]["location_name"]}</li>
                    <li><b>Requested Delivery Date:</b> {state["updated_purchase_order_object"]["requestedDeliveryDate"]}</li>
                    <li><b>Quantity:</b> {state["updated_purchase_order_object"]["quantity"]} - {state["updated_purchase_order_object"]["unitOfMeasure"]}</li>
                </ul>
                <p>Please take note of these changes and confirm receipt of this update.</p>

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
                    f"Failed to update purchase order. Status Code: {response.status}, "
                    f"Response: {error_text}"
                )
    return state

builder = StateGraph(WorkflowState)

builder.add_node("Get Existing Purchase Order Data", get_purchase_order_data)
builder.add_node("Build Updated Purchase Order Object", build_updated_purchase_order_object)
builder.add_node("Get Updated Purchase Order Metadata", get_updated_purchase_order_metadata)
builder.add_node("Seek Manager's Approval", notify_manager)
builder.add_node("Update Purchase Order", update_purchase_order)

builder.add_edge(START, "Get Existing Purchase Order Data")
builder.add_edge("Get Existing Purchase Order Data", "Build Updated Purchase Order Object")
builder.add_edge("Build Updated Purchase Order Object", "Get Updated Purchase Order Metadata")
builder.add_edge("Get Updated Purchase Order Metadata", "Seek Manager's Approval")
builder.add_edge("Update Purchase Order", END)

workflow_graph = builder.compile()

@traceable(name="Modify Purchase Order", project_name="Modify Purchase Order")
async def main(data: dict):

    logging.error(f"Data received: {data}")
    input_state = {
        "purchase_order_Id": data.get("purchase_order_Id") or 0,
        "request_update_message": data.get("request_update_message") or "",
        "purchase_order_object": data.get("purchase_order_object", {}),
        "updated_purchase_order_object": data.get("updated_purchase_order_object", {}),
        "metadata": data.get("metadata", {}),
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