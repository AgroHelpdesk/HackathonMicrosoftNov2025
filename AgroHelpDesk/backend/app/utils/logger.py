import logging

def get_logger(name: str = __name__):
    """Get or create a logger with the given name.
    
    Prevents duplicate log messages by:
    - Checking if handlers already exist
    - Disabling propagation to parent loggers
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger
