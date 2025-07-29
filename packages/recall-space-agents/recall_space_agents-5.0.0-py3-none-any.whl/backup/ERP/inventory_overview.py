from typing import List
import requests
from typing import List, Dict, Any
import datetime

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
        if self.materials == []:
            self.fetch_data()
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
        if self.materials == []:
            self.fetch_data()
        # Safely treat None as empty lists
        movements = self.movements if self.movements else []
        materials = self.materials if self.materials else []
        locations = self.locations if self.locations else []
        customer_orders = self.customer_orders if self.customer_orders else []
        production_orders = self.production_orders if self.production_orders else []
        purchase_orders = self.purchase_orders if self.purchase_orders else []
        source_of_supply = self.source_of_supply if self.source_of_supply else []

        # Compute the current inventory first
        current_stock = self.calculate_current_inventory(
            selected_material, selected_location
        )

        # Get all unique material-location combos from current stock
        combos = set(
            f"{item['materialId']}-{item['locationId']}" for item in current_stock
        )

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
                        move["movementDate"], "%Y-%m-%d %H:%M:%S"
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
                        po["orderDate"], "%Y-%m-%d %H:%M:%S"
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
                        co["orderDate"], "%Y-%m-%d %H:%M:%S"
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
        if self.materials == []:
            self.fetch_data()
        current_inventory = self.calculate_current_inventory(
            selected_material, selected_location
        )

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
        if self.materials == []:
            self.fetch_data()
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
        projected_inventory.sort(
            key=lambda x: (x["materialId"], x["locationId"], x["weekStart"])
        )

        for row in projected_inventory:
            mat_name = material_lookup.get(row["materialId"], str(row["materialId"]))
            loc_name = location_lookup.get(row["locationId"], str(row["locationId"]))
            week_str = datetime.datetime.fromisoformat(row["weekStart"]).strftime(
                "%Y-%m-%d"
            )
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
