"""
Skill: View Material Planning Result

This skill receives the name of a single material planning order proposals file,
downloads it from Azure Blob Storage, reads it as a pandas DataFrame (from a .pkl),
and returns an HTML table representation for easy review.
"""

import os
import io
import logging
import pandas as pd
from typing import Dict, Any, Optional

from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from langsmith import traceable

from recall_space_utils.connectors.blob.azure_blob_connector import AzureBlobConnector

INPUTS_PREFIX = "order_proposals/"

# ========================== STATE DEFINITION ==========================
class ViewMaterialPlanningResultState(Dict):
    from typing import Optional
    filename: str
    html_table: Optional[str]
    error_message: Optional[str]

# ========================== LOGIC ==========================
async def view_order_proposals_file(state: ViewMaterialPlanningResultState) -> Command:
    """
    Loads a .pkl order proposals file from Blob, decodes as DataFrame, 
    returns as HTML with your precise column order and fixed values for Status.
    """
    filename = state["filename"]
    try:
        if not filename or not filename.endswith(".pkl"):
            raise ValueError("A .pkl filename is required (e.g., 'order_proposals_20250425_141758.pkl').")
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container = os.getenv("SYSTEM_CONTAINER_NAME", "material-planning")
        blob = AzureBlobConnector(conn_str, container)
        blob_name = INPUTS_PREFIX + filename

        file_bytes = await blob.download_blob_as_bytes(blob_name)

        df = pd.read_pickle(io.BytesIO(file_bytes))
        df = df[df["proposedOrderQuantity"] > 0].copy()
        df = df.sort_values(by=["weekStart", "materialId"], ascending=[True, True])
        

        # Prepare DataFrame for output (order and mapping as in your desired output)
        output_columns = [
            ("materialId", "Material‑Nr."),
            ("materialName", "Materialname"),
            ("weekStart", "Bedarfsdatum"),
            ("proposedOrderQuantity", "Bestand"),
            ("currentInventory", "Projizierter Bestand"),
            ("projectedInventory", "Menge"),
            ("plannedReceipt", "Zugang"),
            ("demands", "Verbrauch"),
            ("VPE", "VPE"),
            ("Status", "Status"),
        ]
        # Create a new DataFrame copy with the right columns
        out_df = df[[col[0] for col in output_columns[:-1]]].copy()
        # Insert Status as "NEU"
        out_df["Status"] = "NEU"
        # Rename columns to output headers
        out_df.columns = [col[1] for col in output_columns]
        # Ensure Bedarfsdatum is YYYY-MM-DD (or original string if already so)
        out_df["Bedarfsdatum"] = pd.to_datetime(out_df["Bedarfsdatum"]).dt.strftime("%Y-%m-%d")

        html_table = out_df.to_html(index=False, border=1, justify='center', classes="table table-striped", escape=False)
        return Command(goto=END, update={"html_table": html_table, "error_message": None})
    except Exception as e:
        logging.error(f"Failed to render material planning result: {e}")
        return Command(goto=END, update={"html_table": "", "error_message": str(e)})
    
# ========================== BUILD GRAPH ==========================
builder = StateGraph(ViewMaterialPlanningResultState)
builder.add_node("view_order_proposals_file", view_order_proposals_file)
builder.add_edge(START, "view_order_proposals_file")
builder.add_edge("view_order_proposals_file", END)
workflow_graph = builder.compile()

# ========================== ENTRY POINT ==========================
@traceable(name="View Material Planning Result", project_name="View Material Planning Result")
async def main(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point for viewing a single order proposals file as HTML table.
    Args:
        data (dict): {'filename': 'order_proposals_YYYYMMDD_HHMMSS.pkl'}
    Returns:
        {'html_table': ..., 'error_message': ...}
    """
    input_state: ViewMaterialPlanningResultState = {
        "filename": data.get("filename", ""),
        "html_table": None,
        "error_message": None,
    }
    if not input_state["filename"]:
        return {
            "error_message": "Order proposals filename is required.",
            "html_table": ""
        }
    response = await workflow_graph.ainvoke(input_state)
    return response