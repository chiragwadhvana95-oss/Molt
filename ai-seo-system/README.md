# Automated SEO Content System

A comprehensive system for automated SEO content generation, publishing, and management.

## Components

1. **Keyword Research Engine** - Discovers and analyzes keywords
2. **Article Generator** - Creates SEO-optimized content using AI
3. **Internal Linking System** - Smart internal linking network
4. **Homepage Auto-Update** - Dynamic homepage updates
5. **SEO Infrastructure** - Meta tags, schema, sitemaps, robots.txt
6. **Git Deployment** - Automated version control and deployment
7. **Daily Automation** - Scheduled content pipeline
8. **Logging** - Comprehensive logging and monitoring
9. **Safety Checks** - Quality assurance before publishing
10. **Status Reporting** - System health and performance reports

## Directory Structure

```
seo-system/
├── config/
│   └── settings.yaml          # System configuration
├── src/
│   ├── keyword_research.py    # Keyword discovery and analysis
│   ├── article_generator.py   # AI-powered article creation
│   ├── internal_links.py      # Internal linking logic
│   ├── homepage_updater.py    # Homepage dynamic updates
│   ├── seo_optimizer.py       # SEO meta and schema generation
│   ├── git_deployer.py        # Git automation
│   ├── scheduler.py           # Daily automation scheduler
│   ├── logger.py              # Logging setup
│   ├── safety_checker.py      # Pre-publish validation
│   ├── status_reporter.py     # Health and performance reports
│   └── main.py               # Main orchestrator
├── data/
│   ├── keywords/             # Keyword research data
│   ├── articles/             # Generated articles (draft and published)
│   ├── links/                # Internal linking data
│   ├── logs/                 # System logs
│   ├── metrics/              # Performance metrics
│   └── config/               # Runtime configuration
├── tests/                    # Unit and integration tests
├── docs/                     # Documentation
├── venv/                     # Python virtual environment
├── requirements.txt          # Dependencies
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore file
├── README.md                 # This file
└── run.py                   # System entry point
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure
3. Run: `python run.py`

## Configuration

Edit `config/settings.yaml` to customize:
- Target keywords and topics
- AI model preferences
- Publishing schedule
- Git repository settings
- Notification settings

## Environment Variables

Required in `.env`:
- `OPENROUTER_API_KEY` - AI API key for article generation
- `SITE_URL` - Your website URL
- `GIT_REPO` - Git repository for deployment
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
