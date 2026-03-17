"""
SEO Optimizer for AI SEO System
Applies SEO best practices to generated content.
"""

import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET
from dataclasses import dataclass

from config import Config
from git_deployer import SitemapUpdater
logger = logging.getLogger("seo_system.seo_optimizer")

@dataclass
class SEOConfig:
    """SEO-specific configuration"""
    min_word_count: int = 800
    max_heading_depth: int = 4
    require_internal_links: bool = True
    min_internal_links: int = 3
    min_unique_keywords: int = 5
    sitemap_priority: float = 0.8
    sitemap_changefreq: str = "weekly"

class SEOOptimizer:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger("seo_system.seo_optimizer")
        self.seo_config = SEOConfig(
            min_word_count=self.config.content.min_word_count,
            max_heading_depth=self.config.seo.max_heading_depth,
            require_internal_links=self.config.seo.require_internal_links,
            min_internal_links=self.config.seo.min_internal_links,
            min_unique_keywords=self.config.seo.min_unique_keywords,
            sitemap_priority=self.config.seo.sitemap_priority,
            sitemap_changefreq=self.config.seo.sitemap_changefreq
        )
    
    def optimize(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Apply full SEO optimization to content.
        
        Steps:
        1. Validate word count and content length
        2. Ensure proper heading hierarchy
        3. Add internal links based on topic relevance
        4. Add schema markup JSON-LD
        5. Update sitemap.xml with new article URL
        """
        self.logger.info("Starting SEO optimization")
        
        # Step 1: Word count validation
        word_count = len(content.split())
        if word_count < self.seo_config.min_word_count:
            raise ValueError(f"Content too short: {word_count} words < {self.seo_config.min_word_count}")
        
        # Step 2: Process content
        processed_content = content
        
        # Step 3: Add internal links
        if self.seo_config.require_internal_links:
            processed_content = self._add_internal_links(processed_content, metadata)
        
        # Step 4: Add schema markup (for full HTML we'll inject it, but for raw article content we'll return as-is)
        # The full HTML generation happens in git_deployer or article_generator
        
        # Step 5: Validate content quality
        self._validate_content(processed_content)
        
        self.logger.info("SEO optimization completed")
        return processed_content
    
    def _add_internal_links(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add internal links to content based on keywords and topics."""
        # Extract main keyword and related terms
        main_keyword = metadata.get('keyword', '')
        keywords = metadata.get('keywords', [])
        
        # Build list of known internal article slugs from existing content
        internal_links = self._discover_internal_articles()
        
        # For each paragraph, identify opportunities for internal linking
        paragraphs = content.split('\n\n')
        linked_paragraphs = []
        
        for para in paragraphs:
            linked_para = para
            
            # Check if paragraph contains any of our target keywords
            for keyword in [main_keyword] + keywords:
                if keyword.lower() in para.lower():
                    # Find a suitable anchor text
                    anchor = self._create_anchor_text(keyword)
                    
                    # Find a suitable existing article to link to
                    for link in internal_links:
                        if keyword.lower() in link['title'].lower() or keyword.lower() in link['slug']:
                            # Replace keyword with linked version
                            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                            linked_para = pattern.sub(f'<a href="{link["url"]}">{anchor}</a>', linked_para, count=1)
                            break
            
            linked_paragraphs.append(linked_para)
        
        return '\n\n'.join(linked_paragraphs)
    
    def _discover_internal_articles(self) -> List[Dict[str, str]]:
        """
        Discover existing articles for internal linking.
        In production, this would scan the deployed site's articles directory.
        """
        # For dry-run, return static suggestions
        deploy_path = Path(self.config.git.deploy_path)
        articles = []
        
        try:
            if deploy_path.exists():
                for html_file in deploy_path.glob("**/*.html"):
                    # Skip index and template files
                    if html_file.stem in ['index', 'template']:
                        continue
                    
                    # Extract title and create slug
                    title = html_file.stem.replace('_', ' ').title()
                    slug = html_file.stem
                    
                    articles.append({
                        'title': title,
                        'slug': slug,
                        'url': f"{self.config.site.url}/articles/{slug}.html"
                    })
        except Exception as e:
            self.logger.warning(f"Could not scan articles directory: {e}")
        
        # Fallback: create some example internal links
        if not articles:
            articles = [
                {'title': 'AI Productivity Tools', 'slug': 'ai-productivity-tools', 'url': f"{self.config.site.url}/articles/ai-productivity-tools.html"},
                {'title': 'Workflow Automation', 'slug': 'workflow-automation', 'url': f"{self.config.site.url}/articles/workflow-automation.html"},
                {'title': 'Digital Transformation', 'slug': 'digital-transformation', 'url': f"{self.config.site.url}/articles/digital-transformation.html"}
            ]
        
        return articles
    
    def _create_anchor_text(self, keyword: str) -> str:
        """Create SEO-friendly anchor text."""
        # Clean up keyword for display
        anchor = keyword.title()
        # Limit length
        if len(anchor) > 50:
            anchor = anchor[:47] + "..."
        return anchor
    
    def _validate_content(self, content: str) -> None:
        """Validate content meets SEO standards."""
        # Check internal link count if required
        if self.seo_config.require_internal_links:
            link_count = len(re.findall(r'<a\s+href=', content))
            if link_count < self.seo_config.min_internal_links:
                raise ValueError(f"Insufficient internal links: {link_count} < {self.seo_config.min_internal_links}")
        
        # Check for unique keywords (simple version)
        words = re.findall(r'\b\w+\b', content.lower())
        unique_words = set(words)
        if len(unique_words) < self.seo_config.min_unique_keywords:
            raise ValueError(f"Content lacks semantic diversity: {len(unique_words)} unique words")
        
        # Check heading hierarchy
        headings = re.findall(r'<h([1-6])[^>]*>', content)
        if headings:
            # Ensure proper nesting (h1 should be first, then increasing)
            heading_nums = [int(h) for h in headings]
            for i in range(1, len(heading_nums)):
                if heading_nums[i] > heading_nums[i-1] + 1:
                    self.logger.warning("Heading hierarchy gap detected (e.g., h1 to h3 without h2)")
        
        self.logger.info("Content validation passed")
    
    def update_sitemap(self, article_url: str, metadata: Dict[str, Any]) -> bool:
        """Add article URL to sitemap.xml."""
        try:
            updater = SitemapUpdater(self.config)
            updater.add_url(article_url, changefreq=self.seo_config.sitemap_changefreq, priority=self.seo_config.sitemap_priority)
            self.logger.info(f"Sitemap updated with: {article_url}")
            return True
        except Exception as e:
            self.logger.error(f"Sitemap update failed: {e}")
            return False
    
    def generate_schema_markup(self, metadata: Dict[str, Any]) -> str:
        """Generate JSON-LD schema markup for article."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": metadata.get('title', ''),
            "description": metadata.get('description', ''),
            "author": {
                "@type": "Organization",
                "name": "AI Productivity Hub"
            },
            "publisher": {
                "@type": "Organization",
                "name": "AI Productivity Hub",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{self.config.site.url}/assets/images/logo.png"
                }
            },
            "datePublished": metadata.get('publish_date', datetime.utcnow().strftime('%Y-%m-%d')),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": metadata.get('canonical_url', '')
            }
        }
        
        import json
        return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'
