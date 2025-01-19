from typing import Dict
from .utils import send_to_manager, create_response


async def handle_explore_dom(arguments: Dict) -> Dict:
    """Handle explore-dom command by exploring immediate children of a DOM element."""
    try:
        # Get page_id and selector from arguments
        page_id = arguments.get("page_id")
        selector = arguments.get("selector", "body")  # Default to body if no selector provided
        
        if not page_id:
            return create_response("No page_id provided", is_error=True)
            
        response = await send_to_manager("explore-dom", {
            "page_id": page_id,
            "selector": selector
        })
        
        if "error" in response:
            return create_response(f"Error: {response['error']}", is_error=True)
            
        # Format the children info into a tree-like text structure
        children = response.get("children", [])
        if not children:
            return create_response(f"No children found for selector: {selector}")
            
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
            
        return create_response("\n".join(lines))
        
    except Exception as e:
        return create_response(f"Error exploring DOM: {str(e)}", is_error=True) 