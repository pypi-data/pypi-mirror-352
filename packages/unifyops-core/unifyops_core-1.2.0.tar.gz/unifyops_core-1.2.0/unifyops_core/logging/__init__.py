"""
UnifyOps Logging System - Optimized for Signoz
==============================================

A structured logging system for FastAPI applications optimized for Signoz ingestion:
- OpenTelemetry-compliant structured logging
- Automatic trace context correlation
- Signoz-optimized JSON formatting
- Enhanced metadata management
- Distributed tracing support
- Resource attribute management
- Production-ready performance

Key Features
------------
- **Signoz Integration**: Logs are formatted following OpenTelemetry log data model
- **Trace Correlation**: Automatic correlation between logs and traces via trace_id/span_id
- **Structured Logging**: JSON output with proper field organization for efficient queries
- **Context Propagation**: Request context maintained across async boundaries
- **Performance Optimized**: Rate limiting, sampling, and efficient serialization

Usage Examples
-------------

Basic logger acquisition:
```python
from unifyops_core.logging import get_logger

# Create a module-level logger with metadata
logger = get_logger(__name__, metadata={
    "component": "user_service",
    "version": "1.2.0"
})

# Use the logger with structured data
logger.info("User action completed", metadata={
    "user_id": "123",
    "action": "login",
    "ip_address": "192.168.1.1"
})

# Structured logging for better Signoz queries
logger.structured("info", "user_login", 
    user_id="123",
    auth_method="oauth2",
    success=True
)
```

With FastAPI and trace correlation:
```python
from fastapi import FastAPI, Request
from unifyops_core.logging import get_logger, setup_logging_middleware
from unifyops_core.logging.context_vars import set_trace_context

app = FastAPI()
logger = get_logger(__name__)

# Add comprehensive logging middleware with Signoz optimization
setup_logging_middleware(
    app, 
    exclude_paths={"/health", "/metrics"},
    rate_limit_paths={
        r"^/api/v1/search.*": (100, 60.0),  # Rate limit search endpoints
    }
)

@app.get("/api/users/{user_id}")
async def get_user(user_id: str, request: Request):
    # Logs will automatically include trace context from headers
    logger.info("Fetching user", metadata={"user_id": user_id})
    # ... your logic here
```

Advanced context management:
```python
from unifyops_core.logging import get_logger, set_request_context
from unifyops_core.logging.context_vars import get_full_context

logger = get_logger(__name__)

# Set request-specific context
set_request_context(
    request_id="req-123",
    user_id="user-456",
    tenant_id="tenant-789"
)

# All subsequent logs will include this context
logger.info("Processing request")

# Get full context for debugging
context = get_full_context()
logger.debug("Current context", metadata={"context": context})
```

Monitoring and metrics:
```python
from unifyops_core.logging.logger_utils import get_logging_metrics

# Get logging system metrics
metrics = get_logging_metrics()
print(f"Log counts by level: {metrics['log_counts_by_level']}")
print(f"Serialization errors: {metrics['serialization_errors']}")
print(f"Rate limited logs: {metrics['rate_limited_logs']}")
```

Configuration
------------
Set these environment variables for Signoz integration:
- SERVICE_NAME: Your service name (e.g., "user-api")
- SERVICE_VERSION: Service version (e.g., "1.0.0")
- SERVICE_NAMESPACE: Service namespace (e.g., "production")
- DEPLOYMENT_ENVIRONMENT: Deployment environment (e.g., "prod")
- OTEL_RESOURCE_ATTRIBUTES: Additional OpenTelemetry resource attributes
"""

# Import key components for easier access
from unifyops_core.logging.context import get_logger, ContextLoggerAdapter
from unifyops_core.logging.context_vars import (
    set_correlation_id,
    get_correlation_id,
    add_logging_metadata,
    get_logging_metadata,
    set_trace_context,
    clear_trace_context,
    set_request_context,
    get_full_context,
    clear_all_context,
)
from unifyops_core.logging.logger_config import (
    LOG_LEVEL, 
    ENVIRONMENT, 
    IS_LOCAL, 
    SERVICE_NAME, 
    SERVICE_VERSION,
    SERVICE_NAMESPACE,
    DEPLOYMENT_ENVIRONMENT,
)
from unifyops_core.logging.logger_utils import get_logging_metrics, is_rate_limited
from unifyops_core.logging.middleware import setup_logging_middleware, LoggingMiddleware

# Re-export these for convenient access
__all__ = [
    # Core logging components
    "get_logger",
    "ContextLoggerAdapter",
    
    # Context management
    "set_correlation_id",
    "get_correlation_id", 
    "add_logging_metadata",
    "get_logging_metadata",
    "set_trace_context",
    "clear_trace_context",
    "set_request_context",
    "get_full_context",
    "clear_all_context",
    
    # Configuration
    "LOG_LEVEL",
    "ENVIRONMENT",
    "IS_LOCAL",
    "SERVICE_NAME",
    "SERVICE_VERSION",
    "SERVICE_NAMESPACE",
    "DEPLOYMENT_ENVIRONMENT",
    
    # Utilities
    "get_logging_metrics",
    "is_rate_limited",
    
    # Middleware
    "setup_logging_middleware",
    "LoggingMiddleware",
]

# Package version
__version__ = "2.0.0"  # Bumped for Signoz optimization 