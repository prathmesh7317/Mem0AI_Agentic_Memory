"""
Logging Configuration for Mem0 Chatbot
Centralizes ALL logs into ONE file: logs/app.log
"""

import logging
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Single log file for entire application
LOG_FILE = LOGS_DIR / "app.log"

# Global flag to ensure handlers are added only once
_handlers_configured = False


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Setup and return a logger that writes to ONE shared log file
    
    Args:
        name: Logger name (usually __name__ from the calling module)
    
    Returns:
        Configured logger instance (all loggers share same handlers)
    """
    global _handlers_configured
    
    # Get logger for this module
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Configure root logger handlers only once
    if not _handlers_configured:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        root_logger.handlers.clear()
        
        # remove noisy third-party loggers
        logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
        logging.getLogger("watchfiles").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # File handler - ALL logs go to ONE file
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Console handler - only warnings/errors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        _handlers_configured = True
    
    return logger

