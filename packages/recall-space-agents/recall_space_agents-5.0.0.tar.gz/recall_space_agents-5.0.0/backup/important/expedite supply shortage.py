import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from typing import TypedDict, Optional
from azure.identity import UsernamePasswordCredential
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from langsmith import traceable

# Importing necessary modules
from recall_space_agents.toolkits.ms_email.ms_email import MSEmailToolKit
from recall_space_agents.toolkits.ms_bot.ms_bot import MSBotToolKit
from recall_space_agents.utils.workflow_execution_management import \
    WorkflowExecutionManagement
from langchain_openai import AzureChatOpenAI
from recall_space_agents.utils.azure_quere_handler import MessageEnqueuer
import json

from langgraph.errors import NodeInterrupt

# ========================== CONSTANT CONFIGURATION ==========================
load_dotenv()

workflow_flow_name = "Expedite supply shortage"

# ERP Credentials
BASE_URL = "https://erp-system.replit.app/"
USER_NAME = "titus"
PASSWORD = "dev123"

# Manager's Info (Replace with the actual manager's name)
MANAGER_NAME = "Titus Lottig"

# Enqueuer for human-in-the-loop pending workflows
pending_workflows_enqueuer = MessageEnqueuer(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="pending-workflows")

# Enqueuer for node step execution messages to Azure Functions queue
azure_functions_enqueuer = MessageEnqueuer(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="azure-functions-queue")

# Workflow execution management with message enqueuer
workflow_execution_management = WorkflowExecutionManagement(
    db_connection_string=os.getenv("CHECKPOINTERS_DB_URL"),
    message_enqueuer=azure_functions_enqueuer)

credentials = UsernamePasswordCredential(
    client_id=os.getenv("CLIENT_ID"),
    authority=os.getenv("MS_AUTHORITY"),
    tenant_id=os.getenv("TENANT_ID"),
    username=os.getenv("LISA_USER_NAME"),
    password=os.getenv("LISA_PASSWORD"),
)

llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
    temperature=0,  # Deterministic output.
)

email_toolkit = MSEmailToolKit(credentials=credentials)

# Initialize the MSBotToolkit
bot_toolkit = MSBotToolKit(
    credentials=credentials,
    bot_id=os.getenv("BOT_ID"),
    direct_line_secret=os.getenv("DIRECT_LINE_SECRET")
)

# Workaround retry caused by node interrupt
flag_notification_sent = False

# ========================== Helper Functions ==========================

def erp_login(session: requests.Session) -> bool:
    """Log in to the ERP system and maintain the session."""
    login_url = f"{BASE_URL}/api/login"
    login_payload = {"username": USER_NAME, "password": PASSWORD}
    response = session.post(login_url, json=login_payload)
    if response.status_code != 200:
        print("Login failed.")
        return False
    print("Login successful!")
    return True

def get_current_inventory(session: requests.Session, materialId: int) -> Optional[int]:
    """
    Fetch all goods movements for the material and calculate the net inventory.
    """
    url = f"{BASE_URL}/api/goods-movements?materialId={materialId}"
    response = session.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch goods movements for material ID {materialId}. Status Code: {response.status_code}")
        return None
    goods_movements = response.json()
    inventory = 0
    for movement in goods_movements:
        if movement['movementType'] == 'Receipt':
            inventory += float(movement['quantity'])
        elif movement['movementType'] == 'Issue':
            inventory -= float(movement['quantity'])
    return inventory

# ========================== Workflow Graph Definition ==========================

async def check_inventory_levels(state):
    session = requests.Session()

    # Login to get the session cookie
    if not erp_login(session):
        return Command(goto=END, update={})

    # Get the current inventory level for the material
    materialId = state['incoming_order']['materialId']
    current_inventory = get_current_inventory(session, materialId)
    if current_inventory is None:
        print("Failed to retrieve current inventory level.")
        return Command(goto=END, update={})

    print(f"Current inventory for material {materialId}: {current_inventory}")

    # Calculate the new inventory level after the incoming customer order
    ordered_quantity = state['incoming_order']['quantity']
    new_inventory = current_inventory - ordered_quantity
    print(f"New inventory after customer order: {new_inventory}")

    # Check if new inventory level is below minimum_quantity
    if new_inventory < state['minimum_quantity']:
        print("Inventory level is below minimum_quantity.")
        # Update state with new inventory level
        return Command(goto="not_enough_stock", update={"inventory_level": new_inventory})
    else:
        print("Inventory level is sufficient. Workflow will proceed to END.")
        return Command(goto=END, update={"inventory_level": new_inventory})

async def not_enough_stock(state):
    session = requests.Session()

    # Login to get the session cookie
    if not erp_login(session):
        return Command(goto=END, update={})

    materialId = state['incoming_order']['materialId']

    # Fetch sources of supply for the material
    sources_url = f"{BASE_URL}/api/sources-of-supply?materialId={materialId}"
    sources_response = session.get(sources_url)

    if sources_response.status_code != 200:
        print(f"Failed to fetch sources of supply for material ID {materialId}. Status Code: {sources_response.status_code}")
        return Command(goto=END, update={})

    sources = sources_response.json()
    if not sources:
        print("No sources of supply found for the material.")
        return Command(goto=END, update={})

    # For simplicity, choose the first supplier
    source = sources[0]
    supplierId = source['supplierId']
    uom = source.get('uom', 'units')

    # Create a proposed purchase order
    purchase_order = {
        "supplierId": supplierId,
        "materialId": materialId,
        "quantity": state['minimum_quantity'],
        "uom": uom,
        "orderDate": datetime.now().isoformat(),
        "status": "Open"
    }

    # Update the state with the proposed order
    print(f"Proposed purchase order: {purchase_order}")
    return Command(goto="notify_manager", update={"proposed_order": purchase_order})

