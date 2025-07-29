####################################################################################################
# UPDATED SCHEMA MAPPINGS TO ALIGN WITH ACTUAL ERP DATABASE SCHEMA
####################################################################################################
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List, Union

# -----------------------------------------------------------------------------
# CUSTOMER ORDERS
# -----------------------------------------------------------------------------
class CustomerOrderCreateData(BaseModel):
    customerId: int = Field(..., description="ID of the customer placing the order")
    materialId: int = Field(..., description="ID of the material being ordered")
    quantity: float = Field(..., description="Order quantity (must be > 0)")
    unitOfMeasure: str = Field(..., description="E.g.: 'Piece', 'Each', 'Kg', 'Liter', etc.")
    shipToAddress: str = Field(..., description="Shipping address for the order")
    shipFromLocationId: int = Field(..., description="Location ID from where material is shipped")
    orderDate: str = Field(..., description="Order date in ISO8601 or YYYY-MM-DD format")
    status: str = Field(..., description="Status of the order: 'New', 'In Progress', 'Completed', 'Cancelled'")
    requestedDeliveryDate: Optional[str] = Field(None, description="Requested delivery date (optional)")
    confirmedDeliveryDate: Optional[str] = Field(None, description="Confirmed delivery date (optional)")

class CustomerOrderPatchData(BaseModel):
    customerId: Optional[int] = Field(None, description="ID of the customer placing the order")
    materialId: Optional[int] = Field(None, description="ID of the material being ordered")
    quantity: Optional[float] = Field(None, description="Order quantity (must be > 0)")
    unitOfMeasure: Optional[str] = Field(None, description="E.g.: 'Piece', 'Each', 'Kg', 'Liter', etc.")
    shipToAddress: Optional[str] = Field(None, description="Shipping address for the order")
    shipFromLocationId: Optional[int] = Field(None, description="Location ID from where material is shipped")
    orderDate: Optional[str] = Field(None, description="Order date in ISO8601 or YYYY-MM-DD format")
    status: Optional[str] = Field(None, description="Status of the order: 'New', 'In Progress', 'Completed', 'Cancelled'")
    requestedDeliveryDate: Optional[str] = Field(None, description="Requested delivery date (optional)")
    confirmedDeliveryDate: Optional[str] = Field(None, description="Confirmed delivery date (optional)")

class GetCustomerOrdersInputSchema(BaseModel):
    """No specific input needed to retrieve all customer orders."""
    pass

class CreateCustomerOrderInputSchema(BaseModel):
    data: CustomerOrderCreateData

class PatchCustomerOrderInputSchema(BaseModel):
    order_id: int
    data: CustomerOrderPatchData

class DeleteCustomerOrderInputSchema(BaseModel):
    order_id: int

# -----------------------------------------------------------------------------
# FORECASTS
# -----------------------------------------------------------------------------
class ForecastCreateData(BaseModel):
    materialId: int = Field(..., description="Material ID for the forecast")
    locationId: int = Field(..., description="Location ID for the forecast")
    forecastDate: str = Field(..., description="Forecast date in ISO8601 or YYYY-MM-DD format")
    quantity: float = Field(..., description="Forecasted quantity (must be > 0)")
    unitOfMeasure: str = Field(..., description="E.g.: 'Piece', 'Each', 'Kg', 'Liter', etc.")

class ForecastPatchData(BaseModel):
    materialId: Optional[int] = Field(None, description="Material ID for the forecast")
    locationId: Optional[int] = Field(None, description="Location ID for the forecast")
    forecastDate: Optional[str] = Field(None, description="Forecast date in ISO8601 or YYYY-MM-DD format")
    quantity: Optional[float] = Field(None, description="Forecasted quantity")
    unitOfMeasure: Optional[str] = Field(None, description="Unit of measure")

class GetForecastsInputSchema(BaseModel):
    pass

class CreateForecastInputSchema(BaseModel):
    data: ForecastCreateData

class PatchForecastInputSchema(BaseModel):
    forecast_id: int
    data: ForecastPatchData

class DeleteForecastInputSchema(BaseModel):
    forecast_id: int

# -----------------------------------------------------------------------------
# GOODS MOVEMENTS
# -----------------------------------------------------------------------------
class GoodsMovementCreateData(BaseModel):
    materialId: int = Field(..., description="Material ID for the movement")
    locationId: int = Field(..., description="Location ID where movement occurs")
    quantity: float = Field(..., description="Movement quantity (must be > 0)")
    unitOfMeasure: str = Field(..., description="E.g.: 'Piece', 'Each', 'Kg', 'Liter', etc.")
    movementType: str = Field(..., description="One of: 'Receipt', 'Issue', 'Transfer', 'Adjustment'")
    referenceDocumentId: Optional[str] = Field(None, description="Reference document if any")
    movementDate: str = Field(..., description="Movement date in ISO8601 or YYYY-MM-DD format")

