from typing import Dict


async def analyze_page_elements(page) -> Dict:
    """
    Analyzes a page and returns information about interactive elements including anchors, buttons, and form elements.
    Returns a map containing element details including type, classes, ids, test ids, and unique selectors.
    """
    script = """
    () => {
        function getUniqueSelector(element) {
            // Try id first
            if (element.id) {
                return `#${element.id}`;
            }
            
            // Build selector with parent context
            let parts = [];
            let current = element;
            for (let i = 0; i < 3; i++) {
                if (!current || current === document.body) break;
                
                let part = current.tagName.toLowerCase();
                if (current.className) {
                    const classes = Array.from(current.classList).join('.');
                    if (classes) {
                        part += '.' + classes;
                    }
                }
                parts.unshift(part);
                current = current.parentElement;
            }
            return parts.join(' > ');
        }

        function getElementInfo(element) {
            // Get text content and handle null case
            let text = element.textContent || '';
            
            // Basic cleanup: collapse whitespace and trim
            text = text.replace(/[\\s\\n\\r\\t]+/g, ' ').trim();
            
            // Truncate to prevent massive strings
            text = text.substring(0, 50);
            
            // Properly escape the string for JSON
            text = JSON.stringify(text).slice(1, -1);  // Remove the outer quotes that stringify adds
            
            return {
                type: element.tagName.toLowerCase(),
                classes: Array.from(element.classList),
                id: element.id || null,
                testId: element.getAttribute('data-testid') || element.getAttribute('data-test-id') || null,
                selector: getUniqueSelector(element),
                text: text || null,
                name: element.getAttribute('name') || null,
                value: element.getAttribute('value') || null,
                href: element.tagName.toLowerCase() === 'a' ? element.href : null
            };
        }

        const elements = {
            anchors: Array.from(document.querySelectorAll('a')).map(getElementInfo),
            buttons: Array.from(document.querySelectorAll(
                'button, input[type="button"], input[type="submit"]'
            )).map(getElementInfo),
            inputs: Array.from(document.querySelectorAll(
                'input:not([type="button"]):not([type="submit"]), textarea, select'
            )).map(getElementInfo)
        };

        return elements;
    }
    """
    
    return await page.evaluate(script)


async def get_page_elements_map(page) -> Dict:
    """
    High-level function to get a structured map of all interactive elements on the page.
    """
    elements = await analyze_page_elements(page)
    
    # Format the output in a more structured way
    result = {
        "interactive_elements": {
            "anchors": elements["anchors"],
            "buttons": elements["buttons"],
            "form_elements": elements["inputs"]
        },
        "summary": {
            "total_anchors": len(elements["anchors"]),
            "total_buttons": len(elements["buttons"]),
            "total_form_elements": len(elements["inputs"])
        }
    }
    
    return result 


async def explore_dom(page, selector: str = "body") -> Dict:
    """
    Explore immediate children of a DOM element.
    Returns basic information about each child node.
    """
    script = """
    (selector) => {
        const root = document.querySelector(selector);
        if (!root) return { error: 'Element not found' };
        
        function getNodeInfo(node) {
            // Get basic node information
            const info = {
                tag: node.tagName ? node.tagName.toLowerCase() : 'text',
                childCount: node.children ? node.children.length : 0
            };
            
            // Add classes if present
            if (node.classList && node.classList.length) {
                info.classes = Array.from(node.classList);
            }
            
            // Add id if present
            if (node.id) {
                info.id = node.id;
            }
            
            // Add text content for text nodes or elements with direct text
            if (node.nodeType === 3) {  // Text node
                info.text = node.textContent.trim();
            } else if (node.childNodes.length === 1 && node.childNodes[0].nodeType === 3) {
                info.text = node.textContent.trim();
            }
            
            return info;
        }
        
        // Get immediate children
        const children = Array.from(root.childNodes)
            .filter(node => 
                node.nodeType === 1 ||  // Element nodes
                (node.nodeType === 3 && node.textContent.trim())  // Non-empty text nodes
            )
            .map(getNodeInfo);
            
        return { children };
    }
    """
    
    return await page.evaluate(script, selector) 