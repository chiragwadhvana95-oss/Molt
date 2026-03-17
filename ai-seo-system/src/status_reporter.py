"""
Status Reporter for AI SEO System
Tracks system health, article generation, and deployment status.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json

from config import Config

logger = logging.getLogger("seo_system.status_reporter")

@dataclass
class StatusEntry:
    """Represents a single status entry"""
    timestamp: str
    keyword: str
    filename: str
    success: bool
    error: Optional[str] = None
    word_count: int = 0
    sitemap_updated: bool = False
    git_pushed: bool = False

class StatusReporter:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger("seo_system.status_reporter")
        self.status_file = Path(config.status.status_file)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing status data
        self.entries: List[StatusEntry] = self._load_status()
        
        # Statistics cache
        self.cache_valid = False
        self.cache = {}
    
    def record_success(self, keyword: str, filename: str, start_time: datetime, 
                       word_count: int = 0, sitemap_updated: bool = True, git_pushed: bool = True) -> None:
        """Record a successful pipeline execution."""
        entry = StatusEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            keyword=keyword,
            filename=filename,
            success=True,
            word_count=word_count,
            sitemap_updated=sitemap_updated,
            git_pushed=git_pushed
        )
        self._add_entry(entry)
        self._persist()
        self.cache_valid = False
        self.logger.info(f"Recorded success: {keyword} -> {filename}")
    
    def record_failure(self, error: str, start_time: datetime) -> None:
        """Record a failed pipeline execution."""
        entry = StatusEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            keyword="",
            filename="",
            success=False,
            error=error
        )
        self._add_entry(entry)
        self._persist()
        self.cache_valid = False
        self.logger.error(f"Recorded failure: {error}")
    
    def get_today_stats(self) -> Dict[str, Any]:
        """Get statistics for today."""
        if not self.cache_valid:
            self._recalculate_stats()
        return self.cache.get('today', {})
    
    def get_recent_entries(self, hours: int = 24) -> List[StatusEntry]:
        """Get entries from the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat() + "Z"
        return [e for e in self.entries if e.timestamp >= cutoff_str]
    
    def get_success_rate(self, hours: int = 24) -> float:
        """Calculate success rate over last N hours."""
        entries = self.get_recent_entries(hours)
        if not entries:
            return 0.0
        successes = sum(1 for e in entries if e.success)
        return successes / len(entries)
    
    def _add_entry(self, entry: StatusEntry) -> None:
        """Add entry to in-memory list (with size limit)."""
        self.entries.append(entry)
        # Keep only last 1000 entries
        if len(self.entries) > 1000:
            self.entries = self.entries[-1000:]
    
    def _load_status(self) -> List[StatusEntry]:
        """Load status entries from file."""
        entries = []
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = StatusEntry(**json.loads(line))
                            entries.append(entry)
                        except Exception as e:
                            self.logger.warning(f"Failed to parse status line: {e}")
                self.logger.info(f"Loaded {len(entries)} status entries")
        except Exception as e:
            self.logger.error(f"Failed to load status file: {e}")
        return entries
    
    def _persist(self) -> None:
        """Persist status entries to file."""
        try:
            with open(self.status_file, 'w') as f:
                for entry in self.entries:
                    json.dump({
                        'timestamp': entry.timestamp,
                        'keyword': entry.keyword,
                        'filename': entry.filename,
                        'success': entry.success,
                        'error': entry.error,
                        'word_count': entry.word_count,
                        'sitemap_updated': entry.sitemap_updated,
                        'git_pushed': entry.git_pushed
                    }, f)
                    f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to persist status: {e}")
    
    def _recalculate_stats(self) -> None:
        """Recalculate and cache statistics."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        stats = {
            'today': {
                'articles_generated': 0,
                'keywords_used': set(),
                'total_words': 0,
                'successful_deployments': 0,
                'failed_deployments': 0,
                'avg_word_count': 0.0
            },
            'last_24h': {
                'articles_generated': 0,
                'success_rate': 0.0,
                'errors': []
            }
        }
        
        # Calculate today's stats
        today_entries = [e for e in self.entries 
                        if datetime.fromisoformat(e.timestamp.replace('Z', '+00:00')) >= today_start]
        
        for entry in today_entries:
            if entry.success:
                stats['today']['articles_generated'] += 1
                stats['today']['keywords_used'].add(entry.keyword)
                stats['today']['total_words'] += entry.word_count
                stats['today']['successful_deployments'] += 1
            else:
                stats['today']['failed_deployments'] += 1
                if entry.error:
                    stats['today']['errors'].append(entry.error)
        
        if stats['today']['articles_generated'] > 0:
            stats['today']['avg_word_count'] = stats['today']['total_words'] / stats['today']['articles_generated']
        
        stats['today']['keywords_used'] = list(stats['today']['keywords_used'])
        
        # Calculate last 24h stats
        stats['last_24h']['articles_generated'] = len(today_entries)
        stats['last_24h']['success_rate'] = self.get_success_rate(24)
        stats['last_24h']['errors'] = [e.error for e in today_entries if not e.success and e.error]
        
        self.cache = stats
        self.cache_valid = True
    
    def generate_report(self) -> str:
        """Generate a human-readable status report for status.md."""
        stats = self.get_today_stats()
        
        report = f"""# AI SEO System Status

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

## Today's Summary

- **Articles Generated:** {stats['today']['articles_generated']}
- **Successful Deployments:** {stats['today']['successful_deployments']}
- **Failed Deployments:** {stats['today']['failed_deployments']}
- **Average Word Count:** {int(stats['today']['avg_word_count'])}
- **Keywords Used:** {', '.join(stats['today']['keywords_used']) if stats['today']['keywords_used'] else 'None'}

## Last 24 Hours

- **Total Runs:** {stats['last_24h']['articles_generated']}
- **Success Rate:** {stats['last_24h']['success_rate']:.1%}

## Recent Activity

"""
        
        # Add recent entries
        recent = self.get_recent_entries(hours=24)[:10]
        if recent:
            report += "| Time | Keyword | Status | File |\n"
            report += "|------|---------|--------|------|\n"
            for entry in reversed(recent):  # newest first
                status = "✅ Success" if entry.success else f"❌ Failed: {entry.error}"
                file = entry.filename if entry.success else "-"
                time_str = entry.timestamp.replace('Z', '').replace('T', ' ')
                report += f"| {time_str} | {entry.keyword} | {status} | {file} |\n"
        else:
            report += "*No activity in the last 24 hours*\n"
        
        # Add errors section if there are recent failures
        errors = [e for e in recent if not e.success and e.error]
        if errors:
            report += "\n## Recent Errors\n"
            for i, error in enumerate(errors[:5], 1):
                report += f"{i}. {error}\n"
        
        return report