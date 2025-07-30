import json
from typing import (
    Any, 
    Dict, 
    List, 
    Optional, 
    Type, 
    TypeVar, 
    Union, 
    Generator,
    AsyncGenerator,
    cast,
    Generic,
    Literal
)
from pydantic import BaseModel

from ..utils import to_snake_case, to_api_parameter_name, clean_params

T = TypeVar("T", bound="IconicResource")
ModelT = TypeVar("ModelT", bound=BaseModel)

class PaginatedResponse(Generic[T]):
    """
    Generic container for paginated API responses.
    
    Provides access to:
    - items: The list of resource instances
    - limit: The number of items per page
    - offset: The starting offset
    - total_count: The total number of items available
    """
    
    def __init__(self, 
                items: List[T], 
                limit: int, 
                offset: int, 
                total_count: int):
        self.items = items
        self.limit = limit
        self.offset = offset
        self.total_count = total_count
        
    def __len__(self) -> int:
        return len(self.items)
        
    def __iter__(self):
        return iter(self.items)
        
    def __getitem__(self, index):
        return self.items[index]

class IconicResource:
    """
    Base class for all Iconic API resources.
    
    This class implements a hybrid approach where it can represent both:
    1. A collection of resources (when initialized without data)
    2. A specific resource instance (when initialized with data)
    
    The __call__ method behaves as follows:
      - If a resource_id is provided, it returns a single resource instance
      - Otherwise, it returns a list of resources matching any provided filters
    """
    
    endpoint: str = ""
    model_class: Optional[Type[BaseModel]] = None
    
    def __init__(
        self,
        *,
        client: Any,  # IconicClient or IconicAsyncClient
        data: Optional[Dict[str, Any]] = None,
        parent: Optional["IconicResource"] = None,
        parent_path: Optional[str] = None,
    ) -> None:
        self._client = client
        self._data: Dict[str, Any] = data or {}
        self._parent = parent
        self._parent_path = parent_path
        self._model: Optional[BaseModel] = None
        
        # Initialize model if data and model_class are provided
        if data and self.model_class:
            self._model = self.model_class(**data)
    
    def __getattr__(self, name: str) -> Any:
        # First try to get from the model
        if self._model and hasattr(self._model, name):
            return getattr(self._model, name)
            
        # Then try to get from the data dictionary
        if name in self._data:
            return self._data[name]
            
        # If we have an ID, try to treat it as a related resource or custom endpoint
        if self.id:
            # Try to load a related resource class
            try:
                from importlib import import_module
                module = import_module(f"..resources.{name.lower()}", __name__)
                resource_class = getattr(module, name.capitalize())
                return resource_class(
                    client=self._client, 
                    parent=self, 
                    parent_path=self._build_url(self.id)
                )
            except (ModuleNotFoundError, AttributeError):
                # If no module exists, assume it's a custom endpoint
                def dynamic_endpoint(*args, **kwargs):
                    path = f"{self._build_url(self.id)}/{name.replace('_', '/')}"
                    
                    if hasattr(self._client, '_make_request_sync'):
                        return self._client._make_request_sync("GET", path, params=kwargs)
                    else:
                        async def async_endpoint():
                            return await self._client._make_request_async("GET", path, params=kwargs)
                        return async_endpoint()
                        
                return dynamic_endpoint
                
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")
        
    def __repr__(self) -> str:
        if self._data.get("id"):
            return f"<{self.__class__.__name__} id={self._data.get('id')}>"
        return f"<{self.__class__.__name__} collection>"
        
    @property
    def id(self) -> Optional[Union[int, str]]:
        """Return the ID of this resource, if it exists."""
        return getattr(self._model, "id", self._data.get("id"))
    
    @classmethod
    def get_endpoint(cls, pluralised: bool = False) -> str:
        """Get the API endpoint for this resource."""
        return (cls.endpoint or to_snake_case(cls.__name__)) + ("s" if pluralised else "")
        
    def _build_url(self, resource_id: Optional[Any] = None, suffix: str = "", pluralised: bool = False) -> str:
        """Build a URL path for this resource."""
        if self._parent_path:
            base = f"{self._parent_path}/{self.get_endpoint(pluralised)}"
        else:
            base = f"/v2/{self.get_endpoint(pluralised)}"
            
        url = base
        if resource_id is not None:
            url = f"{url}/{resource_id}"
        if suffix:
            url = f"{url}/{suffix}"
            
        return url
        
    def _prepare_request_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare parameters for an API request."""
        return clean_params(params)
        
    def _prepare_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert data for an API request."""
        if hasattr(data, "model_dump"):
            # It's a Pydantic model
            data = data.model_dump(by_alias=True, exclude_none=True)
        return {to_api_parameter_name(k): v for k, v in data.items()}

    def _create_instance(self: T, data: Dict[str, Any], instance_cls: Optional[Type[T]] = None) -> T:
        """Create a new instance of this resource with the given data."""
        instance_cls = instance_cls or self.__class__
        return instance_cls(client=self._client, data=data, parent_path=self._parent_path)

    def _extract_pagination_data(self, response: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract pagination information from a response."""
        if isinstance(response, dict) and "pagination" in response:
            pagination = response.get("pagination", {})
            limit = pagination.get("limit", params.get("limit", 100))
            offset = pagination.get("offset", params.get("offset", 0))
            total_count = pagination.get("totalCount", 0)
            
            return {
                "limit": limit,
                "offset": offset,
                "total_count": total_count
            }
        
        return {
            "limit": params.get("limit", 100),
            "offset": params.get("offset", 0),
            "total_count": len(response) if isinstance(response, list) else 0
        }
        
    def _extract_items(self, response: Any) -> List[Dict[str, Any]]:
        """Extract items from a response."""
        if isinstance(response, dict) and "items" in response:
            return response.get("items", [])
        elif isinstance(response, list):
            return response
        else:
            return [response] if response else []
        
    def to_dict(self, mode: Literal['json', 'python'] = 'python') -> Dict[str, Any]:
        """Convert the resource instance to a dictionary."""
        if self._model:
            return self._model.model_dump(mode=mode, by_alias=True, exclude_none=False)
        return self._data.copy()
        
    # Synchronous methods
    
    def __call__(self: T, resource_id: Optional[Any] = None, **params) -> Union[T, List[T], PaginatedResponse[T]]:
        """
        If a resource_id is provided, fetch a single resource by ID.
        Otherwise, list resources based on the provided parameters.
        """
        if resource_id is not None:
            return self.get(resource_id)
        return self.list(**params)
        
    def get(self: T, resource_id: Any, pluralised: bool = False) -> T:
        """Get a single resource by ID."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(resource_id, pluralised=pluralised)
        response = self._client._make_request_sync("GET", url)
        
        # Handle both single response and list response
        if isinstance(response, list):
            data = response[0] if response else {}
        else:
            data = response
            
        return self._create_instance(data)
        
    def list(
        self: T,
        paginated: bool = False,
        pluralised: bool = False,
        url: Optional[str] = None,
        instance_cls: Optional[Type[ModelT]] = None,
        **params
    ) -> Union[List[T], PaginatedResponse[T]]:
        """
        List resources matching the given parameters.
        
        Args:
            paginated: If True, return a PaginatedResponse object instead of a list
            pluralised: If True, use the pluralized endpoint
            url: Optional custom URL to use for the request
            instance_cls: Optional class to use for creating instances
            **params: Filter parameters for the request
        
        Returns:
            Either a list of resource instances or a PaginatedResponse object
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        url = url or self._build_url(pluralised=pluralised)
        prepared_params = self._prepare_request_params(params)
        response = self._client._make_request_sync("GET", url, params=prepared_params)
        
        # Extract pagination data and items
        items = self._extract_items(response)
        instances = [self._create_instance(item, instance_cls=instance_cls) for item in items]
        
        if paginated:
            pagination_data = self._extract_pagination_data(response, params)
            return PaginatedResponse(
                items=instances,
                limit=pagination_data["limit"],
                offset=pagination_data["offset"],
                total_count=pagination_data["total_count"]
            )
        
        return instances
        
    def create(self: T, data: Dict[str, Any], pluralised: bool = False) -> T:
        """Create a new resource."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        url = self._build_url(pluralised=pluralised)
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
        
    def update(self: T, resource_id: Any, data: Dict[str, Any], pluralised: bool = False) -> T:
        """Update an existing resource."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        url = self._build_url(resource_id, pluralised=pluralised)
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
        
    def delete(self, resource_id: Any, pluralised: bool = False) -> None:
        """Delete a resource."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        url = self._build_url(resource_id, pluralised=pluralised)
        self._client._make_request_sync("DELETE", url)

    def paginate(self: T, url: Optional[str] = None, instance_cls: Optional[Type[ModelT]] = None, **params) -> PaginatedResponse[T]:
        """
        Paginate through resources with automatic handling of pagination parameters.
        
        Args:
            **params: Filter parameters for the request
            
        Returns:
            A PaginatedResponse object containing the first page of results
        """
        return self.list(paginated=True, url=url, instance_cls=instance_cls, **params)

    def paginate_all(self: T, url: Optional[str] = None, instance_cls: Optional[Type[ModelT]] = None, **params) -> List[T]:
        """
        Retrieve all resources matching the given parameters, handling pagination automatically.
        
        Args:
            **params: Filter parameters for the request
            
        Returns:
            A list of all matching resources
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        all_items: List[T] = []
        
        while True:
            params["limit"] = limit
            params["offset"] = offset
            
            page = self.list(paginated=True, url=url, instance_cls=instance_cls, **params)
            all_items.extend(page.items)
            
            if len(page.items) < limit:
                break
                
            offset += limit
            
        return all_items

    def paginate_generator(self: T, url: Optional[str] = None, instance_cls: Optional[Type[ModelT]] = None, **params) -> Generator[T, None, None]:
        """
        Generator that yields all resources matching the given parameters.
        
        Args:
            **params: Filter parameters for the request
            
        Yields:
            Resource instances one at a time
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        
        while True:
            params["limit"] = limit
            params["offset"] = offset
            
            page = self.list(paginated=True, url=url, instance_cls=instance_cls, **params)
            
            if not page.items:
                break
                
            for item in page.items:
                yield item
                
            if len(page.items) < limit:
                break
                
            offset += limit
        
    # Asynchronous methods
    
    async def get_async(self: T, resource_id: Any, pluralised: bool = False) -> T:
        """Get a single resource by ID asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(resource_id, pluralised=pluralised)
        response = await self._client._make_request_async("GET", url)
        
        # Handle both single response and list response
        if isinstance(response, list):
            data = response[0] if response else {}
        else:
            data = response
            
        return self._create_instance(data)

    async def list_async(
        self: T, 
        paginated: bool = False, 
        pluralised: bool = False, 
        url: Optional[str] = None, 
        instance_cls: Optional[Type[ModelT]] = None,
        **params
    ) -> Union[List[T], PaginatedResponse[T]]:
        """
        List resources matching the given parameters asynchronously.
        
        Args:
            paginated: If True, return a PaginatedResponse object instead of a list
            pluralised: If True, use the pluralized endpoint
            url: Optional custom URL to use for the request
            instance_cls: Optional class to use for creating instances
            **params: Filter parameters for the request
        
        Returns:
            Either a list of resource instances or a PaginatedResponse object
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        url = url or self._build_url(pluralised=pluralised)
        prepared_params = self._prepare_request_params(params)
        response = await self._client._make_request_async("GET", url, params=prepared_params)
        
        # Extract pagination data and items
        items = self._extract_items(response)
        instances = [self._create_instance(item, instance_cls=instance_cls) for item in items]
        
        if paginated:
            pagination_data = self._extract_pagination_data(response, params)
            return PaginatedResponse(
                items=instances,
                limit=pagination_data["limit"],
                offset=pagination_data["offset"],
                total_count=pagination_data["total_count"]
            )
        
        return instances
        
    async def create_async(self: T, data: Dict[str, Any], pluralised: bool = False) -> T:
        """Create a new resource asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        url = self._build_url(pluralised=pluralised)
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
        
    async def update_async(self: T, resource_id: Any, data: Dict[str, Any], pluralised: bool = False) -> T:
        """Update an existing resource asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        url = self._build_url(resource_id, pluralised=pluralised)
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
        
    async def delete_async(self, resource_id: Any, pluralised: bool = False) -> None:
        """Delete a resource asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        url = self._build_url(resource_id, pluralised=pluralised)
        await self._client._make_request_async("DELETE", url)

    async def paginate_async(self: T, url: Optional[str] = None, instance_cls: Optional[Type[ModelT]] = None, **params) -> PaginatedResponse[T]:
        """
        Paginate through resources with automatic handling of pagination parameters asynchronously.
        
        Args:
            **params: Filter parameters for the request
            
        Returns:
            A PaginatedResponse object containing the first page of results
        """
        return await self.list_async(paginated=True, url=url, instance_cls=instance_cls, **params)

    async def paginate_all_async(self: T, url: Optional[str] = None, instance_cls: Optional[Type[ModelT]] = None, **params) -> List[T]:
        """
        Retrieve all resources matching the given parameters, handling pagination automatically, asynchronously.
        
        Args:
            **params: Filter parameters for the request
            
        Returns:
            A list of all matching resources
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        all_items: List[T] = []
        
        while True:
            params["limit"] = limit
            params["offset"] = offset

            page = await self.list_async(paginated=True, url=url, instance_cls=instance_cls, **params)
            all_items.extend(page.items)
            
            if len(page.items) < limit:
                break
                
            offset += limit
            
        return all_items

    async def paginate_async_generator(self: T, url: Optional[str] = None, instance_cls: Optional[Type[ModelT]] = None, **params) -> AsyncGenerator[T, None]:
        """
        Async generator that yields all resources matching the given parameters.
        
        Args:
            **params: Filter parameters for the request
            
        Yields:
            Resource instances one at a time
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)
        
        while True:
            params["limit"] = limit
            params["offset"] = offset

            page = await self.list_async(paginated=True, url=url, instance_cls=instance_cls, **params)

            if not page.items:
                break
                
            for item in page.items:
                yield item
                
            if len(page.items) < limit:
                break
                
            offset += limit