"""Tools for the AI agent to interact with web pages using Playwright."""

from typing import Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import Tool
from dotenv import load_dotenv
from ....utils.logging import setup_logging
from ...core.session import session_manager

# Set up logging properly using project's utility
logger = setup_logging("playwright_mcp.browser_daemon.tools.ai_agent")

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
    logger.debug(f"[search_dom] Starting search_dom with context: {ctx.deps}")
    logger.debug(f"[search_dom] Input parameters: {input.model_dump()}")
    
    try:
        logger.debug("[search_dom] Getting page from session manager")
        page = session_manager.get_page(ctx.deps)
        if not page:
            error_msg = f"Error: Page {ctx.deps} not found"
            logger.error(f"[search_dom] {error_msg}")
            return error_msg
            
        if not (input.selector or input.text):
            error_msg = "Error: Please provide either a selector or text to search for"
            logger.error(f"[search_dom] {error_msg}")
            return error_msg
            
        try:
            if input.selector:
                logger.debug(f"[search_dom] Searching by selector: {input.selector}")
                elements = await page.query_selector_all(input.selector)
                logger.debug(f"[search_dom] Found {len(elements)} elements by selector")
            else:
                logger.debug(f"[search_dom] Searching by text: {input.text}")
                elements = await page.get_by_text(input.text).all()
                logger.debug(f"[search_dom] Found {len(elements)} elements by text")
        except Exception as e:
            error_msg = f"Error searching DOM: {str(e)}"
            logger.error(f"[search_dom] {error_msg}")
            return error_msg
        
        results = []
        logger.debug("[search_dom] Processing found elements")
        for i, element in enumerate(elements):
            try:
                logger.debug(f"[search_dom] Processing element {i+1}/{len(elements)}")
                text = await element.text_content()
                tag = await element.evaluate("el => el.tagName.toLowerCase()")
                results.append(f"{tag}: {text}")
                logger.debug(f"[search_dom] Element {i+1} processed: {tag}")
            except Exception as e:
                logger.warning(f"[search_dom] Error processing element {i+1}: {str(e)}")
                continue
        
        logger.info(f"[search_dom] Successfully found and processed {len(results)} elements")
        return "\n".join(results) if results else "No elements found"
    except Exception as e:
        error_msg = f"Unexpected error in search_dom: {str(e)}"
        logger.error(f"[search_dom] {error_msg}")
        return error_msg


async def interact_dom(ctx: RunContext[str], input: InteractDOMInput) -> str:
    """Interact with elements in the DOM."""
    logger.debug(f"[interact_dom] Starting interact_dom with context: {ctx.deps}")
    logger.debug(f"[interact_dom] Input parameters: {input.model_dump()}")
    
    try:
        logger.debug("[interact_dom] Getting page from session manager")
        page = session_manager.get_page(ctx.deps)
        if not page:
            error_msg = f"Error: Page {ctx.deps} not found"
            logger.error(f"[interact_dom] {error_msg}")
            return error_msg
            
        try:
            logger.debug(f"[interact_dom] Finding element with selector: {input.selector}")
            element = await page.query_selector(input.selector)
            logger.debug(f"[interact_dom] Element found: {bool(element)}")
        except Exception as e:
            error_msg = f"Error finding element: {str(e)}"
            logger.error(f"[interact_dom] {error_msg}")
            return error_msg
            
        if not element:
            error_msg = f"Error: No element found with selector: {input.selector}"
            logger.warning(f"[interact_dom] {error_msg}")
            return error_msg
        
        try:
            if input.action == "click":
                logger.debug(f"[interact_dom] Attempting to click element: {input.selector}")
                await element.click()
                logger.info(f"[interact_dom] Successfully clicked element: {input.selector}")
                return "Successfully performed click"
            elif input.action == "type":
                if not input.value:
                    error_msg = "Error: Value required for type action"
                    logger.error(f"[interact_dom] {error_msg}")
                    return error_msg
                logger.debug(f"[interact_dom] Attempting to type into element: {input.selector}")
                await element.type(input.value)
                logger.info(f"[interact_dom] Successfully typed into element: {input.selector}")
                return "Successfully performed type"
            else:
                error_msg = f"Error: Unknown action: {input.action}"
                logger.warning(f"[interact_dom] {error_msg}")
                return error_msg
        except Exception as e:
            error_msg = f"Error performing action: {str(e)}"
            logger.error(f"[interact_dom] {error_msg}")
            return error_msg
    except Exception as e:
        error_msg = f"Unexpected error in interact_dom: {str(e)}"
        logger.error(f"[interact_dom] {error_msg}")
        return error_msg


