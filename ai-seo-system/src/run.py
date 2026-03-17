#!/usr/bin/env python3
"""
AI SEO System - Main Entry Point
Runs the automation pipeline on a scheduled basis.
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from logger import setup_logging
from main import run_pipeline
from scheduler import Scheduler

def main():
    parser = argparse.ArgumentParser(description="AI SEO System")
    parser.add_argument("--dry-run", action="store_true", help="Run one pipeline cycle with mock data")
    parser.add_argument("--once", action="store_true", help="Run one pipeline cycle and exit")
    args = parser.parse_args()

    # Setup logging
    setup_logging()
    
    # Load configuration
    config = Config.load()
    
    if args.dry_run:
        print("Running dry-run test with mock content...")
        run_pipeline(config, dry_run=True)
        print("Dry-run completed successfully!")
        return
    
    if args.once:
        print("Running single pipeline cycle...")
        run_pipeline(config, dry_run=False)
        print("Pipeline cycle completed.")
        return

    # Start scheduler for continuous operation
    scheduler = Scheduler(config)
    scheduler.run_forever()

if __name__ == "__main__":
    main()