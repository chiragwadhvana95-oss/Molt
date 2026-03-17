"""
Article Generator for AI SEO System
Generates SEO-optimized articles using OpenRouter API.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from config import Config
from logger import setup_logging
from keyword_research import Keyword

# Import OpenRouter client and markdown library
from openai import OpenAI
import markdown

logger = logging.getLogger("seo_system.article_generator")

# Modern blog template (simplified for dry-run)
ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AI Productivity Hub</title>
    <meta name="description" content="{description}">
    <link rel="stylesheet" href="/ai-productivity-hub/assets/css/style.css">
</head>
<body>
    <header>
        <h1>AI Productivity Hub</h1>
        <nav>
            <a href="/ai-productivity-hub/">Home</a>
            <a href="/ai-productivity-hub/articles/">Articles</a>
            <a href="/ai-productivity-hub/about/">About</a>
        </nav>
    </header>
    <div class="card">
        <h1>{title}</h1>
        <p>{intro}</p>
        <img src="/ai-productivity-hub/assets/images/ai-tools.jpg" alt="AI Tools" onerror="this.style.display='none'">
    </div>
    <div class="card">
        <h2>Complete Guide</h2>
        {content}
    </div>
    <footer>
        <p>© 2026 AI Productivity Hub. All rights reserved.</p>
    </footer>
</body>
</html>"""

