import os
import io
from typing import TypedDict, Optional, Dict, Any
from datetime import datetime, timezone

from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from langsmith import traceable

from recall_space_utils.connectors.blob.azure_blob_connector import AzureBlobConnector

# ========================== STATE DEFINITION ==========================
class OrderPlacementWorkflowState(TypedDict):
    # State for the Order Placement workflow (no input parameters required)
    order_filename: Optional[str]
    error_message: Optional[str]
    log_message: Optional[str]

# ========================== STEP 1: Search for Most Recent File ==========================
async def find_latest_xlsx_in_blob(
    state: OrderPlacementWorkflowState,
) -> Command:
    SYSTEM_BLOB_CONNSTR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    SYSTEM_CONTAINER = os.getenv("SYSTEM_CONTAINER_NAME", "material-planning")
    OUTPUTS_PREFIX = "outputs/"
    blob = AzureBlobConnector(SYSTEM_BLOB_CONNSTR, SYSTEM_CONTAINER)
    try:
        all_blobs = await blob.list_blobs(OUTPUTS_PREFIX)
        xlsx_files = [
            f for f in all_blobs if f.endswith(".xlsx") and f.startswith(OUTPUTS_PREFIX)
        ]
        if not xlsx_files:
            return Command(goto=END, update={"error_message": "No .xlsx files found in outputs folder."})

        # Get latest by file "last modified" info (sort descending)
        files_with_dates = []
        for f in xlsx_files:
            props = await blob.get_blob_properties(f)
            files_with_dates.append((f, props.get("last_modified", datetime(1970,1,1))))
        files_with_dates.sort(key=lambda x: x[1], reverse=True)
        latest_file = files_with_dates[0][0]
        return Command(goto="download_and_scp", update={"order_filename": latest_file})
    except Exception as e:
        return Command(goto=END, update={"error_message": f"Failed finding latest xlsx: {e}"})


# ========================== STEP 2: Download & Local Transfer ==========================
async def download_and_scp(
    state: OrderPlacementWorkflowState,
) -> Command:
    order_filename = state.get("order_filename")
    if not order_filename:
        return Command(goto=END, update={"error_message": "No file selected for SCP"})

    SYSTEM_BLOB_CONNSTR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    SYSTEM_CONTAINER = os.getenv("SYSTEM_CONTAINER_NAME", "material-planning")
    REMOTE_USER = "recall_space_admin"
    REMOTE_HOST = "20.107.168.178"
    REMOTE_DEST = "Desktop/slr_orders"
    blob = AzureBlobConnector(SYSTEM_BLOB_CONNSTR, SYSTEM_CONTAINER)
    try:
        # Download to memory first
        data = await blob.download_blob_as_bytes(order_filename)
        local_name = os.path.basename(order_filename)
        with open(local_name, "wb") as f:
            f.write(data)

        # SCP to user@host:folder
        import subprocess
        scp_cmd = [
            "scp", local_name,
            f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DEST}/"
        ]
        result = subprocess.run(scp_cmd, capture_output=True)
        if result.returncode != 0:
            return Command(goto=END, update={"error_message": f"SCP failed: {result.stderr.decode()}"})

        return Command(goto="scp_to_lisa", update={"log_message": f"Downloaded and transferred file {local_name} to {REMOTE_USER}@{REMOTE_HOST}"})
    except Exception as e:
        return Command(goto=END, update={"error_message": f"Download and SCP1 failed: {e}"})


