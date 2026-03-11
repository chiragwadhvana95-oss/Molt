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
    api_key: str
    model: str = "gpt-4o-mini"
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.1

@dataclass
class SiteConfig:
    """Website configuration"""
    url: str
    name: str
    description: str
    language: str = "en"
    locale: str = "en_US"
    author: str = "AI SEO Bot"
    default_category: str = "Technology"

@dataclass
class GitConfig:
    """Git deployment configuration"""
    repo_url: str
    branch: str = "main"
    user_name: str = "AI SEO Bot"
    user_email: str = "seo-bot@yourdomain.com"
    deploy_path: str = "./site"

@dataclass
class ContentConfig:
    """Content generation settings"""
    min_word_count: int = 800
    max_keyword_density: float = 2.5
    max_link_density: float = 5.0
    default_meta_description: str = "AI-powered SEO content"
    default_tags: List[str] = field(default_factory=lambda: ["ai", "seo", "content", "automation"])

@dataclass
class SchedulingConfig:
    """Automation scheduling"""
    daily_update_hour: int = 2
    daily_keyword_refresh_days: int = 7
    daily_content_limit: int = 3
    timezone: str = "UTC"

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file: str = "./data/logs/seo-system.log"
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    console: bool = True

@dataclass
class SafetyConfig:
    """Quality and safety thresholds"""
    max_keyword_density: float = 2.5
    max_link_density: float = 5.0
    min_readability_score: float = 60.0
    min_seo_score: float = 70.0
    require_external_links: bool = True
    min_external_links: int = 2
    require_internal_links: bool = True
    min_internal_links: int = 3

@dataclass
class MetricsConfig:
    """Performance metrics and monitoring"""
    enabled: bool = True
    collection_interval: int = 3600
    retention_days: int = 30
    slack_webhook: Optional[str] = None

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///data/ai-seo-system.db"

