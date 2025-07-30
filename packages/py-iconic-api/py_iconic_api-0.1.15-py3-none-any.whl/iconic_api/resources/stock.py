from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from datetime import datetime

from .base import IconicResource
from ..models.stock import StockData, StockUpdateItem, StockUpdateRequest

class Stock(IconicResource):
    """
    Stock resource for managing product inventory levels.
    
    This resource provides methods to retrieve stock information for products
    and product sets, as well as update stock levels for products.
    """
    
    endpoint = "stock"
    model_class = None  # No specific model for the resource itself
    
    def get_product_stock(self, product_id: int) -> StockData:
        """
        Get stock information for a specific product.
        
        Args:
            product_id: The ID of the product to get stock for
            
        Returns:
            StockData object containing product stock information
        """
        url = f"/v2/stock/product/{product_id}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            # Add the product_id to the response for reference
            response["product_id"] = product_id
            return StockData(**response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_product_stock_async(self, product_id: int) -> StockData:
        """
        Get stock information for a specific product asynchronously.
        
        Args:
            product_id: The ID of the product to get stock for
            
        Returns:
            StockData object containing product stock information
        """
        url = f"/v2/stock/product/{product_id}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            # Add the product_id to the response for reference
            response["product_id"] = product_id
            return StockData(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_product_set_stock(self, product_set_id: int) -> List[StockData]:
        """
        Get stock information for all products in a product set.
        
        Args:
            product_set_id: The ID of the product set to get stock for
            
        Returns:
            List of StockData objects containing product stock information
        """
        url = f"/v2/stock/product-set/{product_set_id}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [StockData(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_product_set_stock_async(self, product_set_id: int) -> List[StockData]:
        """
        Get stock information for all products in a product set asynchronously.
        
        Args:
            product_set_id: The ID of the product set to get stock for
            
        Returns:
            List of StockData objects containing product stock information
        """
        url = f"/v2/stock/product-set/{product_set_id}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [StockData(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def update_stock(self, items: Union[List[Dict[str, Any]], List[StockUpdateItem], StockUpdateRequest]) -> List[StockUpdateItem]:
        """
        Update stock levels for multiple products.
        
        This is a synchronous update endpoint with a limit of 100 products that can be updated per request.
        For larger updates, use the asynchronous endpoints or send requests in chunks.
        
        Args:
            items: List of items to update, either as:
                  - List of dictionaries with productId and quantity
                  - List of StockUpdateItem objects
                  - StockUpdateRequest object containing items
            
        Returns:
            List of successful stock updates
        """
        url = "/v2/stock/product"
        
        # Convert the input to the appropriate format
        if isinstance(items, StockUpdateRequest):
            data = items.to_api_params()
        elif all(isinstance(item, StockUpdateItem) for item in items):
            data = [{"productId": item.product_id, "quantity": item.quantity} for item in items]
        else:
            # Assume it's already a list of dictionaries
            data = items
            
        # Validate the number of items
        if len(data) > 100:
            raise ValueError("Cannot update more than 100 products in a single request")
            
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("PUT", url, json_data=data)
            return [StockUpdateItem(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def update_stock_async(self, items: Union[List[Dict[str, Any]], List[StockUpdateItem], StockUpdateRequest]) -> List[StockUpdateItem]:
        """
        Update stock levels for multiple products asynchronously.
        
        This is a synchronous update endpoint with a limit of 100 products that can be updated per request.
        For larger updates, use the asynchronous endpoints or send requests in chunks.
        
        Args:
            items: List of items to update, either as:
                  - List of dictionaries with productId and quantity
                  - List of StockUpdateItem objects
                  - StockUpdateRequest object containing items
            
        Returns:
            List of successful stock updates
        """
        url = "/v2/stock/product"
        
        # Convert the input to the appropriate format
        if isinstance(items, StockUpdateRequest):
            data = items.to_api_params()
        elif all(isinstance(item, StockUpdateItem) for item in items):
            data = [{"productId": item.product_id, "quantity": item.quantity} for item in items]
        else:
            # Assume it's already a list of dictionaries
            data = items
            
        # Validate the number of items
        if len(data) > 100:
            raise ValueError("Cannot update more than 100 products in a single request")
            
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("PUT", url, json_data=data)
            return [StockUpdateItem(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")