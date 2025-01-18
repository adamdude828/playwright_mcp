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
    if not page:
        raise ValueError(f"Page {ctx.deps} not found")
        
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
    """Interact with elements in the DOM."""
    page = await session_manager.get_page(ctx.deps)
    if not page:
        raise ValueError(f"Page {ctx.deps} not found")
        
    element = await page.query_selector(input.selector)
    if not element:
        return f"No element found with selector: {input.selector}"
    
    try:
        if input.action == "click":
            await element.click()
            return "Successfully performed click"
        elif input.action == "type":
            if not input.value:
                return "Value required for type action"
            await element.type(input.value)
            return "Successfully performed type"
        else:
            return f"Unknown action: {input.action}"
    except Exception as e:
        return f"Action failed: {str(e)}"


async def explore_dom(ctx: RunContext[str], input: ExploreDOMInput) -> str:
    """Explore and return the DOM structure."""
    page = await session_manager.get_page(ctx.deps)
    if not page:
        raise ValueError(f"Page {ctx.deps} not found")
        
    if input.selector:
        element = await page.query_selector(input.selector)
        if not element:
            return f"No element found with selector: {input.selector}"
        root = element
    else:
        root = await page.query_selector("body")
        if not root:
            return "Could not find body element"
    
    structure = []

    async def build_structure(element, depth=0):
        tag = await element.evaluate("el => el.tagName.toLowerCase()")
        indent = "  " * depth
        
        if input.include_text:
            text = await element.text_content()
            text = text.strip() if text else ""
            if text:
                structure.append(f"{indent}<{tag}>{text}</{tag}>")
            else:
                structure.append(f"{indent}<{tag}/>")
        else:
            structure.append(f"{indent}<{tag}/>")
        
        children = await element.query_selector_all(":scope > *")
        for child in children:
            await build_structure(child, depth + 1)
    
    await build_structure(root)
    return "\n".join(structure)


def create_agent(page_id: str) -> Agent:
    """Create a new AI agent with the defined tools."""
    agent = Agent(
        model="claude-3-5-sonnet-latest",
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