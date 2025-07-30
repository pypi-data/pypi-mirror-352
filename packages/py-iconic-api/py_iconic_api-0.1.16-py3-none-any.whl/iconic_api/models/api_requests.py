from __future__ import annotations

from datetime import date as date_aliased, datetime as datetime_aliased
from enum import Enum, StrEnum
from typing import Any, Dict, List, Optional, Union, Literal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from ..models import (
    Order, 
    ShipmentProviderType,
    OrderStatus,
    PackedStatus,
    ShipmentTypes,
    FulfillmentType,
    Customer,
    Provider,
    ProductSetRead,
    ProductSetCreated
)

from ..utils import clean_params

class BaseRequestParamsModel(BaseModel):
    """
    Base model for all request models.
    """
    model_config = ConfigDict(
        allow_extra = "allow",
        validate_by_name = True,
        use_enum_values = False,
        json_encoders = {
            datetime_aliased: lambda v: v.isoformat() if isinstance(v, datetime_aliased) else v,
            UUID: lambda v: str(v) if isinstance(v, UUID) else v,
        }
    )
    
    limit: int = 100
    offset: int = 0
    
    def to_api_params(self) -> Dict[str, Any]:
        """
        Converts the model instance to a dictionary of API parameters.
        """
        params = self.model_dump(exclude_none=True)
        cleaned_params = clean_params(params)
        return cleaned_params

