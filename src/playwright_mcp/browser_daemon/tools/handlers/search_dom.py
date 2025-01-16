from mcp.types import TextContent
from .utils import send_to_manager, logger
import json


async def handle_search_dom(arguments: dict) -> dict:
    """Handle search-dom tool."""
    logger.info("Handling search-dom request with args: %s", json.dumps(arguments))
    try:
        response = await send_to_manager("search-dom", arguments)
        logger.debug("Raw response type: %s", type(response))
        logger.debug("Raw response repr: %r", response)
        
        if "error" in response:
            logger.error("DOM search failed: %s", response["error"])
            return {
                "isError": True,
                "content": [
                    TextContent(
                        type="text",
                        text=response["error"]
                    )
                ]
            }

        # Format the matches in a readable way
        matches = response.get("matches", [])
        total = response.get("total", 0)
        logger.debug("Found %d matches", total)

        if total == 0:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="No matches found"
                    )
                ]
            }
        
        # Format each match into a readable string
        formatted_matches = []
        for idx, match in enumerate(matches, 1):
            try:
                match_type = match.get("type", "unknown")
                path = match.get("path", "unknown")
                tag = match.get("tag", "unknown")
                text = match.get("text", "")
                attrs = match.get("attributes", {})
                
                # Build match description
                match_info = [f"Match #{idx}:"]
                match_info.append(f"  Type: {match_type}")
                match_info.append(f"  Tag: {tag}")
                match_info.append(f"  Path: {path}")
                
                if text:
                    text = text[:100] + "..." if len(text) > 100 else text
                    match_info.append(f"  Text: {text}")
                
                if attrs:
                    match_info.append("  Attributes:")
                    for attr, value in attrs.items():
                        match_info.append(f"    {attr}: {value}")
                    
                formatted_matches.append("\n".join(match_info))
                
            except Exception as e:
                logger.error("Error formatting match %d: %s", idx, e)
                logger.error("Problematic match data: %r", match)
                continue

        if not formatted_matches:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Found matches but encountered errors formatting them"
                    )
                ]
            }
        
        summary = f"Found {total} matches in the DOM:"
        formatted_response = {
            "content": [
                TextContent(
                    type="text",
                    text=f"{summary}\n\n" + "\n\n".join(formatted_matches)
                )
            ]
        }
        logger.debug("Final formatted response created successfully")
        return formatted_response

    except Exception as e:
        logger.error("Error in handle_search_dom: %s", str(e))
        logger.error("Full traceback:", exc_info=True)
        return {
            "isError": True,
            "content": [
                TextContent(
                    type="text",
                    text=f"Error processing search results: {str(e)}"
                )
            ]
        } 