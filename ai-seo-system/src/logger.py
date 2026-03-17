"""
Logging configuration for the SEO Content System.
Provides structured logging with file rotation and color output.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from colorlog import ColoredFormatter

from config import LoggingConfig

class SEOFormatter(logging.Formatter):
    """Custom formatter for SEO system logs"""
    
    def format(self, record):
        # Add context fields if they exist
        if hasattr(record, 'article_id'):
            record.article_id = getattr(record, 'article_id')
        return super().format(record)

def setup_logging() -> logging.Logger:
    """
    Setup and return the root logger for the SEO system.
    
    Configures:
    - Console logging with colors
    - File logging with rotation
    - Appropriate log levels
    """
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Load configuration
    config = LoggingConfig()
    
    # Create logger
    logger = logging.getLogger("seo_system")
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplication
    logger.handlers.clear()
    
    # Console handler with color
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Color formatter
    console_formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config.file,
        maxBytes=config.max_bytes,
        backupCount=config.backup_count
    )
    file_handler.setLevel(logging.INFO)
    
    # File formatter
    file_formatter = logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Suppress logging from some noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    return logger