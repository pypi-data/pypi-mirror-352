"""
OpenTelemetry Integration for Signoz

This module provides complete OpenTelemetry integration for proper log correlation
and service attribution in Signoz. It configures:
- OpenTelemetry SDK with proper resource attributes
- Logs exporter for Signoz ingestion
- Resource processors for Kubernetes integration
- Proper service correlation

Usage:
    from unifyops_core.logging.otel_integration import setup_otel_logging
    setup_otel_logging()
"""

import os
import logging
import platform
import uuid
from typing import Optional, Dict, Any

try:
    # OpenTelemetry imports
    from opentelemetry import configure_logger_provider
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.semconv.resource import ResourceAttributes
    
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    print("Warning: OpenTelemetry packages not available. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp")

def generate_service_instance_id() -> str:
    """
    Generate a unique service instance ID following OpenTelemetry recommendations.
    
    Returns:
        A UUID string that uniquely identifies this service instance
    """
    # Check if already set in environment (e.g., by Kubernetes)
    instance_id = os.getenv("SERVICE_INSTANCE_ID")
    if instance_id:
        return instance_id
    
    # For containerized environments, try to use pod UID
    pod_uid = os.getenv("K8S_POD_UID")
    if pod_uid:
        # Use pod UID as basis for UUID v5 (deterministic)
        namespace_uuid = uuid.UUID("4d63009a-8d0f-11ee-aad7-4c796ed8e320")  # OTel recommended namespace
        return str(uuid.uuid5(namespace_uuid, pod_uid))
    
    # Fallback to random UUID v4
    return str(uuid.uuid4())

def create_otel_resource() -> Optional[Resource]:
    """
    Create OpenTelemetry Resource with all required and recommended attributes.
    
    Returns:
        Configured Resource object or None if OTel not available
    """
    if not OTEL_AVAILABLE:
        return None
    
    # Get service information
    service_name = os.getenv("SERVICE_NAME", "unifyops-api")
    service_version = os.getenv("SERVICE_VERSION", "1.0.0")
    service_namespace = os.getenv("SERVICE_NAMESPACE", "unifyops")
    service_instance_id = generate_service_instance_id()
    deployment_environment = os.getenv("DEPLOYMENT_ENVIRONMENT", os.getenv("ENVIRONMENT", "development"))
    
    # Build resource attributes following OpenTelemetry semantic conventions
    resource_attributes = {
        # Required service attributes (OTel stable)
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: service_version,
        ResourceAttributes.SERVICE_INSTANCE_ID: service_instance_id,
        
        # Service namespace (OTel development)
        ResourceAttributes.SERVICE_NAMESPACE: service_namespace,
        
        # Deployment attributes
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: deployment_environment,
        
        # Host attributes
        ResourceAttributes.HOST_NAME: os.getenv("HOSTNAME", platform.node()),
        ResourceAttributes.HOST_TYPE: os.getenv("HOST_TYPE", "container" if os.getenv("KUBERNETES_SERVICE_HOST") else "physical"),
        ResourceAttributes.HOST_ARCH: platform.machine(),
        
        # OS attributes
        ResourceAttributes.OS_TYPE: platform.system().lower(),
        ResourceAttributes.OS_NAME: platform.system(),
        ResourceAttributes.OS_VERSION: platform.release(),
        
        # Process attributes
        ResourceAttributes.PROCESS_PID: os.getpid(),
        ResourceAttributes.PROCESS_EXECUTABLE_NAME: "python",
        ResourceAttributes.PROCESS_RUNTIME_NAME: "python",
        ResourceAttributes.PROCESS_RUNTIME_VERSION: platform.python_version(),
        
        # Telemetry SDK attributes
        ResourceAttributes.TELEMETRY_SDK_LANGUAGE: "python",
        ResourceAttributes.TELEMETRY_SDK_NAME: "opentelemetry",
        ResourceAttributes.TELEMETRY_SDK_VERSION: "1.27.0",
    }
    
    # Add Kubernetes attributes if available
    if os.getenv("K8S_POD_NAME"):
        resource_attributes.update({
            ResourceAttributes.K8S_POD_NAME: os.getenv("K8S_POD_NAME"),
            ResourceAttributes.K8S_POD_UID: os.getenv("K8S_POD_UID"),
            ResourceAttributes.K8S_NAMESPACE_NAME: os.getenv("K8S_NAMESPACE_NAME"),
            ResourceAttributes.K8S_NODE_NAME: os.getenv("K8S_NODE_NAME"),
            ResourceAttributes.K8S_CLUSTER_NAME: os.getenv("K8S_CLUSTER_NAME"),
            ResourceAttributes.CONTAINER_NAME: os.getenv("CONTAINER_NAME", service_name),
            ResourceAttributes.CONTAINER_ID: os.getenv("CONTAINER_ID"),
        })
    
    # Add cloud provider attributes if available
    cloud_provider = os.getenv("CLOUD_PROVIDER")
    if cloud_provider:
        resource_attributes[ResourceAttributes.CLOUD_PROVIDER] = cloud_provider
        resource_attributes[ResourceAttributes.CLOUD_REGION] = os.getenv("CLOUD_REGION")
        resource_attributes[ResourceAttributes.CLOUD_AVAILABILITY_ZONE] = os.getenv("CLOUD_AVAILABILITY_ZONE")
    
    # Filter out None values
    clean_attributes = {k: v for k, v in resource_attributes.items() if v is not None}
    
    return Resource.create(clean_attributes)

