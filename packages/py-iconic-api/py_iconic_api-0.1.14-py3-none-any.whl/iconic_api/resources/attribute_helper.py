from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from .attribute import AttributeResource
    from .attribute_set import AttributeSetResource

class AttributeHelper:
    """
    Helper class for working with attributes when creating or updating product sets.
    
    This class provides methods to:
    1. Fetch attribute information by name or ID
    2. Format attribute values correctly based on attribute type
    3. Prepare attribute dictionaries for product set creation/update
    
    It's designed to make working with attributes more intuitive and less error-prone.
    """
    
    def __init__(self, attribute_set_resource: "AttributeSetResource"):
        """
        Initialize with an attribute set resource.
        
        Args:
            attribute_set_resource: The attribute set resource to use
        """
        self.attribute_set = attribute_set_resource
        self._attributes_cache: Dict[str, "AttributeResource"] = {}
        self._attribute_id_cache: Dict[int, "AttributeResource"] = {}
        self._initialized = False
        self._logger = logging.getLogger(__name__)
        
    def _ensure_initialized(self):
        """Ensure the helper is initialized with attribute data."""
        if not self._initialized:
            self._load_attributes()
            
    def _load_attributes(self):
        """Load all attributes for the attribute set into the cache."""
        attributes = self.attribute_set.get_attributes()
        
        # Cache by name and label (case insensitive)
        for attr in attributes:
            self._attributes_cache[attr.name.lower()] = attr
            if attr.label:
                self._attributes_cache[attr.label.lower()] = attr
            self._attribute_id_cache[attr.id] = attr
            
        self._initialized = True
            
    def get_attribute(self, name_or_id: Union[str, int]) -> Optional["AttributeResource"]:
        """
        Get an attribute by name, label, or ID.
        
        Args:
            name_or_id: The name, label, or ID of the attribute
            
        Returns:
            The attribute resource if found, None otherwise
        """
        self._ensure_initialized()
        
        if isinstance(name_or_id, int):
            return self._attribute_id_cache.get(name_or_id)
        else:
            return self._attributes_cache.get(name_or_id.lower())
            
    def format_attribute_value(self, attribute: Union[str, int, "AttributeResource"], value: Any) -> Any:
        """
        Format an attribute value based on the attribute type.
        
        Args:
            attribute: The attribute name, ID, or resource
            value: The value to format
            
        Returns:
            The formatted value ready for API submission
            
        Raises:
            ValueError: If the attribute is not found or the value is invalid
        """
        self._ensure_initialized()
        
        # Get the attribute resource
        if isinstance(attribute, (str, int)):
            attr_resource = self.get_attribute(attribute)
            if not attr_resource:
                raise ValueError(f"Attribute '{attribute}' not found")
        else:
            attr_resource = attribute
            
        # Format based on attribute type
        attribute_type = attr_resource.attribute_type
        
        if attribute_type == "value":
            # Simple value - convert to string
            return str(value)
            
        elif attribute_type == "option":
            # Single option - can be ID or name
            if isinstance(value, int):
                # Verify the option ID exists
                if attr_resource.options and not any(opt.id == value for opt in attr_resource.options):
                    raise ValueError(f"Option ID {value} not found for attribute '{attr_resource.name}'")
                return value
            elif isinstance(value, str):
                # Convert option name to ID
                if not attr_resource.options:
                    raise ValueError(f"Attribute '{attr_resource.name}' does not have options")
                
                for opt in attr_resource.options:
                    if opt.name.lower() == value.lower():
                        return opt.id
                        
                raise ValueError(f"Option '{value}' not found for attribute '{attr_resource.name}'")
            else:
                raise ValueError(f"Invalid option value type for attribute '{attr_resource.name}': {type(value)}")
                
        elif attribute_type == "multi_option":
            # Multiple options - can be list of IDs or names
            if not isinstance(value, list):
                raise ValueError(f"Multi-option attribute '{attr_resource.name}' requires a list value")
                
            result = []
            
            if all(isinstance(v, int) for v in value):
                # Verify all option IDs exist
                if attr_resource.options:
                    valid_ids = {opt.id for opt in attr_resource.options}
                    for v in value:
                        if v not in valid_ids:
                            raise ValueError(f"Option ID {v} not found for attribute '{attr_resource.name}'")
                return value
            elif all(isinstance(v, str) for v in value):
                # Convert option names to IDs
                if not attr_resource.options:
                    raise ValueError(f"Attribute '{attr_resource.name}' does not have options")
                
                options_map = {opt.name.lower(): opt.id for opt in attr_resource.options}
                for v in value:
                    option_id = options_map.get(v.lower())
                    if option_id is None:
                        raise ValueError(f"Option '{v}' not found for attribute '{attr_resource.name}'")
                    result.append(option_id)
                return result
            else:
                raise ValueError(f"Invalid multi-option value type for attribute '{attr_resource.name}'")
                
        # Default case
        return value
        
    def prepare_attributes(self, attribute_values: Dict[Union[str, int], Any]) -> Dict[str, Any]:
        """
        Prepare a dictionary of attribute values for product set creation/update.
        
        This method:
        1. Converts attribute names to IDs
        2. Formats values according to attribute types
        3. Separates system attributes from regular attributes
        
        Args:
            attribute_values: Dictionary mapping attribute names/IDs to values
            
        Returns:
            Dictionary with 'attributes' field and any system attributes at root level
        """
        self._ensure_initialized()
        
        result = {"attributes": {}}
        
        for attr_key, value in attribute_values.items():
            # Get the attribute resource
            attr_resource = self.get_attribute(attr_key)
            if not attr_resource:
                self._logger.warning(f"Attribute '{attr_key}' not found, skipping")
                continue
                
            # Format the value
            formatted_value = self.format_attribute_value(attr_resource, value)
            
            # Check if it's a system attribute
            if attr_resource.is_system_attribute():
                # System attributes go at the root level
                system_key = attr_resource.feed_name
                result[system_key] = formatted_value
            else:
                # Regular attributes go in the attributes dictionary
                result["attributes"][str(attr_resource.id)] = formatted_value
                
        return result
