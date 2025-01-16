from mcp.types import TextContent
from .utils import send_to_manager, logger


async def handle_search_dom(arguments: dict) -> dict:
    """Handle search-dom tool."""
    logger.info(f"Handling search-dom request with args: {arguments}")
    try:
        response = await send_to_manager("search-dom", arguments)
        logger.info(f"Raw response from manager: {response}")

        if "error" in response:
            logger.error(f"DOM search failed: {response['error']}")
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
                
                # Build match description
                match_info = [f"Match #{idx}:"]
                match_info.append(f"  Type: {match_type}")
                match_info.append(f"  Path: {path}")
                
                if match_type == "attribute":
                    match_info.append(f"  Attribute: {match.get('attribute', '')}")
                    
                formatted_matches.append("\n".join(match_info))
                logger.info(f"Successfully formatted match {idx}")
            except Exception as e:
                logger.error(f"Error formatting match {idx}: {e}")
                logger.error(f"Problematic match data: {match}")
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
        logger.info("Final formatted response created successfully")
        return formatted_response

    except Exception as e:
        logger.error(f"Error in handle_search_dom: {e}")
        return {
            "isError": True,
            "content": [
                TextContent(
                    type="text",
                    text=f"Error processing search results: {str(e)}"
                )
            ]
        } 