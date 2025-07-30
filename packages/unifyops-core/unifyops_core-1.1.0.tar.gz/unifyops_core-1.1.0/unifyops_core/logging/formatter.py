import logging
import sys
import os
import inspect
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any, Union

from unifyops_core.logging.logger_utils import format_log_as_json, format_log_for_signoz

APP_ROOT = os.getenv("APP_ROOT", os.getcwd())

# ANSI color codes
_LEVEL_COLORS = {
    "DEBUG":    "\033[94m",
    "INFO":     "\033[92m",
    "WARNING":  "\033[93m",
    "ERROR":    "\033[91m",
    "CRITICAL": "\033[91m\033[1m",
}
_RESET = "\033[0m"
_DIM   = "\033[2m"

# OpenTelemetry severity mappings for Signoz
OTEL_SEVERITY_NUMBER = {
    "DEBUG": 5,
    "INFO": 9,
    "WARNING": 13,
    "ERROR": 17,
    "CRITICAL": 21,
}


def _find_app_frame() -> Tuple[Optional[str], Optional[int]]:
    """
    Walk the stack and return (filename, lineno) for first .py under APP_ROOT.
    
    This helps identify the actual application code that triggered the log
    even when the log was generated through library code.
    
    Returns:
        Tuple of (filename, line_number) or (None, None) if no app frame found
    """
    for frame in inspect.stack():
        fn = frame.filename or ""
        if fn.startswith(APP_ROOT) and fn.endswith(".py"):
            return fn, frame.lineno
    return None, None


class LevelColorFormatter(logging.Formatter):
    """
    Console formatter that enhances log output with colors and metadata.
    
    Features:
    - Rewrites non-app paths to point to calling app code
    - Shortens paths to basename for readability
    - Colorizes log levels for better visual distinction
    - Adds metadata as bracketed key-value pairs
    
    This formatter is primarily for local development to improve log readability.
    """
    def __init__(
        self, 
        fmt: Optional[str] = None, 
        datefmt: Optional[str] = None, 
        style: str = '%',
        validate: bool = True
    ):
        super().__init__(fmt, datefmt, style, validate)
        self.use_colors = sys.stdout.isatty() and os.getenv("NO_COLOR") is None
        if fmt and "%(levelname)" in fmt and self.use_colors:
            # swap to colored level slot
            self._style._fmt = fmt.replace("%(levelname)s", "%(colored_levelname)s")

    def format(self, record: logging.LogRecord) -> str:
        # rewrite pathname/lineno if outside APP_ROOT
        path = record.pathname or ""
        if not path.startswith(APP_ROOT):
            fn, ln = _find_app_frame()
            if fn:
                record.pathname = fn
                record.lineno   = ln

        # shorten to basename
        record.shortpath = os.path.basename(record.pathname or "<unknown>")

        # colorize level
        if self.use_colors:
            color = _LEVEL_COLORS.get(record.levelname, "")
            record.colored_levelname = f"{color}{record.levelname}{_RESET}"
        else:
            record.colored_levelname = record.levelname

        # build base line
        base = super().format(record)

        # append metadata
        meta = getattr(record, "custom_metadata", None)
        if meta:
            parts = [f"{k}={v}" for k, v in meta.items()]
            block = " ".join(parts)
            if self.use_colors:
                return f"{base} { _DIM }[{block}]{ _RESET }"
            else:
                return f"{base} [{block}]"

        return base

    def formatException(self, exc_info) -> str:
        text = super().formatException(exc_info)
        if self.use_colors:
            return f"{_LEVEL_COLORS['ERROR']}{text}{_RESET}"
        return text


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in production environments.
    
    Features:
    - Remaps source file/line to application code when needed
    - Adds ISO8601Z timestamp for precise time tracking
    - Creates DataDog-compatible structured JSON
    - Preserves all metadata for searchability
    
    This formatter is intended for production use to enable log aggregation,
    indexing, and querying in logging systems like DataDog.
    """
    def format(self, record: logging.LogRecord) -> str:
        # 1) rewrite pathname/lineno if outside APP_ROOT
        path = record.pathname or ""
        if not path.startswith(APP_ROOT):
            fn, ln = _find_app_frame()
            if fn:
                # DataDog JSON builder uses record.pathname & record.lineno
                record.pathname = fn
                record.lineno   = ln

        # 2) let %-formatting run (if you have a message fmt)
        message = super().format(record)

        # 3) inject precise ISO timestamp for dd processing
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc)
        record.iso_timestamp = ts.isoformat(timespec="milliseconds")

        # 4) build the final JSON
        return format_log_as_json(record, message)


class SignozJSONFormatter(JSONFormatter):
    """
    Signoz-optimized JSON formatter for structured logging.
    
    This formatter extends the base JSONFormatter with specific enhancements
    for Signoz ingestion:
    - OpenTelemetry-compliant field names and structure
    - Proper severity number mapping
    - Resource attributes for service identification
    - Optimized field organization for Signoz queries
    - Support for trace context propagation
    
    This formatter ensures logs are properly formatted for efficient
    ingestion and querying in Signoz.
    """
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = '%',
        validate: bool = True,
        service_name: Optional[str] = None,
        service_version: Optional[str] = None,
        service_namespace: Optional[str] = None,
        service_instance_id: Optional[str] = None,
        deployment_environment: Optional[str] = None
    ):
        super().__init__(fmt, datefmt, style, validate)
        self.service_name = service_name or os.getenv("SERVICE_NAME", "unifyops-api")
        self.service_version = service_version or os.getenv("SERVICE_VERSION", "1.0.0")
        self.service_namespace = service_namespace or os.getenv("SERVICE_NAMESPACE", "unifyops")
        self.service_instance_id = service_instance_id or os.getenv("SERVICE_INSTANCE_ID", "unknown")
        self.deployment_environment = deployment_environment or os.getenv("DEPLOYMENT_ENVIRONMENT", "production")
    
    def format(self, record: logging.LogRecord) -> str:
        # 1) rewrite pathname/lineno if outside APP_ROOT
        path = record.pathname or ""
        if not path.startswith(APP_ROOT):
            fn, ln = _find_app_frame()
            if fn:
                record.pathname = fn
                record.lineno = ln
        
        # 2) let %-formatting run (if you have a message fmt)
        message = super(JSONFormatter, self).format(record)
        
        # 3) inject precise ISO timestamp for Signoz
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc)
        record.iso_timestamp = ts.isoformat(timespec="microseconds")
        
        # 4) Add OpenTelemetry severity number
        record.severity_number = OTEL_SEVERITY_NUMBER.get(record.levelname, 0)
        
        # 5) Add service context with full OTel compliance
        record.service_name = self.service_name
        record.service_version = self.service_version
        record.service_namespace = self.service_namespace
        record.service_instance_id = self.service_instance_id
        record.deployment_environment = self.deployment_environment
        
        # 6) build the final JSON optimized for Signoz
        return format_log_for_signoz(record, message)
