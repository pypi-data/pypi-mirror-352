"""
This module provides a toolkit for interacting with the master data of the Recall Space
ERP. It includes functionalities to retrieve data such as materials, locations, suppliers,
and sources of supply, as well as create, update, and delete them.

Classes:
    MasterDataERPToolKit: A toolkit class for interacting with the master data ERP API.
"""

import aiohttp
from agent_builder.builders.tool_builder import ToolBuilder
from typing import List

# Below are the new schema mappings with more explicit field definitions,
# ensuring that the agent / tool knows exactly what data to provide.

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

# ---------------------------
# MATERIALS
# ---------------------------
class MaterialCreateData(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    unitOfMeasure: str = Field(..., min_length=1)
    standardCost: float = Field(..., ge=0.0, description="Must be ≥ 0")

class MaterialPatchData(BaseModel):
    # For patch, all fields are optional
    name: Optional[str] = None
    description: Optional[str] = None
    unitOfMeasure: Optional[str] = None
    standardCost: Optional[float] = Field(None, ge=0.0)

class GetMaterialsInputSchema(BaseModel):
    """No input needed for GET materials."""
    pass

class CreateMaterialInputSchema(BaseModel):
    """Schema for creating a new material record."""
    data: MaterialCreateData

class PatchMaterialInputSchema(BaseModel):
    """Schema for patching an existing material record."""
    material_id: int
    data: MaterialPatchData

class DeleteMaterialInputSchema(BaseModel):
    """Schema for deleting a Material by ID."""
    material_id: int

# ---------------------------
# LOCATIONS
# ---------------------------
class LocationCreateData(BaseModel):
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    capacity: Optional[float] = Field(None, ge=0.0, description="Must be ≥ 0 if provided")
    unitOfMeasure: str = Field(..., min_length=1)

class LocationPatchData(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[float] = Field(None, ge=0.0)
    unitOfMeasure: Optional[str] = None

class GetLocationsInputSchema(BaseModel):
    pass

class CreateLocationInputSchema(BaseModel):
    data: LocationCreateData

class PatchLocationInputSchema(BaseModel):
    location_id: int
    data: LocationPatchData

class DeleteLocationInputSchema(BaseModel):
    location_id: int

# ---------------------------
# SUPPLIERS
# ---------------------------
class SupplierCreateData(BaseModel):
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    contactInfo: str = Field(..., min_length=1)
    performanceScore: float = Field(..., ge=0.0, lt=100.0)
    paymentConditions: Optional[str] = None

class SupplierPatchData(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contactInfo: Optional[str] = None
    performanceScore: Optional[float] = Field(None, ge=0.0, lt=100.0)
    paymentConditions: Optional[str] = None

class GetSuppliersInputSchema(BaseModel):
    pass

class CreateSupplierInputSchema(BaseModel):
    data: SupplierCreateData

class PatchSupplierInputSchema(BaseModel):
    supplier_id: int
    data: SupplierPatchData

class DeleteSupplierInputSchema(BaseModel):
    supplier_id: int

# ---------------------------
# SOURCE OF SUPPLY
# ---------------------------
class SourceOfSupplyCreateData(BaseModel):
    materialId: int
    supplierId: Optional[int] = None
    locationId: int
    billOfMaterialId: Optional[int] = None
    replenishmentLeadtime: float = Field(..., ge=0.0)
    minimumOrderQuantity: float = Field(..., ge=0.0)
    minimumStockLevel: float = Field(..., ge=0.0)
    maximumStockLevel: float = Field(..., ge=0.0)
    deliveryConditions: Optional[str] = None

class SourceOfSupplyPatchData(BaseModel):
    materialId: Optional[int] = None
    supplierId: Optional[int] = None
    locationId: Optional[int] = None
    billOfMaterialId: Optional[int] = None
    replenishmentLeadtime: Optional[float] = Field(None, ge=0.0)
    minimumOrderQuantity: Optional[float] = Field(None, ge=0.0)
    minimumStockLevel: Optional[float] = Field(None, ge=0.0)
    maximumStockLevel: Optional[float] = Field(None, ge=0.0)
    deliveryConditions: Optional[str] = None

class GetSourceOfSupplyInputSchema(BaseModel):
    pass

class CreateSourceOfSupplyInputSchema(BaseModel):
    data: SourceOfSupplyCreateData

class PatchSourceOfSupplyInputSchema(BaseModel):
    source_id: int
    data: SourceOfSupplyPatchData

class DeleteSourceOfSupplyInputSchema(BaseModel):
    source_id: int

# ---------------------------
# SCHEMA MAPPINGS
# ---------------------------
schema_mappings = {
    # Materials
    "aget_materials": {
        "description": "Retrieve a list of all materials.",
        "input_schema": GetMaterialsInputSchema,
    },
    "acreate_material": {
        "description": "Create a new material record.",
        "input_schema": CreateMaterialInputSchema,
    },
    "apatch_material": {
        "description": "Patch (update) an existing material record.",
        "input_schema": PatchMaterialInputSchema,
    },
    "adelete_material": {
        "description": "Delete a material record by its ID.",
        "input_schema": DeleteMaterialInputSchema,
    },

    # Locations
    "aget_locations": {
        "description": "Retrieve a list of all locations.",
        "input_schema": GetLocationsInputSchema,
    },
    "acreate_location": {
        "description": "Create a new location record.",
        "input_schema": CreateLocationInputSchema,
    },
    "apatch_location": {
        "description": "Patch (update) an existing location record.",
        "input_schema": PatchLocationInputSchema,
    },
    "adelete_location": {
        "description": "Delete a location record by its ID.",
        "input_schema": DeleteLocationInputSchema,
    },

    # Suppliers
    "aget_suppliers": {
        "description": "Retrieve a list of all suppliers.",
        "input_schema": GetSuppliersInputSchema,
    },
    "acreate_supplier": {
        "description": "Create a new supplier record.",
        "input_schema": CreateSupplierInputSchema,
    },
    "apatch_supplier": {
        "description": "Patch (update) an existing supplier record.",
        "input_schema": PatchSupplierInputSchema,
    },
    "adelete_supplier": {
        "description": "Delete a supplier record by its ID.",
        "input_schema": DeleteSupplierInputSchema,
    },

    # Source of Supply
    "aget_source_of_supply": {
        "description": "Retrieve source of supply information.",
        "input_schema": GetSourceOfSupplyInputSchema,
    },
    "acreate_source_of_supply": {
        "description": "Create a new source of supply record.",
        "input_schema": CreateSourceOfSupplyInputSchema,
    },
    "apatch_source_of_supply": {
        "description": "Patch (update) an existing source of supply record.",
        "input_schema": PatchSourceOfSupplyInputSchema,
    },
    "adelete_source_of_supply": {
        "description": "Delete a source of supply record by its ID.",
        "input_schema": DeleteSourceOfSupplyInputSchema,
    },
}
