from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from datetime import datetime

from .base import IconicResource
from ..models.attribute import AttributeSet, Attribute
from .attribute import AttributeResource

class AttributeSetResource(IconicResource):
    """
    AttributeSet resource representing attribute sets in the system.
    
    Attribute sets are collections of attributes that are applicable to
    specific product categories. This resource provides methods to retrieve
    attribute set information and the attributes associated with them.
    """
    
    endpoint = "attribute-sets"
    model_class = AttributeSet
    
    def list_attribute_sets(self, attribute_set_ids: Optional[List[int]] = None) -> List["AttributeSetResource"]:
        """
        Get a list of available attribute sets.
        
        Args:
            attribute_set_ids: Optional list of attribute set IDs to filter by
            
        Returns:
            List of attribute set resources
        """
        url = "/v2/attribute-sets"
        params = {}
        
        if attribute_set_ids:
            params["attributeSetIds[]"] = attribute_set_ids
            
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [AttributeSetResource(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_attribute_sets_async(self, attribute_set_ids: Optional[List[int]] = None) -> List["AttributeSetResource"]:
        """
        Get a list of available attribute sets asynchronously.
        
        Args:
            attribute_set_ids: Optional list of attribute set IDs to filter by
            
        Returns:
            List of attribute set resources
        """
        url = "/v2/attribute-sets"
        params = {}
        
        if attribute_set_ids:
            params["attributeSetIds[]"] = attribute_set_ids
            
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [AttributeSetResource(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_attribute_set(self, attribute_set_id: int) -> "AttributeSetResource":
        """
        Get details for a specific attribute set.
        
        Args:
            attribute_set_id: ID of the attribute set to retrieve
            
        Returns:
            AttributeSet resource object
        """
        url = f"/v2/attribute-sets/{attribute_set_id}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return AttributeSetResource(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_attribute_set_async(self, attribute_set_id: int) -> "AttributeSetResource":
        """
        Get details for a specific attribute set asynchronously.
        
        Args:
            attribute_set_id: ID of the attribute set to retrieve
            
        Returns:
            AttributeSet resource object
        """
        url = f"/v2/attribute-sets/{attribute_set_id}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return AttributeSetResource(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_attributes(self, attribute_set_id: Optional[int] = None) -> List[AttributeResource]:
        """
        Get attributes for a specific attribute set.
        
        If attribute_set_id is not provided, it uses this resource's ID.
        
        Args:
            attribute_set_id: Optional ID of the attribute set to get attributes for
            
        Returns:
            List of attribute resources
        """
        # Use the provided ID or this resource's ID
        set_id = attribute_set_id or self.id
        if not set_id:
            raise ValueError("Cannot get attributes without an attribute set ID")
            
        url = f"/v2/attribute-sets/{set_id}/attributes"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [AttributeResource(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_attributes_async(self, attribute_set_id: Optional[int] = None) -> List[AttributeResource]:
        """
        Get attributes for a specific attribute set asynchronously.
        
        If attribute_set_id is not provided, it uses this resource's ID.
        
        Args:
            attribute_set_id: Optional ID of the attribute set to get attributes for
            
        Returns:
            List of attribute resources
        """
        # Use the provided ID or this resource's ID
        set_id = attribute_set_id or self.id
        if not set_id:
            raise ValueError("Cannot get attributes without an attribute set ID")
            
        url = f"/v2/attribute-sets/{set_id}/attributes"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [AttributeResource(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def find_attribute_by_name(self, name: str, attribute_set_id: Optional[int] = None) -> Optional[AttributeResource]:
        """
        Find an attribute in this attribute set by its name.
        
        This is a helper method to easily locate attributes by name instead of ID.
        
        Args:
            name: Name of the attribute to find
            attribute_set_id: Optional ID of the attribute set to search in
            
        Returns:
            AttributeResource if found, None otherwise
        """
        attributes = self.get_attributes(attribute_set_id)
        
        for attribute in attributes:
            if attribute.name.lower() == name.lower() or attribute.label.lower() == name.lower():
                return attribute
                
        return None
        
    async def find_attribute_by_name_async(self, name: str, attribute_set_id: Optional[int] = None) -> Optional[AttributeResource]:
        """
        Find an attribute in this attribute set by its name asynchronously.
        
        This is a helper method to easily locate attributes by name instead of ID.
        
        Args:
            name: Name of the attribute to find
            attribute_set_id: Optional ID of the attribute set to search in
            
        Returns:
            AttributeResource if found, None otherwise
        """
        attributes = await self.get_attributes_async(attribute_set_id)
        
        for attribute in attributes:
            if attribute.name.lower() == name.lower() or attribute.label.lower() == name.lower():
                return attribute
                
        return None
        
    def prepare_attributes_for_product_set(self, 
                                        attribute_values: Dict[str, Any], 
                                        attribute_set_id: Optional[int] = None) -> Dict[int, Any]:
        """
        Convert a dictionary of attribute name/value pairs to the format expected by the API.
        
        This helper method makes it easier to specify attributes by name rather than ID.
        
        Args:
            attribute_values: Dictionary mapping attribute names to values
            attribute_set_id: Optional ID of the attribute set to use
            
        Returns:
            Dictionary mapping attribute IDs to properly formatted values
        """
        # Get all attributes for this attribute set
        attributes = self.get_attributes(attribute_set_id)
        attributes_by_name = {attr.name.lower(): attr for attr in attributes}
        attributes_by_label = {attr.label.lower(): attr for attr in attributes}
        
        result = {}
        
        for name, value in attribute_values.items():
            # Find the attribute by name or label
            attr = attributes_by_name.get(name.lower()) or attributes_by_label.get(name.lower())
            if not attr:
                raise ValueError(f"Attribute '{name}' not found in attribute set")
                
            # Skip system attributes (handled separately in product set creation)
            if attr.is_system_attribute():
                continue
                
            # Format the value according to attribute type
            formatted_value = attr.get_value_for_product_set(value)
            
            # Add to result using attribute ID as key
            result[attr.id] = formatted_value
            
        return result
        
    async def prepare_attributes_for_product_set_async(self, 
                                                    attribute_values: Dict[str, Any], 
                                                    attribute_set_id: Optional[int] = None) -> Dict[int, Any]:
        """
        Convert a dictionary of attribute name/value pairs to the format expected by the API, asynchronously.
        
        This helper method makes it easier to specify attributes by name rather than ID.
        
        Args:
            attribute_values: Dictionary mapping attribute names to values
            attribute_set_id: Optional ID of the attribute set to use
            
        Returns:
            Dictionary mapping attribute IDs to properly formatted values
        """
        # Get all attributes for this attribute set
        attributes = await self.get_attributes_async(attribute_set_id)
        attributes_by_name = {attr.name.lower(): attr for attr in attributes}
        attributes_by_label = {attr.label.lower(): attr for attr in attributes}
        
        result = {}
        
        for name, value in attribute_values.items():
            # Find the attribute by name or label
            attr = attributes_by_name.get(name.lower()) or attributes_by_label.get(name.lower())
            if not attr:
                raise ValueError(f"Attribute '{name}' not found in attribute set")
                
            # Skip system attributes (handled separately in product set creation)
            if attr.is_system_attribute():
                continue
                
            # Format the value according to attribute type
            formatted_value = attr.get_value_for_product_set(value)
            
            # Add to result using attribute ID as key
            result[attr.id] = formatted_value
            
        return result
