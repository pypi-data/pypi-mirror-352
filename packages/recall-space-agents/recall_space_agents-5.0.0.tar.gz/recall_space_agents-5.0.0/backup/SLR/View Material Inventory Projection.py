"""
Skill: View Material Inventory Projection (filtered by materialId as string, original headers)

This skill receives the name of a single inventory projection file,
downloads it from Azure Blob Storage, reads it as a pandas DataFrame (from a .pkl),
filters by 'materialId' (treated as string), and returns a markdown table
of the projections with original column headers preserved.
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

INPUTS_PREFIX = "projections/"  # inventory projections filename prefix

# ========================== STATE DEFINITION ==========================
class ViewMaterialInventoryProjectionState(Dict):
    from typing import Optional
    filename: str
    materialId: Optional[str]  # MATERIALID IS STRING NOW!
    markdown_table: Optional[str]
    error_message: Optional[str]

# ========================== LOGIC ==========================
async def view_inventory_projection_file(state: ViewMaterialInventoryProjectionState) -> Command:
    """
    Loads a .pkl inventory projection file from Blob, decodes as DataFrame,
    filters by materialId (as string), and returns a Markdown table.
    """
    filename = state["filename"]
    material_id = state.get("materialId", None)

    try:
        if not filename or not filename.endswith(".pkl"):
            raise ValueError("A .pkl filename is required (e.g., 'projections_20250507_085104.pkl').")
        if material_id is None:
            raise ValueError("A materialId parameter is required.")

        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container = os.getenv("SYSTEM_CONTAINER_NAME", "material-planning")
        blob = AzureBlobConnector(conn_str, container)
        blob_name = INPUTS_PREFIX + filename

        file_bytes = await blob.download_blob_as_bytes(blob_name)
        df = pd.read_pickle(io.BytesIO(file_bytes))

        # Filter by materialId as string
        filtered_df = df[df["materialId"].astype(str) == str(material_id)].copy()

        # Optional: sort by weekStart and materialId if present in columns
        sort_cols = [col for col in ("weekStart", "materialId") if col in filtered_df.columns]
        if sort_cols:
            filtered_df = filtered_df.sort_values(by=sort_cols)

        markdown_table = filtered_df.to_markdown(index=False, tablefmt="grid")
        return Command(goto=END, update={"markdown_table": markdown_table, "error_message": None})
    except Exception as e:
        logging.error(f"Failed to render material inventory projection: {e}")
        return Command(goto=END, update={"markdown_table": "", "error_message": str(e)})

# ========================== BUILD GRAPH ==========================
builder = StateGraph(ViewMaterialInventoryProjectionState)
builder.add_node("view_inventory_projection_file", view_inventory_projection_file)
builder.add_edge(START, "view_inventory_projection_file")
builder.add_edge("view_inventory_projection_file", END)
workflow_graph = builder.compile()

# ========================== ENTRY POINT ==========================
@traceable(name="View Material Inventory Projection", project_name="View Material Inventory Projection")
async def main(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point for viewing a single inventory projection file, filtered by materialId as string.
    Args:
        data (dict): {'filename': 'projections_YYYYMMDD_HHMMSS.pkl', 'materialId': '231212002'}
    Returns:
        {'markdown_table': ..., 'error_message': ...}
    """
    input_state: ViewMaterialInventoryProjectionState = {
        "filename": data.get("filename", ""),
        "materialId": str(data.get("materialId", "")),  # always string
        "markdown_table": None,
        "error_message": None,
    }
    if not input_state["filename"]:
        return {
            "error_message": "Projection filename is required.",
            "markdown_table": ""
        }
    if not input_state["materialId"]:
        return {
            "error_message": "A materialId parameter is required.",
            "markdown_table": ""
        }
    response = await workflow_graph.ainvoke(input_state)
    return response