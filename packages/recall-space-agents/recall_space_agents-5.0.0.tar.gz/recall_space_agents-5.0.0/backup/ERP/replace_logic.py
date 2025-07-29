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
from recall_space_agents.utils.azure_quere_handler import AzureQueueHandler
import json

from langgraph.errors import NodeInterrupt
from typing import List


# ========================== CONSTANT CONFIGURATION ==========================
load_dotenv()

workflow_flow_name = "Expedite supply shortage"

# ERP Credentials
BASE_URL = "https://erp-system-recall-space.replit.app"
USER_NAME = "gari"
PASSWORD = "pleaseletmein"


# Manager's Info (Replace with the actual manager's name)
MANAGER_NAME = "Titus Lottig"

# Enqueuer for human-in-the-loop pending workflows
pending_workflows_enqueuer = AzureQueueHandler(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="pending-workflows-dev")

# Enqueuer for node step execution messages to Azure Functions queue
azure_functions_enqueuer = AzureQueueHandler(
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
import datetime
import requests
from typing import List, Dict, Any

# Adjust these constants with your actual configuration/URL
BASE_URL = "https://erp-system-recall-space.replit.app"
USER_NAME = "gari"
PASSWORD = "pleaseletmein"


class InventoryOverview:
    """
    Class for managing and analyzing inventory from an ERP system. This class handles
    ERP login, data retrieval, and inventory calculations (both current and projected).
    """

    def __init__(self) -> None:
        """
        Initialize the InventoryOverview class.

        Creates a requests.Session, logs into the ERP system, and then fetches relevant
        data (materials, locations, goods movements, orders, etc.).
        """
        self.session = requests.Session()
        if not self._erp_login():
            raise Exception("Unable to log into the ERP system.")

        # Containers for fetched data
        self.materials: List[Dict[str, Any]] = []
        self.locations: List[Dict[str, Any]] = []
        self.movements: List[Dict[str, Any]] = []
        self.customer_orders: List[Dict[str, Any]] = []
        self.production_orders: List[Dict[str, Any]] = []
        self.purchase_orders: List[Dict[str, Any]] = []
        self.source_of_supply: List[Dict[str, Any]] = []

        # Once logged in, fetch all needed data
        self.fetch_data()

    def _erp_login(self) -> bool:
        """
        Log in to the ERP system and maintain the session.

        Returns:
            bool: True if login successful, False otherwise.
        """
        login_url = f"{BASE_URL}/api/login"
        login_payload = {"username": USER_NAME, "password": PASSWORD}
        response = self.session.post(login_url, json=login_payload)
        if response.status_code != 200:
            print("Login failed.")
            return False
        print("Login successful!")
        return True

    def fetch_data(self) -> None:
        """
        Fetch all needed data from the ERP (materials, locations, movements, etc.).

        This method updates the instance attributes with the latest data
        from the corresponding API endpoints.
        """
        endpoints = {
            "materials": "/api/materials",
            "locations": "/api/locations",
            "movements": "/api/goods-movements",
            "customer_orders": "/api/customer-orders",
            "production_orders": "/api/production-orders",
            "purchase_orders": "/api/purchase-orders",
            "source_of_supply": "/api/source-of-supply",
        }

        for attr, endpoint in endpoints.items():
            url = f"{BASE_URL}{endpoint}"
            resp = self.session.get(url)
            resp.raise_for_status()
            setattr(self, attr, resp.json())

    def calculate_current_inventory(
        self, selected_material: str = "all", selected_location: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Compute the current inventory up to today's date, filtered by material/location.

        Args:
            selected_material (str): If not "all", restricts inventory to the given material ID.
            selected_location (str): If not "all", restricts inventory to the given location ID.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries where each dictionary represents
            the material ID, location ID, and the computed quantity.
        """
        today = datetime.datetime.now()
        inventory: Dict[str, float] = {}

        for movement in self.movements:
            mat_id = str(movement["materialId"])
            loc_id = str(movement["locationId"])

            # Apply filters
            if selected_material != "all" and mat_id != selected_material:
                continue
            if selected_location != "all" and loc_id != selected_location:
                continue

            movement_date = datetime.datetime.fromisoformat(movement["movementDate"])
            if movement_date <= today:
                key = f"{mat_id}-{loc_id}"
                curr_qty = inventory.get(key, 0.0)

                if movement["movementType"] == "Receipt":
                    curr_qty += float(movement["quantity"])
                elif movement["movementType"] == "Issue":
                    curr_qty -= float(movement["quantity"])

                inventory[key] = curr_qty

        # Convert dictionary to a list of dicts
        current_inventory_list = []
        for combo, quantity in inventory.items():
            mat, loc = combo.split("-")
            current_inventory_list.append(
                {
                    "materialId": int(mat),
                    "locationId": int(loc),
                    "quantity": quantity,
                }
            )
        return current_inventory_list

    def calculate_projected_inventory(
        self, selected_material: str = "all", selected_location: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Compute the projected inventory over the next 12 weeks, filtered by material/location.

        This calculation factors in current inventory, future receipts (purchase orders,
        goods movements, production orders), and issues (customer orders, goods movements).

        Args:
            selected_material (str): If not "all", restricts inventory to the given material ID.
            selected_location (str): If not "all", restricts inventory to the given location ID.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries where each dictionary represents
            projected inventory details for each week (up to 12 weeks).
        """

        # Safely treat None as empty lists
        movements = self.movements if self.movements else []
        materials = self.materials if self.materials else []
        locations = self.locations if self.locations else []
        customer_orders = self.customer_orders if self.customer_orders else []
        production_orders = self.production_orders if self.production_orders else []
        purchase_orders = self.purchase_orders if self.purchase_orders else []
        source_of_supply = self.source_of_supply if self.source_of_supply else []

        # Compute the current inventory first
        current_stock = self.calculate_current_inventory(selected_material, selected_location)

        # Get all unique material-location combos from current stock
        combos = set(f"{item['materialId']}-{item['locationId']}" for item in current_stock)

        # Build a quick dictionary for current stock for easy lookups
        current_dict = {
            f"{item['materialId']}-{item['locationId']}": item["quantity"]
            for item in current_stock
        }

        # Determine the Monday of the current week
        today = datetime.date.today()
        offset_to_monday = today.weekday()  # Monday=0, Sunday=6
        start_monday = today - datetime.timedelta(days=offset_to_monday)

        # Generate the next 12 Mondays
        monday_dates = [start_monday + datetime.timedelta(weeks=i) for i in range(12)]

        projected_list: List[Dict[str, Any]] = []

        for combo in combos:
            mat_str, loc_str = combo.split("-")
            mat_id = int(mat_str)
            loc_id = int(loc_str)

            # Apply filters
            if selected_material != "all" and mat_str != selected_material:
                continue
            if selected_location != "all" and loc_str != selected_location:
                continue

            # Starting quantity is from current computed stock
            last_week_qty = current_dict.get(combo, 0.0)

            for week_start_date in monday_dates:
                # The 'weekEnd' is 6 days from weekStart
                week_end_date = week_start_date + datetime.timedelta(days=6)

                receipts = 0.0
                issues = 0.0

                for move in movements:
                    movement_date = datetime.datetime.strptime(
                        move["movementDate"],
                        "%Y-%m-%d %H:%M:%S"
                    ).date()
                    if (
                        move["materialId"] == mat_id
                        and move["locationId"] == loc_id
                        and week_start_date <= movement_date <= week_end_date
                    ):
                        # Adjust logic to suit your system: add for receipts, subtract for issues
                        if move["movementType"] == "Receipt":
                            receipts += float(move["quantity"])
                        elif move["movementType"] == "Issue":
                            issues += float(move["quantity"])

                week_purchase_orders = 0.0
                for po in purchase_orders:
                    order_date = datetime.datetime.strptime(
                        po["orderDate"],
                        "%Y-%m-%d %H:%M:%S"
                    ).date()
                    if (
                        po["materialId"] == mat_id
                        and po["shipToLocationId"] == loc_id
                        and week_start_date <= order_date <= week_end_date
                    ):
                        week_purchase_orders += float(po["quantity"])

                week_customer_orders = 0.0
                for co in customer_orders:
                    order_date = datetime.datetime.strptime(
                        co["orderDate"],
                        "%Y-%m-%d %H:%M:%S"
                    ).date()
                    if (
                        co["materialId"] == mat_id
                        and co["shipFromLocationId"] == loc_id
                        and week_start_date <= order_date <= week_end_date
                    ):
                        week_customer_orders += float(co["quantity"])

                week_production_orders = 0.0
                for prod in production_orders:
                    prod_date = datetime.date.fromisoformat(
                        prod["orderDate"].split("T")[0]
                    )
                    if (
                        prod["materialId"] == mat_id
                        and prod["locationId"] == loc_id
                        and prod["status"] == "Completed"
                        and week_start_date <= prod_date <= week_end_date
                    ):
                        week_production_orders += float(prod["quantity"])

                projected_quantity = (
                    last_week_qty
                    + receipts
                    - issues
                    + week_purchase_orders
                    - week_customer_orders
                    + week_production_orders
                )

                # Minimum/Maximum Stock Levels (from source_of_supply)
                min_stock_level = 0.0
                max_stock_level = 0.0
                for sos in source_of_supply:
                    if sos["materialId"] == mat_id and sos["locationId"] == loc_id:
                        min_stock_level = float(sos.get("minimumStockLevel", 0.0))
                        max_stock_level = float(sos.get("maximumStockLevel", 0.0))
                        break

                projected_list.append(
                    {
                        "materialId": mat_id,
                        "locationId": loc_id,
                        "weekStart": week_start_date.isoformat(),
                        "projectedQuantity": projected_quantity,
                        "receipts": receipts,
                        "issues": issues,
                        "purchaseOrders": week_purchase_orders,
                        "customerOrders": week_customer_orders,
                        "productionOrders": week_production_orders,
                        "minStockLevel": min_stock_level,
                        "maxStockLevel": max_stock_level,
                    }
                )

                last_week_qty = projected_quantity

        return projected_list

    def generate_current_inventory_table(
        self, selected_material: str = "all", selected_location: str = "all"
    ) -> str:
        """
        Generate a markdown table for the current inventory.

        Args:
            selected_material (str): If not "all", restricts inventory to the given material ID.
            selected_location (str): If not "all", restricts inventory to the given location ID.

        Returns:
            str: A markdown string containing a table of current inventory data.
        """
        current_inventory = self.calculate_current_inventory(selected_material, selected_location)

        # Build dictionaries for name lookups (id -> name)
        material_lookup = {m["id"]: m["name"] for m in self.materials}
        location_lookup = {l["id"]: l["name"] for l in self.locations}

        lines = ["| Material | Location | Current Stock |", "| --- | --- | ---: |"]

        for row in current_inventory:
            mat_name = material_lookup.get(row["materialId"], str(row["materialId"]))
            loc_name = location_lookup.get(row["locationId"], str(row["locationId"]))
            quantity_str = f"{row['quantity']:.2f}"
            lines.append(f"| {mat_name} | {loc_name} | {quantity_str} |")

        return "\n".join(lines)

    def generate_projected_inventory_table(
        self, selected_material: str = "all", selected_location: str = "all"
    ) -> str:
        """
        Generate a markdown table for the projected inventory over the next 12 weeks.

        Args:
            selected_material (str): If not "all", restricts inventory to the given material ID.
            selected_location (str): If not "all", restricts inventory to the given location ID.

        Returns:
            str: A markdown string containing a table of projected inventory data
                 for each week (up to 12 weeks).
        """
        projected_inventory = self.calculate_projected_inventory(
            selected_material, selected_location
        )

        # Build dictionaries for name lookups (id -> name)
        material_lookup = {m["id"]: m["name"] for m in self.materials}
        location_lookup = {l["id"]: l["name"] for l in self.locations}

        lines = [
            (
                "| Material | Location | Week Starting | Projected Stock | Receipts | Issues |"
                " Purchase Orders | Customer Orders | Production Orders | Min Stock Lv | Max Stock Lv |"
            ),
            (
                "| --- | --- | --- | ---: | ---: | ---: | ---: |"
                " ---: | ---: | ---: | ---: |"
            ),
        ]

        # Sort results for consistent table order
        projected_inventory.sort(key=lambda x: (x["materialId"], x["locationId"], x["weekStart"]))

        for row in projected_inventory:
            mat_name = material_lookup.get(row["materialId"], str(row["materialId"]))
            loc_name = location_lookup.get(row["locationId"], str(row["locationId"]))
            week_str = datetime.datetime.fromisoformat(row["weekStart"]).strftime("%Y-%m-%d")
            pq = f"{row['projectedQuantity']:.2f}"
            rec = f"{row['receipts']:.2f}"
            iss = f"{row['issues']:.2f}"
            po = f"{row['purchaseOrders']:.2f}"
            co = f"{row['customerOrders']:.2f}"
            prod = f"{row['productionOrders']:.2f}"
            min_lv = f"{row['minStockLevel']:.2f}"
            max_lv = f"{row['maxStockLevel']:.2f}"

            lines.append(
                f"| {mat_name} | {loc_name} | {week_str} | {pq} | {rec} | {iss} |"
                f" {po} | {co} | {prod} | {min_lv} | {max_lv} |"
            )

        return "\n".join(lines)

# ========================== Helper Functions ==========================
inventory_overview = InventoryOverview()

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

async def get_inventory_projection(state):
    projected_inventory= inventory_overview.generate_projected_inventory_table()
    return Command(goto="create_purchase_requisition", update={"projected_inventory":projected_inventory})

async def create_purchase_requisition(state):
    class ProposedPurchaseOrders(TypedDict):
        material : str
        quantity: float
        unitOfMeasure: str
        shipToLocationId: str
        requestedDate: str

    class ListProposedPurchaseOrders(TypedDict):
        listProposedPurchaseOrders: List[ProposedPurchaseOrders]


    llm = AzureChatOpenAI(
        base_url=os.getenv("AZURE_GPTO1_BASE_URL"),
        api_key=os.getenv("AZURE_GPTO1_KEY"),
        api_version=os.getenv("AZURE_GPTO1_API_VERSION")
    )
    purchase_requisition= llm.with_structured_output(ListProposedPurchaseOrders, strict=True).invoke(f"""
    As a material planner, you will use the ERP's inventory projections to maintain stock 
    levels within the weekly minimum and maximum thresholds. Whenever a material-location 
    combination exceeds these limits, propose a purchase order. Keep in mind that inventory 
    in one week affects future weeks, so you'll need to simulate projections across 
    multiple weeks to minimize stock levels without falling below the accepted boundaries.
    {state["projected_inventory"]}

    """)
    return Command(goto="filter_for_material", update={"purchase_requisition": purchase_requisition})

async def filter_for_material(state):

    materials = {po["material"] for po in state["purchase_requisition"]["listProposedPurchaseOrders"]}

    # 2. Filter the 'source_of_supply' data where 'materialName' matches any material in 'materials'
    filtered_sources = [
        sos for sos in inventory_overview.source_of_supply
        if sos["materialName"] in materials
    ]

    # print(filtered_sources)
    # [{'id': 20,
    #   'billOfMaterialId': 0,
    #   'replenishmentLeadtime': '14.00',
    #   'minimumOrderQuantity': '1.00',
    #   'minimumStockLevel': '1.00',
    #   'maximumStockLevel': '5.00',
    #   'deliveryConditions': 'EXW (Chemnitz)',
    #   'materialName': 'FERT-SPEED',
    #   'supplierName': 'Werk Chemnitz',
    #   'locationName': 'Lager Leipzig',
    #   'materialId': 6,
    #   'supplierId': 9,
    #   'locationId': 3}]

    filtered_materials = [
        mat for mat in inventory_overview.materials
        if mat["name"] in materials
    ]

    # filtered_materials
    materials = {po["material"] for po in state["purchase_requisition"]["listProposedPurchaseOrders"]}

    # 2. Filter the 'source_of_supply' data where 'materialName' matches any material in 'materials'
    filtered_sources = [
        sos for sos in inventory_overview.source_of_supply
        if sos["materialName"] in materials
    ]

    # print(filtered_sources)
    # [{'id': 20,
    #   'billOfMaterialId': 0,
    #   'replenishmentLeadtime': '14.00',
    #   'minimumOrderQuantity': '1.00',
    #   'minimumStockLevel': '1.00',
    #   'maximumStockLevel': '5.00',
    #   'deliveryConditions': 'EXW (Chemnitz)',
    #   'materialName': 'FERT-SPEED',
    #   'supplierName': 'Werk Chemnitz',
    #   'locationName': 'Lager Leipzig',
    #   'materialId': 6,
    #   'supplierId': 9,
    #   'locationId': 3}]

    filtered_materials = [
        mat for mat in inventory_overview.materials
        if mat["name"] in materials
    ]

    # filtered_materials

    # [{'id': 6,
    #   'name': 'FERT-SPEED',
    #   'description': 'Rennrad „Speedster“',
    #   'unitOfMeasure': 'Piece',
    #   'standardCost': '1200.00'}]

    return Command(goto="purchase_order", 
                   update={"filtered_sources": filtered_sources, 
                           "filtered_materials": filtered_materials})

async def purchase_order(state):
    class PurchaseOrders(TypedDict):
        supplierId : str
        materialId: float
        quantity: str
        unitOfMeasure: str
        shipToLocationId: str
        orderDate: str
        status: str

    class ListPurchaseOrders(TypedDict):
        listPurchaseOrders: List[PurchaseOrders]

    purchases_order = llm.with_structured_output(ListPurchaseOrders, strict=True).invoke(f"""
    The following purchase requisitions have been identified as necessary. 
    Below is the master data from the source of supply. As a material planner, 
    you must transform these requisitions into purchase orders based on the current master data. 
    Be aware that supplier lead times requires adjustments to the intended delivery dates. Please update the purchase requisitions accordingly.
                                                                                                                                                                                        
    # Purchase Requisition                                                                  
    {state["purchase_requisition"]}

    # Master data - Source of Supply
    {state["filtered_sources"]}

    # Master data - Materials
    {state["filtered_materials"]}

    'status' is always is 'In Progress'

    """)
    return Command(goto="notify_manager", 
                   update={"purchases_order": purchases_order})


async def notify_manager(state):
    """
    Send a Teams message to the manager with the proposed purchase order,
    and handle the approval process.
    """

    # Check if manager_response is empty
    if state["manager_response"] == "":
        # Prepare the Teams message content
        message_markdown = f"""
        **Dear Manager,**

        The following purchase order need to be placed:
        {state['purchases_order']}

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
    purchases_order = state['purchases_order']

    for purchase_order in purchases_order:
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
    incoming_order: dict
    projected_inventory: str
    purchase_requisition: List
    filtered_sources: List
    filtered_materials: List
    purchases_order: List
    thread_id: str
    manager_response: str

# ========================== Build the Workflow Graph ==========================

builder = StateGraph(WorkflowState)

builder.add_node("get_inventory_projection", get_inventory_projection)
builder.add_node("create_purchase_requisition", create_purchase_requisition)
builder.add_node("filter_for_material", filter_for_material)
builder.add_node("purchase_order", purchase_order)
builder.add_node("notify_manager", notify_manager)
builder.add_node("place_purchase_order", place_purchase_order)

builder.add_edge(START, "get_inventory_projection")
builder.add_edge("get_inventory_projection", "create_purchase_requisition")
builder.add_edge("create_purchase_requisition", "filter_for_material")
builder.add_edge("filter_for_material", "purchase_order")
builder.add_edge("purchase_order", "notify_manager")
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
        "incoming_order": data.get("incoming_order", {}),
        "projected_inventory": "",
        "purchase_requisition": "",
        "filtered_sources": "",
        "filtered_materials": "",
        "purchases_order": "",
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



