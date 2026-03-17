"""
Scheduler for AI SEO System
Manages automated pipeline execution on a schedule.
"""

import logging
import time
from datetime import datetime, timedelta
from threading import Event
from typing import Callable, Optional

from config import Config
from logger import setup_logging

logger = logging.getLogger("seo_system.scheduler")

class Scheduler:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger("seo_system.scheduler")
        self.stop_event = Event()
        self.logger.info("Scheduler initialized")
    
    def run_forever(self) -> None:
        """
        Run the scheduler indefinitely, executing pipeline at configured intervals.
        """
        self.logger.info("Scheduler starting")
        
        while not self.stop_event.is_set():
            try:
                self.logger.info(f"Starting pipeline cycle at {datetime.utcnow().isoformat()} UTC")
                
                # Execute pipeline
                self._execute_pipeline()
                
                # Sleep until next cycle or until stop event
                if self.stop_event.wait(self.config.ai_interval_hours * 3600):
                    break
                    
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                # Wait a short time before retrying
                time.sleep(60)
        
        self.logger.info("Scheduler stopped")
    
    def _execute_pipeline(self) -> None:
        """Execute one pipeline cycle."""
        from main import run_pipeline
        
        try:
            run_pipeline(self.config)
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            # Don't re-raise - scheduler should continue
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.stop_event.set()
        self.logger.info("Scheduler stop requested")
    
    def run_once(self) -> None:
        """
        Run one pipeline cycle and exit.
        Used for testing and manual execution.
        """
        self.logger.info("Running single pipeline cycle")
        self._execute_pipeline()
        self.logger.info("Pipeline cycle completed")