class ArticleGenerator:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger("seo_system.article_generator")
        
        # Initialize OpenRouter client
        self.client = OpenAI(
            api_key=config.ai.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    
    def generate(self, keyword: str) -> Dict[str, Any]:
        """
        Generate a complete SEO-optimized article using OpenRouter API.
        """
        logger.info(f"Generating article for keyword: {keyword}")
        
        # Create metadata
        metadata = self._build_metadata(keyword)
        
        # Generate content using OpenRouter
        content = self._generate_content(keyword, metadata)
        
        # Create filename
        filename = self._create_filename(keyword)
        
        return {
            'title': metadata['title'],
            'content': content,
            'filename': filename,
            'keyword': keyword,
            'metadata': metadata
        }
    
    def generate_mock(self, keyword: str) -> Dict[str, Any]:
        """
        Generate mock article content for testing (no API call).
        """
        logger.info(f"Generating mock article for keyword: {keyword}")
        
        # Create metadata
        metadata = self._build_metadata(keyword)
        
        # Generate mock content
        markdown_content = self._generate_mock_content(keyword, metadata)
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=["tables", "fenced_code"]
        )
        
        # Create filename
        filename = self._create_filename(keyword)
        
        return {
            'title': metadata['title'],
            'content': html_content,
            'filename': filename,
            'keyword': keyword,
            'metadata': metadata
        }
    
    def _build_metadata(self, keyword: str) -> Dict[str, Any]:
        """Build article metadata for SEO and processing."""
        
        # Generate SEO-friendly title
        title = f"{keyword.title()}: Complete Guide & Best Practices"
        
        # Generate meta description
        description = f"Learn everything about {keyword} in this comprehensive guide. Discover best practices, tools, and strategies to improve your productivity with AI."
        
        # Generate keywords
        keywords = [keyword, "AI productivity", "automation", "best practices"]
        
        # Generate intro
        intro = f"Welcome to the ultimate guide on {keyword}! In today's fast-paced digital world, understanding {keyword} is crucial for anyone looking to boost their productivity and stay ahead of the curve. Whether you're a beginner or an experienced professional, this comprehensive guide will provide you with actionable insights, practical tips, and the latest strategies to master {keyword}."
        
        # Generate publish date
        publish_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        return {
            'title': title,
            'description': description,
            'keywords': keywords,
            'intro': intro,
            'publish_date': publish_date,
            'canonical_url': f"{self.config.site.url}/articles/{self._slugify(keyword)}"
        }
    
    def _generate_content(self, keyword: str, metadata: Dict[str, Any]) -> str:
        """Generate article content using OpenRouter API."""
        
        try:
            # Create system prompt
            system_prompt = f"""You are an expert SEO content writer. Write a comprehensive, engaging article about "{keyword}" that:
1. Is at least {self.config.content.min_word_count} words
2. Uses semantic topic clustering around {keyword}
3. Includes an introduction, main sections, and conclusion
4. Contains 3-5 key takeaways
5. Suggests 3 related article topics
6. Uses proper heading hierarchy (H1, H2, H3)
7. Has high readability (Flesch-Kincaid score > 60)"""
            
            # Create user prompt
            user_prompt = f"""Write a detailed article about: {keyword}

Structure:
- Introduction: 2-3 paragraphs explaining the topic and why it matters
- Main sections: 4-6 comprehensive sections with H2 headings
- Subsections: Use H3 headings within main sections
- Conclusion: Summary and next steps
- Key takeaways: 3-5 bullet points
- Related topics: 3 suggestions for other articles

Make it informative, engaging, and optimized for search engines."""
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.config.ai.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.config.content.max_word_count * 2,  # generous token limit
                temperature=self.config.ai.temperature,
                top_p=self.config.ai.top_p,
                frequency_penalty=self.config.ai.frequency_penalty,
                presence_penalty=self.config.ai.presence_penalty
            )
            
            # Get content from response
            # Convert markdown content to HTML
            html_content = markdown.markdown(
                response.choices[0].message.content.strip(),
                extensions=["tables", "fenced_code"]
            )
            
            return html_content
            
        except Exception as e:
            logger.error(f"OpenRouter API call failed: {e}")
            # Fallback to mock content if API fails
            return self._generate_mock_content(keyword, metadata)
    
    def _generate_mock_content(self, keyword: str, metadata: Dict[str, Any]) -> str:
        """Generate mock content for testing."""
        
        # Generate longer content to meet word count requirements
        mock_content = f"""## What is {keyword}?

{keyword} is a revolutionary concept that has transformed how we approach productivity and efficiency in the modern workplace. At its core, {keyword} represents a systematic approach to optimizing workflows and eliminating bottlenecks. This comprehensive guide will walk you through everything you need to know about implementing {keyword} in your organization.

### The Evolution of {keyword}

The concept of {keyword} has evolved significantly over the past decade. What started as simple automation tools has grown into sophisticated AI-powered systems that can learn, adapt, and optimize entire business processes. Understanding this evolution helps organizations appreciate the full potential of {keyword} and how it can be leveraged for maximum impact.

#### Early Beginnings

In the early days, {keyword} solutions were limited to basic rule-based automation. These systems required extensive manual configuration and were rigid in their operations. They could handle straightforward tasks but struggled with complex, variable scenarios.

#### Modern Approaches

Today's {keyword} platforms incorporate machine learning and natural language processing. They can analyze patterns, make predictions, and continuously improve their performance. This advancement has made {keyword} accessible to a wider range of businesses and use cases.

## Key Components of {keyword}

Understanding the key components of {keyword} is essential for successful implementation:

1. **Automation Engine**: The core of {keyword} is its ability to automate repetitive tasks, reducing manual effort and minimizing errors. This includes everything from simple task scheduling to complex workflow orchestration.

2. **Integration Layer**: {keyword} solutions must integrate seamlessly with existing tools and platforms. This integration layer ensures data flows smoothly between systems, eliminating silos and improving overall efficiency.

3. **Intelligence Module**: Modern {keyword} systems include AI capabilities that allow them to learn from data, adapt to changing conditions, and make intelligent decisions. This intelligence transforms static automation into dynamic optimization.

4. **Analytics Dashboard**: To measure the effectiveness of {keyword}, robust analytics are essential. These dashboards provide insights into performance metrics, ROI, and areas for improvement.

## Why {keyword} Matters

In today's competitive landscape, {keyword} has become essential for businesses looking to maintain their edge. Here's why:

- **Time Savings**: Organizations using {keyword} report up to 40% reduction in time spent on routine tasks. This frees up employees to focus on higher-value activities that drive innovation and growth.

- **Cost Efficiency**: By automating repetitive processes, {keyword} helps reduce operational costs significantly. The return on investment is often realized within months of implementation.

- **Scalability**: {keyword} solutions can easily scale with your business growth without proportional increases in overhead. This scalability ensures that your investment continues to deliver value as your organization expands.

- **Competitive Advantage**: Early adopters of {keyword} gain a significant competitive edge through improved efficiency, faster time-to-market, and higher quality outputs.

- **Employee Satisfaction**: Automating mundane tasks leads to higher employee satisfaction and retention. Team members can engage in more meaningful work that utilizes their skills and creativity.

## How to Implement {keyword}

Implementing {keyword} requires a strategic approach. Follow these steps for successful adoption:

### 1. Assessment and Planning

Begin by evaluating your current workflows and identifying areas where {keyword} can have the greatest impact. Map out existing processes, pain points, and opportunities for automation. This assessment phase is critical for defining the scope and objectives of your {keyword} initiative.

### 2. Solution Selection

With a clear understanding of your needs, evaluate available {keyword} solutions. Consider factors such as:
- Compatibility with existing systems
- AI capabilities and learning potential
- Ease of integration
- Scalability
- Vendor support and roadmap

### 3. Pilot Program

Before full-scale deployment, implement a pilot program focused on a specific process or department. This allows you to test the solution in a controlled environment, gather feedback, and refine your approach.

### 4. Phased Rollout

Based on pilot results, develop a phased rollout plan. Start with the most impactful processes and gradually expand to other areas. This approach minimizes disruption and allows for continuous improvement.

### 5. Training and Adoption

Ensure your team is properly trained on the new {keyword} system. Provide comprehensive documentation, hands-on workshops, and ongoing support. Adoption is key to realizing the full benefits of {keyword}.

### 6. Optimization and Scaling

Once the system is running, continuously monitor performance and gather feedback. Use analytics to identify optimization opportunities and scale the solution across the organization.

## Best Practices for {keyword}

To get the most out of {keyword}, consider these best practices:

### Start with a Clear Strategy

Define specific goals and KPIs for your {keyword} implementation. Know what success looks like and how you'll measure it. This clarity guides decision-making throughout the project.

### Choose the Right Use Cases

Not all processes are suitable for {keyword}. Focus on high-volume, repetitive tasks with clear rules and inputs. Avoid processes that require frequent human judgment or are constantly changing.

### Ensure Data Quality

{keyword} systems rely on high-quality data. Invest in data cleaning and preparation before implementation. Poor data quality leads to poor automation results.

### Maintain Human Oversight

While {keyword} can automate many tasks, human oversight remains essential. Implement review processes and exception handling to catch errors and handle edge cases.

### Document Everything

Maintain comprehensive documentation of automated processes, decision rules, and system configurations. This documentation is invaluable for troubleshooting, training, and future enhancements.

### Foster a Culture of Continuous Improvement

{keyword} is not a set-it-and-forget-it solution. Encourage your team to regularly review automated processes, suggest improvements, and explore new automation opportunities.

### Measure and Communicate ROI

Track and communicate the benefits of {keyword} to stakeholders. Use concrete metrics like time saved, error reduction, and cost avoidance to demonstrate value and secure ongoing support.

## Common Challenges and Solutions

### Challenge 1: Resistance to Change

Employees may fear that {keyword} will replace their jobs. Address this by emphasizing that {keyword} augments human capabilities rather than replacing them. Show how automation frees people from boring tasks to do more interesting work.

**Solution**: Involve employees early in the process, provide training, and highlight success stories from within the organization.

### Challenge 2: Integration Complexity

Integrating {keyword} with legacy systems can be challenging. Some older systems may lack APIs or use proprietary protocols.

**Solution**: Work with vendors that offer flexible integration options. Consider middleware or iPaaS solutions to bridge compatibility gaps. Budget time for thorough testing.

### Challenge 3: Data Security

{keyword} systems often require access to sensitive data. This raises security and privacy concerns.

**Solution**: Choose solutions with strong security features like encryption, access controls, and audit trails. Implement data governance policies and ensure compliance with relevant regulations.

### Challenge 4: Maintenance Overhead

Automated systems require ongoing maintenance to handle exceptions, update integrations, and adapt to changing business needs.

**Solution**: Allocate dedicated resources for maintenance. Use monitoring tools to proactively identify issues. Choose solutions with good vendor support and regular updates.

## Key Takeaways

- {keyword} is a powerful approach to productivity optimization that combines automation, AI, and integration.
- Successful implementation requires careful planning, pilot testing, and phased rollout.
- Focus on high-value use cases and ensure data quality.
- {keyword} augments human capabilities rather than replacing jobs.
- Continuous improvement and measurement are essential for long-term success.
- Address challenges proactively through communication, training, and robust solutions.

## Related Topics

- AI Productivity Tools
- Workflow Automation
- Digital Transformation
- Business Process Optimization
- Machine Learning Applications
- Robotic Process Automation (RPA)
- Intelligent Automation
- Business Intelligence

This comprehensive guide provides a solid foundation for understanding and implementing {keyword}. However, there's always more to learn. Stay tuned for our upcoming articles on advanced {keyword} techniques, industry-specific applications, and real-world case studies that demonstrate the transformative power of {keyword} in action!"""
        
        return mock_content
    
    def _create_filename(self, keyword: str) -> str:
        """Create a SEO-friendly filename for the article."""
        
        # Create slug from keyword
        slug = self._slugify(keyword)
        
        # Add timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
        
        return f"{slug}_{timestamp}.html"
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        import re
        
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'\s+', '-', text)
        text = re.sub(r'-+', '-', text)
        text = text.strip('-')
        
        return text
    
    def _render_html(self, content: str, metadata: Dict[str, Any]) -> str:
        """Render the final HTML using the template."""
        
        # Replace template variables
        html = ARTICLE_TEMPLATE.format(
            title=metadata['title'],
            description=metadata['description'],
            intro=metadata['intro'],
            content=content,
            keywords=','.join(metadata['keywords']),
            publish_date=metadata['publish_date'],
            canonical_url=metadata['canonical_url']
        )
        
        return html