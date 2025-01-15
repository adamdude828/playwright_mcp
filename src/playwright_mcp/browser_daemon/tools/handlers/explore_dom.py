from typing import Dict, List
from mcp.types import TextContent
from .utils import send_to_manager


async def handle_explore_dom(arguments: Dict) -> List[TextContent]:
    """Handle explore-dom command by exploring immediate children of a DOM element."""
    try:
        # Get page_id and selector from arguments
        page_id = arguments.get("page_id")
        selector = arguments.get("selector", "body")  # Default to body if no selector provided
        
        if not page_id:
            return [TextContent(type="text", text="No page_id provided")]
            
        response = await send_to_manager("explore-dom", {
            "page_id": page_id,
            "selector": selector
        })
        
        if "error" in response:
            return [TextContent(type="text", text=f"Error: {response['error']}")]
            
        # Format the children info into a tree-like text structure
        children = response.get("children", [])
        if not children:
            return [TextContent(type="text", text=f"No children found for selector: {selector}")]
            
        # Build output text
        lines = [f"Element: {selector}"]
        for i, child in enumerate(children):
            prefix = "└── " if i == len(children) - 1 else "├── "
            text = child.get("text", "").strip()
            text_preview = f" \"{text[:30]}...\"" if text else ""
            child_count = child.get("childCount", 0)
            child_info = f"{child['tag']}"
            if child.get("id"):
                child_info += f"#{child['id']}"
            if child.get("classes"):
                child_info += f".{'.'.join(child['classes'])}"
            if child_count:
                child_info += f" ({child_count} children)"
            lines.append(f"{prefix}{child_info}{text_preview}")
            
        return [TextContent(type="text", text="\n".join(lines))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error exploring DOM: {str(e)}")] 