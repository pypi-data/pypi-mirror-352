from __future__ import annotations

from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict

from .api_requests import BaseRequestParamsModel

class WarehouseStock(BaseModel):
    """Model representing stock in a specific warehouse."""
    name: str
    stock: int
    warehouse_id: int = Field(alias="warehouseId")

class ConsignmentStock(BaseModel):
    """Model representing consignment stock levels."""
    received: Optional[int] = None
    quarantined: Optional[int] = None
    defective: Optional[int] = None
    canceled: Optional[int] = None
    returned: Optional[int] = None
    failed: Optional[int] = None

class StockData(BaseModel):
    """Model representing product stock information."""
    shop_sku: Optional[str] = Field(None, alias="shopSku")
    seller_sku: str = Field(alias="sellerSku")
    name: str
    quantity: int
    reserved_stock: int = Field(alias="reservedStock")
    pre_verification_stock: Optional[int] = Field(None, alias="preVerificationStock")
    available: int
    consignments: Optional[ConsignmentStock] = None
    sellable_stock: Optional[int] = Field(None, alias="sellableStock")
    non_sellable_stock: Optional[int] = Field(None, alias="nonSellableStock")
    warehouses: Optional[List[WarehouseStock]] = None
    product_id: Optional[int] = None  # Used internally, not from API

class StockUpdateItem(BaseModel):
    """Model representing a single item in a stock update request."""
    product_id: int = Field(alias="productId")
    quantity: int

class StockUpdateRequest(BaseRequestParamsModel):
    """Request model for updating stock of multiple products."""
    items: List[StockUpdateItem]

    def to_api_params(self) -> List[Dict[str, Any]]:
        """
        Converts the model instance to a list of API parameters.
        
        Returns:
            List of dictionaries with productId and quantity
        """
        return [{"productId": item.product_id, "quantity": item.quantity} for item in self.items]