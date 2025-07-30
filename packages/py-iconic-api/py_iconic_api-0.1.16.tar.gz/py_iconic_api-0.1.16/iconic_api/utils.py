import hashlib
import hmac
import datetime
import time
import base64
import random
import string
from urllib.parse import urlparse, parse_qs, urlencode, quote
from typing import Optional, Any, Dict, Union, List

def chunks(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Splits a list into chunks of size n.
    
    Args:
        lst: The list to split.
        n: The size of each chunk.
        
    Returns:
        A list of chunks, each containing up to n elements.
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def generate_nonce(length: int = 32) -> str:
    """Generates a random nonce."""
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_signature(
    app_secret: str,
    http_method: str,
    request_path_with_query: str,
    timestamp: int,
    nonce: str,
    body: Optional[bytes] = None,
) -> str:
    """
    Calculates the HMAC-SHA256 signature for a request.
    """
    body_hash_str = ""
    if body:
        body_hash = hashlib.sha256(body).hexdigest()
        body_hash_str = f"body_hash={body_hash}"
    
    # Ensure path and query are correctly formed.
    # The example shows path with query already encoded: /my/path?foo=bar&zzz=second%20parameter
    # We will assume request_path_with_query is correctly pre-encoded.
    
    signature_content_parts = [
        f"{http_method.upper()} {request_path_with_query}",
        f"timestamp={timestamp}",
        f"nonce={nonce}",
    ]
    # The example signature content has "body_hash=" on a new line even if empty.
    if body_hash_str:
        signature_content_parts.append(body_hash_str)
    else:
        signature_content_parts.append("body_hash=")

    # Each part is on a new line, and the whole string ends with a newline.
    signature_base_string = "\n".join(signature_content_parts) + "\n"

    hashed = hmac.new(
        app_secret.encode("utf-8"),
        signature_base_string.encode("utf-8"),
        hashlib.sha256,
    )
    return hashed.hexdigest()

def to_api_parameter_name(python_name: str) -> str:
    """Converts snake_case to camelCase for API query/body parameters."""
    parts = python_name.split('_')
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

def to_snake_case(camel_case: str) -> str:
    """Converts camelCase to snake_case for Python variables."""
    result = []
    for char in camel_case:
        if char in ('-', '_', '[', ']'):
            continue
        if char.isupper():
            if result:
                result.append('_')
            result.append(char.lower())
        else:
            result.append(char)
    return ''.join(result)

def clean_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Removes None values and prepares list parameters for httpx.
    Example: {'brand_ids': [1,2]} -> {'brandIds[]': [1,2]}
    """
    cleaned = {}
    for key, value in params.items():
        if value is None:
            continue
        
        api_key = to_api_parameter_name(key)
        if isinstance(value, list): 
            if not key.endswith("[]"): # Heuristic for list params
                api_key += "[]"
            for val in value:
                cleaned[api_key] = val

        if isinstance(value, bool):
            cleaned[api_key] = int(value)
        else:
            cleaned[api_key] = value
            
        # Handle date/datetime conversion (to isoformat e.g. 2022-12-11T08:46:12.123456Z)
        if isinstance(value, datetime.date) or isinstance(value, datetime.datetime):
            cleaned[api_key] = value.isoformat() + "Z" if isinstance(value, datetime.datetime) else value.isoformat()
        
        if isinstance(value, dict):
            cleaned[api_key] = clean_params(value)
            
    return cleaned

def build_params(params: Dict[str, Any]) -> str:
    """
    Since array vals in params need to be split out (e.g. orderNumbers[]=[1,2,3] -> orderNumbers[]=1&orderNumbers[]=2&orderNumbers[]=3)
    We can't use the httpx build_request method directly for signing. We need to construct the URL manually.
    """
    params_to_build = []
    for key, value in params.items():
        if isinstance(value, list):
            for item in value:
                params_to_build.append((f"{key}[]" if not key.endswith("[]") else key, item))
        else:
            params_to_build.append((key, value))
    return "&".join(f"{quote(k)}={quote(str(v))}" for k, v in params_to_build)