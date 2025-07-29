"""

Below is an example "TransactionDataERPToolKit" module, similar to the "MasterDataERPToolKit."
It includes the toolkit class with
methods to interact with the Recall Space ERP's transaction-related API endpoints.

Adjust field definitions or add validations as needed for your specific use case.
"""

import aiohttp
from typing import Optional, Any, Dict, Union, List
from pydantic import BaseModel, Field
from agent_builder.builders.tool_builder import ToolBuilder
from recall_space_agents.toolkits.transcational_data_erp.schema_mappings import (
    schema_mappings,
)


class TransactionDataERPToolKit:
    """
    A toolkit class for interacting with the Transaction Data ERP system API.
    It provides asynchronous methods for retrieving, creating, updating, and
    deleting transaction data such as customer orders, forecasts, goods movements,
    purchase orders, and production orders.
    """

    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize the TransactionDataERPToolKit with necessary credentials.

        Args:
            base_url (str): The base URL of the ERP API.
            username (str): Username for authentication.
            password (str): Password for authentication.
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = aiohttp.ClientSession()
        self.schema_mappings = schema_mappings
        self._logged_in = False

    async def _login(self) -> None:
        """
        Logs into the ERP system and sets up the session for subsequent API requests.
        """
        login_url = f"{self.base_url}/api/login"
        login_payload = {"username": self.username, "password": self.password}
        async with self.session.post(login_url, json=login_payload) as response:
            if response.status != 200:
                raise Exception("Login failed.")
            self._logged_in = True
            print("Login successful!")

    def _ensure_dict(self, payload: Any) -> Union[Dict[str, Any], None]:
        """
        Helper method to ensure that 'payload' is a JSON-serializable dictionary.
        If it's a Pydantic BaseModel, convert it to dict. Otherwise, return as is.
        """
        from pydantic import BaseModel

        if isinstance(payload, BaseModel):
            return payload.model_dump(exclude_unset=True)
        return payload

    # ---------------
    # Customer Orders
    # ---------------
    async def aget_customer_orders(self):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/customer-orders"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def acreate_customer_order(self, data: Dict[str, Any]):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/customer-orders"
        payload = self._ensure_dict(data)
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def apatch_customer_order(self, order_id: int, data: Dict[str, Any]):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/customer-orders/{order_id}"
        payload = self._ensure_dict(data)
        async with self.session.patch(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def adelete_customer_order(self, order_id: int):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/customer-orders/{order_id}"
        async with self.session.delete(url) as response:
            response.raise_for_status()
            return await response.json()

    # ---------------
    # Forecasts
    # ---------------
    async def aget_forecasts(self):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/forecasts"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def acreate_forecast(self, data: Dict[str, Any]):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/forecasts"
        payload = self._ensure_dict(data)
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def apatch_forecast(self, forecast_id: int, data: Dict[str, Any]):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/forecasts/{forecast_id}"
        payload = self._ensure_dict(data)
        async with self.session.patch(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def adelete_forecast(self, forecast_id: int):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/forecasts/{forecast_id}"
        async with self.session.delete(url) as response:
            response.raise_for_status()
            return await response.json()

    # ---------------
    # Goods Movements
    # ---------------
    async def aget_goods_movements(self):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/goods-movements"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def acreate_goods_movement(self, data: Dict[str, Any]):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/goods-movements"
        payload = self._ensure_dict(data)
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def apatch_goods_movement(self, movement_id: int, data: Dict[str, Any]):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/goods-movements/{movement_id}"
        payload = self._ensure_dict(data)
        async with self.session.patch(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def adelete_goods_movement(self, movement_id: int):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/goods-movements/{movement_id}"
        async with self.session.delete(url) as response:
            response.raise_for_status()
            return await response.json()

    # ---------------
    # Purchase Orders
    # ---------------
    async def aget_purchase_orders(self):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/purchase-orders"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def acreate_purchase_order(self, data: Dict[str, Any]):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/purchase-orders"
        payload = self._ensure_dict(data)
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def apatch_purchase_order(self, purchase_order_id: int, data: Dict[str, Any]):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/purchase-orders/{purchase_order_id}"
        payload = self._ensure_dict(data)
        async with self.session.patch(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def adelete_purchase_order(self, purchase_order_id: int):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/purchase-orders/{purchase_order_id}"
        async with self.session.delete(url) as response:
            response.raise_for_status()
            return await response.json()

    # ---------------
    # Production Orders
    # ---------------
    async def aget_production_orders(self):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/production-orders"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def acreate_production_order(self, data: Dict[str, Any]):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/production-orders"
        payload = self._ensure_dict(data)
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def apatch_production_order(
        self, production_order_id: int, data: Dict[str, Any]
    ):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/production-orders/{production_order_id}"
        payload = self._ensure_dict(data)
        async with self.session.patch(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def adelete_production_order(self, production_order_id: int):
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/production-orders/{production_order_id}"
        async with self.session.delete(url) as response:
            response.raise_for_status()
            return await response.json()

    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in the toolkit.

        Returns:
            list of ToolBuilder objects, each representing a method in the toolkit.
        """
        tools = []
        for method_name, method_info in self.schema_mappings.items():
            tool_builder = ToolBuilder()
            tool_builder.set_name(name=method_name)
            tool_builder.set_function(getattr(self, method_name))
            tool_builder.set_coroutine(getattr(self, method_name))
            tool_builder.set_description(description=method_info["description"])
            tool_builder.set_schema(schema=method_info["input_schema"])
            tool = tool_builder.build()
            tools.append(tool)
        return tools

    async def close(self):
        """Closes the aiohttp session."""
        await self.session.close()
