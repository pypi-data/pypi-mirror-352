import time
import logging
import random
from typing import Dict, Optional, Union, Any, Generator

import httpx

from .exceptions import (
    NeoVortexError, ValidationError, TimeoutError, 
    NetworkError, RateLimitError, ResponseError, SecurityError
)
from .models import NeoVortexRequest, NeoVortexResponse
from .validator import RequestValidator
from .middleware import MiddlewareManager
from .hooks import HookManager
from .ratelimit import RateLimiter
from .plugins.registry import registry
from .auth import AuthBase

logger = logging.getLogger("neovortex")

class NeoVortexClient:
    """
    HTTP client for making requests with advanced features.
    
    Features:
    - Automatic retries with exponential backoff
    - Middleware support
    - Plugin system
    - Comprehensive error handling
    - Rate limiting
    - Connection pooling
    """
    
    def __init__(
        self,
        base_url: str = "",
        connect_timeout: float = 5.0,
        read_timeout: float = 30.0,
        auth: Optional[AuthBase] = None,
        headers: Optional[Dict[str, str]] = None,
        proxies: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True,
        max_retries: int = 3,
        max_connections: int = 100,
        max_keepalive: int = 20,
        max_body_size: int = 100 * 1024 * 1024,  # 100MB
    ):
        """Initialize the client with enhanced configuration options."""
        self.base_url = base_url
        self.proxies = proxies
        self.max_body_size = max_body_size
        
        # Validate timeouts
        RequestValidator.validate_timeout(connect_timeout)
        RequestValidator.validate_timeout(read_timeout)
        
        # Validate headers
        RequestValidator.validate_headers(headers)
        
        if proxies:
            for key, value in proxies.items():
                if value and not value.startswith("https://"):
                    raise SecurityError(f"Non-HTTPS proxy detected for {key}. Use HTTPS instead.")
        
        self.client = httpx.Client(
            timeout=httpx.Timeout(
                connect=connect_timeout,
                read=read_timeout,
                write=connect_timeout,
                pool=connect_timeout
            ),
            verify=verify_ssl,
            http2=True,
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive,
            ),
            mounts={
                "https://": httpx.HTTPTransport(proxy=proxies.get("https")) if proxies else None,
            } if proxies else None,
        )
        
        self.auth = auth
        self.headers = headers or {}
        self.middleware = MiddlewareManager()
        self.hooks = HookManager()
        self.rate_limiter = RateLimiter()
        self.max_retries = max_retries
    
    def _handle_auth(self, request: NeoVortexRequest) -> NeoVortexRequest:
        """Apply authentication to the request."""
        if self.auth:
            try:
                return self.auth.authenticate(request)
            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                raise SecurityError(f"Authentication failed: {str(e)}")
        return request
    
    def _process_plugins(self, request: NeoVortexRequest, response=None, start_time=None):
        """Process plugins for the request or response."""
        if response is None:
            # Process request plugins
            for plugin_name, plugin in registry.plugins.items():
                if hasattr(plugin, "process_request"):
                    try:
                        request = plugin.process_request(request)
                    except Exception as e:
                        logger.warning(f"Error in plugin {plugin_name} processing request: {str(e)}")
            return request
        else:
            # Process response plugins
            for plugin_name, plugin in registry.plugins.items():
                if hasattr(plugin, "process_response"):
                    try:
                        response = plugin.process_response(request, response, start_time)
                    except Exception as e:
                        logger.warning(f"Error in plugin {plugin_name} processing response: {str(e)}")
            return response
    
    def stream(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Generator[bytes, None, None]:
        """Stream response data with generator."""
        try:
            with self.client.stream(method, url, **kwargs) as response:
                for chunk in response.iter_bytes():
                    yield chunk
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Stream timed out: {str(e)}")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error during streaming: {str(e)}")
        except Exception as e:
            raise NeoVortexError(f"Streaming error: {str(e)}")
    
    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        priority: int = 0,
        stream: bool = False,
    ) -> Union[NeoVortexResponse, Generator[bytes, None, None]]:
        """Send an HTTP request with enhanced validation and error handling."""
        try:
            # Validate input parameters
            RequestValidator.validate_method(method)
            RequestValidator.validate_url(url)
            RequestValidator.validate_headers(headers)
            RequestValidator.validate_body(data, json)
            
            request = NeoVortexRequest(
                method=method,
                url=self._build_url(url),
                params=params,
                data=data,
                json=json,
                files=files,
                headers={**self.headers, **(headers or {})},
                priority=priority,
            )
            
            request = self._handle_auth(request)
            self.hooks.run("pre_request", request)
            request = self.middleware.process_request(request)
            start_time = time.time()
            request = self._process_plugins(request)
            
            try:
                self.rate_limiter.check_limit(request)
            except Exception as e:
                raise RateLimitError(str(e))
            
            if stream:
                return self.stream(method, url, **request.to_dict())
            
            response = self._send_request(request)
            response = self.middleware.process_response(response)
            response = self._process_plugins(request, response, start_time)
            self.hooks.run("post_response", response)
            self.rate_limiter.update_from_response(response)
            
            return response
            
        except ValidationError:
            raise
        except TimeoutError:
            raise
        except NetworkError:
            raise
        except RateLimitError:
            raise
        except Exception as e:
            if sentry_plugin := registry.get("sentry"):
                sentry_plugin.capture_exception(e)
            raise NeoVortexError(f"Request failed: {str(e)}")
    
    def _build_url(self, url: str) -> str:
        """Build the complete URL with validation."""
        complete_url = f"{self.base_url}{url}" if self.base_url else url
        RequestValidator.validate_url(complete_url)
        return complete_url
    
    def _send_request(self, request: NeoVortexRequest) -> NeoVortexResponse:
        """Send the request with retry logic and enhanced error handling."""
        if metrics_plugin := registry.get("metrics"):
            metrics_plugin.track_start()
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                httpx_response = self.client.request(
                    method=request.method,
                    url=request.url,
                    params=request.params,
                    data=request.data,
                    json=request.json,
                    files=request.files,
                    headers=request.headers,
                )
                
                # Validate response
                if not isinstance(httpx_response, httpx.Response):
                    raise ResponseError("Invalid response type received from HTTP client")
                
                response = NeoVortexResponse(httpx_response)
                
                # Handle error status codes
                if response.status_code >= 400:
                    error_data = None
                    try:
                        if 'application/json' in response.headers.get('content-type', ''):
                            error_data = response.json()
                    except (ValueError, KeyError, AttributeError):
                        pass
                    
                    if response.status_code >= 500:
                        raise NetworkError(f"Server error: {response.status_code}", response=response, error_data=error_data)
                    else:
                        raise ResponseError(f"Client error: {response.status_code}", response=response, error_data=error_data)
                
                return response
                
            except httpx.TimeoutException as e:
                last_error = TimeoutError(f"Request timed out: {str(e)}")
            except httpx.NetworkError as e:
                last_error = NetworkError(f"Network error: {str(e)}")
            except (ResponseError, NetworkError) as e:
                last_error = e
            except Exception as e:
                last_error = NeoVortexError(f"Unexpected error: {str(e)}")
            
            if attempt < self.max_retries - 1:
                logger.warning(f"Retrying request (attempt {attempt + 1}/{self.max_retries}): {str(last_error)}")
                time.sleep(2 ** attempt + random.randint(0, 100) / 1000.0)  # Exponential backoff with jitter
            else:
                raise last_error
    
    def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        try:
            self.client.close()
        except Exception as e:
            logger.error(f"Error closing client: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()