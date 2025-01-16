from typing import Dict, Any
from bs4 import BeautifulSoup
import re
from ..core.logging import setup_logging
from ..core.session import session_manager

logger = setup_logging("search_dom_handler")


async def handle_search_dom(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search the entire DOM for elements matching the search text in ids, classes, or attributes
    """
    try:
        page_id = args.get("page_id")
        search_text = args.get("search_text")
        
        if not page_id:
            return {"error": "No page_id provided"}
            
        if not search_text:
            return {"error": "No search text provided"}
            
        # Get the page from the session manager singleton
        page = session_manager.get_page(page_id)
        if not page:
            return {"error": f"No page found with ID: {page_id}"}
            
        # Get full page content
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        matches = []
        
        # Search by ID
        for elem in soup.find_all(id=re.compile(search_text, re.IGNORECASE)):
            matches.append({
                "type": "id",
                "tag": elem.name,
                "id": elem.get('id'),
                "classes": elem.get('class', []),
                "text": elem.text[:100] if elem.text else "",
                "html": str(elem)[:200]
            })
            
        # Search by class
        for elem in soup.find_all(class_=re.compile(search_text, re.IGNORECASE)):
            matches.append({
                "type": "class",
                "tag": elem.name,
                "id": elem.get('id'),
                "classes": elem.get('class', []),
                "text": elem.text[:100] if elem.text else "",
                "html": str(elem)[:200]
            })
            
        # Search other attributes
        for elem in soup.find_all():
            for attr, value in elem.attrs.items():
                if attr not in ['id', 'class']:
                    if isinstance(value, str) and re.search(search_text, value, re.IGNORECASE):
                        matches.append({
                            "type": "attribute",
                            "attribute": attr,
                            "tag": elem.name,
                            "id": elem.get('id'),
                            "classes": elem.get('class', []),
                            "text": elem.text[:100] if elem.text else "",
                            "html": str(elem)[:200]
                        })
        
        return {
            "matches": matches,
            "total": len(matches)
        }
        
    except Exception as e:
        logger.error(f"Error searching DOM: {e}")
        return {"error": str(e)} 