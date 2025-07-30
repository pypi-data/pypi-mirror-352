from typing import Dict, Any, List, Optional, Union, Generator
from datetime import datetime

from .base import IconicResource, T
from .transaction import Transaction
from ..models import (
    # Transaction,
    FinanceStatement,
    FinanceStatementListParamsModel,
    FinanceStatementDetails,
    FinanceTransactionsV21,
    TransactionType,
    AccountStatementGroup,
    TransactionVariablesListParamsModel
)

class Finance(IconicResource):
    """
    Finance resource for managing financial statements and related data.
    
    Provides methods for accessing finance statements, their details, and more.
    """
    
    endpoint = "finance"
    model_class = None  # No specific model for the resource itself
    
    def list_statements(self, **params: Union[Dict[str, Any], FinanceStatementListParamsModel]) -> List[FinanceStatement]:
        """
        Get a list of finance statements based on specified parameters.
        
        Args:
            **params: Union[Dict[str, Any], FinanceStatementListParamsModel]
        Returns:
            List of finance statements
        """
        
        if isinstance(params, dict):
            params = FinanceStatementListParamsModel(**params)
            
        params = params.model_dump(exclude_none=True)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        response = self._client._make_request_sync("GET", "/v2/finance/statements", params=params)
        
        return [
            FinanceStatement(**item) for item in response.get("items", [])
        ]

    async def list_statements_async(self, **params: Union[Dict[str, Any], FinanceStatementListParamsModel]) -> List[FinanceStatement]:
        """
        Get a list of finance statements based on specified parameters, asynchronously.
        
        Args:
            **params: Query parameters for filtering the statements
                See list_statements for available parameters
                
        Returns:
            List of finance statements
        """
        
        if isinstance(params, dict):
            params = FinanceStatementListParamsModel(**params)
            
        params = params.model_dump(exclude_none=True)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        response = await self._client._make_request_async("GET", "/v2/finance/statements", params=params)
        
        return [
            FinanceStatement(**item) for item in response.get("items", [])
        ]
        
    def get_statement(self, statement_id: int) -> FinanceStatement:
        """
        Get a single finance statement by ID.
        
        Args:
            statement_id: ID of the finance statement to retrieve
            
        Returns:
            The finance statement
        """
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        response = self._client._make_request_sync("GET", f"/v2/finance/statements/{statement_id}")
        
        return FinanceStatement(**response)
            
    async def get_statement_async(self, statement_id: int) -> FinanceStatement:
        """
        Get a single finance statement by ID, asynchronously.
        
        Args:
            statement_id: ID of the finance statement to retrieve
            
        Returns:
            The finance statement
        """
        url = f"/v2/finance/statements/{statement_id}"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return FinanceStatement(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_statement_details(self, statement_id: int) -> FinanceStatementDetails:
        """
        Get details of a single finance statement by ID.
        
        Args:
            statement_id: ID of the finance statement
            
        Returns:
            The finance statement details
        """
        url = f"/v2/finance/statements/{statement_id}/details"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return FinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_statement_details_async(self, statement_id: int) -> FinanceStatementDetails:
        """
        Get details of a single finance statement by ID, asynchronously.
        
        Args:
            statement_id: ID of the finance statement
            
        Returns:
            The finance statement details
        """
        url = f"/v2/finance/statements/{statement_id}/details"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return FinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_current_statement(self, country: str, statement_type: str = "marketplace") -> FinanceStatement:
        """
        Get a current finance statement for a specific country.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            The current finance statement
        """
        url = f"/v2/finance/statements/current/{country}"
        params = {"type": statement_type}
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return FinanceStatement(**response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_current_statement_async(self, country: str, statement_type: str = "marketplace") -> FinanceStatement:
        """
        Get a current finance statement for a specific country, asynchronously.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            The current finance statement
        """
        url = f"/v2/finance/statements/current/{country}"
        params = {"type": statement_type}
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return FinanceStatement(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_current_statement_details(self, country: str, statement_type: str = "marketplace") -> FinanceStatementDetails:
        """
        Get details of the current finance statement for a specific country.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            The current finance statement details
        """
        url = f"/v2/finance/statements/current/{country}/details"
        params = {"type": statement_type}
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return FinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_current_statement_details_async(self, country: str, statement_type: str = "marketplace") -> FinanceStatementDetails:
        """
        Get details of the current finance statement for a specific country, asynchronously.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            The current finance statement details
        """
        url = f"/v2/finance/statements/current/{country}/details"
        params = {"type": statement_type}
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return FinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def get_future_statements(self, country: str, statement_type: str = "marketplace") -> List[FinanceStatement]:
        """
        Get collection of possible future statements with installment payments.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            List of future finance statements
        """
        url = f"/v2/finance/statements/future/{country}"
        params = {"type": statement_type}
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [FinanceStatement(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
    
    async def get_future_statements_async(self, country: str, statement_type: str = "marketplace") -> List[FinanceStatement]:
        """
        Get collection of possible future statements with installment payments, asynchronously.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            List of future finance statements
        """
        url = f"/v2/finance/statements/future/{country}"
        params = {"type": statement_type}
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [FinanceStatement(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def get_future_statement_details(self, country: str, start_date: datetime, end_date: datetime, statement_type: str = "marketplace") -> FinanceStatementDetails:
        """
        Get details of a concrete future statement.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            start_date: Start date of the expected future statement
            end_date: End date of the expected future statement
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            The future statement details
        """
        url = f"/v2/finance/statements/future/{country}/details"
        params = {
            "type": statement_type,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat()
        }
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return FinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires a synchronous client")
    
    async def get_future_statement_details_async(self, country: str, start_date: datetime, end_date: datetime, statement_type: str = "marketplace") -> FinanceStatementDetails:
        """
        Get details of a concrete future statement, asynchronously.
        
        Args:
            country: Country code (ISO 3166-1 alpha-2 format)
            start_date: Start date of the expected future statement
            end_date: End date of the expected future statement
            statement_type: Type of the statement ('marketplace' or 'consignment')
            
        Returns:
            The future statement details
        """
        url = f"/v2/finance/statements/future/{country}/details"
        params = {
            "type": statement_type,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat()
        }
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return FinanceStatementDetails(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
            
    def list_transactions(self, **params) -> Dict[str, Any]:
        """
        Returns a list of transactions for the specified period and statement IDs.
        
        Args:
            statement_ids: List of IDs of the financial statements
            seller_id: ID of the seller (admin only)
            start_date: Start date for transactions
            end_date: End date for transactions
            source: Source of transactions ('sellercenter', 'web', 'csv')
            country: Country filter
            order_item_id: ID of the order item
            order_item_src_id: Source ID of the order item
            order_numbers: List of order numbers
            sort: Field to sort by ('id', 'date')
            sort_dir: Sort direction ('asc', 'desc')
            numbers: List of transaction numbers
            type_ids: List of transaction type IDs
            is_hybrid: Filter by order item is_hybrid field
            is_outlet: Filter by order item is_outlet field
            is_paid: Filter by paid statement
            product: Filter by product data (name/shop sku/seller sku)
            statement_type: Filter by statement type ('marketplace', 'consignment')
            limit: Maximum number of items to return
            offset: Offset for pagination
            
        Returns:
            Dict containing transactions list with Transaction objects and pagination info
        """
        url = "/v2/finance/transactions"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            
            # Convert transaction items to Transaction objects
            if isinstance(response, dict) and "items" in response:
                from .transaction import Transaction
                
                # Create Transaction objects but preserve pagination info
                result = response.copy()
                result["items"] = [Transaction(client=self._client, data=item) for item in response["items"]]
                return result
            
            return response
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def list_transactions_async(self, **params) -> Dict[str, Any]:
        """
        Returns a list of transactions for the specified period and statement IDs, asynchronously.
        
        Args:
            See list_transactions method for available parameters
            
        Returns:
            Dict containing transactions list with Transaction objects and pagination info
        """
        url = "/v2/finance/transactions"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            
            # Convert transaction items to Transaction objects
            if isinstance(response, dict) and "items" in response:
                from .transaction import Transaction
                
                # Create Transaction objects but preserve pagination info
                result = response.copy()
                result["items"] = [Transaction(client=self._client, data=item) for item in response["items"]]
                return result
                
            return response
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def paginate_transactions(self: T, **params) -> Generator["Transaction", None, None]:
        """Generator to paginate through transactions."""
        return self.paginate_generator(url="/v2/finance/transactions", instance_cls=Transaction, **params)
    
    def list_transactions_v2(self, **params) -> Dict[str, Any]:
        """
        Returns a list of transactions by filter criteria (v2.1 API).
        
        Args:
            statement_type: Filter by statement type ('marketplace', 'consignment')
            seller_id: Filter by seller ID (admin only)
            gte_created_at: Filter by creation date >= value
            lte_created_at: Filter by creation date <= value
            country: Filter by country
            source: Filter by source ('sellercenter', 'api', 'web', 'csv')
            order_item_ids: Filter by order item IDs
            order_item_src_ids: Filter by order item source IDs
            order_numbers: Filter by order numbers
            numbers: Filter by transaction numbers
            products: Filter by product data
            statement_id: Filter by statement ID (0 for current)
            transaction_type_ids: Filter by transaction type IDs
            is_outlet: Filter by order item is_outlet field
            is_hybrid: Filter by order item is_hybrid field
            is_paid: Filter by paid statement
            sort: Sort field ('createdAt', 'transactionType', 'transactionNumber', 'amount')
            sort_dir: Sort direction ('asc', 'desc')
            limit: Maximum number of items to return
            offset: Offset for pagination
            
        Returns:
            Dict containing transactions list with Transaction objects and pagination info
        """
        url = "/v2.1/finance/transactions"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            
            # Convert transaction items to Transaction objects
            if isinstance(response, dict) and "items" in response:
                from .transaction import Transaction
                
                # Create Transaction objects but preserve pagination info
                result = response.copy()
                result["items"] = [Transaction(client=self._client, data=item) for item in response["items"]]
                return result
                
            return response
        else:
            raise TypeError("This method requires a synchronous client")
    
    async def list_transactions_v2_async(self, **params) -> Dict[str, Any]:
        """
        Returns a list of transactions by filter criteria (v2.1 API), asynchronously.
        
        Args:
            See list_transactions_v2 method for available parameters
            
        Returns:
            Dict containing transactions list with Transaction objects and pagination info
        """
        url = "/v2.1/finance/transactions"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            
            # Convert transaction items to Transaction objects
            if isinstance(response, dict) and "items" in response:
                from .transaction import Transaction
                
                # Create Transaction objects but preserve pagination info
                result = response.copy()
                result["items"] = [Transaction(client=self._client, data=item) for item in response["items"]]
                return result
                
            return response
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def list_order_item_transactions(self, **params) -> Dict[str, Any]:
        """
        Returns a list of order item transactions for the specified period.
        
        Args:
            statement_id: Filter by statement ID
            start_date: Start date for transactions
            end_date: End date for transactions
            products: Filter by product data
            product_skus: Filter by product SKUs
            order_numbers: Filter by order numbers
            payout_status: Filter by payout status ('paid', 'unpaid', 'partiallyPaid')
            shipment_types: Filter by shipment types
            status: Filter by order item status
            is_hybrid: Filter by order item is_hybrid field
            is_outlet: Filter by order item is_outlet field
            statement_type: Filter by statement type
            limit: Maximum number of items to return
            offset: Offset for pagination
            sort: Field to sort by
            sort_dir: Sort direction ('asc', 'desc')
            
        Returns:
            Dict containing transactions list with Transaction objects and pagination info
        """
        url = "/v2/finance/order-item-transactions"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            
            # Convert transaction items to Transaction objects
            if isinstance(response, dict) and "items" in response:
                from .transaction import Transaction
                
                # Create Transaction objects but preserve pagination info
                result = response.copy()
                result["items"] = [Transaction(client=self._client, data=item) for item in response["items"]]
                return result
                
            return response
        else:
            raise TypeError("This method requires a synchronous client")
    
    async def list_order_item_transactions_async(self, **params) -> Dict[str, Any]:
        """
        Returns a list of order item transactions for the specified period, asynchronously.
        
        Args:
            See list_order_item_transactions method for available parameters
            
        Returns:
            Dict containing transactions list with Transaction objects and pagination info
        """
        url = "/v2/finance/order-item-transactions"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            
            # Convert transaction items to Transaction objects
            if isinstance(response, dict) and "items" in response:
                from .transaction import Transaction
                
                # Create Transaction objects but preserve pagination info
                result = response.copy()
                result["items"] = [Transaction(client=self._client, data=item) for item in response["items"]]
                return result
                
            return response
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def get_transaction_types(self) -> List[TransactionType]:
        """
        Get the entire list of transaction types.
        
        Returns:
            List of transaction types
        """
        url = "/v2/finance/transaction/types"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url)
            return [TransactionType(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
    
    async def get_transaction_types_async(self) -> List[TransactionType]:
        """
        Get the entire list of transaction types, asynchronously.
        
        Returns:
            List of transaction types
        """
        url = "/v2/finance/transaction/types"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url)
            return [TransactionType(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def get_account_statement_groups(self, statement_type: str = "marketplace") -> List[AccountStatementGroup]:
        """
        Get the entire list of transaction account statement groups.
        
        Args:
            statement_type: Filter by statement type ('marketplace', 'consignment')
            
        Returns:
            List of account statement groups
        """
        url = "/v2/finance/transactions/account-statement-groups"
        params = {"statementType": statement_type}
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("GET", url, params=params)
            return [AccountStatementGroup(**item) for item in response]
        else:
            raise TypeError("This method requires a synchronous client")
    
    async def get_account_statement_groups_async(self, statement_type: str = "marketplace") -> List[AccountStatementGroup]:
        """
        Get the entire list of transaction account statement groups, asynchronously.
        
        Args:
            statement_type: Filter by statement type ('marketplace', 'consignment')
            
        Returns:
            List of account statement groups
        """
        url = "/v2/finance/transactions/account-statement-groups"
        params = {"statementType": statement_type}
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("GET", url, params=params)
            return [AccountStatementGroup(**item) for item in response]
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def create_transaction(self, data: Dict[str, Any]) -> FinanceTransactionsV21:
        """
        Creates a transaction. Available only for admin role and requires request signing.
        
        Args:
            data: Dict containing transaction data with the following fields:
                seller_id: Seller identifier (required)
                transaction_type_id: Transaction type identifier (required)
                account_statement_group_id: Account statement group identifier (required)
                value: Transaction value (required)
                currency: Transaction currency (required)
                description: Transaction description
                reference_id: Reference identifier
                vat_tax: VAT tax value
                wht_tax: WHT tax value
                
        Returns:
            Created transaction
        """
        url = "/v2/finance/transaction"
        
        if hasattr(self._client, '_make_request_sync'):
            response = self._client._make_request_sync("POST", url, json_data=data, requires_signing=True)
            return FinanceTransactionsV21(**response)
        else:
            raise TypeError("This method requires a synchronous client")
    
    async def create_transaction_async(self, data: Dict[str, Any]) -> FinanceTransactionsV21:
        """
        Creates a transaction asynchronously. Available only for admin role and requires request signing.
        
        Args:
            data: Dict containing transaction data with required fields
                (see create_transaction method for details)
                
        Returns:
            Created transaction
        """
        url = "/v2/finance/transaction"
        
        if hasattr(self._client, '_make_request_async'):
            response = await self._client._make_request_async("POST", url, json_data=data, requires_signing=True)
            return FinanceTransactionsV21(**response)
        else:
            raise TypeError("This method requires an asynchronous client")
    
    def list_variables(self, **params: Union[Dict[str, Any], TransactionVariablesListParamsModel]) -> Dict[str, Any]:
        """
        Returns a list of TRE variables which belongs to Global -> Seller inheritance group.
        This endpoint is only available for the admin role.
        
        Args:
            seller_id: The ID of the seller
            seller_src_id: External ID of the seller from third party service
            variable_name: Exact name of TRE variable
            variable_value: Exact value of TRE variable
            limit: Maximum number of items to return
            offset: Offset for pagination
            
        Returns:
            Dict containing variables and pagination info
        """
        url = "/v2/finance/variables"
        
        if isinstance(params, Dict):
            params = TransactionVariablesListParamsModel(**params)
            
        params = params.model_dump(exclude_none=True)
            
        if hasattr(self._client, '_make_request_sync'):
            return self._client._make_request_sync("GET", url, params=params)
        else:
            raise TypeError("This method requires a synchronous client")
    
    async def list_variables_async(self, **params: Union[Dict[str, Any], TransactionVariablesListParamsModel]) -> Dict[str, Any]:
        """
        Returns a list of TRE variables asynchronously.
        
        Args:
            See list_variables method for available parameters
            
        Returns:
            Dict containing variables and pagination info
        """
        url = "/v2/finance/variables"
        
        if isinstance(params, TransactionVariablesListParamsModel):
            params = params.to_api_params()
            
        if hasattr(self._client, '_make_request_async'):
            return await self._client._make_request_async("GET", url, params=params)
        else:
            raise TypeError("This method requires an asynchronous client")
