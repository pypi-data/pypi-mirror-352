import httpx
import asyncio
import time
import base64
import logging
from typing import Optional, Any, Dict, Union, Type, Tuple, List
from urllib.parse import urlparse

from leakybucket import LeakyBucket, AsyncLeakyBucket
from leakybucket.persistence import InMemoryLeakyBucketStorage, RedisLeakyBucketStorage

from .exceptions import (
    IconicAPIError, 
    AuthenticationError, 
    create_exception_from_response
)
from . import utils
from .resources import (
    Product,
    ProductSet,
    Brand,
    Category,
    Order,
    Transaction,
    Finance,
    Invoice,
    AttributeResource,
    AttributeSetResource,
    Stock
)
from .throttler import throttler, async_throttler

logger = logging.getLogger(__name__)

DEFAULT_TOKEN_BUFFER_SECONDS = 300  # Refresh token 5 minutes before expiry
DEFAULT_RATE_LIMIT_RPS = 25 # Default to 25 requests per second



class BaseIconicClient:
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        instance_domain: str, # e.g., "your-instance.com" (used for both token and API base URLs)
        redis_url: Optional[str] = None,
        rate_limit_rps: float = DEFAULT_RATE_LIMIT_RPS,
        timeout: float = 60.0,
        token_buffer_seconds: int = DEFAULT_TOKEN_BUFFER_SECONDS,
        max_retries: int = 5,
    ):
        if not all([client_id, client_secret, instance_domain]):
            raise ValueError("client_id, client_secret, and instance_domain are required.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.instance_domain = instance_domain.replace("https://", "").replace("http://", "")
        
        self.token_url = f"https://{self.instance_domain}/oauth/client-credentials"
        self.base_api_url = f"https://{self.instance_domain}"
        
        self.timeout = timeout
        self.token_buffer_seconds = token_buffer_seconds
        self.max_retries = max_retries
        self.utils = utils # Make utils accessible

        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

        self._client: Union[httpx.Client, httpx.AsyncClient] # To be defined in subclasses
        
        # Initialize resource classes
        self._initialize_resources()

    def _initialize_resources(self):
        """Initialize resource classes."""
        self.products = Product(client=self)
        self.product_sets = ProductSet(client=self)
        self.brands = Brand(client=self)
        self.categories = Category(client=self)
        self.orders = Order(client=self)
        self.transactions = Transaction(client=self)
        self.finance = Finance(client=self)
        self.invoices = Invoice(client=self)
        self.attributes = AttributeResource(client=self)
        self.attribute_sets = AttributeSetResource(client=self)
        self.stock = Stock(client=self)

    def _get_basic_auth_header(self) -> str:
        auth_str = f"{self.client_id}:{self.client_secret}"
        return "Basic " + base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

    def _is_token_expired(self) -> bool:
        return not self._access_token or time.time() >= (self._token_expires_at - self.token_buffer_seconds)

    def _handle_error_response(self, response: httpx.Response, method: str, url: str, **kwargs):
        """Centralized error handling."""
        logger.error(
            f"API Error: {response.status_code} on {method} {url}. "
            f"Response: {response.content[:500]}"
        )
        
        # When tokens expire, force a refresh
        if response.status_code == 401:
            self._access_token = None  # Force token refresh on next attempt
            
        # Use our generic exception creation helper
        raise create_exception_from_response(response, method, url, **kwargs)

    def _prepare_signed_headers(
        self, http_method: str, full_url: str, body: Optional[bytes] = None
    ) -> Dict[str, str]:
        timestamp = int(time.time())
        nonce = utils.generate_nonce()
        
        parsed_url = urlparse(full_url)
        path_with_query = parsed_url.path
        if parsed_url.query:
            path_with_query += "?" + parsed_url.query
            
        signature = utils.generate_signature(
            app_secret=self.client_secret, # API spec says "application secret" for signing
            http_method=http_method,
            request_path_with_query=path_with_query,
            timestamp=timestamp,
            nonce=nonce,
            body=body,
        )
        return {
            "X-Timestamp": str(timestamp),
            "X-Nonce": nonce,
            "X-Signature-Algorithm": "HMAC-SHA256",
            "X-Signature": signature,
        }


class IconicClient(BaseIconicClient):
    def __init__(self, *args, **kwargs):
        self._client = None  # Initialize to avoid type checking errors before super().__init__
        super().__init__(*args, **kwargs)
        self._client = httpx.Client(base_url=self.base_api_url, timeout=self.timeout)

    def _fetch_new_token_sync(self) -> None:
        headers = {"Authorization": self._get_basic_auth_header()}
        data = {"grant_type": "client_credentials"}
        
        logger.info(f"Fetching new OAuth2 token from {self.token_url}")
        try:
            # Use a separate client for token fetching to avoid circular dependencies or auth issues
            with httpx.Client(timeout=self.timeout) as token_client:
                response = token_client.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data["access_token"]
            self._token_expires_at = time.time() + token_data["expires_in"]
            logger.info("Successfully fetched new OAuth2 token.")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch OAuth2 token: {e.response.status_code} - {e.response.text}")
            self._access_token = None # Ensure token is cleared on failure
            raise AuthenticationError(
                message=f"Failed to fetch OAuth2 token: {e.response.text}",
                response=e.response
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching OAuth2 token: {e}")
            self._access_token = None
            # Create a dummy response for error creation
            dummy_response = httpx.Response(500, request=httpx.Request("POST", self.token_url))
            raise AuthenticationError(
                message=f"Unexpected error fetching token: {str(e)}",
                response=dummy_response
            )

    def _ensure_token_valid_sync(self) -> None:
        if self._is_token_expired():
            self._fetch_new_token_sync()

    
    @throttler.throttle()
    def _make_request_sync(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        requires_signing: bool = False,
    ) -> Any:
        self._ensure_token_valid_sync()
        
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
        }
        
        params = utils.clean_params(params) if params else {}
        
        request_body_bytes: Optional[bytes] = None
        if json_data:
            # httpx will serialize json_data to bytes. We need it for signing.
            # Create a temporary request to get the body.
            temp_req = httpx.Request(method, self.base_api_url + path.lstrip("/"), json=json_data)
            request_body_bytes = temp_req.content

        # Since array vals in params need to be split out (e.g. orderNumbers[]=[1,2,3] -> orderNumbers[]=1&orderNumbers[]=2&orderNumbers[]=3)
        # We can't use the httpx build_request method directly for signing. We need to construct the URL manually.
        url = path + utils.build_params(params) if params else path
        
        if requires_signing:
            # Construct full URL for signing
            # Note: params need to be encoded into the URL string before signing
            # url_for_signing = self._client.build_request(method, path, params=params).url
            signed_headers = self._prepare_signed_headers(method, str(url), request_body_bytes)
            headers.update(signed_headers)

        retries = self.max_retries
        while True:
            try:
                response = self._client.request(
                    method,
                    path,
                    params=params,
                    json=json_data,
                    data=form_data,
                    files=files,
                    headers=headers,
                )
            
                if 200 <= response.status_code < 300:
                    if response.content:
                        return response.json()
                    return {} # For 204 No Content
                
                retry_after_header = response.headers.get("Retry-After")
                should_retry_rate_limit = response.status_code == 429 and retry_after_header and retry_after_header.isdigit()
                should_retry_maintenance = response.status_code == 503 and retry_after_header and retry_after_header.isdigit()
                
                if (should_retry_rate_limit or should_retry_maintenance) and retries > 0:
                    wait_time = int(retry_after_header) # type: ignore
                    logger.warning(f"Status {response.status_code}, retrying after {wait_time}s. Retries left: {retries-1}")
                    time.sleep(wait_time)
                    retries -= 1
                    self._ensure_token_valid_sync() # Re-check token before retry
                    headers["Authorization"] = f"Bearer {self._access_token}" # Re-apply token
                    continue

                self._handle_error_response(response, method, path, params=params, json=json_data, data=form_data)
                return {} # Should not be reached due to raise in _handle_error_response

            except (IconicAPIError) as e:
                if hasattr(e, 'retry_after') and getattr(e, 'retry_after') and retries > 0:
                    logger.warning(f"Caught {type(e).__name__}, retrying after {e.retry_after}s. Retries left: {retries-1}")
                    time.sleep(e.retry_after)
                    retries -= 1
                    self._ensure_token_valid_sync()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    continue
                raise # Reraise if no retry_after or no retries left
            except httpx.RequestError as e: # Network errors
                if retries > 0:
                    logger.warning(f"Network error: {e}. Retrying in 3s. Retries left: {retries-1}")
                    time.sleep(3)
                    retries -= 1
                    continue
                # Create a dummy response for network errors
                dummy_response = httpx.Response(500, request=httpx.Request(method, self.base_api_url + path.lstrip("/")))
                raise IconicAPIError(
                    message=f"Network request failed: {str(e)}",
                    response=dummy_response
                )

    def close(self):
        if self._client:
            self._client.close()


class IconicAsyncClient(BaseIconicClient):
    def __init__(self, *args, **kwargs):
        self._client = None  # Initialize to avoid type checking errors before super().__init__
        super().__init__(*args, **kwargs)
        self._client = httpx.AsyncClient(base_url=self.base_api_url, timeout=self.timeout)

    async def _fetch_new_token_async(self) -> None:
        headers = {"Authorization": self._get_basic_auth_header()}
        data = {"grant_type": "client_credentials"}

        logger.info(f"Fetching new OAuth2 token asynchronously from {self.token_url}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as token_client:
                response = await token_client.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data["access_token"]
            self._token_expires_at = time.time() + token_data["expires_in"]
            logger.info("Successfully fetched new OAuth2 token asynchronously.")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch OAuth2 token asynchronously: {e.response.status_code} - {e.response.text}")
            self._access_token = None
            raise AuthenticationError(
                message=f"Failed to fetch OAuth2 token: {e.response.text}",
                response=e.response
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching OAuth2 token asynchronously: {e}")
            self._access_token = None
            # Create a dummy response for error creation
            dummy_response = httpx.Response(500, request=httpx.Request("POST", self.token_url))
            raise AuthenticationError(
                message=f"Unexpected error fetching token: {str(e)}",
                response=dummy_response
            )

    async def _ensure_token_valid_async(self) -> None:
        if self._is_token_expired():
            await self._fetch_new_token_async()

    @async_throttler.throttle()
    async def _make_request_async(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        requires_signing: bool = False,
    ) -> Any:
        await self._ensure_token_valid_async()
        
        params = utils.clean_params(params) if params else {}
        
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
        }
        
        request_body_bytes: Optional[bytes] = None
        if json_data:
            temp_req = httpx.Request(method, self.base_api_url + path.lstrip("/"), json=json_data)
            request_body_bytes = temp_req.content
            
        if requires_signing:
            url_for_signing = self._client.build_request(method, path, params=params).url
            signed_headers = self._prepare_signed_headers(method, str(url_for_signing), request_body_bytes)
            headers.update(signed_headers)

        retries = self.max_retries
        while True:
            try:
                response = await self._client.request(
                    method,
                    path,
                    params=params,
                    json=json_data,
                    data=form_data,
                    files=files,
                    headers=headers,
                )
                
                if 200 <= response.status_code < 300:
                    if response.content:
                        return response.json()
                    return {}

                retry_after_header = response.headers.get("Retry-After")
                should_retry_rate_limit = response.status_code == 429 and retry_after_header and retry_after_header.isdigit()
                should_retry_maintenance = response.status_code == 503 and retry_after_header and retry_after_header.isdigit()

                if (should_retry_rate_limit or should_retry_maintenance) and retries > 0:
                    wait_time = int(retry_after_header) # type: ignore
                    logger.warning(f"Status {response.status_code}, retrying after {wait_time}s. Retries left: {retries-1}")
                    await asyncio.sleep(wait_time)
                    retries -= 1
                    await self._ensure_token_valid_async()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    continue
                
                self._handle_error_response(response, method, path, params=params, json=json_data, data=form_data)
                return {} # Should not be reached

            except (IconicAPIError) as e:
                if hasattr(e, 'retry_after') and getattr(e, 'retry_after') and retries > 0:
                    logger.warning(f"Caught {type(e).__name__}, retrying after {e.retry_after}s. Retries left: {retries-1}")
                    await asyncio.sleep(e.retry_after)
                    retries -= 1
                    await self._ensure_token_valid_async()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    continue
                raise
            except httpx.RequestError as e:
                if retries > 0:
                    logger.warning(f"Network error: {e}. Retrying in 3s. Retries left: {retries-1}")
                    await asyncio.sleep(3)
                    retries -= 1
                    continue
                # Create a dummy response for network errors
                dummy_response = httpx.Response(500, request=httpx.Request(method, self.base_api_url + path.lstrip("/")))
                raise IconicAPIError(
                    message=f"Network request failed: {str(e)}",
                    response=dummy_response
                )
                
    async def close(self):
        if self._client:
            await self._client.aclose()