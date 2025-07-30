from typing import Dict, Any, List, Optional, Union, Generator, Literal
from datetime import date, datetime

from .base import IconicResource, T
from .finance import Finance
from .transaction import Transaction
from .. import utils
from ..models import (
    Order as OrderModel,
    ListOrdersRequest
)

class Order(IconicResource):
    """
    Order resource representing a single order or a collection of orders.
    
    When initialized with data, it represents a specific order.
    Otherwise, it represents the collection of all orders.
    """
    
    endpoint = "orders"
    model_class = OrderModel
    
    def paginate_generator(self: T, **params: ListOrdersRequest) -> Generator["Order", None, None]:
        """Generator to paginate through orders."""
        if not isinstance(params, ListOrdersRequest):
            params = ListOrdersRequest(**params)
            
        params = params.to_api_params()
        
        return super().paginate_generator(**params)
    
    def list_orders(self, **params: Union[Dict[str, Any], ListOrdersRequest]) -> List["Order"]:
        """List orders based on filter criteria."""
        if not isinstance(params, ListOrdersRequest):
            params = ListOrdersRequest(**params)
            
        params = params.to_api_params()
            
        url = "/v2/orders"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            if isinstance(response, dict) and "items" in response:
                items = response.get("items", [])
            else:
                items = response
            return [Order(client=self._client, data=item) for item in items]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_orders_async(self, **params: Union[Dict[str, Any], ListOrdersRequest]) -> List["Order"]:
        """List orders based on filter criteria asynchronously."""
        if not isinstance(params, ListOrdersRequest):
            params = ListOrdersRequest(**params)
            
        params = params.to_api_params()
        
        url = "/v2/orders"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            if isinstance(response, dict) and "items" in response:
                items = response.get("items", [])
            else:
                items = response
            return [Order(client=self._client, data=item) for item in items]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_by_order_number(self, order_number: str) -> "Order":
        """Get an order by its order number."""
        url = f"/v2/orders/{order_number}"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return Order(client=self._client, data=response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_by_order_number_async(self, order_number: str) -> "Order":
        """Get an order by its order number asynchronously."""
        url = f"/v2/orders/{order_number}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return Order(client=self._client, data=response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_documents(self) -> List[Dict[str, Any]]:
        """Get documents for this order."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot get documents without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/documents"
        
        if hasattr(self._client, '_make_request_sync'):
            return self._client._make_request_sync("GET", url)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_documents_async(self) -> List[Dict[str, Any]]:
        """Get documents for this order asynchronously."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot get documents without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/documents"
        
        if hasattr(self._client, '_make_request_async'):
            return await self._client._make_request_async("GET", url)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def update_status(self, status: str) -> "Order":
        """Update the status of this order."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot update status without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/status"
        payload = {"status": status}
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("PUT", url, json_data=payload)
            # Update this instance's data
            self._data = response
            if self.model_class:
                self._model = self.model_class(**response)
            return self
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def update_status_async(self, status: str) -> "Order":
        """Update the status of this order asynchronously."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot update status without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/status"
        payload = {"status": status}
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("PUT", url, json_data=payload)
            # Update this instance's data
            self._data = response
            if self.model_class:
                self._model = self.model_class(**response)
            return self
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def mark_as_packed(self) -> "Order":
        """Mark this order as packed."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot mark as packed without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/packed"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("PUT", url)
            # Update this instance's data
            self._data = response
            if self.model_class:
                self._model = self.model_class(**response)
            return self
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def mark_as_packed_async(self) -> "Order":
        """Mark this order as packed asynchronously."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot mark as packed without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/packed"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("PUT", url)
            # Update this instance's data
            self._data = response
            if self.model_class:
                self._model = self.model_class(**response)
            return self
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def update_shipment(self, tracking_number: str, shipping_provider: str, shipping_type: Optional[str] = None) -> "Order":
        """Update shipment information for this order."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot update shipment without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/shipment"
        
        payload = {
            "trackingNumber": tracking_number,
            "shippingProvider": shipping_provider
        }
        
        if shipping_type:
            payload["shippingType"] = shipping_type
            
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("PUT", url, json_data=payload)
            # Update this instance's data
            self._data = response
            if self.model_class:
                self._model = self.model_class(**response)
            return self
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def update_shipment_async(self, tracking_number: str, shipping_provider: str, shipping_type: Optional[str] = None) -> "Order":
        """Update shipment information for this order asynchronously."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot update shipment without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/shipment"
        
        payload = {
            "trackingNumber": tracking_number,
            "shippingProvider": shipping_provider
        }
        
        if shipping_type:
            payload["shippingType"] = shipping_type
            
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("PUT", url, json_data=payload)
            # Update this instance's data
            self._data = response
            if self.model_class:
                self._model = self.model_class(**response)
            return self
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def cancel(self, reason: str) -> "Order":
        """Cancel this order."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot cancel without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/cancel"
        payload = {"reason": reason}
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("PUT", url, json_data=payload)
            # Update this instance's data
            self._data = response
            if self.model_class:
                self._model = self.model_class(**response)
            return self
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def cancel_async(self, reason: str) -> "Order":
        """Cancel this order asynchronously."""
        if not self._data.get("orderNumber"):
            raise ValueError("Cannot cancel without an order number")
            
        order_number = self._data["orderNumber"]
        url = f"/v2/orders/{order_number}/cancel"
        payload = {"reason": reason}
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("PUT", url, json_data=payload)
            # Update this instance's data
            self._data = response
            if self.model_class:
                self._model = self.model_class(**response)
            return self
        else:
            raise TypeError("This method requires an asynchronous client")

    def list_finance_transactions(self) -> List["Transaction"]:
        """List financial transactions associated with this order."""
        if not self._data.get("number"):
            raise ValueError("Cannot list transactions without an order number")
        
        finance_client: Finance = self._client.finance
        
        return finance_client.list_transactions(order_numbers=[self._data["number"]])
    
    def bulk_fetch_transactions(self, orders: List["Order"]) -> List[Dict[Literal['order', 'transactions'], Union["Order", List["Transaction"]]]]:
        """Bulk fetch transactions for a list of orders and return a list of dictionaries with order and transactions."""
        
        finance_client: Finance = self._client.finance

        all_transactions = []
        for chunk in utils.chunks(orders, 100):
            all_transactions.extend(finance_client.paginate_transactions(order_numbers=[order.number for order in chunk]))
            
        transactions_by_order = {}
        for order in orders:
            transactions_by_order[order] = [
                transaction for transaction in all_transactions if transaction.orderNumber == order.number
            ]
            
        return [
            {"order": order, "transactions": transactions_by_order[order]}
            for order in orders
        ]