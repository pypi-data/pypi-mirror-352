from typing import Dict, Any, List, Optional, Union, Literal, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from ..models.stock import StockData

from .base import IconicResource
from ..models import (
    Product,
    ProductSetRead,
    ProductSetCreated,
    ProductRead,
    CreateProductSetRequest,
    UpdateProductSetRequest,
    AddProductSetImageRequest,
    UpdateProductSetImageRequest,
    Image,
    ProductSetsImage,
    ProductSetsCoverImage,
    ProductSetsTag,
    QualityControlStatus,
    PriceRead,
    UpdateProductSetPriceRequest,
    ProductGroupRequest,
)

class ProductSet(IconicResource):
    """
    ProductSet resource representing a single product set or a collection of product sets.
    
    When initialized with data, it represents a specific product set.
    Otherwise, it represents the collection of all product sets.
    """
    
    endpoint = "product-set"
    model_class = ProductSetRead
    
    def list(self, paginated: bool = False, **params) -> List["ProductSet"]:
        return super().list(paginated=paginated, pluralised=True, **params)
    
    def get_products(self) -> List["Product"]:
        """Get products in this product set."""
        if not self.id:
            raise ValueError("Cannot get products without a product set ID")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        return [Product(**item) for item in self.products()]
        
    async def get_products_async(self) -> List["Product"]:
        """Get products in this product set asynchronously."""
        if not self.id:
            raise ValueError("Cannot get products without a product set ID")
            
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        return [Product(**item) for item in (await self.products())]
    
    def get_product(self, product_id: int) -> "Product":
        """Get a specific product in this product set."""
        if not self.id:
            raise ValueError("Cannot get a product without a product set ID")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        return Product(client=self._client, data=self.products(product_id=product_id))
        
    async def get_product_async(self, product_id: int) -> "Product":
        """Get a specific product in this product set asynchronously."""
        if not self.id:
            raise ValueError("Cannot get a product without a product set ID")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        return Product(client=self._client, data=await self.products(product_id=product_id))
        
    def create_product_set(self, data: Union[Dict[str, Any], CreateProductSetRequest], use_attribute_helper: bool = True) -> "ProductSet":
        """
        Create a new product set.
        
        Args:
            data: Data for creating the product set, either as a dictionary or a CreateProductSetRequest model
            use_attribute_helper: Whether to process attribute values using the attribute helper
                                 (which automatically converts attribute names to IDs and formats values)
            
        Returns:
            New ProductSet resource
        """
        if isinstance(data, CreateProductSetRequest):
            data_dict = data.model_dump(by_alias=True, exclude_none=True)
        else:
            data_dict = dict(data)
            
        # If attribute helper is enabled and primary_category_id is provided,
        # process attributes using the helper
        if use_attribute_helper and ('primary_category_id' in data_dict or 'primaryCategoryId' in data_dict):
            try:
                # Get the primary category ID
                primary_category_id = data_dict.get('primary_category_id') or data_dict.get('primaryCategoryId')
                
                # Extract attribute_values if present
                attribute_values = data_dict.pop('attribute_values', None)
                if attribute_values:
                    # Get the category to find its attribute set
                    category = self._client.categories.get(primary_category_id)
                    attribute_set_id = category._data.get('attributeSetId')
                    
                    if attribute_set_id:
                        # Use the attribute set resource to process attributes
                        attribute_set = self._client.attribute_sets.get_attribute_set(attribute_set_id)
                        
                        # Process attributes through the attribute helper
                        from .attribute_helper import AttributeHelper
                        helper = AttributeHelper(attribute_set)
                        prepared_data = helper.prepare_attributes(attribute_values)
                        
                        # Merge the prepared data with the original data
                        if 'attributes' in prepared_data:
                            data_dict['attributes'] = prepared_data['attributes']
                            
                        # Add system attributes to the root level
                        for key, value in prepared_data.items():
                            if key != 'attributes':
                                data_dict[key] = value
            except Exception as e:
                # Log the error but continue with normal processing
                import logging
                logging.getLogger(__name__).warning(f"Error using attribute helper: {e}")
            
        url = "/v2/product-set"  # Direct endpoint for product set creation
        prepared_data = self._prepare_request_data(data_dict)
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=prepared_data)
            return ProductSet(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def create_product_set_async(self, data: Union[Dict[str, Any], CreateProductSetRequest], use_attribute_helper: bool = True) -> "ProductSet":
        """
        Create a new product set asynchronously.
        
        Args:
            data: Data for creating the product set, either as a dictionary or a CreateProductSetRequest model
            use_attribute_helper: Whether to process attribute values using the attribute helper
                                 (which automatically converts attribute names to IDs and formats values)
            
        Returns:
            New ProductSet resource
        """
        if isinstance(data, CreateProductSetRequest):
            data_dict = data.model_dump(by_alias=True, exclude_none=True)
        else:
            data_dict = dict(data)
            
        # If attribute helper is enabled and primary_category_id is provided,
        # process attributes using the helper
        if use_attribute_helper and ('primary_category_id' in data_dict or 'primaryCategoryId' in data_dict):
            try:
                # Get the primary category ID
                primary_category_id = data_dict.get('primary_category_id') or data_dict.get('primaryCategoryId')
                
                # Extract attribute_values if present
                attribute_values = data_dict.pop('attribute_values', None)
                if attribute_values:
                    # Get the category to find its attribute set
                    category = await self._client.categories.get_async(primary_category_id)
                    attribute_set_id = category._data.get('attributeSetId')
                    
                    if attribute_set_id:
                        # Use the attribute set resource to process attributes
                        attribute_set = await self._client.attribute_sets.get_attribute_set_async(attribute_set_id)
                        
                        # Process attributes through the attribute helper
                        from .attribute_helper import AttributeHelper
                        helper = AttributeHelper(attribute_set)
                        prepared_data = helper.prepare_attributes(attribute_values)
                        
                        # Merge the prepared data with the original data
                        if 'attributes' in prepared_data:
                            data_dict['attributes'] = prepared_data['attributes']
                            
                        # Add system attributes to the root level
                        for key, value in prepared_data.items():
                            if key != 'attributes':
                                data_dict[key] = value
            except Exception as e:
                # Log the error but continue with normal processing
                import logging
                logging.getLogger(__name__).warning(f"Error using attribute helper: {e}")
            
        url = "/v2/product-set"  # Direct endpoint for product set creation
        prepared_data = self._prepare_request_data(data_dict)
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=prepared_data)
            return ProductSet(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def update_product_set(self, data: Union[Dict[str, Any], UpdateProductSetRequest], use_attribute_helper: bool = True) -> "ProductSet":
        """
        Update this product set.
        
        Args:
            data: Data for updating the product set, either as a dictionary or an UpdateProductSetRequest model
            use_attribute_helper: Whether to process attribute values using the attribute helper
                                 (which automatically converts attribute names to IDs and formats values)
            
        Returns:
            Updated ProductSet resource
        """
        if not self.id:
            raise ValueError("Cannot update a product set without an ID")
            
        if isinstance(data, UpdateProductSetRequest):
            data_dict = data.model_dump(by_alias=True, exclude_none=True)
        else:
            data_dict = dict(data)
            
        # If attribute helper is enabled, process attributes using the helper
        if use_attribute_helper:
            try:
                # Extract attribute_values if present
                attribute_values = data_dict.pop('attribute_values', None)
                if attribute_values:
                    # Use the attribute set associated with this product set
                    attribute_set_id = self._data.get('attributeSetId')
                    
                    if attribute_set_id:
                        # Use the attribute set resource to process attributes
                        attribute_set = self._client.attribute_sets.get_attribute_set(attribute_set_id)
                        
                        # Process attributes through the attribute helper
                        from .attribute_helper import AttributeHelper
                        helper = AttributeHelper(attribute_set)
                        prepared_data = helper.prepare_attributes(attribute_values)
                        
                        # Merge the prepared data with the original data
                        if 'attributes' in prepared_data:
                            data_dict['attributes'] = prepared_data['attributes']
                            
                        # Add system attributes to the root level
                        for key, value in prepared_data.items():
                            if key != 'attributes':
                                data_dict[key] = value
            except Exception as e:
                # Log the error but continue with normal processing
                import logging
                logging.getLogger(__name__).warning(f"Error using attribute helper: {e}")
            
        url = f"/v2/product-set/{self.id}"
        prepared_data = self._prepare_request_data(data_dict)
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
            # Update this instance's data
            self._data = response
            if self.model_class:
                self._model = self.model_class(**response)
            return self
        else:
            raise TypeError("This method requires a synchronous client")
    
    async def update_product_set_async(self, data: Union[Dict[str, Any], UpdateProductSetRequest], use_attribute_helper: bool = True) -> "ProductSet":
        """
        Update this product set asynchronously.
        
        Args:
            data: Data for updating the product set, either as a dictionary or an UpdateProductSetRequest model
            use_attribute_helper: Whether to process attribute values using the attribute helper
                                 (which automatically converts attribute names to IDs and formats values)
            
        Returns:
            Updated ProductSet resource
        """
        if not self.id:
            raise ValueError("Cannot update a product set without an ID")
            
        if isinstance(data, UpdateProductSetRequest):
            data_dict = data.model_dump(by_alias=True, exclude_none=True)
        else:
            data_dict = dict(data)
            
        # If attribute helper is enabled, process attributes using the helper
        if use_attribute_helper:
            try:
                # Extract attribute_values if present
                attribute_values = data_dict.pop('attribute_values', None)
                if attribute_values:
                    # Use the attribute set associated with this product set
                    attribute_set_id = self._data.get('attributeSetId')
                    
                    if attribute_set_id:
                        # Use the attribute set resource to process attributes
                        attribute_set = await self._client.attribute_sets.get_attribute_set_async(attribute_set_id)
                        
                        # Process attributes through the attribute helper
                        from .attribute_helper import AttributeHelper
                        helper = AttributeHelper(attribute_set)
                        prepared_data = helper.prepare_attributes(attribute_values)
                        
                        # Merge the prepared data with the original data
                        if 'attributes' in prepared_data:
                            data_dict['attributes'] = prepared_data['attributes']
                            
                        # Add system attributes to the root level
                        for key, value in prepared_data.items():
                            if key != 'attributes':
                                data_dict[key] = value
            except Exception as e:
                # Log the error but continue with normal processing
                import logging
                logging.getLogger(__name__).warning(f"Error using attribute helper: {e}")
        
        url = f"/v2/product-set/{self.id}"
        prepared_data = self._prepare_request_data(data_dict)
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
            # Update this instance's data
            self._data = response
            if self.model_class:
                self._model = self.model_class(**response)
            return self
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Products related methods
    
    def get_products(self) -> List["Product"]:
        """Get all products for this product set."""
        if not self.id:
            raise ValueError("Cannot get products without a product set ID")
            
        url = f"/v2/product-set/{self.id}/products"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            
            from .product import Product
            return [Product(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_products_async(self) -> List["Product"]:
        """Get all products for this product set asynchronously."""
        if not self.id:
            raise ValueError("Cannot get products without a product set ID")
            
        url = f"/v2/product-set/{self.id}/products"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            
            from .product import Product
            return [Product(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def create_product(self, data: Dict[str, Any]) -> "Product":
        """Create a new product for this product set."""
        if not self.id:
            raise ValueError("Cannot create a product without a product set ID")
            
        url = f"/v2/product-set/{self.id}/products"
        prepared_data = self._prepare_request_data(data)
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=prepared_data)
            
            from .product import Product
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def create_product_async(self, data: Dict[str, Any]) -> "Product":
        """Create a new product for this product set asynchronously."""
        if not self.id:
            raise ValueError("Cannot create a product without a product set ID")
            
        url = f"/v2/product-set/{self.id}/products"
        prepared_data = self._prepare_request_data(data)
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=prepared_data)
            
            from .product import Product
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_product(self, product_id: int) -> "Product":
        """Get a specific product in this product set."""
        if not self.id:
            raise ValueError("Cannot get a product without a product set ID")
            
        url = f"/v2/product-set/{self.id}/products/{product_id}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            
            from .product import Product
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_product_async(self, product_id: int) -> "Product":
        """Get a specific product in this product set asynchronously."""
        if not self.id:
            raise ValueError("Cannot get a product without a product set ID")
            
        url = f"/v2/product-set/{self.id}/products/{product_id}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            
            from .product import Product
            return Product(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Images related methods
    
    def get_images(self) -> List[Image]:
        """Get all images for this product set."""
        if not self.id:
            raise ValueError("Cannot get images without a product set ID")
            
        url = f"/v2/product-set/{self.id}/images"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [Image(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_images_async(self) -> List[Image]:
        """Get all images for this product set asynchronously."""
        if not self.id:
            raise ValueError("Cannot get images without a product set ID")
            
        url = f"/v2/product-set/{self.id}/images"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [Image(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def add_image(self, data: Union[Dict[str, Any], AddProductSetImageRequest]) -> Image:
        """Add an image to this product set."""
        if not self.id:
            raise ValueError("Cannot add an image without a product set ID")
            
        if isinstance(data, AddProductSetImageRequest):
            data = data.model_dump(by_alias=True, exclude_none=True)
            
        url = f"/v2/product-set/{self.id}/images"
        prepared_data = self._prepare_request_data(data)
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=prepared_data)
            return Image(**response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def add_image_async(self, data: Union[Dict[str, Any], AddProductSetImageRequest]) -> Image:
        """Add an image to this product set asynchronously."""
        if not self.id:
            raise ValueError("Cannot add an image without a product set ID")
            
        if isinstance(data, AddProductSetImageRequest):
            data = data.model_dump(by_alias=True, exclude_none=True)
            
        url = f"/v2/product-set/{self.id}/images"
        prepared_data = self._prepare_request_data(data)
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=prepared_data)
            return Image(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def upload_image(self, image_file_path: str, position: Optional[int] = None, overwrite: bool = False) -> Image:
        """Upload an image file to this product set."""
        if not self.id:
            raise ValueError("Cannot upload an image without a product set ID")
            
        url = f"/v2/product-set/{self.id}/images"
        
        with open(image_file_path, "rb") as f:
            files = {"file1": (image_file_path.split('/')[-1], f)}
            form_data = {}
            
            if position is not None:
                form_data["position"] = str(position)
                
            if overwrite:
                form_data["overwrite"] = "true"
            
            if hasattr(self._client, '_make_request_sync'):
                response = self._client._make_request_sync("POST", url, form_data=form_data, files=files)
                return Image(**response)
            else:
                raise TypeError("This method requires a synchronous client")
                
    async def upload_image_async(self, image_file_path: str, position: Optional[int] = None, overwrite: bool = False) -> Image:
        """Upload an image file to this product set asynchronously."""
        if not self.id:
            raise ValueError("Cannot upload an image without a product set ID")
            
        url = f"/v2/product-set/{self.id}/images"
        
        with open(image_file_path, "rb") as f:
            files = {"file1": (image_file_path.split('/')[-1], f)}
            form_data = {}
            
            if position is not None:
                form_data["position"] = str(position)
                
            if overwrite:
                form_data["overwrite"] = "true"
            
            if hasattr(self._client, '_make_request_async'):
                response = await self._client._make_request_async("POST", url, form_data=form_data, files=files)
                return Image(**response)
            else:
                raise TypeError("This method requires an asynchronous client")
                
    # Group related methods
    
    def get_group(self) -> Dict[str, str]:
        """Get the group this product set belongs to."""
        if not self.id:
            raise ValueError("Cannot get group without a product set ID")
            
        url = f"/v2/product-set/{self.id}/group"
        
        if hasattr(self._client, '_make_request_sync'):
            return self._client._make_request_sync("GET", url)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_group_async(self) -> Dict[str, str]:
        """Get the group this product set belongs to asynchronously."""
        if not self.id:
            raise ValueError("Cannot get group without a product set ID")
            
        url = f"/v2/product-set/{self.id}/group"
        
        if hasattr(self._client, '_make_request_async'):
            return await self._client._make_request_async("GET", url)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def add_to_group(self, data: Union[Dict[str, Any], ProductGroupRequest]) -> Dict[str, str]:
        """Add this product set to a group."""
        if not self.id:
            raise ValueError("Cannot add to group without a product set ID")
            
        if isinstance(data, ProductGroupRequest):
            data = data.model_dump(by_alias=True, exclude_none=True)
            
        url = f"/v2/product-set/{self.id}/group"
        prepared_data = self._prepare_request_data(data)
        
        if hasattr(self._client, '_make_request_sync'):
            return self._client._make_request_sync("POST", url, json_data=prepared_data)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def add_to_group_async(self, data: Union[Dict[str, Any], ProductGroupRequest]) -> Dict[str, str]:
        """Add this product set to a group asynchronously."""
        if not self.id:
            raise ValueError("Cannot add to group without a product set ID")
            
        if isinstance(data, ProductGroupRequest):
            data = data.model_dump(by_alias=True, exclude_none=True)
            
        url = f"/v2/product-set/{self.id}/group"
        prepared_data = self._prepare_request_data(data)
        
        if hasattr(self._client, '_make_request_async'):
            return await self._client._make_request_async("POST", url, json_data=prepared_data)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def remove_from_group(self) -> None:
        """Remove this product set from its group."""
        if not self.id:
            raise ValueError("Cannot remove from group without a product set ID")
            
        url = f"/v2/product-set/{self.id}/group"
        
        if hasattr(self._client, '_make_request_sync'):
            self._client._make_request_sync("DELETE", url)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def remove_from_group_async(self) -> None:
        """Remove this product set from its group asynchronously."""
        if not self.id:
            raise ValueError("Cannot remove from group without a product set ID")
            
        url = f"/v2/product-set/{self.id}/group"
        
        if hasattr(self._client, '_make_request_async'):
            await self._client._make_request_async("DELETE", url)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    # Stock related methods
    
    def get_product_stocks(self) -> List["StockData"]:
        """
        Get stock information for all products in this product set.
        
        Returns:
            List of StockData objects containing product stock information
        """
        if not self.id:
            raise ValueError("Cannot get stock without a product set ID")
            
        if hasattr(self._client, 'stock'):
            return self._client.stock.get_product_set_stock(self.id)
        else:
            raise ValueError("Client does not have a stock resource")
            
    async def get_product_stocks_async(self) -> List["StockData"]:
        """
        Get stock information for all products in this product set asynchronously.
        
        Returns:
            List of StockData objects containing product stock information
        """
        if not self.id:
            raise ValueError("Cannot get stock without a product set ID")
            
        if hasattr(self._client, 'stock'):
            return await self._client.stock.get_product_set_stock_async(self.id)
        else:
            raise ValueError("Client does not have a stock resource")
    
    # Static methods for operating on multiple product sets
    
    @classmethod
    def get_cover_images(cls, client: Any, product_set_ids: List[int]) -> List[ProductSetsCoverImage]:
        """Get cover images for multiple product sets."""
        url = "/v2/product-sets/cover-image"
        params = {"productSetIds[]": product_set_ids}
        
        if hasattr(client, '_make_request_sync'):
            response = client._make_request_sync("GET", url, params=params)
            return [ProductSetsCoverImage(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    @classmethod
    async def get_cover_images_async(cls, client: Any, product_set_ids: List[int]) -> List[ProductSetsCoverImage]:
        """Get cover images for multiple product sets asynchronously."""
        url = "/v2/product-sets/cover-image"
        params = {"productSetIds[]": product_set_ids}
        
        if hasattr(client, '_make_request_async'):
            response = await client._make_request_async("GET", url, params=params)
            return [ProductSetsCoverImage(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
