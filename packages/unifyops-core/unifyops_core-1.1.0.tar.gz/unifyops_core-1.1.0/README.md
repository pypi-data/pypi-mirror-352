# UnifyOps Core

Core utilities for UnifyOps Python projects. This package provides shared functionality that can be used across all UnifyOps Python applications.

## Features

- **Logging**: Standardized logging configuration with JSON support
- **Exceptions**: Common exception classes with proper HTTP status code mapping

## Installation

```bash
pip install unifyops-core
```

## Usage

### Logging

```python
from unifyops_core.logging import get_logger

# Create a standard logger
logger = get_logger("my_app")
logger.info("This is a log message")

# Create a JSON logger
json_logger = get_logger("my_app.json", json_format=True)
json_logger.info("This is a structured log", extra={"props": {"user_id": "123", "action": "login"}})

# Log with context
from unifyops_core.logging import log_with_context
log_with_context(logger, logger.INFO, "User logged in", user_id="123", action="login")
```

### Exceptions

```python
from unifyops_core.exceptions import NotFoundError, ValidationError

# Raise standard exceptions
raise NotFoundError("User not found")
raise ValidationError("Invalid email format", details={"email": "Invalid format"})

# Custom exception with details
from unifyops_core.exceptions import UnifyOpsException
raise UnifyOpsException(
    message="Payment processing failed",
    code="PAYMENT_ERROR",
    status_code=400,
    details={"payment_id": "123", "reason": "Insufficient funds"}
)
```

## License

This project is licensed under the MIT License.
