from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .base import IconicResource
from ..models import (
    Transaction,
    FinanceTransaction,
    TransactionTriggerEvent,
    TransactionStatement
)

class Transaction(IconicResource):
    """
    Transaction resource representing financial transactions and related entities.
    
    When initialized with data, it represents a specific transaction.
    Otherwise, it represents the collection of all transactions.
    """
    
    endpoint = "transaction"
    model_class = FinanceTransaction
    
    def list_by_order_items(self, order_item_ids: List[int]) -> List["Transaction"]:
        """
        Get transactions by order item IDs.
        
        Args:
            order_item_ids: List of order item IDs to fetch transactions for
            
        Returns:
            List of Transaction resources
        """
        url = "/v2/transactions"
        params = {"orderItemIds[]": order_item_ids}
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [Transaction(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_by_order_items_async(self, order_item_ids: List[int]) -> List["Transaction"]:
        """
        Get transactions by order item IDs asynchronously.
        
        Args:
            order_item_ids: List of order item IDs to fetch transactions for
            
        Returns:
            List of Transaction resources
        """
        url = "/v2/transactions"
        params = {"orderItemIds[]": order_item_ids}
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [Transaction(client=self._client, data=item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_trigger_events(self) -> List[TransactionTriggerEvent]:
        """
        Get all transaction trigger events.
        
        Returns:
            List of transaction trigger events
        """
        url = "/v2/transaction/trigger-events"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [TransactionTriggerEvent(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_trigger_events_async(self) -> List[TransactionTriggerEvent]:
        """
        Get all transaction trigger events asynchronously.
        
        Returns:
            List of transaction trigger events
        """
        url = "/v2/transaction/trigger-events"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [TransactionTriggerEvent(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_statements(self, statement_ids: List[int]) -> List[TransactionStatement]:
        """
        Get transaction statements by IDs.
        
        Args:
            statement_ids: List of statement IDs to fetch
            
        Returns:
            List of transaction statements
        """
        url = "/v2/transaction/statements"
        params = {"ids[]": statement_ids}
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [TransactionStatement(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_statements_async(self, statement_ids: List[int]) -> List[TransactionStatement]:
        """
        Get transaction statements by IDs asynchronously.
        
        Args:
            statement_ids: List of statement IDs to fetch
            
        Returns:
            List of transaction statements
        """
        url = "/v2/transaction/statements"
        params = {"ids[]": statement_ids}
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [TransactionStatement(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
