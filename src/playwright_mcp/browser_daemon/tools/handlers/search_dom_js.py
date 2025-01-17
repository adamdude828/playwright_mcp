from mcp.types import TextContent
from .utils import send_to_manager, logger
import json


# JavaScript functions for DOM searching
JS_SEARCH_FUNCTIONS = """
function searchByText(text) {
    try {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        const matches = [];
        let node;
        
        while (node = walker.nextNode()) {
            if (node.textContent.includes(text)) {
                const element = node.parentElement;
                matches.push({
                    type: 'text',
                    tag: element.tagName.toLowerCase(),
                    path: getElementPath(element),
                    text: node.textContent.trim(),
                    attributes: getElementAttributes(element)
                });
            }
        }
        return { success: true, matches };
    } catch (e) {
        return { success: false, error: e.toString() };
    }
}

function searchByTag(tagName) {
    try {
        const elements = document.getElementsByTagName(tagName);
        const matches = Array.from(elements).map(element => ({
            type: 'tag',
            tag: element.tagName.toLowerCase(),
            path: getElementPath(element),
            text: element.textContent.trim(),
            attributes: getElementAttributes(element)
        }));
        return { success: true, matches };
    } catch (e) {
        return { success: false, error: e.toString() };
    }
}

function searchByAttribute(attrName, attrValue) {
    try {
        const matches = [];
        const elements = document.querySelectorAll(`[${attrName}="${attrValue}"]`);
        elements.forEach(element => {
            matches.push({
                type: 'attribute',
                tag: element.tagName.toLowerCase(),
                path: getElementPath(element),
                text: element.textContent.trim(),
                attributes: getElementAttributes(element)
            });
        });
        return { success: true, matches };
    } catch (e) {
        return { success: false, error: e.toString() };
    }
}

function searchByClass(className) {
    try {
        const elements = document.getElementsByClassName(className);
        const matches = Array.from(elements).map(element => ({
            type: 'class',
            tag: element.tagName.toLowerCase(),
            path: getElementPath(element),
            text: element.textContent.trim(),
            attributes: getElementAttributes(element)
        }));
        return { success: true, matches };
    } catch (e) {
        return { success: false, error: e.toString() };
    }
}

function searchById(id) {
    try {
        const element = document.getElementById(id);
        if (!element) return { success: true, matches: [] };
        
        return {
            success: true,
            matches: [{
                type: 'id',
                tag: element.tagName.toLowerCase(),
                path: getElementPath(element),
                text: element.textContent.trim(),
                attributes: getElementAttributes(element)
            }]
        };
    } catch (e) {
        return { success: false, error: e.toString() };
    }
}

function getElementPath(element) {
    if (!element) return '';
    if (element === document.body) return 'body';
    
    let path = '';
    while (element && element !== document.body) {
        let tag = element.tagName.toLowerCase();
        let siblings = element.parentNode ? Array.from(element.parentNode.children) : [];
        if (siblings.length > 1) {
            let index = siblings.indexOf(element) + 1;
            tag += `:nth-child(${index})`;
        }
        path = tag + (path ? ' > ' + path : '');
        element = element.parentNode;
    }
    return 'body > ' + path;
}

function getElementAttributes(element) {
    const attributes = {};
    for (const attr of element.attributes) {
        attributes[attr.name] = attr.value;
    }
    return attributes;
}
"""


async def handle_search_dom_js(arguments: dict) -> dict:
    """Handle search-dom-js tool."""
    logger.info("Handling search-dom-js request with args: %s", json.dumps(arguments))
    try:
        # First, inject the search functions if not already present
        page_id = arguments.get("page_id")
        if not page_id:
            return {
                "isError": True,
                "content": [TextContent(type="text", text="page_id is required")]
            }

        # Inject search functions
        inject_result = await send_to_manager("evaluate", {
            "page_id": page_id,
            "expression": JS_SEARCH_FUNCTIONS
        })

        if "error" in inject_result:
            error_msg = f"Failed to inject search functions: {inject_result['error']}"
            return {
                "isError": True,
                "content": [TextContent(type="text", text=error_msg)]
            }

        all_matches = []
        errors = []

        # Perform searches based on provided criteria
        if "text" in arguments:
            result = await send_to_manager("evaluate", {
                "page_id": page_id,
                "expression": f"searchByText('{arguments['text']}')"
            })
            if result.get("success"):
                all_matches.extend(result.get("matches", []))
            else:
                errors.append(f"Text search failed: {result.get('error')}")

        if "tag" in arguments:
            result = await send_to_manager("evaluate", {
                "page_id": page_id,
                "expression": f"searchByTag('{arguments['tag']}')"
            })
            if result.get("success"):
                all_matches.extend(result.get("matches", []))
            else:
                errors.append(f"Tag search failed: {result.get('error')}")

        if "class_name" in arguments:
            result = await send_to_manager("evaluate", {
                "page_id": page_id,
                "expression": f"searchByClass('{arguments['class_name']}')"
            })
            if result.get("success"):
                all_matches.extend(result.get("matches", []))
            else:
                errors.append(f"Class search failed: {result.get('error')}")

        if "id" in arguments:
            result = await send_to_manager("evaluate", {
                "page_id": page_id,
                "expression": f"searchById('{arguments['id']}')"
            })
            if result.get("success"):
                all_matches.extend(result.get("matches", []))
            else:
                errors.append(f"ID search failed: {result.get('error')}")

        if "attribute" in arguments:
            for attr_name, attr_value in arguments["attribute"].items():
                result = await send_to_manager("evaluate", {
                    "page_id": page_id,
                    "expression": f"searchByAttribute('{attr_name}', '{attr_value}')"
                })
                if result.get("success"):
                    all_matches.extend(result.get("matches", []))
                else:
                    errors.append(f"Attribute search failed: {result.get('error')}")

        # Format response
        if not all_matches and errors:
            return {
                "isError": True,
                "content": [TextContent(type="text", text="\n".join(errors))]
            }

        if not all_matches:
            return {
                "content": [TextContent(type="text", text="No matches found")]
            }

        # Format matches similar to search-dom
        formatted_matches = []
        for idx, match in enumerate(all_matches, 1):
            try:
                match_type = match.get("type", "unknown")
                path = match.get("path", "unknown")
                tag = match.get("tag", "unknown")
                text = match.get("text", "")
                attrs = match.get("attributes", {})
                
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

        summary = f"Found {len(all_matches)} matches in the DOM:"
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"{summary}\n\n" + "\n\n".join(formatted_matches)
                )
            ]
        }

    except Exception as e:
        logger.error("Error in handle_search_dom_js: %s", str(e))
        logger.error("Full traceback:", exc_info=True)
        return {
            "isError": True,
            "content": [
                TextContent(
                    type="text",
                    text=f"Error executing search-dom-js: {str(e)}"
                )
            ]
        } 