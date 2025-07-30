"""
Context variables for maintaining logging state across async boundaries.

This module defines context variables that persist across asynchronous
operations, ensuring consistent logging context throughout request lifecycles.
These variables are particularly important for:
- Correlation ID tracking across microservices
- OpenTelemetry trace context propagation
- Request-scoped metadata management
- Signoz integration with proper trace correlation
"""

from contextvars import ContextVar
from typing import Dict, Any, Optional

# Core context variables
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
metadata_var: ContextVar[Optional[Dict[str, Any]]] = ContextVar('metadata', default=None)

# OpenTelemetry trace context variables for Signoz correlation
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
span_id_var: ContextVar[Optional[str]] = ContextVar('span_id', default=None)
trace_flags_var: ContextVar[Optional[int]] = ContextVar('trace_flags', default=None)

# Additional context for enhanced observability
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
tenant_id_var: ContextVar[Optional[str]] = ContextVar('tenant_id', default=None)

def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context."""
    correlation_id_var.set(correlation_id)
    
def get_correlation_id() -> Optional[str]:
    """Get the correlation ID from the current context."""
    return correlation_id_var.get()

def add_logging_metadata(**kwargs) -> None:
    """Add metadata to the current logging context."""
    current = metadata_var.get() or {}
    current.update(kwargs)
    metadata_var.set(current)
    
def get_logging_metadata() -> Dict[str, Any]:
    """Get all metadata from the current logging context."""
    return metadata_var.get() or {}

def set_trace_context(trace_id: str, span_id: str, trace_flags: int = 1) -> None:
    """
    Set OpenTelemetry trace context for log correlation.
    
    Args:
        trace_id: The trace ID in hex format
        span_id: The span ID in hex format
        trace_flags: OpenTelemetry trace flags (default: 1 for sampled)
    """
    trace_id_var.set(trace_id)
    span_id_var.set(span_id)
    trace_flags_var.set(trace_flags)

def clear_trace_context() -> None:
    """Clear the OpenTelemetry trace context."""
    trace_id_var.set(None)
    span_id_var.set(None)
    trace_flags_var.set(None)

def set_request_context(request_id: str, user_id: Optional[str] = None, tenant_id: Optional[str] = None) -> None:
    """
    Set request-specific context for enhanced observability.
    
    Args:
        request_id: Unique identifier for the request
        user_id: Optional user identifier
        tenant_id: Optional tenant identifier for multi-tenant systems
    """
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if tenant_id:
        tenant_id_var.set(tenant_id)

def get_full_context() -> Dict[str, Any]:
    """
    Get all context variables as a dictionary.
    
    Returns:
        Dictionary containing all context variables with their current values
    """
    context = {
        "correlation_id": correlation_id_var.get(),
        "trace_id": trace_id_var.get(),
        "span_id": span_id_var.get(),
        "trace_flags": trace_flags_var.get(),
        "request_id": request_id_var.get(),
        "user_id": user_id_var.get(),
        "tenant_id": tenant_id_var.get(),
    }
    
    # Remove None values
    return {k: v for k, v in context.items() if v is not None}

def clear_all_context() -> None:
    """Clear all context variables. Useful for cleanup between requests."""
    correlation_id_var.set(None)
    metadata_var.set(None)
    trace_id_var.set(None)
    span_id_var.set(None)
    trace_flags_var.set(None)
    request_id_var.set(None)
    user_id_var.set(None)
    tenant_id_var.set(None) 