@dataclass
class Config:
    """Main configuration class holding all settings"""
    ai: AIConfig
    site: SiteConfig
    git: GitConfig
    content: ContentConfig
    scheduling: SchedulingConfig
    logging: LoggingConfig
    safety: SafetyConfig
    metrics: MetricsConfig
    database: DatabaseConfig
    keywords: List[str] = field(default_factory=list)
    niche: str = ""

    @classmethod
    def load(cls, config_path: str = "config/settings.yaml", env_path: str = ".env") -> "Config":
        """Load configuration from files and environment"""

        # Load environment variables
        load_dotenv(env_path)

        # Load YAML config
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f) or {}

        # Environment variable overrides
        ai_config = AIConfig(
            api_key=os.getenv("OPENROUTER_API_KEY", config_data.get("ai", {}).get("api_key", "")),
            model=os.getenv("OPENROUTER_MODEL", config_data.get("ai", {}).get("model", "gpt-4o-mini")),
            max_tokens=config_data.get("ai", {}).get("max_tokens", 4000),
            temperature=config_data.get("ai", {}).get("temperature", 0.7),
            top_p=config_data.get("ai", {}).get("top_p", 0.9),
            frequency_penalty=config_data.get("ai", {}).get("frequency_penalty", 0.1),
            presence_penalty=config_data.get("ai", {}).get("presence_penalty", 0.1),
        )

        site_config = SiteConfig(
            url=os.getenv("SITE_URL", config_data.get("site", {}).get("url", "")),
            name=os.getenv("SITE_NAME", config_data.get("site", {}).get("name", "AI SEO Hub")),
            description=os.getenv("SITE_DESCRIPTION", config_data.get("site", {}).get("description", "")),
            language=os.getenv("CONTENT_LANGUAGE", config_data.get("site", {}).get("language", "en")),
            locale=os.getenv("CONTENT_LOCALE", config_data.get("site", {}).get("locale", "en_US")),
            author=os.getenv("DEFAULT_AUTHOR", config_data.get("site", {}).get("author", "AI SEO Bot")),
            default_category=os.getenv("DEFAULT_CATEGORY", config_data.get("site", {}).get("default_category", "Technology")),
        )

        git_config = GitConfig(
            repo_url=os.getenv("GIT_REPO", config_data.get("git", {}).get("repo_url", "")),
            branch=os.getenv("GIT_BRANCH", config_data.get("git", {}).get("branch", "main")),
            user_name=os.getenv("GIT_USER_NAME", config_data.get("git", {}).get("user_name", "AI SEO Bot")),
            user_email=os.getenv("GIT_USER_EMAIL", config_data.get("git", {}).get("user_email", "seo-bot@yourdomain.com")),
            deploy_path=os.getenv("GIT_DEPLOY_PATH", config_data.get("git", {}).get("deploy_path", "./site")),
        )

        content_config = ContentConfig(
            min_word_count=config_data.get("content", {}).get("min_word_count", 800),
            max_keyword_density=config_data.get("content", {}).get("max_keyword_density", 2.5),
            max_link_density=config_data.get("content", {}).get("max_link_density", 5.0),
            default_meta_description=os.getenv("DEFAULT_META_DESCRIPTION", config_data.get("content", {}).get("default_meta_description", "AI-powered SEO content")),
            default_tags=config_data.get("content", {}).get("default_tags", ["ai", "seo", "content", "automation"]),
        )

        safety_config = SafetyConfig(
            max_keyword_density=config_data.get("safety", {}).get("max_keyword_density", 2.5),
            max_link_density=config_data.get("safety", {}).get("max_link_density", 5.0),
            min_readability_score=config_data.get("safety", {}).get("min_readability_score", 60.0),
            min_seo_score=config_data.get("safety", {}).get("min_seo_score", 70.0),
            require_external_links=config_data.get("safety", {}).get("require_external_links", True),
            min_external_links=config_data.get("safety", {}).get("min_external_links", 2),
            require_internal_links=config_data.get("safety", {}).get("require_internal_links", True),
            min_internal_links=config_data.get("safety", {}).get("min_internal_links", 3),
        )

        logging_config = LoggingConfig(
            level=os.getenv("LOG_LEVEL", config_data.get("logging", {}).get("level", "INFO")),
            file=os.getenv("LOG_FILE", config_data.get("logging", {}).get("file", "./data/logs/seo-system.log")),
            max_bytes=config_data.get("logging", {}).get("max_bytes", 10485760),
            backup_count=config_data.get("logging", {}).get("backup_count", 5),
            console=config_data.get("logging", {}).get("console", True),
        )

        metrics_config = MetricsConfig(
            enabled=os.getenv("ENABLE_METRICS", config_data.get("metrics", {}).get("enabled", True)),
            collection_interval=int(os.getenv("METRICS_INTERVAL", config_data.get("metrics", {}).get("collection_interval", 3600))),
            retention_days=config_data.get("metrics", {}).get("retention_days", 30),
            slack_webhook=os.getenv("SLACK_WEBHOOK_URL", config_data.get("metrics", {}).get("slack_webhook")),
        )

        database_config = DatabaseConfig(
            url=os.getenv("DATABASE_URL", config_data.get("database", {}).get("url", "sqlite:///data/ai-seo-system.db")),
        )

        scheduling_config = SchedulingConfig(
            daily_update_hour=int(os.getenv("DAILY_UPDATE_HOUR", config_data.get("scheduling", {}).get("daily_update_hour", 2))),
            daily_keyword_refresh_days=int(os.getenv("DAILY_KEYWORD_REFRESH_DAYS", config_data.get("scheduling", {}).get("daily_keyword_refresh_days", 7))),
            daily_content_limit=int(os.getenv("DAILY_CONTENT_GENERATION_LIMIT", config_data.get("scheduling", {}).get("daily_content_limit", 3))),
            timezone=os.getenv("TIMEZONE", config_data.get("scheduling", {}).get("timezone", "UTC")),
        )

        # Get niche and seed keywords
        niche = config_data.get("niche", "")
        keywords = config_data.get("keywords", [])

        return cls(
            ai=ai_config,
            site=site_config,
            git=git_config,
            content=content_config,
            scheduling=scheduling_config,
            logging=logging_config,
            safety=safety_config,
            metrics=metrics_config,
            database=database_config,
            keywords=keywords,
            niche=niche,
        )

    def validate(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []

        if not self.ai.api_key:
            errors.append("Missing OPENROUTER_API_KEY")

        if not self.site.url:
            errors.append("Missing SITE_URL")

        if not self.git.repo_url:
            errors.append("Missing GIT_REPO")

        if not self.keywords and not self.niche:
            errors.append("Must specify either niche or keywords")

        return errors
