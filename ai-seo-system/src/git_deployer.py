import subprocess
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("seo_system.git_deployer")

class GitDeployer:
    def __init__(self, config):
        self.config = config
        self.repo_path = Path(config.site.deploy_path)
        self.articles_path = self.repo_path / "articles"

    def deploy(self, html_content: str, filename: str) -> bool:
        try:
            # Ensure articles folder exists
            self.articles_path.mkdir(parents=True, exist_ok=True)

            # Save file
            file_path = self.articles_path / filename
            file_path.write_text(html_content)

            # Update sitemap with new article URL
            sitemap_updater = SitemapUpdater(self.config)
            article_url = f"{self.config.site.url}/articles/{filename}"
            sitemap_success = sitemap_updater.add_url(article_url)
            if not sitemap_success:
                logger.warning("Failed to update sitemap, but continuing deployment")

            # Git operations
            subprocess.run(["git", "add", "."], cwd=str(self.repo_path), check=True)
            subprocess.run(["git", "commit", "-m", f"Add article {filename}"], cwd=str(self.repo_path), check=True)
            subprocess.run(["git", "push"], cwd=str(self.repo_path), check=True)

            logger.info("Deployment successful")
            return True
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False

class SitemapUpdater:
    def __init__(self, config):
        self.config = config
        self.sitemap_path = Path(config.site.deploy_path) / "sitemap-articles.xml"

    def add_url(self, url: str, changefreq: str = "weekly", priority: float = 0.8) -> bool:
        try:
            if not self.sitemap_path.exists():
                logger.warning(f"Sitemap file not found: {self.sitemap_path}")
                return False

            content = self.sitemap_path.read_text()

            new_entry = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>
"""

            # Insert before closing </urlset>
            content = content.replace("</urlset>", new_entry + "</urlset>")
            self.sitemap_path.write_text(content)

            logger.info(f"Added URL to sitemap: {url}")
            return True
        except Exception as e:
            logger.error(f"Sitemap update failed: {e}")
            return False
