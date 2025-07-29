import os
import logging
from typing import Optional

class Logger:
    """
    A logger class that configures logging with a log level from the LOG_LEVEL environment variable.
    Default log level is INFO if not specified in the environment.
    """
    _instance = None
    _initialized = False

    def __new__(cls, name: str = None):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, name: str = None):
        if not self._initialized:
            self.name = name or __name__
            self.logger = logging.getLogger(self.name)
            self._setup_logger()
            self._initialized = True

    def _setup_logger(self):
        """Configure the logger with the log level from environment variable."""
        # Default log level if not specified in environment
        default_level = logging.INFO
        
        # Get log level from environment variable
        log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, default_level)
        
        # Configure the logger
        self.logger.setLevel(log_level)
        
        # Create console handler and set level
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        
        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        ch.setFormatter(formatter)
        
        # Remove any existing handlers to avoid duplicate logs
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
            
        # Add the handler to the logger
        self.logger.addHandler(ch)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger

# Create a default logger instance
def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: The name of the logger. If None, uses the module's name.
        
    Returns:
        A configured logging.Logger instance.
    """
    return Logger(name).get_logger()
