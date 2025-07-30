from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from datetime import datetime

from .base import IconicResource, PaginatedResponse
from ..models import ListAttributesRequest
from ..models.attribute import (
    Attribute,
    AttributeSet
)

class AttributeResource(IconicResource):
    """
    Attribute resource representing attributes in the system.
    
    This resource provides methods to retrieve attribute information and
    attribute details, which are essential for working with product categories
    and creating/updating product sets.
    """
    
    endpoint = "attributes"
    model_class = Attribute
    
    def list_attributes(self, 
                      **kwargs: Union[Dict[str, Any], ListAttributesRequest]) -> PaginatedResponse:
        """
        List attributes according to provided filters.
        
        Args:
            **kwargs: Either individual parameters or a ListAttributesRequest model:
                attribute_ids: List of attribute IDs to filter by
                attribute_set_ids: List of attribute set IDs to filter by
                only_visible: Whether to return visible items only
                limit: Maximum number of items to return
                offset: Starting offset for pagination
                
        Returns:
            Paginated response containing attribute objects
        """
        # Handle input as either a model, dict, or individual parameters
        if len(kwargs) == 1 and isinstance(next(iter(kwargs.values())), ListAttributesRequest):
            # If passed as a single model parameter
            request = next(iter(kwargs.values()))
            params = request.to_api_params()
        else:
            # If passed as dictionary of parameters
            request = ListAttributesRequest(**kwargs)
            params = request.to_api_params()
            
        url = "/v2/attributes"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            
            # Create attribute objects from items and include pagination info
            if isinstance(response, dict) and "items" in response:
                attributes = [AttributeResource(client=self._client, data=item) for item in response["items"]]
                
                # Extract pagination data
                pagination = response.get("pagination", {})
                limit = pagination.get("limit", params.get("limit", 100))
                offset = pagination.get("offset", params.get("offset", 0))
                total_count = pagination.get("totalCount", 0)
                
                return PaginatedResponse(
                    items=attributes,
                    limit=limit,
                    offset=offset,
                    total_count=total_count
                )
            
            return PaginatedResponse(
                items=[],
                limit=params.get("limit", 100),
                offset=params.get("offset", 0),
                total_count=0
            )
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_attributes_async(self, 
                                 **kwargs: Union[Dict[str, Any], ListAttributesRequest]) -> PaginatedResponse:
        """
        List attributes according to provided filters asynchronously.
        
        Args:
            **kwargs: Either individual parameters or a ListAttributesRequest model:
                attribute_ids: List of attribute IDs to filter by
                attribute_set_ids: List of attribute set IDs to filter by
                only_visible: Whether to return visible items only
                limit: Maximum number of items to return
                offset: Starting offset for pagination
                
        Returns:
            Paginated response containing attribute objects
        """
        # Handle input as either a model, dict, or individual parameters
        if len(kwargs) == 1 and isinstance(next(iter(kwargs.values())), ListAttributesRequest):
            # If passed as a single model parameter
            request = next(iter(kwargs.values()))
            params = request.to_api_params()
        else:
            # If passed as dictionary of parameters
            request = ListAttributesRequest(**kwargs)
            params = request.to_api_params()
            
        url = "/v2/attributes"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            
            # Create attribute objects from items and include pagination info
            if isinstance(response, dict) and "items" in response:
                attributes = [AttributeResource(client=self._client, data=item) for item in response["items"]]
                
                # Extract pagination data
                pagination = response.get("pagination", {})
                limit = pagination.get("limit", params.get("limit", 100))
                offset = pagination.get("offset", params.get("offset", 0))
                total_count = pagination.get("totalCount", 0)
                
                return PaginatedResponse(
                    items=attributes,
                    limit=limit,
                    offset=offset,
                    total_count=total_count
                )
            
            return PaginatedResponse(
                items=[],
                limit=params.get("limit", 100),
                offset=params.get("offset", 0),
                total_count=0
            )
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_attribute(self, attribute_id: int) -> "AttributeResource":
        """
        Get details for a specific attribute.
        
        Args:
            attribute_id: ID of the attribute to retrieve
            
        Returns:
            Attribute resource object
        """
        url = f"/v2/attributes/{attribute_id}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return AttributeResource(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_attribute_async(self, attribute_id: int) -> "AttributeResource":
        """
        Get details for a specific attribute asynchronously.
        
        Args:
            attribute_id: ID of the attribute to retrieve
            
        Returns:
            Attribute resource object
        """
        url = f"/v2/attributes/{attribute_id}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return AttributeResource(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Helper methods for working with attributes
    
    def get_value_for_product_set(self, value: Any) -> Any:
        """
        Format an attribute value for use in product set creation/update.
        
        Based on the attribute type, ensures the value is in the correct format.
        
        Args:
            value: The raw value to format
            
        Returns:
            Properly formatted attribute value for API submission
        """
        attribute_type = self.attribute_type
        
        if attribute_type == "value":
            return str(value)
        elif attribute_type == "option":
            # If value is a string, try to find the option ID
            if isinstance(value, str) and self.options:
                for option in self.options:
                    if option["name"].lower() == value.lower():
                        return option["id"]
                raise ValueError(f"Option '{value}' not found for attribute {self.id}")
            return value  # Assume it's already an ID
        elif attribute_type == "multi_option":
            # If values are strings, convert to option IDs
            if all(isinstance(v, str) for v in value) and self.options:
                result = []
                for v in value:
                    found = False
                    for option in self.options:
                        if option["name"].lower() == v.lower():
                            result.append(option["id"])
                            found = True
                            break
                    if not found:
                        raise ValueError(f"Option '{v}' not found for attribute {self.id}")
                return result
            return value  # Assume it's already a list of IDs
        
        return value
