"""Tools for the AI agent to interact with web pages using Playwright."""

from typing import Optional
import logging
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import Tool
from dotenv import load_dotenv
from ....core.session import session_manager

# Set up logging
logger = logging.getLogger(__name__)

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
    logger.info(f"Searching DOM with input: {input.model_dump()}")
    page = session_manager.get_page(ctx.deps)
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
    
    logger.info(f"Found {len(results)} elements")
    return "\n".join(results) if results else "No elements found"


async def interact_dom(ctx: RunContext[str], input: InteractDOMInput) -> str:
    """Interact with elements in the DOM."""
    logger.info(f"Interacting with DOM: {input.model_dump()}")
    page = session_manager.get_page(ctx.deps)
    if not page:
        raise ValueError(f"Page {ctx.deps} not found")
        
    element = await page.query_selector(input.selector)
    if not element:
        logger.warning(f"No element found with selector: {input.selector}")
        return f"No element found with selector: {input.selector}"
    
    try:
        if input.action == "click":
            await element.click()
            logger.info(f"Successfully clicked element: {input.selector}")
            return "Successfully performed click"
        elif input.action == "type":
            if not input.value:
                return "Value required for type action"
            await element.type(input.value)
            logger.info(f"Successfully typed into element: {input.selector}")
            return "Successfully performed type"
        else:
            logger.warning(f"Unknown action: {input.action}")
            return f"Unknown action: {input.action}"
    except Exception as e:
        logger.error(f"Action failed: {str(e)}")
        return f"Action failed: {str(e)}"


async def explore_dom(ctx: RunContext[str], input: ExploreDOMInput) -> str:
    """Explore and return the DOM structure."""
    logger.info(f"Exploring DOM with input: {input.model_dump()}")
    page = session_manager.get_page(ctx.deps)
    if not page:
        raise ValueError(f"Page {ctx.deps} not found")
        
    if input.selector:
        element = await page.query_selector(input.selector)
        if not element:
            logger.warning(f"No element found with selector: {input.selector}")
            return f"No element found with selector: {input.selector}"
        root = element
    else:
        root = await page.query_selector("body")
        if not root:
            logger.warning("Could not find body element")
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
    logger.info(f"Built DOM structure with {len(structure)} elements")
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