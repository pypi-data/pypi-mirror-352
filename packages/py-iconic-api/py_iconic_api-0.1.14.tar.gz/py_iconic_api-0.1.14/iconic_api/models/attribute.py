from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict

# Enums for attribute properties
class AttributeInputType(StrEnum):
    """Input type for attributes."""
    CHECKBOX = "checkbox"
    DATEFIELD = "datefield"
    DATETIME = "datetime"
    DROPDOWN = "dropdown"
    MULTISELECT = "multiselect"
    NUMBERFIELD = "numberfield"
    TEXTAREA = "textarea"
    TEXTFIELD = "textfield"

class AttributeType(StrEnum):
    """Type of attribute storage."""
    VALUE = "value"
    OPTION = "option"
    MULTI_OPTION = "multi_option"
    SYSTEM = "system"

class AttributeDefinitionType(StrEnum):
    """Definition type for attribute."""
    DEFAULT = "default"
    PRICE_STATUS = "price_status"
    PRICE = "price"
    SPECIAL_PRICE = "special_price"
    SALE_START = "sale_start"
    SALE_END = "sale_end"

class AttributeDefinitionCountry(StrEnum):
    """Country/vendor for attribute."""
    TW = "TW"
    SG = "SG"
    PH = "PH"
    ID = "ID"
    MY = "MY"
    HK = "HK"

class AttributeInputMode(StrEnum):
    """Input mode for attribute."""
    EDIT = "edit"
    DISPLAY = "display"
    INVISIBLE = "invisible"
    EDIT_ON_CREATE = "edit_on_create"

# Models for attribute-related responses
class AttributeOption(BaseModel):
    """Model for attribute option."""
    id: int
    name: str
    is_default: Optional[bool] = None

    # For compatibility with API response field names
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda s: "isDefault" if s == "is_default" else s
    )

class Attribute(BaseModel):
    """Model for attribute details."""
    id: Optional[int] = None
    label: Optional[str] = None
    name: str
    feed_name: str = Field(alias="feedName")
    group_name: Optional[str] = Field(None, alias="groupName")
    is_mandatory: bool = Field(alias="isMandatory")
    is_global_attribute: Optional[bool] = Field(None, alias="isGlobalAttribute")
    description: Optional[str] = None
    product_type: str = Field(alias="productType")
    input_type: AttributeInputType = Field(alias="inputType")
    attribute_type: AttributeType = Field(alias="attributeType")
    example_value: Optional[str] = Field(None, alias="exampleValue")
    max_length: Optional[int] = Field(None, alias="maxLength")
    is_visible_for_hybrid: bool = Field(alias="isVisibleForHybrid")
    attribute_definition_type: Optional[AttributeDefinitionType] = Field(None, alias="attributeDefinitionType")
    attribute_definition_country: Optional[AttributeDefinitionCountry] = Field(None, alias="attributeDefinitionCountry") 
    input_mode: Optional[AttributeInputMode] = Field(None, alias="inputMode")
    forbid_empty: bool = Field(alias="forbidEmpty")
    options: Optional[List[AttributeOption]] = None
    is_edition_by_seller_blocked: bool = Field(alias="isEditionBySellerBlocked")
    is_used_in_consignment_formulas: bool = Field(alias="isUsedInConsignmentFormulas")

    # Helper method to get option by name
    def get_option_id_by_name(self, name: str) -> Optional[int]:
        """Get option ID by option name."""
        if not self.options:
            return None
        
        for option in self.options:
            if option.name.lower() == name.lower():
                return option.id
        return None

    # Helper method to get option by ID
    def get_option_name_by_id(self, option_id: int) -> Optional[str]:
        """Get option name by option ID."""
        if not self.options:
            return None
        
        for option in self.options:
            if option.id == option_id:
                return option.name
        return None

    def is_system_attribute(self) -> bool:
        """Check if this is a system attribute."""
        return self.attribute_type == AttributeType.SYSTEM

class AttributeSet(BaseModel):
    """Model for attribute set."""
    id: int
    name: str
    label: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class AttributeValue:
    """
    Utility class to help create attribute values for product sets.
    This is not a Pydantic model but a helper class to make attribute handling easier.
    """
    @staticmethod
    def text(value: str) -> str:
        """Create a text attribute value."""
        return value

    @staticmethod
    def option(attribute: Attribute, option_name: str) -> int:
        """
        Create an option attribute value by name.
        
        Args:
            attribute: The attribute object that contains the options
            option_name: The name of the option to select
            
        Returns:
            The ID of the selected option
            
        Raises:
            ValueError: If the option name doesn't exist for the attribute
        """
        option_id = attribute.get_option_id_by_name(option_name)
        if option_id is None:
            raise ValueError(f"Option '{option_name}' not found for attribute '{attribute.name}'")
        return option_id

    @staticmethod
    def multi_option(attribute: Attribute, option_names: List[str]) -> List[int]:
        """
        Create a multi-option attribute value by names.
        
        Args:
            attribute: The attribute object that contains the options
            option_names: The names of the options to select
            
        Returns:
            List of option IDs
            
        Raises:
            ValueError: If any option name doesn't exist for the attribute
        """
        option_ids = []
        for name in option_names:
            option_id = attribute.get_option_id_by_name(name)
            if option_id is None:
                raise ValueError(f"Option '{name}' not found for attribute '{attribute.name}'")
            option_ids.append(option_id)
        return option_ids

    @staticmethod
    def multi_text(values: List[str]) -> List[str]:
        """Create a multi-text attribute value."""
        return values
