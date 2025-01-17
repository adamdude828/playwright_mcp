"""Tools for the AI agent to interact with web pages using Playwright."""

from typing import Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import Tool
from dotenv import load_dotenv
from ....core.session import session_manager

# Try to load from .env file first
load_dotenv()


class SearchDOMInput(BaseModel):
    """Input for searching the DOM."""
    text: Optional[str] = Field(None, description="Text content to search for")
    selector: Optional[str] = Field(None, description="CSS selector to search for")


class InteractDOMInput(BaseModel):
    """Input for DOM interactions."""
    selector: str = Field(..., description="CSS selector for the element")
    action: str = Field(..., description="Action to perform (click, type, etc)")
    value: Optional[str] = Field(None, description="Value for the action (e.g. text to type)")


class ExploreDOMInput(BaseModel):
    """Input for exploring the DOM structure."""
    selector: Optional[str] = Field(None, description="CSS selector to start exploring from")
    include_text: bool = Field(True, description="Whether to include text content")


async def search_dom(ctx: RunContext[str], input: SearchDOMInput) -> str:
    """Search for elements in the DOM using a selector or text content."""
    page = await session_manager.get_page(ctx.deps)
    if input.selector:
        elements = await page.query_selector_all(input.selector)
    elif input.text:
        # Use text search
        elements = await page.get_by_text(input.text).all()
    else:
        return "Please provide either a selector or text to search for"
    
    results = []
    for element in elements:
        text = await element.text_content()
        tag = await element.evaluate("el => el.tagName.toLowerCase()")
        results.append(f"{tag}: {text}")
    
    return "\n".join(results) if results else "No elements found"


async def interact_dom(ctx: RunContext[str], input: InteractDOMInput) -> str:
    """Interact with elements in the DOM (click, type, hover)."""
    page = await session_manager.get_page(ctx.deps)
    element = await page.query_selector(input.selector)
    if not element:
        return f"No element found with selector: {input.selector}"

    try:
        if input.action == "click":
            await element.click()
        elif input.action == "type" and input.value:
            await element.type(input.value)
        elif input.action == "hover":
            await element.hover()
        else:
            return f"Unsupported action: {input.action}"
        return f"Successfully performed {input.action} on element"
    except Exception as e:
        return f"Error performing {input.action}: {str(e)}"


async def explore_dom(ctx: RunContext[str], input: ExploreDOMInput) -> str:
    """Explore and return the DOM structure."""
    page = await session_manager.get_page(ctx.deps)
    if input.selector:
        element = await page.query_selector(input.selector)
        if not element:
            return f"No element found with selector: {input.selector}"
        html = await element.evaluate("el => el.outerHTML")
    else:
        html = await page.content()
    
    if not input.include_text:
        # Could add logic to strip text content if needed
        pass
        
    return html


def create_agent(page_id: str) -> Agent:
    """Create a new AI agent with the defined tools."""
    agent = Agent(
        model="anthropic:claude-3-sonnet-20240229",
        deps_type=str,  # page_id as dependency
        system_prompt="""You are a web automation assistant that uses Playwright to interact with web pages.
        You have access to tools that map directly to Playwright operations.
        Break down complex tasks into simple steps using the available tools.
        Always verify your actions and provide clear feedback.""",
        tools=[
            Tool(
                search_dom,
                name="search_dom",
                description="Search for elements in the DOM using a selector or text content",
            ),
            Tool(
                interact_dom,
                name="interact_dom", 
                description="Interact with elements in the DOM (click, type, hover)",
            ),
            Tool(
                explore_dom,
                name="explore_dom",
                description="Explore and return the DOM structure",
            )
        ]
    )
    return agent 