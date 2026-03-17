"""
AI SEO System - Main Pipeline Orchestrator
"""

import logging
from datetime import datetime
from typing import Dict, Any

from config import Config
from keyword_research import KeywordResearcher
from article_generator import ArticleGenerator
from seo_optimizer import SEOOptimizer
from safety_checker import SafetyChecker
from git_deployer import GitDeployer
from status_reporter import StatusReporter

logger = logging.getLogger("seo_system.main")

def run_pipeline(config: Config, dry_run: bool = False) -> None:
    """
    Execute the full AI SEO pipeline once.

    Steps:
    1. Keyword research: discover target keywords
    2. Article generation: create content via OpenRouter
    3. SEO optimization: add meta tags, internal links, schema
    4. Safety check: validate word count, duplicates, quality
    5. Git deployment: save HTML, update sitemap, commit & push
    6. Status reporting: update status.md
    """

    pipeline_start = datetime.utcnow()
    logger.info("Starting AI SEO pipeline cycle")

    try:
        # 1. Keyword discovery
        researcher = KeywordResearcher(config)
        keywords = researcher.discover_keywords()
        if not keywords:
            logger.warning("No keywords discovered, using fallback mock keyword")
            # We'll create a simple object with a keyword attribute for consistency
            class FallbackKeyword:
                def __init__(self):
                    self.keyword = "AI productivity tools"
            keywords = [FallbackKeyword()]
        keyword = keywords[0].keyword
        logger.info(f"Selected keyword: {keyword}")

        # 2. Article generation
        generator = ArticleGenerator(config)
        if dry_run:
            article = generator.generate_mock(keyword)
        else:
            article = generator.generate(keyword)
        logger.info(f"Article generated: {article['title']}")

        # 3. SEO optimization
        optimizer = SEOOptimizer(config)
        optimized_html = optimizer.optimize(article['content'], article['metadata'])
        article['optimized_content'] = optimized_html
        logger.info("SEO optimization applied")

        # 4. Safety check (disabled for dry-run)
        if not dry_run:
            checker = SafetyChecker(config)
            is_safe, issues = checker.check(optimized_html, article['metadata'])
            if not is_safe:
                logger.error(f"Safety check failed: {issues}")
                raise ValueError(f"Content failed safety checks: {issues}")
            logger.info("Safety check passed")
        else:
            logger.info("Safety check skipped for dry-run")

        # 5. Git deployment
        deployer = GitDeployer(config)
        filename = article['filename']
        success = deployer.deploy(optimized_html, filename)
        if not success:
            raise RuntimeError("Git deployment failed")
        logger.info(f"Deployed article: {filename}")

        # 6. Status reporting
        reporter = StatusReporter(config)
        reporter.record_success(keyword, filename, pipeline_start)

        logger.info("Pipeline cycle completed successfully")

    except Exception as e:
        logger.exception("Pipeline cycle failed")
        # Still report the failure
        try:
            reporter = StatusReporter(config)
            reporter.record_failure(str(e), pipeline_start)
        except:
            pass
        raise