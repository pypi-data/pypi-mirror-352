from typing import Dict, Any, List, Optional, Union

from .base import IconicResource
from ..models import (
    ProductSetRead,
    Category,
    CategoryTree,
    CategoryAttribute,
    CategoryMapping,
    CategoryById,
    CategorySetting
)

class Category(IconicResource):
    """
    Category resource representing a single category or a collection of categories.
    
    When initialized with data, it represents a specific category.
    Otherwise, it represents the collection of all categories.
    """
    
    endpoint = "category"
    model_class = Category
    
    def get_tree(self) -> List[CategoryTree]:
        """Get the categories tree."""
        url = "/v2/category/tree"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [CategoryTree(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_tree_async(self) -> List[CategoryTree]:
        """Get the categories tree asynchronously."""
        url = "/v2/category/tree"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [CategoryTree(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_attributes(self) -> List[CategoryAttribute]:
        """Get attributes for this category."""
        if not self.id:
            raise ValueError("Cannot get attributes without a category ID")
            
        url = f"/v2/category/{self.id}/attributes"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [CategoryAttribute(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_attributes_async(self) -> List[CategoryAttribute]:
        """Get attributes for this category asynchronously."""
        if not self.id:
            raise ValueError("Cannot get attributes without a category ID")
            
        url = f"/v2/category/{self.id}/attributes"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [CategoryAttribute(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_root(self) -> "Category":
        """Get the root category."""
        url = "/v2/category/root"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return Category(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_root_async(self) -> "Category":
        """Get the root category asynchronously."""
        url = "/v2/category/root"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return Category(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_detailed(self) -> CategoryById:
        """Get detailed information about this category."""
        if not self.id:
            raise ValueError("Cannot get detailed information without a category ID")
            
        url = f"/v2/category/{self.id}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return CategoryById(**response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_detailed_async(self) -> CategoryById:
        """Get detailed information about this category asynchronously."""
        if not self.id:
            raise ValueError("Cannot get detailed information without a category ID")
            
        url = f"/v2/category/{self.id}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return CategoryById(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_children(self) -> List["Category"]:
        """Get this category's direct children."""
        if not self.id:
            raise ValueError("Cannot get children without a category ID")
            
        url = f"/v2/category/{self.id}/children"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [Category(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_children_async(self) -> List["Category"]:
        """Get this category's direct children asynchronously."""
        if not self.id:
            raise ValueError("Cannot get children without a category ID")
            
        url = f"/v2/category/{self.id}/children"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [Category(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_settings(self) -> List[CategorySetting]:
        """Get settings for this category."""
        if not self.id:
            raise ValueError("Cannot get settings without a category ID")
            
        url = f"/v2/category/{self.id}/settings"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [CategorySetting(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_settings_async(self) -> List[CategorySetting]:
        """Get settings for this category asynchronously."""
        if not self.id:
            raise ValueError("Cannot get settings without a category ID")
            
        url = f"/v2/category/{self.id}/settings"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [CategorySetting(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_mappings(self) -> List[CategoryMapping]:
        """Get all category-to-attribute mapping information."""
        url = "/v2/category/mappings"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [CategoryMapping(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_mappings_async(self) -> List[CategoryMapping]:
        """Get all category-to-attribute mapping information asynchronously."""
        url = "/v2/category/mappings"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [CategoryMapping(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_automatic_nomenclature(self) -> str:
        """Get formula for calculating automatic nomenclature for this category."""
        if not self.id:
            raise ValueError("Cannot get automatic nomenclature without a category ID")
            
        url = f"/v2/category/{self.id}/automatic-nomenclature"
        
        if hasattr(self._client, '_make_request_sync'):
            return self._client._make_request_sync("GET", url)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_automatic_nomenclature_async(self) -> str:
        """Get formula for calculating automatic nomenclature for this category asynchronously."""
        if not self.id:
            raise ValueError("Cannot get automatic nomenclature without a category ID")
            
        url = f"/v2/category/{self.id}/automatic-nomenclature"
        
        if hasattr(self._client, '_make_request_async'):
            return await self._client._make_request_async("GET", url)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Helper methods
    
    def get_product_sets(self, **params) -> List["ProductSetRead"]:
        """Get product sets that belong to this category."""
        if not self.id:
            raise ValueError("Cannot get product sets without a category ID")
            
        from .product_set import ProductSet
        
        params["category_ids"] = [self.id]
        
        product_set = ProductSet(client=self._client)
        return product_set.list(**params)
        
    async def get_product_sets_async(self, **params) -> List["ProductSetRead"]:
        """Get product sets that belong to this category asynchronously."""
        if not self.id:
            raise ValueError("Cannot get product sets without a category ID")
            
        from .product_set import ProductSet
        
        params["category_ids"] = [self.id]
        
        product_set = ProductSet(client=self._client)
        return await product_set.list_async(**params)
