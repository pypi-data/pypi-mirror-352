from typing import Dict, Any, List, Optional, Union

from .base import IconicResource
from ..models import (
    Brand,
    BrandAttribute,
    ProductSetRead,
    ListBrandsRequest,
)

class Brand(IconicResource):
    """
    Brand resource representing a single brand or a collection of brands.
    
    When initialized with data, it represents a specific brand.
    Otherwise, it represents the collection of all brands.
    """
    
    endpoint = "brands"
    model_class = Brand
    
    def list_brands(self, params: Union[Dict[str, Any], ListBrandsRequest]) -> List["Brand"]:
        """List brands based on filter criteria."""
        if isinstance(params, ListBrandsRequest):
            params = params.to_api_params()
            
        url = "/v2/brands"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [Brand(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_brands_async(self, params: Union[Dict[str, Any], ListBrandsRequest]) -> List["Brand"]:
        """List brands based on filter criteria asynchronously."""
        if isinstance(params, ListBrandsRequest):
            params = params.to_api_params()
            
        url = "/v2/brands"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [Brand(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_attributes(self) -> List[BrandAttribute]:
        """Get mapped attribute options for this brand."""
        if not self.id:
            raise ValueError("Cannot get attributes without a brand ID")
            
        url = f"/v2/brands/{self.id}/attributes"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [BrandAttribute(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_attributes_async(self) -> List[BrandAttribute]:
        """Get mapped attribute options for this brand asynchronously."""
        if not self.id:
            raise ValueError("Cannot get attributes without a brand ID")
            
        url = f"/v2/brands/{self.id}/attributes"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [BrandAttribute(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Helper methods
    
    def get_product_sets(self, **params) -> List["ProductSetRead"]:
        """Get product sets that belong to this brand."""
        if not self.id:
            raise ValueError("Cannot get product sets without a brand ID")
            
        from .product_set import ProductSet
        
        params["brand_ids"] = [self.id]
        
        product_set = ProductSet(client=self._client)
        return product_set.list(**params)
        
    async def get_product_sets_async(self, **params) -> List["ProductSetRead"]:
        """Get product sets that belong to this brand asynchronously."""
        if not self.id:
            raise ValueError("Cannot get product sets without a brand ID")
            
        from .product_set import ProductSet
        
        params["brand_ids"] = [self.id]
        
        product_set = ProductSet(client=self._client)
        return await product_set.list_async(**params)