class GoodsMovementPatchData(BaseModel):
    materialId: Optional[int] = Field(None, description="Material ID for the movement")
    locationId: Optional[int] = Field(None, description="Location ID where movement occurs")
    quantity: Optional[float] = Field(None, description="Movement quantity (must be > 0)")
    unitOfMeasure: Optional[str] = Field(None, description="E.g.: 'Piece', 'Each', 'Kg', 'Liter', etc.")
    movementType: Optional[str] = Field(None, description="One of: 'Receipt', 'Issue', 'Transfer', 'Adjustment'")
    referenceDocumentId: Optional[str] = Field(None, description="Reference document if any")
    movementDate: Optional[str] = Field(None, description="Movement date in ISO8601 or YYYY-MM-DD format")

class GetGoodsMovementsInputSchema(BaseModel):
    pass

class CreateGoodsMovementInputSchema(BaseModel):
    data: GoodsMovementCreateData

class PatchGoodsMovementInputSchema(BaseModel):
    movement_id: int
    data: GoodsMovementPatchData

class DeleteGoodsMovementInputSchema(BaseModel):
    movement_id: int

# -----------------------------------------------------------------------------
# PURCHASE ORDERS
# -----------------------------------------------------------------------------
class PurchaseOrderCreateData(BaseModel):
    supplierId: int = Field(..., description="ID of the supplier")
    materialId: int = Field(..., description="ID of the material")
    quantity: float = Field(..., description="Order quantity (must be > 0)")
    unitOfMeasure: str = Field(..., description="E.g.: 'Piece', 'Each', 'Kg', 'Liter', etc.")
    shipToLocationId: int = Field(..., description="Location ID where items are delivered")
    orderDate: str = Field(..., description="Order date in ISO8601 or YYYY-MM-DD format")
    status: str = Field(..., description="Status of the order: 'New', 'In Progress', 'Completed', 'Cancelled'")
    requestedDeliveryDate: Optional[str] = Field(None, description="Requested delivery date (optional)")
    confirmedDeliveryDate: Optional[str] = Field(None, description="Confirmed delivery date (optional)")

class PurchaseOrderPatchData(BaseModel):
    supplierId: Optional[int] = Field(None, description="ID of the supplier")
    materialId: Optional[int] = Field(None, description="ID of the material")
    quantity: Optional[float] = Field(None, description="Order quantity (must be > 0)")
    unitOfMeasure: Optional[str] = Field(None, description="E.g.: 'Piece', 'Each', 'Kg', 'Liter', etc.")
    shipToLocationId: Optional[int] = Field(None, description="Location ID where items are delivered")
    orderDate: Optional[str] = Field(None, description="Order date in ISO8601 or YYYY-MM-DD format")
    status: Optional[str] = Field(None, description="Status: 'New', 'In Progress', 'Completed', 'Cancelled'")
    requestedDeliveryDate: Optional[str] = Field(None, description="Requested delivery date (optional)")
    confirmedDeliveryDate: Optional[str] = Field(None, description="Confirmed delivery date (optional)")

class GetPurchaseOrdersInputSchema(BaseModel):
    pass

class CreatePurchaseOrderInputSchema(BaseModel):
    data: PurchaseOrderCreateData

class PatchPurchaseOrderInputSchema(BaseModel):
    purchase_order_id: int
    data: PurchaseOrderPatchData

class DeletePurchaseOrderInputSchema(BaseModel):
    purchase_order_id: int

# -----------------------------------------------------------------------------
# PRODUCTION ORDERS
# -----------------------------------------------------------------------------
class ProductionOrderCreateData(BaseModel):
    materialId: int = Field(..., description="ID of the material to be produced")
    locationId: int = Field(..., description="Location ID where production occurs")
    billOfMaterialId: int = Field(..., description="ID of the associated Bill of Material")
    quantity: float = Field(..., description="Production quantity (must be > 0)")
    unitOfMeasure: str = Field(..., description="E.g.: 'Piece', 'Each', 'Kg', 'Liter', etc.")
    orderDate: str = Field(..., description="Order date in ISO8601 or YYYY-MM-DD format")
    status: str = Field(..., description="Status: 'New', 'In Progress', 'Completed', 'Cancelled'")
    plannedStartDate: Optional[str] = Field(None, description="Planned start date (optional)")
    plannedFinishDate: Optional[str] = Field(None, description="Planned finish date (optional)")