# ========================== STEP 3: Remote Transfer from recall_space_admin to lisa.ai ==========================
async def scp_to_lisa(
    state: OrderPlacementWorkflowState,
) -> Command:
    # This assumes SSH keys and permissions are configured on recall_space_admin's machine.
    # This node *instructs* the remote to do the next hop (SCP to lisa.ai)
    REMOTE_USER = "recall_space_admin"
    REMOTE_HOST = "20.107.168.178"
    REMOTE_FILE = os.path.basename(state.get("order_filename"))
    DESKTOP_SRC = f"/home/{REMOTE_USER}/Desktop/slr_orders/{REMOTE_FILE}"
    LISA_USER = "lisa.ai"
    LISA_HOST = "145.253.160.50"
    LISA_DEST = "C:/Users/lisa.ai/Desktop/slr_orders/"

    try:
        # Issue SSH command to 20.107.168.178, which runs SCP to lisa.ai
        import subprocess
        ssh_cmd = [
            "ssh",
            f"{REMOTE_USER}@{REMOTE_HOST}",
            f"scp '{DESKTOP_SRC}' '{LISA_USER}@{LISA_HOST}:{LISA_DEST}'"
        ]
        result = subprocess.run(ssh_cmd, capture_output=True)
        if result.returncode != 0:
            return Command(goto=END, update={"error_message": f"Remote SCP to lisa.ai failed: {result.stderr.decode()}"})
        return Command(goto="run_powershell_on_lisa", update={"log_message": "SCP to lisa.ai initiated successfully"})
    except Exception as e:
        return Command(goto=END, update={"error_message": f"SCP to lisa.ai failed: {e}"})


# ========================== STEP 4: Execute PowerShell Script on lisa.ai ==========================
async def run_powershell_on_lisa(
    state: OrderPlacementWorkflowState,
) -> Command:
    """
    Executes the updated PowerShell script on lisa.ai, using x86 PowerShell and the .xlsx as input.
    """
    LISA_USER = "lisa.ai"
    LISA_HOST = "145.253.160.50"
    ps_script = r'C:\Users\lisa.ai\Desktop\slr_orders\insert-order-from-xlsx.ps1'
    excel_file = rf'C:\Users\lisa.ai\Desktop\slr_orders\{os.path.basename(state.get("order_filename"))}'

    # Use x86 PowerShell explicitly
    x86_powershell = r"C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe"
    powershell_cmd = f'"{x86_powershell}" -ExecutionPolicy Bypass -File "{ps_script}" -excelPath "{excel_file}"'
    # Escape the quotes for the ssh command-line
    full_cmd = f'{powershell_cmd}'

    try:
        import subprocess
        ssh_cmd = [
            "ssh",
            f"{LISA_USER}@{LISA_HOST}",
            full_cmd
        ]
        result = subprocess.run(ssh_cmd, capture_output=True)
        if result.returncode != 0:
            return Command(goto=END, update={"error_message": f"PowerShell script execution (x86) failed: {result.stderr.decode()}"})
        return Command(goto=END, update={"log_message": "x86 PowerShell script executed on lisa.ai"})
    except Exception as e:
        return Command(goto=END, update={"error_message": f"Failed to run PowerShell (x86) script: {e}"})

# ========================== BUILD GRAPH ==========================
builder = StateGraph(OrderPlacementWorkflowState)
builder.add_node("find_latest_xlsx_in_blob", find_latest_xlsx_in_blob)
builder.add_node("download_and_scp", download_and_scp)
builder.add_node("scp_to_lisa", scp_to_lisa)
builder.add_node("run_powershell_on_lisa", run_powershell_on_lisa)
builder.add_edge(START, "find_latest_xlsx_in_blob")
builder.add_edge("find_latest_xlsx_in_blob", "download_and_scp")
builder.add_edge("download_and_scp", "scp_to_lisa")
builder.add_edge("scp_to_lisa", "run_powershell_on_lisa")
builder.add_edge("run_powershell_on_lisa", END)
workflow_graph = builder.compile()

# ========================== ENTRY POINT ==========================
@traceable(name="Order Placement Workflow", project_name="Material Planning")
async def main(data: Dict[str, Any] = {}) -> Dict[str, Any]:
    input_state: OrderPlacementWorkflowState = {
        "order_filename": None,
        "error_message": None,
        "log_message": None,
    }
    result = await workflow_graph.ainvoke(input_state)
    return result

# Usage:
# await main()