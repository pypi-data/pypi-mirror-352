"""
Module for getting inventory projections.

This module provides functionality to fetch and calculate projected inventory
using the InventoryOverview class.
"""

import os
import logging
from typing import TypedDict

from langsmith import traceable
from langgraph.graph import END, START, StateGraph
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

from recall_space_utils.recall_space_erp.inventory_overview import (
    InventoryOverview,
)
from recall_space_agents.utils.azure_quere_handler import AzureQueueHandler

load_dotenv()

workflow_flow_name = "Get Inventory Projection"

class WorkflowState(TypedDict):
    materialId: int
    locationId: int
    projected_inventory: list

BASE_URL = "https://erp.greenwave-c759a37d.northeurope.azurecontainerapps.io"
USER_NAME = "Lisa"
PASSWORD = "GoLisa2025"

async def get_inventory_projection(state: WorkflowState) -> WorkflowState:
    selected_material = state.get("materialId") or "all"
    selected_location = state.get("locationId") or "all"
    selected_material = str(selected_material)
    selected_location = str(selected_location)
    logging.error(f"Selected material: {selected_material}")
    logging.error(f"Selected location: {selected_location}")

    async with InventoryOverview(BASE_URL, USER_NAME, PASSWORD) as inventory_overview:
        logging.error("Fetching data")
        await inventory_overview.fetch_data()
        logging.error("Calculating projected inventory")
        projected_inventory = inventory_overview.calculate_projected_inventory(
            selected_material,
            selected_location
        )
        logging.error(f"Projected inventory: {projected_inventory}")

    state["projected_inventory"] = projected_inventory
    return state

workflow_llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
)

builder = StateGraph(WorkflowState)

builder.add_node("Get Inventory Projection", get_inventory_projection)

builder.add_edge(START, "Get Inventory Projection")
builder.add_edge("Get Inventory Projection", END)

workflow_graph = builder.compile()

@traceable(name="Get Inventory Projection", project_name="Get Inventory Projection")
async def main(data: dict) -> list:
    logging.error(f"Data received: {data}")
    input_state = {
        "materialId": data["materialId"],
        "locationId": data["locationId"],
    }

    response = await workflow_graph.ainvoke(input_state)

    return response["projected_inventory"]