#!/usr/bin/env python3
"""
AI SEO System – Dry‑Run Test
Test the pipeline with mock data without API calls.
"""

import sys
import os
from pathlib import Path

# Configure paths
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / 'src'))

def main():
    print("\n\n🔧 AI SEO System – Dry‑Run Test")
    print("=" * 50)
    
    try:
        from main import run_pipeline
        from config import Config
        from status_reporter import StatusReporter
        from datetime import datetime
        
        config = Config.load()
        print(f"✅ Configuration loaded")
        
        print(f"🔄 Running pipeline with mock data...")
        run_pipeline(config, dry_run=True)
        
        print(f"✅ Dry‑run completed successfully")
        
        # Show a quick status report
        reporter = StatusReporter(config)
        print("\n📊 Status Report:\n")
        print(reporter.generate_report())
        
        return 0
        
    except Exception as e:
        import traceback
        print("❌ Dry‑run failed")
        traceback.print_exc()
        
        # Record failure
        try:
            from status_reporter import StatusReporter
            reporter = StatusReporter(config)
            reporter.record_failure(str(e), datetime.utcnow())
        except:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())