class UpdateProductSetRequest(BaseRequestParamsModel):
    """
    Request model for updating a product set.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    parent_sku: Optional[str] = None
    brand_id: Optional[int] = None
    primary_category_id: Optional[int] = None
    categories: Optional[List[int]] = None
    attributes: Optional[Dict[str, Any]] = None
    size_system: Optional[int] = None
    browse_nodes: Optional[List[int]] = None

class GetCountByAttributeSetRequest(BaseRequestParamsModel):
    """
    Request model for getting count of product sets by attribute set.
    """
    status: Optional[Literal["all", "active", "inactive-all", "deleted-all", "image-missing", 
                            "pending", "rejected", "disapproved", "sold-out", 
                            "not-authorized", "price-rejected"]] = None
    keyword: Optional[Union[str, List[str]]] = None
    create_date_start: Optional[date_aliased] = None
    create_date_end: Optional[date_aliased] = None
    update_date_start: Optional[date_aliased] = None
    update_date_end: Optional[date_aliased] = None
    brand_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    visibility: Optional[Literal["Syncing"]] = None
    in_stock: Optional[bool] = None
    reserved: Optional[bool] = None
    category_ids: Optional[List[int]] = None
    only_with_tags: Optional[bool] = None
    parent_sku: Optional[str] = None
    group: Optional[str] = None
    
class ListBrandsRequest(BaseRequestParamsModel):
    """
    Request model for listing brands.
    """
    name: Optional[str] = None
    brand_ids: Optional[List[int]] = None
    brand_uuids: Optional[List[str]] = None
    include_inaccessible: Optional[bool] = None
    restricted_only: Optional[bool] = None
    sort: Optional[Literal["createdAt", "updatedAt", "name"]] = None
    sort_dir: Optional[Literal["asc", "desc"]] = None
    
class ListOrdersRequest(BaseRequestParamsModel):
    """
    Request model for listing orders.
    """
    x_context: Optional[Literal["admin", "seller"]] = "seller"
    section: Optional[Union[OrderStatus, ShipmentProviderType]] = None
    date_start: Optional[Union[date_aliased, datetime_aliased]] = None
    date_end: Optional[Union[date_aliased, datetime_aliased]] = None
    order_numbers: Optional[List[str]] = None
    packed: Optional[PackedStatus] = None
    customers: Optional[Customer] = None
    tags: Optional[List[str]] = None
    product_sku: Optional[List[str]] = None
    shipment_type: Optional[ShipmentTypes] = None
    shipment_providers: Optional[List[Provider]] = None
    outlet: bool = False
    invoice_required: bool = False
    cancelation_reasons: List[str] = None
    cancelation_reason_ids: List[int] = None
    fulfilment_type: Optional[FulfillmentType] = None
    order_sources: Optional[List[str]] = None
    seller_names: Optional[List[str]] = None
    seller_ids: Optional[List[int]] = None
    update_date_start: Optional[Union[date_aliased, datetime_aliased]] = None
    update_date_end: Optional[Union[date_aliased, datetime_aliased]] = None
    warehouses: Optional[List[str]] = None
    order_ids: Optional[List[int]] = None
    include_voucher_details: Optional[bool] = None
    sort: Optional[Literal["createdAt", "updatedAt"]] = None
    sort_dir: Optional[Literal["asc", "desc"]] = None
    
    def to_api_params(self) -> Dict[str, Any]:
        if self.section is not None:
            if isinstance(self.section, OrderStatus):
                section = f"status_{self.section.value}"
            elif isinstance(self.section, ShipmentProviderType):
                section = f"group_{self.section.value}"
            else:
                section = self.section
        else:
            section = None
        
        if self.customers is not None:
            customers_ = []  
            for customer in self.customers:
                customers_.extend([customer.firstName, customer.lastName])
        else:
            customers_ = None
        
        if self.shipment_providers is not None:
            shipment_providers = [provider.id for provider in self.shipment_providers]
        else:
            shipment_providers = None
        
        if self.fulfilment_type is not None:
            fulfilment_type = self.fulfilment_type.value
        else:
            fulfilment_type = None
            
        if self.shipment_type is not None:
            shipment_type = self.shipment_type.value
        else:
            shipment_type = None
            
        params = {k: v for k,v in {
            **self.model_dump(exclude_none=True),
            "section": section,
            "customers": customers_,
            "shipment_providers": shipment_providers,
            "fulfilment_type": fulfilment_type,
            "shipment_type": shipment_type,
        }.items() if k != 'x_context' and v is not None}
        
        cleaned_params = clean_params(params)
        return cleaned_params

class ListProductSetsRequest(BaseRequestParamsModel):
    """
    Request model for listing product sets.
    """
    status: Optional[Literal["all", "active", "inactive-all", "deleted-all", "image-missing", 
                            "pending", "rejected", "disapproved", "sold-out", 
                            "not-authorized", "price-rejected"]] = None
    keyword: Optional[List[str]] = None
    create_date_start: Optional[date_aliased] = None
    create_date_end: Optional[date_aliased] = None
    update_date_start: Optional[date_aliased] = None
    update_date_end: Optional[date_aliased] = None
    brand_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    visibility: Optional[Literal["Syncing"]] = None
    in_stock: Optional[bool] = None
    reserved: Optional[bool] = None
    category_ids: Optional[List[int]] = None
    only_with_tags: Optional[bool] = None
    parent_sku: Optional[str] = None
    product_set_uuids: Optional[List[str]] = None
    product_set_ids: Optional[List[int]] = None
    group: Optional[str] = None
    order_by: Optional[Literal["createdAt"]] = None
    order_direction: Optional[Literal["ASC", "DESC"]] = None

class CreateProductSetRequest(BaseRequestParamsModel):
    """
    Request model for creating a product set.
    """
    name: str
    price: float
    status: Optional[Literal["active", "inactive"]] = "active"
    seller_sku: str
    parent_sku: Optional[str] = None
    description: Optional[str] = None
    brand_id: int
    primary_category_id: int
    categories: Optional[List[int]] = None
    attributes: Dict[str, Any]
    size_system: Optional[int] = None
    browse_nodes: Optional[List[int]] = Field(default_factory=list)
    variation: Optional[str] = None
    shipment_type_id: Optional[int] = None
    product_identifier: Optional[str] = None

class AddProductSetImageRequest(BaseRequestParamsModel):
    """
    Request model for adding an image to a product set.
    """
    position: Optional[int] = None
    display_url: Optional[str] = None
    overwrite: bool = False

class UpdateProductSetImageRequest(BaseRequestParamsModel):
    """
    Request model for updating a product set image via URL.
    """
    position: Optional[int] = None
    display_url: Optional[str] = None

class ProductSetIdsRequest(BaseRequestParamsModel):
    """
    Request model for endpoints that accept a list of product set IDs.
    """
    product_set_ids: List[int]

class CreateProductRequest(BaseRequestParamsModel):
    """
    Request model for creating a product for a product set.
    """
    seller_sku: str
    variation: str
    status: Optional[Literal["active", "inactive", "deleted"]] = "active"
    shipment_type_id: Optional[int] = None
    product_identifier: Optional[str] = None
    name: Optional[str] = None

class UpdateProductRequest(BaseRequestParamsModel):
    """
    Request model for updating a product.
    """
    seller_sku: Optional[str] = None
    variation: Optional[str] = None
    status: Optional[Literal["active", "inactive", "deleted"]] = None
    shipment_type_id: Optional[int] = None
    product_identifier: Optional[str] = None
    name: Optional[str] = None

class UpdateProductSetPriceRequest(BaseRequestParamsModel):
    """
    Request model for updating a product set price.
    """
    product_id: int
    country: str
    price: Optional[float] = None
    sale_price: Optional[float] = None
    sale_start_date: Optional[datetime_aliased] = None
    sale_end_date: Optional[datetime_aliased] = None
    status: Optional[Literal["active", "inactive"]] = "active"


class SearchHybridRequest(BaseRequestParamsModel):
    """
    Request model for searching hybrid products.
    """
    query: str

class CreateProductBySinRequest(BaseRequestParamsModel):
    """
    Request model for creating products by SIN.
    """
    sin: str

class ProductGroupRequest(BaseRequestParamsModel):
    """
    Request model for product group operations.
    """
    name: str

class GetQualityControlStatusRequest(BaseRequestParamsModel):
    """
    Request model for getting quality control status of ProductSets.
    """
    product_set_ids: Optional[List[int]] = None

class GetImagesBySKURequest(BaseRequestParamsModel):
    """
    Request model for getting images by product shop SKU or Seller SKU.
    """
    product_skus: List[str]

class FinanceStatementListParamsModel(BaseRequestParamsModel):
    """
    Request model for listing finance statements.
    """
    seller_id: Optional[int] = None
    start_date: Optional[datetime_aliased] = None
    end_date: Optional[datetime_aliased] = None
    paid: Optional[bool] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    type: Optional[Literal["marketplace", "consignment"]] = "marketplace"
    sort: Optional[Literal["id", "createdAt", "startDate"]] = "id"
    sort_dir: Optional[Literal["asc", "desc"]] = "desc"

class TransactionVariablesListParamsModel(BaseRequestParamsModel):
    """
    Request model for listing TRE variables.
    """
    seller_id: Optional[int] = None
    seller_src_id: Optional[str] = None
    variable_name: Optional[str] = None
    variable_value: Optional[str] = None


class InvoiceDocumentType(StrEnum):
    """
    Enumeration of invoice document types supported by the API.
    """
    # Inbound documents
    INBOUND_COMPLEMENTARY_NOTE = "inbound-complementary-note"
    INBOUND_CORRECTION_LETTER = "inbound-correction-letter"
    INBOUND_NORMAL_ISSUE = "inbound-normal-issue"
    INBOUND_CANCELED = "inbound-canceled"
    INBOUND_UNUSED = "inbound-unused"
    INBOUND_RETURN_COMPLEMENTARY_NOTE = "inbound-return-complementary-note"
    INBOUND_RETURN_CORRECTION_LETTER = "inbound-return-correction-letter"
    INBOUND_RETURN_NORMAL_ISSUE = "inbound-return-normal-issue"
    INBOUND_RETURN_CANCELED = "inbound-return-canceled"
    INBOUND_RETURN_UNUSED = "inbound-return-unused"
    
    # Sale documents
    SALE_COMPLEMENTARY_NOTE = "sale-complementary-note"
    SALE_CORRECTION_LETTER = "sale-correction-letter"
    SALE_NORMAL_ISSUE = "sale-normal-issue"
    SALE_SYMBOLIC_RETURN = "sale-symbolic-return"
    SALE_CANCELED = "sale-canceled"
    SALE_UNUSED = "sale-unused"
    SALE_DEVOLUTION_COMPLEMENTARY_NOTE = "sale-devolution-complementary-note"
    SALE_DEVOLUTION_CORRECTION_LETTER = "sale-devolution-correction-letter"
    SALE_DEVOLUTION_NORMAL_ISSUE = "sale-devolution-normal-issue"
    SALE_DEVOLUTION_SHIPPING_SYMBOLIC = "sale-devolution-shipping-symbolic"
    SALE_DEVOLUTION_CANCELED = "sale-devolution-canceled"
    SALE_DEVOLUTION_UNUSED = "sale-devolution-unused"
    
    # Stock decrease documents
    STOCK_DECREASE_COMPLEMENTARY_NOTE = "stock-decrease-complementary-note"
    STOCK_DECREASE_CORRECTION_LETTER = "stock-decrease-correction-letter"
    STOCK_DECREASE_NORMAL_ISSUE = "stock-decrease-normal-issue"
    STOCK_DECREASE_CANCELED = "stock-decrease-canceled"
    STOCK_DECREASE_UNUSED = "stock-decrease-unused"


class InvoiceRequest(BaseRequestParamsModel):
    """
    Request model for retrieving invoice files.
    """
    order_numbers: Optional[List[str]] = None
    invoice_numbers: Optional[List[str]] = None
    po_numbers: Optional[List[str]] = None
    document_types: Optional[List[InvoiceDocumentType]] = None
    start_date: Optional[date_aliased] = None
    end_date: Optional[date_aliased] = None
    
    def to_api_params(self) -> Dict[str, Any]:
        params = {}
        
        if self.order_numbers:
            params["orderNumbers[]"] = self.order_numbers
        if self.invoice_numbers:
            params["invoiceNumbers[]"] = self.invoice_numbers
        if self.po_numbers:
            params["poNumbers[]"] = self.po_numbers
        if self.document_types:
            params["documentTypes[]"] = [dt.value for dt in self.document_types]
        if self.start_date:
            params["startDate"] = self.start_date.isoformat()
        if self.end_date:
            params["endDate"] = self.end_date.isoformat()
            
        return params
    

class ListAttributesRequest(BaseRequestParamsModel):
    """Request model for listing attributes."""
    attribute_ids: Optional[List[int]] = None
    attribute_set_ids: Optional[List[int]] = None
    only_visible: Optional[bool] = True
    limit: int = 100
    offset: int = 0

    def to_api_params(self) -> Dict[str, Any]:
        params = {}
        
        if self.attribute_ids:
            params["attributeIds[]"] = self.attribute_ids
        if self.attribute_set_ids:
            params["attributeSetIds[]"] = self.attribute_set_ids
        if self.only_visible is not None:
            params["onlyVisible"] = self.only_visible
        
        params["limit"] = self.limit
        params["offset"] = self.offset
        
        return clean_params(params)