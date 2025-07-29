from typing import Dict, Any, List, Optional, Union
from datetime import date, datetime

from .base import IconicResource
from ..models import (
    InvoiceDocumentType,
    InvoiceRequest
)

class Invoice(IconicResource):
    """
    Invoice resource for retrieving and downloading invoice files.
    
    This resource provides methods to access tax documents from external storage
    in zipped format, supporting both individual files and all associated files.
    """
    
    endpoint = "invoices"
    model_class = None  # This endpoint returns binary data, not a structured response
    
    def get_invoice_files(self, 
                        **kwargs: Union[Dict[str, Any], InvoiceRequest]) -> bytes:
        """
        Get and download invoice files as a zip archive.
        
        Args:
            **kwargs: Either individual parameters or an InvoiceRequest model:
                order_numbers: List of order numbers to filter by
                invoice_numbers: List of invoice numbers to filter by
                po_numbers: List of purchase order numbers to filter by
                document_types: List of document types to filter by
                start_date: Start date for filtering by creation date
                end_date: End date for filtering by creation date
            
        Returns:
            Binary data containing the zip file with requested documents
        """
        # Handle input as either a model, dict, or individual parameters
        if len(kwargs) == 1 and isinstance(next(iter(kwargs.values())), InvoiceRequest):
            # If passed as a single model parameter
            request = next(iter(kwargs.values()))
            params = request.to_api_params()
        else:
            # If passed as dictionary of parameters
            request = InvoiceRequest(**kwargs)
            params = request.to_api_params()
            
        url = "/v2/invoices"
        
        if hasattr(self._client, '_make_request_sync'):
            # Note: Need to handle binary response differently
            response = self._client._client.get(url, params=params)
            response.raise_for_status()
            return response.content
        else:
            raise TypeError("This method requires a synchronous client")
            
    async def get_invoice_files_async(self, 
                                   **kwargs: Union[Dict[str, Any], InvoiceRequest]) -> bytes:
        """
        Get and download invoice files as a zip archive asynchronously.
        
        Args:
            **kwargs: Either individual parameters or an InvoiceRequest model:
                order_numbers: List of order numbers to filter by
                invoice_numbers: List of invoice numbers to filter by
                po_numbers: List of purchase order numbers to filter by
                document_types: List of document types to filter by
                start_date: Start date for filtering by creation date
                end_date: End date for filtering by creation date
            
        Returns:
            Binary data containing the zip file with requested documents
        """
        # Handle input as either a model, dict, or individual parameters
        if len(kwargs) == 1 and isinstance(next(iter(kwargs.values())), InvoiceRequest):
            # If passed as a single model parameter
            request = next(iter(kwargs.values()))
            params = request.to_api_params()
        else:
            # If passed as dictionary of parameters
            request = InvoiceRequest(**kwargs)
            params = request.to_api_params()
            
        url = "/v2/invoices"
        
        if hasattr(self._client, '_make_request_async'):
            # Note: Need to handle binary response differently
            response = await self._client._client.get(url, params=params)
            response.raise_for_status()
            return response.content
        else:
            raise TypeError("This method requires an asynchronous client")
