"""CLI entry point for functional tests."""
import os
import sys
import click
from functional_tests import explore_response, highlight_breaking_articles, click_newsletter, test_ai_agent

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)


@click.group()
def cli():
    """Functional test runner CLI."""
    pass


@cli.command()
def explore():
    """Run the explore response test."""
    import asyncio
    asyncio.run(explore_response.main())


@cli.command()
def highlight():
    """Run the highlight breaking articles test."""
    import asyncio
    asyncio.run(highlight_breaking_articles.main())


@cli.command()
def newsletter():
    """Run the newsletter subscribe test."""
    import asyncio
    asyncio.run(click_newsletter.main())


@cli.command()
def agent():
    """Run the AI agent test."""
    import asyncio
    asyncio.run(test_ai_agent.main())


if __name__ == "__main__":
    cli() 