"""Module for handling changes on purchase orders from suppliers.

This module defines a workflow that processes changes made by suppliers to purchase orders.
It simulates inventory projections, explores mitigation procedures,
and runs the mitigation procedures if necessary.
"""

import datetime
import logging
import os
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from langsmith import traceable
from recall_space_agents.utils.azure_quere_handler import AzureQueueHandler
from recall_space_agents.utils.workflow_execution_management import (
    WorkflowExecutionManagement,
)
from recall_space_utils.connectors.lisa.lisa_connector import LisaConnector
from recall_space_utils.recall_space_erp.inventory_overview import InventoryOverview

load_dotenv()

LISA_API = os.getenv("LISA_API")
API_KEY = os.getenv("API_KEY")

BASE_URL = "https://erp.greenwave-c759a37d.northeurope.azurecontainerapps.io"
USER_NAME = "Lisa"
PASSWORD = "GoLisa2025"

workflow_flow_name = "Handle Changes on Purchase Order from Suppliers"

# Enqueuer for node step execution messages to Azure Functions queue
azure_functions_enqueuer = AzureQueueHandler(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="azure-functions-queue",
)



workflow_llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
)
lisa_connector = LisaConnector(lisa_api=LISA_API, lisa_key=API_KEY)


class WorkflowState(TypedDict):
    """Typed dictionary representing the workflow state."""

    conversation_with_supplier: str
    supplier_id: str
    purchase_order_id: int
    purchase_order: dict
    projected_inventory: list
    simulated_projected_inventory: list
    mitigation_procedure: str
    mitigation_result: str
    reply_to_supplier: str
    is_further_analysis_required: bool


async def get_purchase_order_id(
    state,
) -> Command[Literal["__end__", "Simulate Inventory Projection"]]:
    """Get the Purchase Order ID that the supplier is referring to.

    This function prompts the LLM to select the purchase order that the supplier is referring to,
    based on the conversation with the supplier and the list of current active purchase orders.
    If the purchase order is not found, it will end the workflow.

    Args:
        state (dict): The current state of the workflow, including the conversation with the supplier.

    Returns:
        Command: A command indicating whether to end the workflow or proceed to "Simulate Inventory Projection",
        along with any updates to the workflow state.
    """

    async with InventoryOverview(BASE_URL, USER_NAME, PASSWORD) as inventory_overview:
        logging.error("Fetching data")
        await inventory_overview.fetch_data()

    class PurchaseOrder(TypedDict):
        """Typed dictionary representing a purchase order."""

        supplierId: int
        materialId: int
        RequestedQuantity: float
        SuppliersProposedQuantity: float
        RequestedDeliveryDate: str
        SuppliersDeliveryDate: str
        supplierName: str
        materialName: str
        locationName: str
        purchaseOrder: int
        shipToLocationId: int

    in_progress_purchase_orders = [
        each for each in inventory_overview.purchase_orders if each["status"] == "In Progress"
    ]

    input_prompt = f"""
    Please select the purchase order the supplier is referring to.

    + Current active purchase orders
    ```
    {in_progress_purchase_orders}
    ```

    + Conversation with suppliers
    ```
    {state["conversation_with_supplier"]}
    ```

    If purchase order that the supplier is referring to is not there,
    set the materialId to -1
    """

    purchase_order = await workflow_llm.with_structured_output(
        PurchaseOrder, strict=True
    ).ainvoke(input_prompt)
    logging.error(f"{purchase_order}: purchase_order")



    if purchase_order["materialId"] == -1:
        return Command(goto=END)
    else:
        projected_inventory = inventory_overview.calculate_projected_inventory(
        selected_material=str(purchase_order["materialId"]),
        selected_location=str(purchase_order["shipToLocationId"]),
        select_fields=[
            "materialId",
            "locationId",
            "weekStart",
            "projectedQuantity",
            "minStockLevel",
            "maxStockLevel",
            ],
        )
        return Command(
            goto="Simulate Inventory Projection", update={
                "purchase_order": purchase_order,
                "projected_inventory": projected_inventory}
        )


async def simulate_inventory_projection(
    state,
) -> Command[Literal["__end__", "Explore Mitigation Procedure"]]:
    """Simulate the inventory projection after the purchase order change.

    This function calculates the projected inventory based on the selected material and location.
    It then simulates the impact of the purchase order change on the projected inventory.
    If the projected stock goes below zero, it determines that further analysis is required.

    Args:
        state (dict): The current state of the workflow, including the selected purchase order.

    Returns:
        Command: A command indicating whether to end the workflow or proceed to "Explore Mitigation Procedure",
        along with any updates to the workflow state.
    """
    logging.error(f"simulate_inventory_projection")
    # Calculate the projected inventory


    # Create a copy of projected_inventory to work with
    simulated_projected_inventory = [each.copy() for each in state["projected_inventory"]]

    # Get the denied purchase order details
    changed_po = state["purchase_order"]
    changed_quantity = (
        changed_po["RequestedQuantity"] - changed_po["SuppliersProposedQuantity"]
    )
    order_date_str = changed_po["RequestedDeliveryDate"]

    # Parse the orderDate into a date object
    order_date = datetime.datetime.strptime(order_date_str, "%Y-%m-%d").date()
    is_further_analysis_required = False

    # Adjust the projected inventory
    # Only if projected stock goes below 0 this workflow would continue.
    for entry in simulated_projected_inventory:
        # Parse the weekStart into a date object
        entry_week_start = datetime.datetime.strptime(
            entry["weekStart"], "%Y-%m-%d"
        ).date()
        # If the entry's weekStart is on or after the order's week start, adjust the projectedQuantity
        if entry_week_start >= order_date:
            entry["projectedQuantity"] -= changed_quantity
            if entry["projectedQuantity"] <= 0:
                is_further_analysis_required = True
    logging.error(f"projected_inventory")
    logging.error(state["projected_inventory"])
    logging.error(f"simulated_projected_inventory")
    logging.error(simulated_projected_inventory)
    if is_further_analysis_required is False:
        return Command(goto=END, update={})
    else:
        # Now, simulated_projected_inventory contains the adjusted projected quantities
        return Command(
            goto="Explore Mitigation Procedure",
            update={
                "simulated_projected_inventory": simulated_projected_inventory,
                "is_further_analysis_required": is_further_analysis_required,
            },
        )


