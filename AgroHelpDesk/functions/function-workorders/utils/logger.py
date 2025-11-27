"""Logging configuration for Azure Functions.

This module provides structured logging following Azure Functions best practices,
with integration to Application Insights when available.
"""

import logging
import os
import sys
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        level: Optional log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use default
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # Console handler for Azure Functions
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level, logging.INFO))
        
        # Detailed format for troubleshooting
        enable_detailed = os.getenv("ENABLE_DETAILED_LOGGING", "false").lower() == "true"
        
        if enable_detailed:
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def log_function_start(logger: logging.Logger, function_name: str, **kwargs):
    """Log function execution start.
    
    Args:
        logger: Logger instance
        function_name: Name of the function
        **kwargs: Additional context to log
    """
    context_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"Function '{function_name}' started. Context: {context_str}")


def log_function_end(logger: logging.Logger, function_name: str, duration_ms: float):
    """Log function execution completion.
    
    Args:
        logger: Logger instance
        function_name: Name of the function
        duration_ms: Execution duration in milliseconds
    """
    logger.info(f"Function '{function_name}' completed in {duration_ms:.2f}ms")


def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None):
    """Log error with context.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Optional context description
    """
    context_msg = f" [{context}]" if context else ""
    logger.error(f"Error{context_msg}: {type(error).__name__} - {str(error)}", exc_info=True)
