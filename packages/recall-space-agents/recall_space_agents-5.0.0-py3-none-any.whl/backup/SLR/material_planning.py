"""
material_planning_workflow.py

Material Planning Orchestration Workflow.

This module defines and executes a skill which sequentially triggers three
internal skill endpoints for material requirements planning:

1. POST /load_material_overview_data
2. POST /calculate_inventory_projection
3. POST /compute_order_proposals

The output of each step is passed as an input to the next, enabling end-to-end
material planning from uploaded order Excel files.
"""

import ast
import logging
from typing import Dict, Any, Optional

import aiohttp
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from langsmith import traceable

# ========================== STATE DEFINITION ==========================
class MaterialPlanningWorkflowState(Dict):
    """Workflow runtime state for material planning orchestration."""
    customer_orders_filename: str
    purchase_orders_filename: str
    log_message: Optional[str]
    error_message: Optional[str]
    overview_blob: Optional[str]
    projection_blob: Optional[str]
    order_proposals_blob: Optional[str]

# ========================== WORKFLOW STEPS ==========================
async def load_material_overview(state: MaterialPlanningWorkflowState) -> Command:
    """
    Step 1: Loads and canonicalizes material overview data from input files.
    Calls /load_material_overview_data, extracts resulting blob filename for next stage.
    """
    try:
        logging.error("on load_material_overview")
        logging.error(state["customer_orders_filename"])
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/load_material_overview_data",
                json={
                    "customer_orders_filename": state["customer_orders_filename"],
                    "purchase_orders_filename": state["purchase_orders_filename"],
                },
                timeout=aiohttp.ClientTimeout(total=180)
            ) as response:
                data = await response.json()
                result_str = data.get("result")
                result_dict = ast.literal_eval(result_str)
                overview_blob = result_dict.get("output_blob_name").split("/")[-1]
                if not overview_blob:
                    raise Exception("No 'output_blob_name' in response")
    except Exception as e:
        logging.error("gone into Exception")
        logging.error(f"Step1 failed: {e}")
        return Command(goto=END, update={"error_message": f"Step1 failed: {e}"})
    logging.error(f"overview_blob: {overview_blob}")
    return Command(goto="calculate_inventory_projection", update={"overview_blob": overview_blob})

async def calculate_inventory_projection(state: MaterialPlanningWorkflowState) -> Command:
    """
    Step 2: Calculates inventory projection based on the overview data.
    Calls /calculate_inventory_projection, extracts resulting projection filename.
    """
    logging.error("on calculate_inventory_projection")
    logging.error(state["overview_blob"])
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/calculate_inventory_projection",
                json={"material_overview_filename": state["overview_blob"]},
                timeout=aiohttp.ClientTimeout(total=180)
            ) as response:
                data = await response.json()
                result_str = data.get("result")
                result_dict = ast.literal_eval(result_str)
                projection_blob = result_dict.get("output_blob_name").split("/")[-1]
                if not projection_blob:
                    raise Exception("No 'output_blob_name' in response")
    except Exception as e:
        return Command(goto=END, update={"error_message": f"Step2 failed: {e}"})
    return Command(goto="compute_order_proposals", update={"projection_blob": projection_blob})

async def compute_order_proposals(state: MaterialPlanningWorkflowState) -> Command:
    """
    Step 3: Computes order proposals given the projected inventory.
    Calls /compute_order_proposals, extracts resulting proposals filename.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/compute_order_proposals",
                json={"projection_filename": state["projection_blob"]},
                timeout=aiohttp.ClientTimeout(total=180)
            ) as response:
                data = await response.json()
                result_str = data.get("result")
                result_dict = ast.literal_eval(result_str)
                order_proposals_blob = result_dict.get("output_blob_name").split("/")[-1]
                if not order_proposals_blob:
                    raise Exception("No 'output_blob_name' in response")
    except Exception as e:
        return Command(goto=END, update={"error_message": f"Step3 failed: {e}"})
    return Command(
        goto=END,
        update={
            "order_proposals_blob": order_proposals_blob,
            "log_message": "Workflow complete"
        }
    )

# ========================== BUILD GRAPH ==========================
builder = StateGraph(MaterialPlanningWorkflowState)
builder.add_node("load_material_overview", load_material_overview)
builder.add_node("calculate_inventory_projection", calculate_inventory_projection)
builder.add_node("compute_order_proposals", compute_order_proposals)
builder.add_edge(START, "load_material_overview")
builder.add_edge("load_material_overview", "calculate_inventory_projection")
builder.add_edge("calculate_inventory_projection", "compute_order_proposals")
builder.add_edge("compute_order_proposals", END)
workflow_graph = builder.compile()

# ========================== ENTRY POINT ==========================
@traceable(name="Material Planning", project_name="Material Planning")
async def main(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point for material planning workflow execution.
    Requires:
        data (dict): Keys 'customer_orders_filename' and 'purchase_orders_filename'.
    """
    input_state: MaterialPlanningWorkflowState = {
        "customer_orders_filename": data.get("customer_orders_filename") or "",
        "purchase_orders_filename": data.get("purchase_orders_filename") or "",
        "log_message": None,
        "error_message": None,
        "overview_blob": None,
        "projection_blob": None,
        "order_proposals_blob": None,
    }
    if (
        not input_state["customer_orders_filename"]
        or not input_state["purchase_orders_filename"]
    ):
        return {"error_message": "Both input filenames are required."}
    response = await workflow_graph.ainvoke(input_state)
    return response

# Example usage (not executed):
# await main({
#     "customer_orders_filename": "20250428DispositionslisteHilfstoffe.xlsx",
#     "purchase_orders_filename": "Mawi_offene_Bestellungen.xlsx"
# })