from dotenv import load_dotenv
import os
load_dotenv()

"""
Configuration loader for the SEO Content System.
Handles YAML config files and environment variables.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

@dataclass
class AIConfig:
    """AI/LLM configuration"""
    api_key: str = "YOUR_KEY_HERE"
    model: str = "gpt-4o-mini"
    max_tokens: int = 8000
    temperature: float = 0.8
    top_p: float = 0.95
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.1

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file: str = "logs/seo_system.log"
    max_bytes: int = 1024 * 1024
    backup_count: int = 5

@dataclass
class ContentConfig:
    """Content generation configuration"""
    min_word_count: int = 800
    max_word_count: int = 3000
    max_duplicate_sentences: int = 3
    max_placeholder_ratio: float = 0.1
    forbidden_phrases: List[str] = field(default_factory=lambda: [] )
    required_quality_signals: Dict[str, Any] = field(default_factory=lambda: {})

@dataclass
class SEOConfig:
    """SEO configuration"""
    max_heading_depth: int = 4
    require_internal_links: bool = True
    min_internal_links: int = 3
    min_unique_keywords: int = 5
    sitemap_priority: float = 0.8
    sitemap_changefreq: str = "weekly"

@dataclass
class SiteConfig:
    """Site configuration"""
    url: str = "https://ai-productivity-hub.com"
    deploy_path: str = "/home/kali/.openclaw/workspace/site"
    assets_path: str = "/home/kali/.openclaw/workspace/site/assets"

@dataclass
class GitConfig:
    """Git configuration"""
    deploy_path: str = "/home/kali/.openclaw/workspace/site"
    repo_url: str = "https://github.com/chiragwadhvana95-oss/ai-productivity-hub"
    commit_message_template: str = "AI generated article: {filename}"

@dataclass
class StatusConfig:
    """Status reporting configuration"""
    status_file: str = "status.md"
    update_interval: int = 60

@dataclass
class Config:
    """Main configuration class"""
    ai: AIConfig = field(default_factory=AIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    content: ContentConfig = field(default_factory=ContentConfig)
    seo: SEOConfig = field(default_factory=SEOConfig)
    site: SiteConfig = field(default_factory=SiteConfig)
    git: GitConfig = field(default_factory=GitConfig)
    status: StatusConfig = field(default_factory=StatusConfig)
    ai_interval_hours: int = 3

    @classmethod
    def load(cls) -> 'Config':
        """Load configuration from YAML and environment variables."""
        # Load environment variables from .env
        load_dotenv()
        
        # Create default config
        config = cls()
        
        # Load YAML config
        yaml_path = Path("config/settings.yaml")
        if yaml_path.exists():
            with open(yaml_path, 'r') as f:
                yaml_config = yaml.safe_load(f) or {}
            config = cls._merge_from_dict(config, yaml_config)
        
        # Override with environment variables
        config = cls._override_with_env(config)
        
        return config
    
    @classmethod
    def _merge_from_dict(cls, config: 'Config', data: Dict[str, Any]) -> 'Config':
        """Merge dictionary data into config."""
        if not data:
            return config
        
        def merge_dicts(target, source):
            for key, value in source.items():
                if isinstance(value, dict):
                    target[key] = merge_dicts(target.get(key, {}), value)
                else:
                    target[key] = value
            return target
        
        # Merge top-level keys
        for key, value in data.items():
            if hasattr(config, key):
                current = getattr(config, key)
                if isinstance(current, dict):
                    merged = merge_dicts(current.__dict__, value)
                    setattr(config, key, type(current)(**merged))
                elif isinstance(current, list):
                    setattr(config, key, value)
                else:
                    setattr(config, key, value)
        
        return config
    
    @classmethod
    def _override_with_env(cls, config: 'Config') -> 'Config':
        """Override config with environment variables."""
        # Helper to get env var or default
        def env_or_default(var: str, default: str) -> str:
            return os.getenv(var, default)
        
        # AI config
        config.ai.api_key = env_or_default("OPENROUTER_API_KEY", config.ai.api_key)
        config.ai.model = env_or_default("AI_MODEL", config.ai.model)
        config.ai.max_tokens = int(env_or_default("AI_MAX_TOKENS", str(config.ai.max_tokens)))
        config.ai.temperature = float(env_or_default("AI_TEMPERATURE", str(config.ai.temperature)))
        config.ai.top_p = float(env_or_default("AI_TOP_P", str(config.ai.top_p)))
        
        # Content config
        config.content.min_word_count = int(env_or_default("CONTENT_MIN_WORD_COUNT", str(config.content.min_word_count)))
        config.content.max_word_count = int(env_or_default("CONTENT_MAX_WORD_COUNT", str(config.content.max_word_count)))
        
        # Site config
        config.site.url = env_or_default("SITE_URL", config.site.url)
        config.site.deploy_path = env_or_default("SITE_DEPLOY_PATH", config.site.deploy_path)
        
        # Git config
        config.git.repo_url = env_or_default("GIT_REPO_URL", config.git.repo_url)
        
        return config