async def explore_dom(ctx: RunContext[str], input: ExploreDOMInput) -> str:
    """Explore and return the DOM structure."""
    logger.debug(f"[explore_dom] Starting explore_dom with context: {ctx.deps}")
    logger.debug(f"[explore_dom] Input parameters: {input.model_dump()}")
    
    try:
        logger.debug("[explore_dom] Getting page from session manager")
        page = session_manager.get_page(ctx.deps)
        if not page:
            error_msg = f"Error: Page {ctx.deps} not found"
            logger.error(f"[explore_dom] {error_msg}")
            return error_msg
            
        try:
            if input.selector:
                logger.debug(f"[explore_dom] Finding element with selector: {input.selector}")
                element = await page.query_selector(input.selector)
                logger.debug(f"[explore_dom] Element found: {bool(element)}")
                if not element:
                    error_msg = f"Error: No element found with selector: {input.selector}"
                    logger.warning(f"[explore_dom] {error_msg}")
                    return error_msg
                root = element
            else:
                logger.debug("[explore_dom] Finding body element")
                root = await page.query_selector("body")
                logger.debug(f"[explore_dom] Body element found: {bool(root)}")
                if not root:
                    error_msg = "Error: Could not find body element"
                    logger.warning(f"[explore_dom] {error_msg}")
                    return error_msg
        except Exception as e:
            error_msg = f"Error finding root element: {str(e)}"
            logger.error(f"[explore_dom] {error_msg}")
            return error_msg
        
        structure = []
        logger.debug("[explore_dom] Starting DOM structure traversal")

        async def build_structure(element, depth=0):
            try:
                logger.debug(f"[explore_dom] Processing element at depth {depth}")
                tag = await element.evaluate("el => el.tagName.toLowerCase()")
                indent = "  " * depth
                
                if input.include_text:
                    text = await element.text_content()
                    text = text.strip() if text else ""
                    if text:
                        structure.append(f"{indent}<{tag}>{text}</{tag}>")
                        logger.debug(f"[explore_dom] Added element with text at depth {depth}: {tag}")
                    else:
                        structure.append(f"{indent}<{tag}/>")
                        logger.debug(f"[explore_dom] Added empty element at depth {depth}: {tag}")
                else:
                    structure.append(f"{indent}<{tag}/>")
                    logger.debug(f"[explore_dom] Added element at depth {depth}: {tag}")
                
                logger.debug(f"[explore_dom] Finding children for element at depth {depth}")
                children = await element.query_selector_all(":scope > *")
                logger.debug(f"[explore_dom] Found {len(children)} children at depth {depth}")
                for i, child in enumerate(children):
                    logger.debug(f"[explore_dom] Processing child {i+1}/{len(children)} at depth {depth}")
                    await build_structure(child, depth + 1)
            except Exception as e:
                logger.warning(f"[explore_dom] Error processing element at depth {depth}: {str(e)}")
                structure.append(f"{indent}<error>Failed to process element: {str(e)}</error>")
        
        await build_structure(root)
        logger.info(f"[explore_dom] Successfully built DOM structure with {len(structure)} elements")
        return "\n".join(structure)
    except Exception as e:
        error_msg = f"Unexpected error in explore_dom: {str(e)}"
        logger.error(f"[explore_dom] {error_msg}")
        return error_msg


def create_agent(page_id: str) -> Agent:
    """Create a new AI agent with the defined tools."""
    logger.debug(f"[create_agent] Creating AI agent for page: {page_id}")
    agent = Agent(
        model="claude-3-5-sonnet-latest",
        deps_type=str,  # page_id as dependency
        system_prompt="""You are a web automation assistant that uses Playwright to interact with web pages.
        You have access to tools that map directly to Playwright operations.
        Break down complex tasks into simple steps using the available tools.
        Try and anticipate actions needed that might be required to run before the main task.
        Don't be afriad to interact with the page as neded. 
        Ask the user clarifying questions if needed.
        If you receive an error message from any tool, analyze it and try an alternative approach if possible.
        Always verify your actions and provide clear feedback about successes and failures.""",
        tools=[
            Tool(
                search_dom,
                name="search_dom",
                description=(
                    "Search for elements in the DOM using a selector or text content. "
                    "Returns error message if operation fails."
                ),
            ),
            Tool(
                interact_dom,
                name="interact_dom", 
                description=(
                    "Interact with elements in the DOM (click, type, hover). "
                    "Returns error message if operation fails."
                ),
            ),
            Tool(
                explore_dom,
                name="explore_dom",
                description=(
                    "Explore and return the DOM structure. "
                    "Returns error message if operation fails."
                ),
            )
        ],
    )
    logger.debug("[create_agent] AI agent created successfully")
    return agent 