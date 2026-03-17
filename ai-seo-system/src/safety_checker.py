import logging
from typing import Tuple, List, Dict, Any
from config import Config

logger = logging.getLogger("seo_system.safety_checker")

class SafetyChecker:
    def __init__(self, config: Config):
        self.config = config
        self.min_word_count = config.content.min_word_count

    def check(self, content: str, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        issues = []
        if len(content.split()) < self.min_word_count:
            issues.append("Content too short")
        return len(issues) == 0, issues
