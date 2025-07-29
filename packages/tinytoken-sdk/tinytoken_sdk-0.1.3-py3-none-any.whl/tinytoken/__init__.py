"""TinyToken Python SDK"""

import requests

__version__ = "0.1.3"
__all__ = ["compress", "TinyTokenError"]


class TinyTokenError(Exception):
    """Exception raised for TinyToken API errors."""
    pass

class TinyToken:
    def __init__(self, api_key: str):
        if not api_key or not api_key.strip():
            raise TinyTokenError("API key is required")
        self.api_key = api_key
    
    def compress(self, text: str, quality: float = None) -> str:
        return compress(text, self.api_key, quality)

def compress(text: str, api_key: str, quality: float = None) -> str:
    """
    Compress text using the TinyToken API.
    
    Args:
        text: Text to compress (required)
        api_key: API key for authentication (required)
        quality: Compression quality (optional)
    
    Returns:
        Compressed text as string
    
    Raises:
        TinyTokenError: For any API errors
    """
    
    # Validate required parameters
    if not api_key or not api_key.strip():
        raise TinyTokenError("API key is required")
    
    # Build headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Build the request payload
    payload = {"text": text}
    if quality is not None:
        payload["quality"] = quality
    
    try:
        response = requests.post(
            "https://api.tinytoken.org/compress",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 401:
            raise TinyTokenError("Invalid API key")
        elif response.status_code == 400:
            raise TinyTokenError("Invalid request parameters")
        elif response.status_code == 429:
            raise TinyTokenError("Rate limit exceeded")
        elif not response.ok:
            raise TinyTokenError(f"API error: {response.status_code}")
        
        data = response.json()
        
        if "compressed_text" not in data:
            raise TinyTokenError("Invalid response format")
        
        return data["compressed_text"]
        
    except requests.exceptions.Timeout:
        raise TinyTokenError("Request timeout")
    except requests.exceptions.ConnectionError:
        raise TinyTokenError("Connection error")
    except requests.exceptions.RequestException as e:
        raise TinyTokenError(f"Request failed: {str(e)}")
    except ValueError as e:
        raise TinyTokenError(f"Invalid JSON response: {str(e)}")