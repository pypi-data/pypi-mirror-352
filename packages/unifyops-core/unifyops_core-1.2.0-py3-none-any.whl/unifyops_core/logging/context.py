import logging
from typing import Optional, Dict, Any, cast

from unifyops_core.logging.context_vars import (
    correlation_id_var, 
    metadata_var,
    trace_id_var,
    span_id_var,
    trace_flags_var,
    request_id_var,
    user_id_var,
    tenant_id_var,
    get_full_context
)

class ContextLoggerAdapter(logging.LoggerAdapter):
    """
    Enhanced logger adapter that injects contextual information into log records.
    
    This adapter enriches log entries with:
      1) module‑level metadata (from adapter construction)
      2) per‑request metadata (from ContextVar)
      3) inline metadata (supplied in individual log calls)
      4) correlation_id (from ContextVar)
      5) OpenTelemetry trace context for Signoz correlation
      6) Request-specific context (user_id, tenant_id, etc.)
    
    This allows for consistent logging across asynchronous request boundaries
    with full support for distributed tracing and Signoz integration.
    """
    def __init__(
        self,
        logger: logging.Logger,
        module_metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(logger, {})
        self.module_metadata = module_metadata or {}

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        extra = kwargs.setdefault("extra", {})

        # 1) module‑level metadata
        if self.module_metadata:
            extra.setdefault("custom_metadata", {}).update(self.module_metadata)

        # 2) per‑request metadata from context
        req_meta = metadata_var.get()
        if req_meta:
            extra.setdefault("custom_metadata", {}).update(req_meta)

        # 3) inline metadata
        inline = kwargs.pop("metadata", None)
        if inline:
            extra.setdefault("custom_metadata", {}).update(inline)

        # 4) correlation ID
        cid = correlation_id_var.get()
        if cid:
            extra["correlation_id"] = cid
        
        # 5) OpenTelemetry trace context for Signoz
        trace_id = trace_id_var.get()
        span_id = span_id_var.get()
        trace_flags = trace_flags_var.get()
        
        if trace_id:
            extra["trace_id"] = trace_id
        if span_id:
            extra["span_id"] = span_id
        if trace_flags is not None:
            extra["trace_flags"] = trace_flags
        
        # 6) Request-specific context
        request_id = request_id_var.get()
        user_id = user_id_var.get()
        tenant_id = tenant_id_var.get()
        
        if request_id:
            extra.setdefault("custom_metadata", {})["request_id"] = request_id
        if user_id:
            extra.setdefault("custom_metadata", {})["user_id"] = user_id
        if tenant_id:
            extra.setdefault("custom_metadata", {})["tenant_id"] = tenant_id

        # ensure correct caller file/line
        kwargs.setdefault("stacklevel", 2)
        return msg, kwargs

    def structured(self, level: str, event: str, **kwargs):
        """
        Log a structured event with key-value pairs.
        
        This method is optimized for Signoz ingestion with proper
        event categorization and metadata structure.
        
        Args:
            level: Log level (debug, info, warn, error)
            event: Event name/type for categorization
            **kwargs: Key-value pairs to include as structured data
        """
        level_method = getattr(self, level.lower(), self.info)
        # Add event type as metadata for better Signoz queries
        enhanced_metadata = {"event.type": event, **kwargs}
        level_method(f"{event}", metadata=enhanced_metadata)
    
    def with_context(self, **context_vars) -> "ContextLoggerAdapter":
        """
        Create a new logger adapter with additional context.
        
        This is useful for adding temporary context that should only
        apply to a specific scope without affecting the global context.
        
        Args:
            **context_vars: Additional context variables to include
            
        Returns:
            A new ContextLoggerAdapter with the additional context
        """
        combined_metadata = {**self.module_metadata, **context_vars}
        return ContextLoggerAdapter(self.logger, combined_metadata)
    
    def log_with_trace(self, level: int, msg: str, trace_id: str, span_id: str, **kwargs):
        """
        Log with explicit trace context.
        
        This is useful when you have trace information from an external
        source (e.g., incoming HTTP headers) that you want to associate
        with the log entry.
        
        Args:
            level: Log level as integer
            msg: Log message
            trace_id: OpenTelemetry trace ID
            span_id: OpenTelemetry span ID
            **kwargs: Additional log arguments
        """
        kwargs.setdefault("extra", {})
        kwargs["extra"]["trace_id"] = trace_id
        kwargs["extra"]["span_id"] = span_id
        self.log(level, msg, **kwargs)
    
    def debug_context(self, msg: str, **kwargs):
        """Log debug message with full context dump."""
        full_context = get_full_context()
        kwargs.setdefault("metadata", {}).update({"context": full_context})
        self.debug(msg, **kwargs)
    
    def error_with_exception(self, msg: str, exc: Exception, **kwargs):
        """
        Log an error with exception details properly formatted for Signoz.
        
        Args:
            msg: Error message
            exc: The exception object
            **kwargs: Additional log arguments
        """
        kwargs.setdefault("metadata", {}).update({
            "error.type": type(exc).__name__,
            "error.message": str(exc),
        })
        self.error(msg, exc_info=exc, **kwargs)


def get_logger(
    name: str = __name__,
    metadata: Optional[Dict[str, Any]] = None
) -> ContextLoggerAdapter:
    """
    Get a context-aware logger with optional module-level metadata.
    
    This is the preferred way to obtain a logger throughout the application.
    The returned logger will automatically include correlation IDs, trace
    context, and metadata in all log entries for optimal Signoz integration.
    
    Args:
        name: Logger name (typically __name__)
        metadata: Module-level metadata to include in all log entries
        
    Returns:
        A context-aware logger adapter with Signoz optimizations
        
    Example:
        ```python
        # In your module
        logger = get_logger(__name__, metadata={
            "component": "auth_service",
            "version": "2.1.0"
        })
        
        # Later in request handling
        logger.info("User authenticated", metadata={
            "user_id": user.id,
            "auth_method": "oauth2"
        })
        
        # Structured logging
        logger.structured("info", "user_login", 
            user_id=user.id,
            ip_address=request.client.host
        )
        ```
    """
    base = logging.getLogger(name)
    return ContextLoggerAdapter(base, module_metadata=metadata)
