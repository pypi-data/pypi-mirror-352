# unifyops_core/logging/logger_config.py

import logging.config
from typing import Dict, Any
import logging
import os
import uuid
import platform

from app.config import settings
from unifyops_core.logging.formatter import LevelColorFormatter, SignozJSONFormatter

"""
Centralized logging configuration for the UnifyOps application with Signoz optimization.

This module configures the Python logging system with enhanced support for Signoz ingestion:
- OpenTelemetry-compliant structured logging
- Signoz-optimized JSON formatting
- Enhanced trace context propagation
- Proper resource attributes for service identification

Environment variables that control behavior:
- ENVIRONMENT: The deployment environment (local, test, staging, prod)
- LOG_LEVEL: The minimum log level to record (DEBUG, INFO, WARNING, etc.)
- LOG_STYLE: Force a specific logging style (auto, console, json)
- SERVICE_NAME: The name of the service for Signoz identification
- SERVICE_VERSION: The version of the service
- DEPLOYMENT_ENVIRONMENT: The deployment environment for Signoz
- SERVICE_INSTANCE_ID: Unique identifier for this service instance (auto-generated if not set)
"""

# Generate a unique service instance ID following OTel recommendations
def _generate_service_instance_id() -> str:
    """
    Generate a unique service instance ID following OpenTelemetry recommendations.
    
    Uses UUID v4 as recommended by the OTel spec. This ensures each service
    instance has a globally unique identifier.
    
    Returns:
        A UUID v4 string that uniquely identifies this service instance
    """
    # Check if already set in environment (e.g., by Kubernetes)
    instance_id = os.getenv("SERVICE_INSTANCE_ID")
    if instance_id:
        return instance_id
    
    # For containerized environments, try to use pod UID or container ID
    pod_uid = os.getenv("K8S_POD_UID")
    if pod_uid:
        # Use pod UID as basis for UUID v5 (deterministic)
        namespace_uuid = uuid.UUID("4d63009a-8d0f-11ee-aad7-4c796ed8e320")  # OTel recommended namespace
        return str(uuid.uuid5(namespace_uuid, pod_uid))
    
    # Fallback to random UUID v4
    return str(uuid.uuid4())

# Centralized settings with Signoz-specific enhancements
ENVIRONMENT: str = settings.ENVIRONMENT.lower()
IS_LOCAL: bool = ENVIRONMENT in ("local", "test")
LOG_LEVEL: str = settings.LOG_LEVEL.upper() if hasattr(settings.LOG_LEVEL, 'upper') else settings.LOG_LEVEL
LOG_STYLE: str = settings.LOG_STYLE
SERVICE_NAME = getattr(settings, 'SERVICE_NAME', 'unifyops-api')
SERVICE_VERSION = getattr(settings, 'VERSION', '1.0.0')
SERVICE_NAMESPACE = getattr(settings, 'SERVICE_NAMESPACE', 'unifyops')
DEPLOYMENT_ENVIRONMENT = getattr(settings, 'DEPLOYMENT_ENVIRONMENT', ENVIRONMENT)
SERVICE_INSTANCE_ID = _generate_service_instance_id()
LOG_RETENTION_DAYS = getattr(settings, 'LOG_RETENTION_DAYS', 30)

# OpenTelemetry resource attributes for Signoz - fully compliant with OTel spec
OTEL_RESOURCE_ATTRIBUTES = {
    # Service identification (OTel stable attributes)
    "service.name": SERVICE_NAME,
    "service.version": SERVICE_VERSION,
    "service.instance.id": SERVICE_INSTANCE_ID,
    
    # Service namespace (OTel development attribute)
    "service.namespace": SERVICE_NAMESPACE,
    
    # Deployment information (OTel semantic conventions)
    "deployment.environment.name": DEPLOYMENT_ENVIRONMENT,
    
    # Host information (OTel semantic conventions)
    "host.hostname": platform.node(),
    "host.os.type": platform.system().lower(),
    "host.arch": platform.machine(),
    
    # Telemetry SDK information
    "telemetry.sdk.language": "python",
    "telemetry.sdk.name": "opentelemetry",
    "telemetry.sdk.version": "1.27.0",  # Update as needed
    
    # Process information
    "process.pid": str(os.getpid()),
}

# Add Kubernetes-specific attributes if available
k8s_pod_name = os.getenv("K8S_POD_NAME")
k8s_pod_uid = os.getenv("K8S_POD_UID")
k8s_namespace = os.getenv("K8S_NAMESPACE_NAME")
k8s_node_name = os.getenv("K8S_NODE_NAME")

