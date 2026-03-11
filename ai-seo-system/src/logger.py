"""
Logging configuration for the SEO Content System.
Provides structured logging with file rotation and color output.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from colorlog import ColoredFormatter

from .config import LoggingConfig

class SEOFormatter(logging.Formatter):
    """Custom formatter for SEO system logs"""

    def format(self, record):
        # Add context fields if they exist
        if hasattr(record, 'article_id'):
            record.article_id = getattr(record, 'article_id')
        else:
            record.article_id = '-'

        if hasattr(record, 'keyword'):
            record.keyword = getattr(record, 'keyword')
        else:
            record.keyword = '-'

        return super().format(record)

def setup_logging(config: LoggingConfig) -> logging.Logger:
    """Configure and return the root logger"""

    # Create logs directory if it doesn't exist
    log_file = Path(config.file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Get the root logger
    logger = logging.getLogger("seo_system")
    logger.setLevel(getattr(logging, config.level.upper()))

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter
    if config.console:
        console_format = "%(log_color)s%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
        console_formatter = ColoredFormatter(
            console_format,
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    else:
        console_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    file_format = "%(asctime)s [%(levelname)-8s] %(name)s [%(article_id)s/%(keyword)s]: %(message)s"
    file_formatter = SEOFormatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler
    if config.console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=config.file,
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Set level for third-party loggers to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("git").setLevel(logging.WARNING)

    logger.info(f"Logging initialized at level {config.level}")
    logger.debug(f"Log file: {config.file}")

    return logger

class ArticleLogger:
    """Context manager for article-specific logging"""

    def __init__(self, logger: logging.Logger, article_id: str, keyword: str):
        self.logger = logger
        self.article_id = article_id
        self.keyword = keyword
        self.extra = {'article_id': article_id, 'keyword': keyword}

    def info(self, msg: str, **kwargs):
        self.logger.info(msg, extra=self.extra, **kwargs)

    def debug(self, msg: str, **kwargs):
        self.logger.debug(msg, extra=self.extra, **kwargs)

    def warning(self, msg: str, **kwargs):
        self.logger.warning(msg, extra=self.extra, **kwargs)

    def error(self, msg: str, **kwargs):
        self.logger.error(msg, extra=self.extra, **kwargs)

    def critical(self, msg: str, **kwargs):
        self.logger.critical(msg, extra=self.extra, **kwargs)
