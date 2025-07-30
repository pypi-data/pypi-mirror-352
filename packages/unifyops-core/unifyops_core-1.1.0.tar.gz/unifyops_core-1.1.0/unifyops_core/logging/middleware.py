"""
FastAPI middleware for request logging and correlation ID tracking.

This module provides middleware for FastAPI applications to:
1. Track correlation IDs across requests
2. Log request details including timing
3. Set up context for structured logging
4. Extract W3C Trace Context headers for distributed tracing

Use this middleware in your FastAPI application to enable
consistent logging and correlation ID tracking.
"""

import time
import uuid
import json
import re
from typing import Optional, Set, Callable, Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI

from unifyops_core.logging import (
    get_logger, 
    set_correlation_id, 
    add_logging_metadata,
    set_trace_context,
    set_request_context,
    clear_all_context
)
from unifyops_core.logging.logger_utils import is_rate_limited

logger = get_logger(__name__, metadata={"component": "logging_middleware"})

# OpenTelemetry trace context headers
TRACE_PARENT_HEADER = "traceparent"
TRACE_STATE_HEADER = "tracestate"
BAGGAGE_HEADER = "baggage"

# Pattern for W3C trace context
TRACE_PARENT_PATTERN = re.compile(
    r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$"
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for comprehensive request/response logging with Signoz optimization.
    
    Features:
    - Automatic correlation ID generation and propagation
    - OpenTelemetry trace context extraction and propagation
    - Request/response timing and metadata collection
    - Configurable path exclusions for health checks
    - Rate limiting for high-frequency endpoints
    - Structured logging optimized for Signoz
    - Automatic context cleanup after requests
    """
    
    def __init__(
        self, 
        app: FastAPI,
        exclude_paths: Optional[Set[str]] = None,
        rate_limit_paths: Optional[Dict[str, tuple[int, float]]] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
        mask_sensitive_headers: bool = True
    ):
        """
        Initialize the logging middleware.
        
        Args:
            app: FastAPI application instance
            exclude_paths: Set of paths to exclude from logging
            rate_limit_paths: Dict of path patterns to (max_count, time_window) tuples
            log_request_body: Whether to log request bodies (be careful with PII)
            log_response_body: Whether to log response bodies (be careful with PII)
            mask_sensitive_headers: Whether to mask sensitive headers in logs
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or {"/health", "/metrics", "/docs", "/redoc", "/openapi.json"}
        self.rate_limit_paths = rate_limit_paths or {}
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.mask_sensitive_headers = mask_sensitive_headers
        self.sensitive_headers = {"authorization", "cookie", "x-api-key", "x-auth-token"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Check rate limiting
        for path_pattern, (max_count, time_window) in self.rate_limit_paths.items():
            if re.match(path_pattern, request.url.path):
                if is_rate_limited(f"path:{request.url.path}", max_count, time_window):
                    return await call_next(request)
        
        # Clear any previous context
        clear_all_context()
        
        # Extract or generate correlation ID
        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
        set_correlation_id(correlation_id)
        
        # Extract OpenTelemetry trace context from headers
        trace_parent = request.headers.get(TRACE_PARENT_HEADER)
        if trace_parent:
            trace_context = self._parse_trace_parent(trace_parent)
            if trace_context:
                set_trace_context(
                    trace_id=trace_context["trace_id"],
                    span_id=trace_context["span_id"],
                    trace_flags=trace_context["trace_flags"]
                )
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Extract user information if available
        user_id = request.headers.get("x-user-id")
        tenant_id = request.headers.get("x-tenant-id")
        
        # Set request context
        set_request_context(request_id, user_id, tenant_id)
        
        # Collect request metadata
        request_metadata = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "client_port": request.client.port if request.client else None,
            "scheme": request.url.scheme,
            "headers": self._get_safe_headers(request),
        }
        
        # Add metadata to logging context
        add_logging_metadata(**request_metadata)
        
        # Log request start with structured data
        logger.structured(
            "info",
            "http_request_started",
            correlation_id=correlation_id,
            request_id=request_id,
            **request_metadata
        )
        
        # Track timing
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate request duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful response
            response_metadata = {
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "response_headers": dict(response.headers),
            }
            
            # Determine log level based on status code
            if response.status_code >= 500:
                log_level = "error"
            elif response.status_code >= 400:
                log_level = "warn"
            else:
                log_level = "info"
            
            # Log response with structured data
            logger.structured(
                log_level,
                "http_request_completed",
                correlation_id=correlation_id,
                request_id=request_id,
                **{**request_metadata, **response_metadata}
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Calculate request duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log exception with full context
            logger.error_with_exception(
                "Request processing failed",
                exc,
                correlation_id=correlation_id,
                request_id=request_id,
                duration_ms=round(duration_ms, 2),
                **request_metadata
            )
            
            # Re-raise the exception
            raise
        
        finally:
            # Clean up context after request
            clear_all_context()
    
    def _parse_trace_parent(self, trace_parent: str) -> Optional[Dict[str, Any]]:
        """
        Parse W3C trace parent header.
        
        Format: version-trace_id-span_id-trace_flags
        Example: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
        
        Args:
            trace_parent: The traceparent header value
            
        Returns:
            Dictionary with trace context or None if invalid
        """
        match = TRACE_PARENT_PATTERN.match(trace_parent.strip())
        if not match:
            logger.debug(f"Invalid trace parent format: {trace_parent}")
            return None
        
        version, trace_id, span_id, trace_flags = match.groups()
        
        # Validate version (currently only 00 is supported)
        if version != "00":
            logger.debug(f"Unsupported trace parent version: {version}")
            return None
        
        return {
            "trace_id": trace_id,
            "span_id": span_id,
            "trace_flags": int(trace_flags, 16)
        }
    
    def _get_safe_headers(self, request: Request) -> Dict[str, str]:
        """
        Get request headers with sensitive values masked.
        
        Args:
            request: The incoming request
            
        Returns:
            Dictionary of headers with sensitive values masked
        """
        headers = dict(request.headers)
        
        if self.mask_sensitive_headers:
            for header in self.sensitive_headers:
                if header in headers:
                    headers[header] = "***MASKED***"
        
        return headers


def setup_logging_middleware(
    app: FastAPI,
    exclude_paths: Optional[Set[str]] = None,
    rate_limit_paths: Optional[Dict[str, tuple[int, float]]] = None,
    **kwargs
) -> None:
    """
    Convenience function to set up logging middleware on a FastAPI app.
    
    Args:
        app: FastAPI application instance
        exclude_paths: Set of paths to exclude from logging
        rate_limit_paths: Dict of path patterns to (max_count, time_window) tuples
        **kwargs: Additional arguments passed to LoggingMiddleware
        
    Example:
        ```python
        from fastapi import FastAPI
        from unifyops_core.logging.middleware import setup_logging_middleware
        
        app = FastAPI()
        
        # Basic setup
        setup_logging_middleware(app)
        
        # Advanced setup with rate limiting
        setup_logging_middleware(
            app,
            exclude_paths={"/health", "/metrics", "/internal/*"},
            rate_limit_paths={
                r"^/api/v1/search.*": (100, 60.0),  # 100 requests per minute
                r"^/api/v1/analytics.*": (10, 60.0), # 10 requests per minute
            },
            log_request_body=True,
            mask_sensitive_headers=True
        )
        ```
    """
    app.add_middleware(
        LoggingMiddleware,
        exclude_paths=exclude_paths,
        rate_limit_paths=rate_limit_paths,
        **kwargs
    )
    
    logger.info(
        "Logging middleware configured",
        metadata={
            "exclude_paths": list(exclude_paths) if exclude_paths else [],
            "rate_limit_paths": list(rate_limit_paths.keys()) if rate_limit_paths else [],
            "signoz_optimized": True
        }
    ) 