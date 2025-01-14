from typing import Dict
from playwright.async_api import Page


async def explore_dom(page: Page, selector: str = "body") -> Dict:
    """
    Explore the DOM starting from a given selector, returning information about immediate children.
    
    Args:
        page: The Playwright page object
        selector: CSS selector to start exploration from (defaults to body)
        
    Returns:
        Dict containing information about the children elements
    """
    # JavaScript to get element info and its immediate children
    script = """
    (selector) => {
        const element = document.querySelector(selector);
        if (!element) return null;
        
        const getElementInfo = (el) => {
            const classes = Array.from(el.classList);
            const text = el.textContent;
            const childCount = el.children.length;
            return {
                tag: el.tagName.toLowerCase(),
                id: el.id,
                classes: classes,
                text: text,
                childCount: childCount
            };
        };
        
        const children = Array.from(element.children).map(getElementInfo);
        return { children };
    }
    """
    
    result = await page.evaluate(script, selector)
    if not result:
        return {"error": f"No element found for selector: {selector}"}
    
    return result 