"""
Keyword Research Engine for SEO Content System.
Discovers and analyzes keywords for content generation.
"""

import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging

from ..src.config import Config

logger = logging.getLogger("seo_system.keyword_research")

@dataclass
class Keyword:
    """Represents a keyword with its metrics"""
    keyword: str
    search_volume: int = 0
    competition: float = 0.0
    cpc: float = 0.0
    difficulty: float = 0.0
    trend: List[int] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    related_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "keyword": self.keyword,
            "search_volume": self.search_volume,
            "competition": self.competition,
            "cpc": self.cpc,
            "difficulty": self.difficulty,
            "trend": self.trend,
            "categories": self.categories,
            "last_updated": self.last_updated.isoformat(),
            "related_keywords": self.related_keywords,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Keyword":
        """Create Keyword from dictionary"""
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)

class KeywordResearcher:
    """Main keyword research engine"""

    def __init__(self, config: Config):
        self.config = config
        self.data_dir = Path("data/keywords")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Use Google Custom Search API if available, otherwise use placeholder
        self.google_api_key = config.ai.api_key  # Can be repurposed for Google API
        self.search_engine_id = getattr(config, 'google_search_engine_id', None)

    def discover_keywords(self, seed_keywords: List[str], max_results: int = 50) -> List[Keyword]:
        """
        Discover related keywords from seed keywords.

        Args:
            seed_keywords: Initial keywords to expand from
            max_results: Maximum number of keywords to return

        Returns:
            List of Keyword objects with metrics
        """
        logger.info(f"Discovering keywords from {len(seed_keywords)} seed keywords")

        keywords = []

        # Add seed keywords first
        for seed in seed_keywords[:max_results]:
            keyword = self._create_keyword(seed)
            keywords.append(keyword)

            # Get related keywords if we have API access
            if len(keywords) < max_results and self.search_engine_id:
                related = self._fetch_related_keywords(seed, max_results - len(keywords))
                for r in related:
                    if r.keyword not in [k.keyword for k in keywords]:
                        keywords.append(r)

        # If we don't have enough, generate variations
        if len(keywords) < max_results:
            variations = self._generate_variations(seed_keywords)
            for var in variations:
                if len(keywords) >= max_results:
                    break
                if var not in [k.keyword for k in keywords]:
                    keywords.append(self._create_keyword(var))

        # Sort by search volume and difficulty (prefer medium difficulty)
        keywords.sort(key=lambda k: (k.search_volume, -abs(k.difficulty - 50)), reverse=True)

        logger.info(f"Discovered {len(keywords)} keywords")
        return keywords[:max_results]

    def _create_keyword(self, keyword: str) -> Keyword:
        """
        Create a Keyword object with estimated metrics.
        In production, this would query real APIs (Google Keyword Planner, etc.)
        """
        # Simulate metrics based on keyword characteristics
        words = len(keyword.split())
        volume = self._estimate_search_volume(keyword)
        difficulty = self._estimate_difficulty(keyword, words)

        return Keyword(
            keyword=keyword,
            search_volume=volume,
            competition=min(difficulty / 100, 1.0),
            cpc=volume * 0.01 * (difficulty / 100),
            difficulty=difficulty,
            trend=self._generate_trend(volume),
            categories=self._categorize_keyword(keyword),
            related_keywords=[],
        )

    def _estimate_search_volume(self, keyword: str) -> int:
        """
        Estimate search volume. In production, this would use real data.
        """
        # Simple heuristics for demo purposes
        base = 1000
        words = len(keyword.split())

        # Shorter keywords have higher volume typically
        if words == 1:
            base *= 10
        elif words == 2:
            base *= 5
        elif words == 3:
            base *= 2

        # AI-related keywords are popular
        ai_terms = ['ai', 'artificial intelligence', 'machine learning', 'gpt', 'llm']
        if any(term in keyword.lower() for term in ai_terms):
            base *= 3

        # Add some randomness
        import random
        volume = int(base * (0.5 + random.random()))

        return max(10, min(volume, 50000))

    def _estimate_difficulty(self, keyword: str, words: int) -> float:
        """
        Estimate SEO difficulty (0-100). Higher means harder to rank.
        """
        difficulty = 50.0  # Base difficulty

        # Longer-tail keywords are easier
        if words >= 3:
            difficulty -= 20
        if words >= 4:
            difficulty -= 10

        # Very short, competitive terms are harder
        if words == 1:
            difficulty += 20

        # Add some variance
        import random
        difficulty += random.uniform(-10, 10)

        return max(0, min(100, difficulty))

    def _generate_trend(self, volume: int, months: int = 12) -> List[int]:
        """Generate a simulated 12-month trend"""
        import random
        trend = []
        for i in range(months):
            # Add seasonal variation and noise
            seasonal = 1.0 + 0.2 * ((i % 12) / 12)
            noise = random.uniform(0.9, 1.1)
            trend_value = int(volume * seasonal * noise)
            trend.append(trend_value)
        return trend

    def _categorize_keyword(self, keyword: str) -> List[str]:
        """Categorize keyword based on content"""
        keyword_lower = keyword.lower()
        categories = []

        # AI/ML categories
        ai_terms = {
            'ai tools': ['tools', 'software', 'platform'],
            'ai writing': ['writing', 'content', 'copywriting', 'blog'],
            'ai automation': ['automation', 'workflow', 'auto', 'automatic'],
            'ai productivity': ['productivity', 'efficiency', 'time management'],
            'ai development': ['development', 'coding', 'programming', 'developer'],
            'ai business': ['business', 'enterprise', 'marketing', 'sales'],
            'ai education': ['learning', 'education', 'course', 'tutorial'],
        }

        for category, terms in ai_terms.items():
            if any(term in keyword_lower for term in terms):
                categories.append(category)

        if not categories:
            categories.append("general")

        return categories

    def _generate_variations(self, seed_keywords: List[str]) -> List[str]:
        """Generate keyword variations"""
        variations = []
        modifiers = [
            "best", "top", "how to", "guide", "tutorial",
            "tools", "software", "platform", "services",
            "2024", "2025", "free", "online", "automated"
        ]

        for seed in seed_keywords:
            seed_lower = seed.lower()

            # Word order variations
            words = seed.split()
            if len(words) > 1:
                variations.append(" ".join(reversed(words)))

            # Add modifiers
            for mod in modifiers:
                if mod not in seed_lower:
                    variations.append(f"{mod} {seed}")
                    variations.append(f"{seed} {mod}")

        return variations

    def _fetch_related_keywords(self, keyword: str, limit: int) -> List[Keyword]:
        """Fetch related keywords from Google API or similar"""
        # Placeholder - would implement Google API integration
        return []

    def save_keywords(self, keywords: List[Keyword], filename: str = "discovered_keywords.json"):
        """Save keywords to file"""
        filepath = self.data_dir / filename
        data = [k.to_dict() for k in keywords]

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(keywords)} keywords to {filepath}")

    def load_keywords(self, filename: str = "discovered_keywords.json") -> List[Keyword]:
        """Load keywords from file"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            return []

        with open(filepath, 'r') as f:
            data = json.load(f)

        keywords = [Keyword.from_dict(k) for k in data]
        logger.info(f"Loaded {len(keywords)} keywords from {filepath}")
        return keywords

    def get_top_keywords(self, limit: int = 10, min_volume: int = 100) -> List[Keyword]:
        """
        Get top keywords for content generation based on volume and difficulty.
        Prefers keywords with medium difficulty (30-70) and good volume.
        """
        keywords = self.load_keywords()

        # Filter and score
        scored = []
        for kw in keywords:
            if kw.search_volume < min_volume:
                continue

            # Score = volume * (1 - difficulty/100) * (competition factor)
            # Prefer medium difficulty
            score = kw.search_volume * (1 - abs(kw.difficulty - 50) / 100)
            scored.append((score, kw))

        scored.sort(reverse=True)
        return [kw for _, kw in scored[:limit]]

    def refresh_keywords(self):
        """
        Refresh keyword list if it's older than configured days.
        """
        keywords_file = self.data_dir / "discovered_keywords.json"
        if keywords_file.exists():
            import os
            age_days = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(str(keywords_file)))).days

            if age_days >= self.config.scheduling.daily_keyword_refresh_days:
                logger.info(f"Keywords are {age_days} days old, refreshing...")
                seeds = self.config.keywords if self.config.keywords else [self.config.niche]
                new_keywords = self.discover_keywords(seeds, max_results=50)
                self.save_keywords(new_keywords)
            else:
                logger.info(f"Keywords are fresh ({age_days} days old)")
        else:
            logger.info("No existing keywords found, discovering new ones")
            seeds = self.config.keywords if self.config.keywords else [self.config.niche]
            keywords = self.discover_keywords(seeds, max_results=50)
            self.save_keywords(keywords)

if __name__ == "__main__":
    # Test the keyword researcher
    from config import Config
    import os

    os.makedirs("data/keywords", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)

    # Create a minimal config for testing
    config = Config(
        ai=None,  # Would need proper config
        site=None,
        git=None,
        content=None,
        scheduling=None,
        logging=None,
        safety=None,
        metrics=None,
        database=None,
    )

    # This would need proper initialization
