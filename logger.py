import logging
import sys

def setup_logger(name: str = "ai_drops_system") -> logging.Logger:
    """
    Configure and return a structured logger.
    """
    logger = logging.getLogger(name)
    
    # If logger is already configured, return it
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(module)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    
    logger.addHandler(ch)
    return logger

# Create a default logger instance
logger = setup_logger()
