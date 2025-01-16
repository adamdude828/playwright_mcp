from typing import Dict
from mcp.types import TextContent
from .utils import send_to_manager, logger
import traceback
import pathlib
import os


async def handle_highlight_element(arguments: Dict) -> Dict:
    """Handle highlight-element command by highlighting an element and returning its visual context."""
    logger.info(f"Handling highlight-element request with args: {arguments}")
    try:
        # Get required arguments
        page_id = arguments.get("page_id")
        selector = arguments.get("selector")
        save_path = arguments.get("save_path")
        
        if not all([page_id, selector, save_path]):
            return {
                "isError": True,
                "content": [
                    TextContent(
                        type="text",
                        text="page_id, selector, and save_path are required"
                    )
                ]
            }
        
        # Validate absolute path
        if not os.path.isabs(save_path):
            return {
                "isError": True,
                "content": [
                    TextContent(
                        type="text",
                        text="save_path must be an absolute path"
                    )
                ]
            }
            
        # Ensure the directory exists
        save_path = pathlib.Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
            
        # First, get element info and add highlight
        response = await send_to_manager("highlight-element", {
            "page_id": page_id,
            "selector": selector,
            "style": """
                outline: 3px solid #FF4444 !important;
                box-shadow: 0 0 10px #FF4444 !important;
                transition: all 0.3s ease-in-out !important;
            """
        })
        
        if "error" in response:
            return {
                "isError": True,
                "content": [
                    TextContent(
                        type="text",
                        text=f"Error: {response['error']}"
                    )
                ]
            }
        
        # Take screenshot of the area
        screenshot_response = await send_to_manager("screenshot", {
            "page_id": page_id,
            "selector": selector,
            "padding": 50,  # Add padding around the element for context
            "save_path": str(save_path)
        })
        
        if "error" in screenshot_response:
            return {
                "isError": True,
                "content": [
                    TextContent(
                        type="text",
                        text=f"Error taking screenshot: {screenshot_response['error']}"
                    )
                ]
            }
        
        # Get element dimensions and position
        metrics = response.get("metrics", {})
        
        # Format the response
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"""Screenshot saved to: {save_path}

Element Information:
- Selector: {selector}
- Position: (x: {metrics.get('x', 'N/A')}, y: {metrics.get('y', 'N/A')})
- Dimensions: {metrics.get('width', 'N/A')}x{metrics.get('height', 'N/A')}px
- Visible: {metrics.get('visible', 'Unknown')}
"""
                )
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in handle_highlight_element: {e}")
        logger.error(traceback.format_exc())
        return {
            "isError": True,
            "content": [
                TextContent(
                    type="text",
                    text=f"Error highlighting element: {str(e)}"
                )
            ]
        } 