"""Response builder utilities for Azure Functions HTTP responses."""

import json
from typing import Any, Dict, Optional
from datetime import datetime


def build_success_response(
    data: Any,
    status_code: int = 200,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """Build successful HTTP response.
    
    Args:
        data: Response data
        status_code: HTTP status code (default 200)
        message: Optional success message
        
    Returns:
        HTTP response dictionary
    """
    body = {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if message:
        body["message"] = message
    
    return {
        "status_code": status_code,
        "body": json.dumps(body, default=str, ensure_ascii=False),
        "headers": {
            "Content-Type": "application/json; charset=utf-8"
        }
    }


def build_error_response(
    error_message: str,
    status_code: int = 400,
    errors: Optional[list] = None,
    error_code: Optional[str] = None
) -> Dict[str, Any]:
    """Build error HTTP response.
    
    Args:
        error_message: Main error message
        status_code: HTTP status code (default 400)
        errors: Optional list of detailed error messages
        error_code: Optional error code for client handling
        
    Returns:
        HTTP response dictionary
    """
    body = {
        "success": False,
        "error": error_message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if errors:
        body["errors"] = errors
    
    if error_code:
        body["error_code"] = error_code
    
    return {
        "status_code": status_code,
        "body": json.dumps(body, default=str, ensure_ascii=False),
        "headers": {
            "Content-Type": "application/json; charset=utf-8"
        }
    }


def build_validation_error_response(validation_errors: list) -> Dict[str, Any]:
    """Build validation error response.
    
    Args:
        validation_errors: List of validation error messages
        
    Returns:
        HTTP response dictionary
    """
    return build_error_response(
        error_message="Validation failed",
        status_code=422,
        errors=validation_errors,
        error_code="VALIDATION_ERROR"
    )


def build_not_found_response(resource: str = "Resource") -> Dict[str, Any]:
    """Build not found response.
    
    Args:
        resource: Name of the resource not found
        
    Returns:
        HTTP response dictionary
    """
    return build_error_response(
        error_message=f"{resource} not found",
        status_code=404,
        error_code="NOT_FOUND"
    )


def build_server_error_response(error: Optional[Exception] = None) -> Dict[str, Any]:
    """Build internal server error response.
    
    Args:
        error: Optional exception for logging context
        
    Returns:
        HTTP response dictionary
    """
    error_message = "Internal server error occurred"
    
    # In development, include error details
    import os
    if os.getenv("ENABLE_DETAILED_LOGGING", "false").lower() == "true" and error:
        error_message = f"{error_message}: {str(error)}"
    
    return build_error_response(
        error_message=error_message,
        status_code=500,
        error_code="INTERNAL_ERROR"
    )