def setup_otel_logging(
    signoz_endpoint: Optional[str] = None,
    enable_console_logs: bool = True,
    log_level: str = "INFO"
) -> bool:
    """
    Set up OpenTelemetry logging with Signoz integration.
    
    Args:
        signoz_endpoint: Signoz OTLP endpoint (auto-detected if not provided)
        enable_console_logs: Whether to also enable console logging
        log_level: Minimum log level
        
    Returns:
        True if setup successful, False otherwise
    """
    if not OTEL_AVAILABLE:
        print("OpenTelemetry not available. Using fallback JSON logging.")
        return False
    
    try:
        # Create resource with all service attributes
        resource = create_otel_resource()
        if not resource:
            print("Failed to create OpenTelemetry resource")
            return False
        
        # Determine Signoz endpoint
        if not signoz_endpoint:
            # Auto-detect common Signoz endpoints
            signoz_endpoint = (
                os.getenv("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT") or
                os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or
                os.getenv("SIGNOZ_ENDPOINT") or
                "http://localhost:4317"  # Default Signoz endpoint
            )
        
        # Configure OTLP exporter for Signoz
        otlp_exporter = OTLPLogExporter(
            endpoint=signoz_endpoint,
            insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true",
            headers=_get_otlp_headers()
        )
        
        # Create logger provider with resource
        logger_provider = LoggerProvider(resource=resource)
        
        # Add batch processor for efficient log export
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(
                otlp_exporter,
                max_queue_size=2048,
                export_timeout_millis=30000,
                max_export_batch_size=512
            )
        )
        
        # Set the global logger provider
        set_logger_provider(logger_provider)
        
        # Create OpenTelemetry logging handler
        otel_handler = LoggingHandler(
            level=getattr(logging, log_level.upper()),
            logger_provider=logger_provider
        )
        
        # Configure root logger to use OpenTelemetry handler
        root_logger = logging.getLogger()
        
        # Remove existing handlers if we're taking over
        if not enable_console_logs:
            root_logger.handlers.clear()
        
        # Add OpenTelemetry handler
        root_logger.addHandler(otel_handler)
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Log successful setup with service information
        setup_logger = logging.getLogger(__name__)
        setup_logger.info(
            "OpenTelemetry logging configured for Signoz",
            extra={
                "otel.setup.status": "success",
                "otel.exporter.endpoint": signoz_endpoint,
                "service.name": resource.attributes.get(ResourceAttributes.SERVICE_NAME),
                "service.version": resource.attributes.get(ResourceAttributes.SERVICE_VERSION),
                "service.instance.id": resource.attributes.get(ResourceAttributes.SERVICE_INSTANCE_ID),
                "service.namespace": resource.attributes.get(ResourceAttributes.SERVICE_NAMESPACE)
            }
        )
        
        return True
        
    except Exception as e:
        print(f"Failed to setup OpenTelemetry logging: {e}")
        return False

def _get_otlp_headers() -> Dict[str, str]:
    """
    Get OTLP headers for authentication and configuration.
    
    Returns:
        Dictionary of headers for OTLP exporter
    """
    headers = {}
    
    # Add authentication headers if available
    auth_header = os.getenv("OTEL_EXPORTER_OTLP_HEADERS")
    if auth_header:
        # Parse headers in format "key1=value1,key2=value2"
        for header_pair in auth_header.split(","):
            if "=" in header_pair:
                key, value = header_pair.strip().split("=", 1)
                headers[key] = value
    
    # Add Signoz-specific headers
    signoz_access_token = os.getenv("SIGNOZ_ACCESS_TOKEN")
    if signoz_access_token:
        headers["signoz-access-token"] = signoz_access_token
    
    return headers

def verify_otel_setup() -> Dict[str, Any]:
    """
    Verify OpenTelemetry setup and return status information.
    
    Returns:
        Dictionary with setup status and configuration
    """
    from opentelemetry._logs import get_logger_provider
    
    try:
        logger_provider = get_logger_provider()
        resource = getattr(logger_provider, '_resource', None)
        
        if resource:
            return {
                "status": "configured",
                "otel_available": OTEL_AVAILABLE,
                "resource_attributes": dict(resource.attributes),
                "service_name": resource.attributes.get(ResourceAttributes.SERVICE_NAME),
                "service_instance_id": resource.attributes.get(ResourceAttributes.SERVICE_INSTANCE_ID)
            }
        else:
            return {
                "status": "not_configured",
                "otel_available": OTEL_AVAILABLE,
                "error": "No resource configured"
            }
    except Exception as e:
        return {
            "status": "error",
            "otel_available": OTEL_AVAILABLE,
            "error": str(e)
        }

# Auto-setup if environment variable is set
if os.getenv("AUTO_SETUP_OTEL", "false").lower() == "true":
    setup_otel_logging() 