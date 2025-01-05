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
            return {
                type: element.tagName.toLowerCase(),
                classes: Array.from(element.classList),
                id: element.id || null,
                testId: element.getAttribute('data-testid') || element.getAttribute('data-test-id') || null,
                selector: getUniqueSelector(element),
                text: element.textContent.trim().substring(0, 100),
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