if k8s_pod_name:
    OTEL_RESOURCE_ATTRIBUTES["k8s.pod.name"] = k8s_pod_name
if k8s_pod_uid:
    OTEL_RESOURCE_ATTRIBUTES["k8s.pod.uid"] = k8s_pod_uid
if k8s_namespace:
    OTEL_RESOURCE_ATTRIBUTES["k8s.namespace.name"] = k8s_namespace
if k8s_node_name:
    OTEL_RESOURCE_ATTRIBUTES["k8s.node.name"] = k8s_node_name

# Export resource attributes as environment variable for OTel SDK
if not os.getenv("OTEL_RESOURCE_ATTRIBUTES"):
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = ",".join(
        [f"{k}={v}" for k, v in OTEL_RESOURCE_ATTRIBUTES.items()]
    )

# Decide console vs JSON
if LOG_STYLE == "auto":
    use_console = IS_LOCAL
elif LOG_STYLE == "console":
    use_console = True
else:
    use_console = False

# Base handler (app logs) with Signoz optimization
handlers: Dict[str, Dict[str, Any]] = {
    "stdout": {
        "class":     "logging.StreamHandler",
        "formatter": "console" if use_console else "signoz_json",
        "level":     LOG_LEVEL,
        "stream":    "ext://sys.stdout",
    }
}

# Null handler for suppressing unwanted logs
handlers["null"] = {
    "class": "logging.NullHandler",
}

# Configure third-party loggers to reduce noise
third_party_loggers = {
    # Uvicorn loggers
    "uvicorn":        {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "uvicorn.access": {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "uvicorn.error":  {"level": "ERROR", "handlers": ["stdout"], "propagate": False},
    
    # HTTP client libraries
    "httpx":          {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "httpcore":       {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "urllib3":        {"level": "WARNING", "handlers": ["null"], "propagate": False},
    
    # Database libraries
    "sqlalchemy":     {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "sqlalchemy.engine": {"level": "WARNING", "handlers": ["null"], "propagate": False},
    
    # Other common libraries
    "asyncio":        {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "watchfiles":     {"level": "WARNING", "handlers": ["null"], "propagate": False},
}

# Full logging configuration dictionary with Signoz enhancements
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "console": {
            "()": LevelColorFormatter,
            "format": "%(asctime)s [%(colored_levelname)s] %(message)s (%(shortpath)s:%(lineno)d)",
            "datefmt": "%H:%M:%S",
        },
        "signoz_json": {
            "()": SignozJSONFormatter,
            "format": "%(message)s",
            # Signoz-specific configuration with OTel compliance
            "service_name": SERVICE_NAME,
            "service_version": SERVICE_VERSION,
            "service_namespace": SERVICE_NAMESPACE,
            "service_instance_id": SERVICE_INSTANCE_ID,
            "deployment_environment": DEPLOYMENT_ENVIRONMENT,
        },
    },

    "handlers": handlers,

    "root": {
        "handlers": ["stdout"],
        "level":    LOG_LEVEL,
    },

    "loggers": {
        **third_party_loggers,
        # Application-specific loggers
        "unifyops": {
            "level": LOG_LEVEL,
            "handlers": ["stdout"],
            "propagate": False,
        },
    },
}

# Apply configuration
def configure_logging() -> None:
    """
    Configure the Python logging system with Signoz-optimized settings.
    
    This function applies the LOGGING_CONFIG to Python's logging system with
    enhancements for Signoz ingestion including proper resource attributes
    and full OpenTelemetry compliance.
    
    Raises:
        ValueError: If an invalid log level is specified
    """
    try:
        logging.config.dictConfig(LOGGING_CONFIG)
        
        # Log initial configuration info with OTel-compliant attributes
        logger = logging.getLogger(__name__)
        logger.info(
            "Logging configured for Signoz ingestion with OpenTelemetry compliance",
            extra={
                "service.name": SERVICE_NAME,
                "service.version": SERVICE_VERSION,
                "service.namespace": SERVICE_NAMESPACE,
                "service.instance.id": SERVICE_INSTANCE_ID,
                "deployment.environment.name": DEPLOYMENT_ENVIRONMENT,
                "log.level": LOG_LEVEL,
                "otel.compliance": "1.27.0"
            }
        )
    except ValueError as e:
        # Provide a more helpful error message for log level issues
        if "Unknown level" in str(e):
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            print(f"ERROR: Invalid log level '{settings.LOG_LEVEL}'. Valid levels are: {', '.join(valid_levels)}")
        raise

# Apply configuration when this module is imported
configure_logging()
