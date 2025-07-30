"""
UnifyOps Exceptions System
=========================

A comprehensive exceptions system for FastAPI applications that provides:
- Standardized error responses
- Consistent error handling patterns
- Structured error logging integration
- Detailed error tracking with unique IDs
- Domain-specific exception hierarchies
- Exception handlers for FastAPI

Usage Examples
-------------

Basic exception raising:
```python
from unifyops_core.exceptions import ResourceNotFoundError

# Raise a standard exception
raise ResourceNotFoundError(message="User not found", details=[{"loc": ["user_id"], "msg": "User with ID 123 not found"}])
```

Raising domain-specific exceptions:
```python
from unifyops_core.exceptions import DataValidationError

# Raise a validation error with details
raise DataValidationError(
    message="Invalid data format",
    details=[
        {"loc": ["data", "email"], "msg": "Invalid email format"},
        {"loc": ["data", "age"], "msg": "Must be greater than 0"}
    ]
)
```

Extending with custom exceptions:
```python
from unifyops_core.exceptions import AppException
from fastapi import status

class CustomServiceError(AppException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_type = "service_unavailable"
    
    def __init__(self, service_name, *args, **kwargs):
        message = f"Service {service_name} is unavailable"
        super().__init__(message=message, *args, **kwargs)
"""

# Import base exception classes
from unifyops_core.exceptions.base import (
    AppException,
    ErrorDetail,
    ErrorResponse,
    ClientError,
    ServerError,
)

# Import HTTP exceptions
from unifyops_core.exceptions.http import (
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    MethodNotAllowedError,
    NotAcceptableError,
    RequestTimeoutError,
    ConflictError,
    GoneError,
    PreconditionFailedError,
    PayloadTooLargeError,
    UnsupportedMediaTypeError,
    UnprocessableEntityError,
    PreconditionRequiredError,
    TooManyRequestsError,
    InternalServerError,
    NotImplementedError,
    BadGatewayError,
    ServiceUnavailableError,
    GatewayTimeoutError,
)

# Import validation exceptions
from unifyops_core.exceptions.validation import (
    DataValidationError,
    SchemaValidationError,
    ConstraintViolationError,
)

# Import domain exceptions
from unifyops_core.exceptions.domain import (
    DomainError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    ResourceStateError,
    DependencyError,
    BusinessRuleViolationError,
    TerraformResourceError,
    DomainNotFoundError,
)

# Import operational exceptions
from unifyops_core.exceptions.operational import (
    OperationalError,
    ConfigurationError,
    OperationTimeoutError,
    ServiceConnectionError,
    ThrottlingError,
    ExternalServiceError,
    TerraformError,
    AsyncTaskError,
)

# Import database exceptions
from unifyops_core.exceptions.database import (
    DatabaseError,
    QueryError,
    TransactionError,
    MigrationError,
    IntegrityError,
)

# Import security exceptions
from unifyops_core.exceptions.security import (
    AuthenticationError,
    AuthorizationError,
    PermissionDeniedError,
    TokenExpiredError,
    TokenInvalidError,
)

# Import API exceptions
from unifyops_core.exceptions.api import (
    ApiError,
    ApiClientError,
    ApiResponseError,
    ApiAuthenticationError,
    ApiNotFoundError,
    ApiConflictError,
    ApiRateLimitError,
    ApiTimeoutError,
    ApiServiceUnavailableError,
)

# Import handlers for FastAPI integration
from unifyops_core.exceptions.handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    register_exception_handlers,
)

# Import utility functions
from unifyops_core.exceptions.utils import (
    format_exception,
    error_context,
    error_boundary,
    capture_exception,
)

# Re-export these for convenient access
__all__ = [
    # Base exceptions
    "AppException",
    "ErrorDetail",
    "ErrorResponse",
    "ClientError",
    "ServerError",
    
    # HTTP exceptions
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "MethodNotAllowedError",
    "NotAcceptableError",
    "RequestTimeoutError",
    "ConflictError",
    "GoneError",
    "PreconditionFailedError",
    "PayloadTooLargeError",
    "UnsupportedMediaTypeError",
    "UnprocessableEntityError",
    "PreconditionRequiredError",
    "TooManyRequestsError", 
    "InternalServerError",
    "NotImplementedError",
    "BadGatewayError",
    "ServiceUnavailableError",
    "GatewayTimeoutError",
    
    # Validation exceptions
    "DataValidationError",
    "SchemaValidationError",
    "ConstraintViolationError",
    
    # Domain exceptions
    "DomainError",
    "ResourceAlreadyExistsError", 
    "ResourceNotFoundError",
    "ResourceStateError",
    "DependencyError",
    "BusinessRuleViolationError",
    "TerraformResourceError",
    "DomainNotFoundError",
    
    # Operational exceptions
    "OperationalError",
    "ConfigurationError",
    "OperationTimeoutError",
    "ServiceConnectionError",
    "ThrottlingError",
    "ExternalServiceError",
    "TerraformError",
    "AsyncTaskError",
    
    # Database exceptions
    "DatabaseError",
    "QueryError",
    "TransactionError", 
    "MigrationError",
    "IntegrityError",
    
    # Security exceptions
    "AuthenticationError",
    "AuthorizationError", 
    "PermissionDeniedError",
    "TokenExpiredError",
    "TokenInvalidError",
    
    # API exceptions
    "ApiError",
    "ApiClientError",
    "ApiResponseError",
    "ApiAuthenticationError",
    "ApiNotFoundError",
    "ApiConflictError",
    "ApiRateLimitError",
    "ApiTimeoutError",
    "ApiServiceUnavailableError",
    
    # Exception handlers
    "app_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
    "register_exception_handlers",
    
    # Utilities
    "format_exception",
    "error_context",
    "error_boundary",
    "capture_exception",
] 