async def explore_mitigation_procedure(
    state,
) -> Command[Literal["__end__", "Run Mitigation Procedure"]]:
    """Explore possible mitigation procedures for the purchase order change.

    This function asks Lisa to check for any specific mitigation procedures to handle
    the supplier and material combination affected by the purchase order change.
    If no mitigation procedure is found, it sends a Teams message to request training.

    Args:
        state (dict): The current state of the workflow.

    Returns:
        Command: A command indicating whether to end the workflow or proceed to "Run Mitigation Procedure",
        along with any updates to the workflow state.
    """
    logging.error("explore_mitigation_procedure")
    input_prompt = f"""
    Hi Lisa,

    We have a problem: a purchase order to a supplier was changed by them.

    Please use your recalling tool to see if there are specific mitigation 
    procedures to handle this supplierName, materialName.

    Changed Purchase Order:
    {state["purchase_order"]}

    If a mitigation procedure is not found, please just reply with "NOT FOUND".
    """
    lisas_response = await lisa_connector.ask_question(input_prompt)

    logging.error(f"lisas_response on explore_mitigation_procedure: {lisas_response}")

    current_timestamp = datetime.datetime.now()
    timestamp_str = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    # If there is no mitigation procedure the workflows ends
    if "NOT FOUND" in lisas_response.upper().strip():
        input_prompt = f"""
        Hi Lisa, please send a Teams Message to Gari Jose Ciodaro Guerra asking 
        for training on how to mitigate Purchase orders changes like the one below.

        Rejected Purchase order:
        {state["purchase_order"]}

        The prior Purchase order rejection was processed today {timestamp_str}
        """
        
        await lisa_connector.ask_question(input_prompt)
        return Command(goto=END, update={})
    else:
        return Command(
            goto="Run Mitigation Procedure", update={"mitigation_procedure": lisas_response}
        )


async def run_mitigation_procedure(state):
    """Run the mitigation procedure provided by Lisa.

    This function asks Lisa to run the mitigation procedure for the changed purchase order,
    taking into account the projected inventory before and after the change.

    Args:
        state (dict): The current state of the workflow, including the mitigation procedure.

    Returns:
        dict: The updated workflow state after running the mitigation procedure.
    """
    logging.error(f"run_mitigation_procedure")
    input_prompt = f"""
    Please run the mitigation Procedure.

    # Mitigation Procedure
    ```
    {state["mitigation_procedure"]}
    ```

    # Changed Purchase Order by supplier.
    ```
    {state["purchase_order"]}
    ```

    # Projected inventory Before Purchase Order Change
    ```
    {state["projected_inventory"]}
    ```

    # Projected inventory After Purchase Order Change
    ```
    {state["simulated_projected_inventory"]}
    ```

    # Original conversation with suppliers
    {state["conversation_with_supplier"]}
    """
    lisas_response = await lisa_connector.ask_question(input_prompt)
    state["mitigation_result"] = lisas_response
    logging.error(f"mitigation_result: {lisas_response}")
    return state


builder = StateGraph(WorkflowState)
builder.add_node("Get Purchase Order Id", get_purchase_order_id)
builder.add_node("Simulate Inventory Projection", simulate_inventory_projection)
builder.add_node("Explore Mitigation Procedure", explore_mitigation_procedure)
builder.add_node("Run Mitigation Procedure", run_mitigation_procedure)

builder.add_edge(START, "Get Purchase Order Id")
builder.add_edge("Run Mitigation Procedure", END)

workflow_graph = builder.compile()



@traceable(
    name="Handle Changes on Purchase Order from Suppliers",
    project_name="Handle Changes on Purchase Order from Suppliers",
)
async def main(data: dict):
    """Main function to execute the workflow.

    This function initializes the workflow state and executes the workflow graph,
    managing the execution with a message queue.

    Args:
        data (dict): Input data containing the conversation with the supplier.

    Returns:
        final_response: Instruction to supplier.
    """
    input_state = {
        "conversation_with_supplier": data["conversation_with_supplier"],
        "supplier_id": "",
        "purchase_order_id": 0,
        "purchase_order": {},
        "projected_inventory": [],
        "simulated_projected_inventory":  [],
        "mitigation_procedure": "",
        "mitigation_result": "",
        "reply_to_supplier": "",
        "is_further_analysis_required": False,
    }
    response = await WorkflowExecutionManagement.astream_with_queue_workflow(
        message_enqueuer=azure_functions_enqueuer,
        compile_graph=workflow_graph,
        state=input_state,
        stream_mode="values",
    )
    if response[-1]["is_further_analysis_required"] is True:
        final_response = """
        After analyzing the situation, we have escalated it to the inventory management team. 
        Please inform the supplier that we will reach out later to them to better understand the
        situation and find a solution."""
    else:
        final_response = """
        After analyzing the situation, we have assessed and accepted the impact, 
        and no further action is required. Please inform the supplier that changes are accepted."""
    logging.error(f"final response to supplier: {final_response}")
    return final_response