class ProductionOrderPatchData(BaseModel):
    materialId: Optional[int] = Field(None, description="ID of the material to be produced")
    locationId: Optional[int] = Field(None, description="Location ID where production occurs")
    billOfMaterialId: Optional[int] = Field(None, description="ID of the associated Bill of Material")
    quantity: Optional[float] = Field(None, description="Production quantity (must be > 0)")
    unitOfMeasure: Optional[str] = Field(None, description="E.g.: 'Piece', 'Each', 'Kg', 'Liter', etc.")
    orderDate: Optional[str] = Field(None, description="Order date in ISO8601 or YYYY-MM-DD format")
    status: Optional[str] = Field(None, description="Status: 'New', 'In Progress', 'Completed', 'Cancelled'")
    plannedStartDate: Optional[str] = Field(None, description="Planned start date (optional)")
    plannedFinishDate: Optional[str] = Field(None, description="Planned finish date (optional)")

class GetProductionOrdersInputSchema(BaseModel):
    pass

class CreateProductionOrderInputSchema(BaseModel):
    data: ProductionOrderCreateData

class PatchProductionOrderInputSchema(BaseModel):
    production_order_id: int
    data: ProductionOrderPatchData

class DeleteProductionOrderInputSchema(BaseModel):
    production_order_id: int


# -----------------------------------------------------------------------------
# UPDATED SCHEMA MAPPING DICTIONARY
# -----------------------------------------------------------------------------
schema_mappings = {
    # Customer Orders
    "aget_customer_orders": {
        "description": "Retrieve a list of all customer orders.",
        "input_schema": GetCustomerOrdersInputSchema,
    },
    "acreate_customer_order": {
        "description": "Create a new customer order record.",
        "input_schema": CreateCustomerOrderInputSchema,
    },
    "apatch_customer_order": {
        "description": "Patch (update) an existing customer order record.",
        "input_schema": PatchCustomerOrderInputSchema,
    },
    "adelete_customer_order": {
        "description": "Delete a customer order record by its ID.",
        "input_schema": DeleteCustomerOrderInputSchema,
    },
    # Forecasts
    "aget_forecasts": {
        "description": "Retrieve a list of all forecasts.",
        "input_schema": GetForecastsInputSchema,
    },
    "acreate_forecast": {
        "description": "Create a new forecast record.",
        "input_schema": CreateForecastInputSchema,
    },
    "apatch_forecast": {
        "description": "Patch (update) an existing forecast record.",
        "input_schema": PatchForecastInputSchema,
    },
    "adelete_forecast": {
        "description": "Delete a forecast record by its ID.",
        "input_schema": DeleteForecastInputSchema,
    },
    # Goods Movements
    "aget_goods_movements": {
        "description": "Retrieve a list of all goods movements.",
        "input_schema": GetGoodsMovementsInputSchema,
    },
    "acreate_goods_movement": {
        "description": "Create a new goods movement record.",
        "input_schema": CreateGoodsMovementInputSchema,
    },
    "apatch_goods_movement": {
        "description": "Patch (update) an existing goods movement record.",
        "input_schema": PatchGoodsMovementInputSchema,
    },
    "adelete_goods_movement": {
        "description": "Delete a goods movement record by its ID.",
        "input_schema": DeleteGoodsMovementInputSchema,
    },
    # Purchase Orders
    "aget_purchase_orders": {
        "description": "Retrieve a list of all purchase orders.",
        "input_schema": GetPurchaseOrdersInputSchema,
    },
    "acreate_purchase_order": {
        "description": "Create a new purchase order record.",
        "input_schema": CreatePurchaseOrderInputSchema,
    },
    "apatch_purchase_order": {
        "description": "Patch (update) an existing purchase order record.",
        "input_schema": PatchPurchaseOrderInputSchema,
    },
    "adelete_purchase_order": {
        "description": "Delete a purchase order record by its ID.",
        "input_schema": DeletePurchaseOrderInputSchema,
    },
    # Production Orders
    "aget_production_orders": {
        "description": "Retrieve a list of all production orders.",
        "input_schema": GetProductionOrdersInputSchema,
    },
    "acreate_production_order": {
        "description": "Create a new production order record.",
        "input_schema": CreateProductionOrderInputSchema,
    },
    "apatch_production_order": {
        "description": "Patch (update) an existing production order record.",
        "input_schema": PatchProductionOrderInputSchema,
    },
    "adelete_production_order": {
        "description": "Delete a production order record by its ID.",
        "input_schema": DeleteProductionOrderInputSchema,
    },
}
