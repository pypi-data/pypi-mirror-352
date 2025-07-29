"""
Skill: List Inventory Projections Results

Use this skill to receive a date (format YYYY-MM-DD) and get a list of all 
inventory projection files generated on that date. It scans Azure Blob storage 
'projections/' folder for files matching the naming pattern:
    projection_YYYYMMDD_HHMMSS.pkl

Each result includes the filename and a human-readable CEST time
converted from the file's HHMMSS suffix.
"""

import os
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from langsmith import traceable

from recall_space_utils.connectors.blob.azure_blob_connector import AzureBlobConnector

INPUTS_PREFIX = "projections/"

# ========================== STATE DEFINITION ==========================
class ListInventoryProjectionsResultsState(Dict):
    from typing import Dict, Optional, List
    date: str
    results: Optional[List[Dict[str, str]]]
    error_message: Optional[str]

# ========================== TIME HELPER ==========================
def hhmmss_to_cest_string(hhmmss: str) -> str:
    """
    Convert HHMMSS string (e.g. '172806') to human-readable CEST time.
    Assumes input is UTC and adds 2 hours for CEST (UTC+2).
    Returns format: '19:28:06 (CEST)'
    """
    utc_time = datetime.strptime(hhmmss, "%H%M%S")
    cest_offset = timedelta(hours=2)  # CEST is UTC+2
    cest_time = (utc_time + cest_offset).time()
    return cest_time.strftime('%H:%M:%S (CEST)')

def _extract_time_suffix(filename: str) -> int:
    """
    Helper to extract the HHMMSS integer from filename (for sorting).
    Example: projection_20250430_085720.pkl -> 085720
    """
    match = re.search(r'_(\d{6})\.pkl$', filename)
    return int(match.group(1)) if match else -1

def format_results_human_readable(results: List[str]) -> List[Dict[str, str]]:
    """
    Convert filenames to a list of dicts with CET/CEST human-readable time.
    """
    formatted = []
    for fn in results:
        match = re.search(r'_(\d{6})\.pkl$', fn)
        if match:
            cest_time = hhmmss_to_cest_string(match.group(1))
            formatted.append({"filename": fn, "time_cest": cest_time})
        else:
            formatted.append({"filename": fn, "time_cest": ""})
    return formatted

# ========================== LOGIC ==========================
async def list_inventory_projections_for_date(state: ListInventoryProjectionsResultsState) -> Command:
    """
    Lists projection pkl files from 'projections/' for the specified date,
    sorted by descending timestamp (most recent first), 
    and returns their CEST time for human readability.
    Date must be in YYYY-MM-DD format.
    """
    date_input = state["date"]
    try:
        # Validate and reformat date
        if not re.match(r"\d{4}-\d{2}-\d{2}", date_input):
            raise ValueError("Date must be in YYYY-MM-DD format.")
        date_compact = date_input.replace("-", "")  # e.g., '20250430'

        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container = os.getenv("SYSTEM_CONTAINER_NAME", "material-planning")
        blob = AzureBlobConnector(conn_str, container)

        # Prefix for all files of the day
        prefix = f"{INPUTS_PREFIX}projection_{date_compact}"
        blob_list = await blob.list_blobs(prefix)

        # Remove prefix for clean filenames
        matches = [each.replace(INPUTS_PREFIX, "") for each in blob_list]

        # Sort by latest HHMMSS first
        matches_sorted = sorted(matches, key=_extract_time_suffix, reverse=True)
        matches_sorted_human = format_results_human_readable(matches_sorted)
        return Command(
            goto=END, 
            update={"results": matches_sorted_human, "error_message": None}
        )
    except Exception as e:
        return Command(goto=END, update={"results": [], "error_message": str(e)})

# ========================== BUILD GRAPH ==========================
builder = StateGraph(ListInventoryProjectionsResultsState)
builder.add_node("list_inventory_projections_for_date", list_inventory_projections_for_date)
builder.add_edge(START, "list_inventory_projections_for_date")
builder.add_edge("list_inventory_projections_for_date", END)
workflow_graph = builder.compile()

# ========================== ENTRY POINT ==========================
@traceable(name="List Inventory Projections Results", project_name="List Inventory Projections Results")
async def main(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point for listing inventory projections given a date.
    Args:
        data (dict): {'date': 'YYYY-MM-DD'}
    Returns:
        {'results': [{'filename':..., 'time_cest':...}, ...], 'error_message': ...}
    """
    input_state: ListInventoryProjectionsResultsState = {
        "date": data.get("date", ""),
        "results": None,
        "error_message": None,
    }
    if not input_state["date"]:
        return {
            "error_message": "Date input is required (YYYY-MM-DD).",
            "results": []
        }
    response = await workflow_graph.ainvoke(input_state)
    return response