async def notify_manager(state):
    """
    Send a Teams message to the manager with the proposed purchase order,
    and handle the approval process.
    """
    proposed_order = state['proposed_order']

    # Check if manager_response is empty
    if state["manager_response"] == "":
        # Prepare the Teams message content
        message_markdown = f"""
        **Dear Manager,**

        The inventory level for material ID {proposed_order['materialId']} has fallen below the minimum required quantity.

        A proposed purchase order has been created with the following details:

        - **Supplier ID:** {proposed_order['supplierId']}
        - **Material ID:** {proposed_order['materialId']}
        - **Quantity:** {proposed_order['quantity']}
        - **Unit of Measure:** {proposed_order['uom']}
        - **Order Date:** {proposed_order['orderDate']}
        - **Status:** {proposed_order['status']}

        Request review for workflow run: {state["thread_id"]}
        """

        # Enqueue message for human-in-the-loop
        enqueu_message_dict = {
            "thread_id": state["thread_id"],
            "workflow_flow_name": workflow_flow_name,
            "editable_state": {
                "manager_response": state["manager_response"]
            }
        }
        enqueu_message = json.dumps(enqueu_message_dict)

        global flag_notification_sent
        if flag_notification_sent is False:
            await pending_workflows_enqueuer.enqueue_message(enqueu_message, time_to_live=600, delay=0)

            # Send the Teams message to the manager
            await bot_toolkit.asend_team_message_by_name(
                message=message_markdown,
                to_recipient_by_name=MANAGER_NAME  # Manager's name
            )
            

            print("Notification sent to the manager via Teams.")
        flag_notification_sent = True
        # Pause the workflow
        raise NodeInterrupt("Waiting for manager's approval.")

    else:
        # Manager's response received, check if APPROVE or REJECT
        response_text = state["manager_response"].strip().upper()
        if "APPROVE" in response_text:
            print("Manager approved the purchase order.")
            return Command(goto="place_purchase_order")
        else:
            print("Manager did not approve the purchase order.")
            return Command(goto=END, update={})

async def place_purchase_order(state):
    session = requests.Session()

    # Login to get the session cookie
    if not erp_login(session):
        return Command(goto=END, update={})

    # Place the purchase order
    purchase_order = state['proposed_order']
    url = f"{BASE_URL}/api/purchase-orders"

    response = session.post(url, json=purchase_order)

    if response.status_code == 201:
        # Purchase order placed successfully
        print("Purchase order placed successfully.")
        return Command(goto=END, update={})
    else:
        print(f"Failed to place purchase order. Status Code: {response.status_code}")
        return Command(goto=END, update={})

# ========================== State Definition ==========================

class WorkflowState(TypedDict):
    minimum_quantity: int
    incoming_order: dict
    inventory_level: Optional[int]
    proposed_order: Optional[dict]
    thread_id: str
    manager_response: str

# ========================== Build the Workflow Graph ==========================

builder = StateGraph(WorkflowState)

builder.add_node("check_inventory_levels", check_inventory_levels)
builder.add_node("not_enough_stock", not_enough_stock)
builder.add_node("notify_manager", notify_manager)
builder.add_node("place_purchase_order", place_purchase_order)

builder.add_edge(START, "check_inventory_levels")
builder.add_edge("check_inventory_levels", END)
builder.add_edge("check_inventory_levels", "not_enough_stock")
builder.add_edge("not_enough_stock", "notify_manager")
builder.add_edge("notify_manager", "place_purchase_order")
builder.add_edge("notify_manager", END)
builder.add_edge("place_purchase_order", END)

workflow_graph = builder.compile()

# ========================== WORKFLOW EXECUTION TEMPLATE ==========================

@traceable(name="Inventory Workflow", project_name="Inventory Workflow")
async def main(data: dict):
    """
    Main entry point for executing the workflow.
    """
    input_state = {
        "minimum_quantity": data.get("minimum_quantity", 10),  # Default to 10
        "incoming_order": data.get("incoming_order", {}),
        "inventory_level": None,
        "proposed_order": None,
        "thread_id": data.get("thread_id", ""),
        "manager_response": data.get("manager_response", "")
    }

    # Normal execution
    if input_state["thread_id"] == "":
        # Workaround retry caused by node interrupt
        global flag_notification_sent
        flag_notification_sent = False

        run_response = await workflow_execution_management.run_workflow(
            graph_builder=builder,
            state=input_state,
            llm=llm,
            workflow_name=workflow_flow_name)

    # Resume execution, thread_id is required.
    if input_state["thread_id"] != "":
        run_response = await workflow_execution_management.resume_workflow(
            thread_id=input_state["thread_id"],
            graph_builder=builder,
            resume_state=input_state
        )

    # Return the response for logging or further processing.
    return run_response