from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from datetime import datetime

from .base import IconicResource
from ..models import (
    ProductRead,
    PriceRead,
    RejectedProductSet
)

from ..models.stock import StockData, StockUpdateItem

if TYPE_CHECKING:
    from .product_set import ProductSet
    from ..models.stock import StockData, StockUpdateItem

class Product(IconicResource):
    """
    Product resource representing a single product or a collection of products.
    
    When initialized with data, it represents a specific product.
    Otherwise, it represents the collection of all products.
    """
    
    endpoint = "product"
    model_class = ProductRead
    
    def list(self, paginated: bool = False, **params) -> List["Product"]:
        return super().list(paginated=paginated, pluralised=True, **params)
    
    def get_by_shop_sku(self, shop_sku: str) -> "Product":
        """Get a product by its shop SKU."""
        url = f"/v2/product/shop-sku/{shop_sku}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_by_shop_sku_async(self, shop_sku: str) -> "Product":
        """Get a product by its shop SKU asynchronously."""
        url = f"/v2/product/shop-sku/{shop_sku}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_by_seller_sku(self, seller_sku: str) -> "Product":
        """Get a product by its seller SKU."""
        url = f"/v2/product/seller-sku/{seller_sku}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_by_seller_sku_async(self, seller_sku: str) -> "Product":
        """Get a product by its seller SKU asynchronously."""
        url = f"/v2/product/seller-sku/{seller_sku}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def list_by_seller_skus(self, seller_skus: List[str], limit: int = 100, offset: int = 0) -> List["Product"]:
        """Get products by multiple seller SKUs."""
        url = "/v2/product/seller-skus"
        params = {
            "sellerSkus[]": seller_skus,
            "limit": limit,
            "offset": offset
        }
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            
            if isinstance(response, dict) and "items" in response:
                items = response.get("items", [])
            else:
                items = response
                
            return [Product(client=self._client, data=item) for item in items]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_by_seller_skus_async(self, seller_skus: List[str], limit: int = 100, offset: int = 0) -> List["Product"]:
        """Get products by multiple seller SKUs asynchronously."""
        url = "/v2/product/seller-skus"
        params = {
            "sellerSkus[]": seller_skus,
            "limit": limit,
            "offset": offset
        }
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            
            if isinstance(response, dict) and "items" in response:
                items = response.get("items", [])
            else:
                items = response
                
            return [Product(client=self._client, data=item) for item in items]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Price related methods
    
    def update_price(self, 
                   country: str,
                   price: Optional[float] = None,
                   sale_price: Optional[float] = None,
                   sale_start_date: Optional[datetime] = None,
                   sale_end_date: Optional[datetime] = None,
                   status: str = "active") -> PriceRead:
        """Update the price of this product for a given country."""
        if not self.id:
            raise ValueError("Cannot update price without a product ID")
            
        url = f"/v2/product/{self.id}/prices/{country}"
        
        payload = {}
        if price is not None:
            payload["price"] = price
        if sale_price is not None:
            payload["salePrice"] = sale_price
        if sale_start_date is not None:
            payload["saleStartDate"] = sale_start_date.isoformat() + "Z"
        if sale_end_date is not None:
            payload["saleEndDate"] = sale_end_date.isoformat() + "Z"
        if status:
            payload["status"] = status
            
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("PUT", url, json_data=payload)
            return PriceRead(**response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def update_price_async(self, 
                              country: str,
                              price: Optional[float] = None,
                              sale_price: Optional[float] = None,
                              sale_start_date: Optional[datetime] = None,
                              sale_end_date: Optional[datetime] = None,
                              status: str = "active") -> PriceRead:
        """Update the price of this product for a given country asynchronously."""
        if not self.id:
            raise ValueError("Cannot update price without a product ID")
            
        url = f"/v2/product/{self.id}/prices/{country}"
        
        payload = {}
        if price is not None:
            payload["price"] = price
        if sale_price is not None:
            payload["salePrice"] = sale_price
        if sale_start_date is not None:
            payload["saleStartDate"] = sale_start_date.isoformat() + "Z"
        if sale_end_date is not None:
            payload["saleEndDate"] = sale_end_date.isoformat() + "Z"
        if status:
            payload["status"] = status
            
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("PUT", url, json_data=payload)
            return PriceRead(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def update_price_status(self, country: str, status: str) -> None:
        """Update the price status of this product for a given country."""
        if not self.id:
            raise ValueError("Cannot update price status without a product ID")
            
        url = f"/v2/product/{self.id}/prices/{country}/status"
        payload = {"status": status}
        
        if hasattr(self._client, '_make_request_sync'):
            self._client._make_request_sync("PUT", url, json_data=payload)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def update_price_status_async(self, country: str, status: str) -> None:
        """Update the price status of this product for a given country asynchronously."""
        if not self.id:
            raise ValueError("Cannot update price status without a product ID")
            
        url = f"/v2/product/{self.id}/prices/{country}/status"
        payload = {"status": status}
        
        if hasattr(self._client, '_make_request_async'):
            await self._client._make_request_async("PUT", url, json_data=payload)
        else:
            raise TypeError("This method requires an asynchronous client")
    
    # Product set related methods
    
    @property
    def product_set_id(self) -> Optional[int]:
        """Get the product set ID that this product belongs to."""
        return self._data.get("productSetId")
    
    def get_product_set(self) -> "ProductSet":
        """Get the product set that this product belongs to."""
        if not self.product_set_id:
            raise ValueError("This product does not have a product set ID")
            
        from .product_set import ProductSet
        
        if hasattr(self._client, '_make_request_sync'):
            url = f"/v2/product-set/{self.product_set_id}"
            response = self._client._make_request_sync("GET", url)
            return ProductSet(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_product_set_async(self) -> "ProductSet":
        """Get the product set that this product belongs to asynchronously."""
        if not self.product_set_id:
            raise ValueError("This product does not have a product set ID")
            
        from .product_set import ProductSet
        
        if hasattr(self._client, '_make_request_async'):
            url = f"/v2/product-set/{self.product_set_id}"
            response = await self._client._make_request_async("GET", url)
            return ProductSet(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Status related methods
    
    def update_status(self, status: str) -> "Product":
        """Update the status of this product."""
        if not self.id or not self.product_set_id:
            raise ValueError("Cannot update status without a product ID and product set ID")
            
        url = f"/v2/product-set/{self.product_set_id}/products/{self.id}/status"
        params = {"status": status}
        
        if hasattr(self._client, '_make_request_sync'):
            self._client._make_request_sync("PUT", url, params=params)
            # Update the local status
            self._data["status"] = status
            if self._model:
                setattr(self._model, "status", status)
            return self
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def update_status_async(self, status: str) -> "Product":
        """Update the status of this product asynchronously."""
        if not self.id or not self.product_set_id:
            raise ValueError("Cannot update status without a product ID and product set ID")
            
        url = f"/v2/product-set/{self.product_set_id}/products/{self.id}/status"
        params = {"status": status}
        
        if hasattr(self._client, '_make_request_async'):
            await self._client._make_request_async("PUT", url, params=params)
            # Update the local status
            self._data["status"] = status
            if self._model:
                setattr(self._model, "status", status)
            return self
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def update(self, data: Dict[str, Any]) -> "Product":
        """Update this product."""
        if not self.id or not self.product_set_id:
            raise ValueError("Cannot update without a product ID and product set ID")
            
        url = f"/v2/product-set/{self.product_set_id}/products/{self.id}"
        prepared_data = self._prepare_request_data(data)
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
            # Update this instance's data
            self._data.update(response)
            if self.model_class:
                self._model = self.model_class(**self._data)
            return self
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def update_async(self, data: Dict[str, Any]) -> "Product":
        """Update this product asynchronously."""
        if not self.id or not self.product_set_id:
            raise ValueError("Cannot update without a product ID and product set ID")
            
        url = f"/v2/product-set/{self.product_set_id}/products/{self.id}"
        prepared_data = self._prepare_request_data(data)
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
            # Update this instance's data
            self._data.update(response)
            if self.model_class:
                self._model = self.model_class(**self._data)
            return self
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Stock related methods
    
    def get_stock(self) -> "StockData":
        """
        Get stock information for this product.
        
        Returns:
            StockData object containing product stock information
        """
        if not self.id:
            raise ValueError("Cannot get stock without a product ID")
            
        if hasattr(self._client, 'stock'):
            return self._client.stock.get_product_stock(self.id)
        else:
            raise ValueError("Client does not have a stock resource")
            
    async def get_stock_async(self) -> "StockData":
        """
        Get stock information for this product asynchronously.
        
        Returns:
            StockData object containing product stock information
        """
        if not self.id:
            raise ValueError("Cannot get stock without a product ID")
            
        if hasattr(self._client, 'stock'):
            return await self._client.stock.get_product_stock_async(self.id)
        else:
            raise ValueError("Client does not have a stock resource")
            
    def update_stock(self, quantity: int) -> "StockUpdateItem":
        """
        Update the stock quantity for this product.
        
        Args:
            quantity: The new stock quantity
            
        Returns:
            StockUpdateItem containing the update confirmation
        """
        if not self.id:
            raise ValueError("Cannot update stock without a product ID")
            
        if hasattr(self._client, 'stock'):
            result = self._client.stock.update_stock([
                {"productId": self.id, "quantity": quantity}
            ])
            return result[0] if result else None
        else:
            raise ValueError("Client does not have a stock resource")
            
    async def update_stock_async(self, quantity: int) -> "StockUpdateItem":
        """
        Update the stock quantity for this product asynchronously.
        
        Args:
            quantity: The new stock quantity
            
        Returns:
            StockUpdateItem containing the update confirmation
        """
        if not self.id:
            raise ValueError("Cannot update stock without a product ID")
            
        if hasattr(self._client, 'stock'):
            result = await self._client.stock.update_stock_async([
                {"productId": self.id, "quantity": quantity}
            ])
            return result[0] if result else None
        else:
            raise ValueError("Client does not have a stock resource")
    
    # Quality control related methods
    
    @classmethod
    def get_rejected_product_sets(cls, client: Any, product_set_ids: List[int]) -> List[RejectedProductSet]:
        """Get information about rejected product sets."""
        url = "/v2/product-quality-control/rejected"
        params = {"productSetIds[]": product_set_ids}
        
        if hasattr(client, '_make_request_sync'):
            response = client._make_request_sync("GET", url, params=params)
            return [RejectedProductSet(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    @classmethod
    async def get_rejected_product_sets_async(cls, client: Any, product_set_ids: List[int]) -> List[RejectedProductSet]:
        """Get information about rejected product sets asynchronously."""
        url = "/v2/product-quality-control/rejected"
        params = {"productSetIds[]": product_set_ids}
        
        if hasattr(client, '_make_request_async'):
            response = await client._make_request_async("GET", url, params=params)
            return [RejectedProductSet(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
