"""

This module provides a toolkit for interacting with the master data of the Recall Space
ERP. It includes functionalities to retrieve data such as materials, locations,
suppliers, and sources of supply, as well as create, update, and delete them.

Classes:
    MasterDataERPToolKit: A toolkit class for interacting with the master data ERP API.
"""

import aiohttp
from typing import Optional, Any, Dict, Union
from pydantic import BaseModel
from agent_builder.builders.tool_builder import ToolBuilder
from recall_space_agents.toolkits.master_data_erp.schema_mappings import schema_mappings


class MasterDataERPToolKit:
    """
    A toolkit class for interacting with the Master Data ERP system API.
    """

    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize the MasterDataERPToolKit with necessary credentials.

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
        if isinstance(payload, BaseModel):
            # For PATCH, you might use exclude_unset=True so you only send changed fields.
            return payload.model_dump(exclude_unset=True)
        return payload

    # -----------------------
    # Materials
    # -----------------------
    async def aget_materials(self):
        """Asynchronously retrieve a list of materials."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/materials"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def acreate_material(self, data: Dict[str, Any]):
        """Asynchronously create a new material."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/materials"
        # Ensure data is a dictionary
        payload = self._ensure_dict(data)
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def apatch_material(self, material_id: int, data: Dict[str, Any]):
        """Asynchronously update (patch) an existing material."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/materials/{material_id}"
        payload = self._ensure_dict(data)
        async with self.session.patch(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def adelete_material(self, material_id: int):
        """Asynchronously delete a material by its ID."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/materials/{material_id}"
        async with self.session.delete(url) as response:
            response.raise_for_status()
            return await response.json()

    # -----------------------
    # Locations
    # -----------------------
    async def aget_locations(self):
        """Asynchronously retrieve a list of locations."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/locations"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def acreate_location(self, data: Dict[str, Any]):
        """Asynchronously create a new location."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/locations"
        payload = self._ensure_dict(data)
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def apatch_location(self, location_id: int, data: Dict[str, Any]):
        """Asynchronously update (patch) an existing location."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/locations/{location_id}"
        payload = self._ensure_dict(data)
        async with self.session.patch(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def adelete_location(self, location_id: int):
        """Asynchronously delete a location by its ID."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/locations/{location_id}"
        async with self.session.delete(url) as response:
            response.raise_for_status()
            return await response.json()

    # -----------------------
    # Suppliers
    # -----------------------
    async def aget_suppliers(self):
        """Asynchronously retrieve a list of suppliers."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/suppliers"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def acreate_supplier(self, data: Dict[str, Any]):
        """Asynchronously create a new supplier."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/suppliers"
        payload = self._ensure_dict(data)
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def apatch_supplier(self, supplier_id: int, data: Dict[str, Any]):
        """Asynchronously update (patch) an existing supplier."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/suppliers/{supplier_id}"
        payload = self._ensure_dict(data)
        async with self.session.patch(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def adelete_supplier(self, supplier_id: int):
        """Asynchronously delete a supplier by its ID."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/suppliers/{supplier_id}"
        async with self.session.delete(url) as response:
            response.raise_for_status()
            return await response.json()

    # -----------------------
    # Source of Supply
    # -----------------------
    async def aget_source_of_supply(self):
        """Asynchronously retrieve the source of supply information."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/source-of-supply"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def acreate_source_of_supply(self, data: Dict[str, Any]):
        """Asynchronously create a new source of supply."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/source-of-supply"
        payload = self._ensure_dict(data)
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def apatch_source_of_supply(self, source_id: int, data: Dict[str, Any]):
        """Asynchronously update (patch) an existing source of supply record."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/source-of-supply/{source_id}"
        payload = self._ensure_dict(data)
        async with self.session.patch(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def adelete_source_of_supply(self, source_id: int):
        """Asynchronously delete a source of supply by its ID."""
        if not self._logged_in:
            await self._login()
        url = f"{self.base_url}/api/source-of-supply/{source_id}"
        async with self.session.delete(url) as response:
            response.raise_for_status()
            return await response.json()

    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in the toolkit.

        Returns:
            list: A list of ToolBuilder objects, each representing a method in the toolkit.
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
