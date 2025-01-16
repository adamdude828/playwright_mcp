from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_find_similar_selectors(arguments: dict) -> dict:
    """Handle find-similar-selectors tool."""
    logger.info(f"Handling find-similar-selectors request with args: {arguments}")
    try:
        # Extract the required arguments
        base_selector = arguments.get("selector")
        session_id = arguments.get("session_id")
        page_id = arguments.get("page_id")
        
        if not all([base_selector, session_id, page_id]):
            return {
                "isError": True,
                "content": [
                    TextContent(
                        type="text",
                        text="selector, session_id, and page_id are required"
                    )
                ]
            }

        # Execute JavaScript to find similar elements
        script = """
        (baseSelector) => {
            const results = {
                similarElements: [],
                commonPatterns: [],
                hierarchyRelationships: []
            };
            
            try {
                // Find all elements matching the base selector
                const baseElements = Array.from(document.querySelectorAll(baseSelector));
                if (!baseElements.length) return { error: 'No elements found matching base selector' };
                
                // Helper to get all attributes of an element
                const getElementAttributes = (el) => {
                    const attrs = {};
                    for (const attr of el.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                };

                // Helper to get classes as a set
                const getClassSet = (el) => new Set(el.classList);

                // Helper to calculate similarity score between two elements
                const getSimilarityScore = (el1, el2) => {
                    let score = 0;
                    
                    // Same tag type
                    if (el1.tagName === el2.tagName) score += 1;
                    
                    // Class similarity
                    const classes1 = getClassSet(el1);
                    const classes2 = getClassSet(el2);
                    const commonClasses = new Set([...classes1].filter(x => classes2.has(x)));
                    if (commonClasses.size > 0) {
                        score += commonClasses.size / Math.max(classes1.size, classes2.size);
                    }
                    
                    // Attribute similarity
                    const attrs1 = getElementAttributes(el1);
                    const attrs2 = getElementAttributes(el2);
                    const commonAttrs = Object.keys(attrs1).filter(key => 
                        attrs2[key] === attrs1[key] && 
                        key !== 'id' && // Ignore unique identifiers
                        !key.startsWith('data-') // Ignore data attributes
                    );
                    if (commonAttrs.length > 0) {
                        score += commonAttrs.length / Math.max(Object.keys(attrs1).length, Object.keys(attrs2).length);
                    }
                    
                    // Similar structure
                    if (el1.children.length === el2.children.length) score += 0.5;
                    
                    return score;
                };
                
                // Find similar elements
                const baseElement = baseElements[0];
                const allElements = document.getElementsByTagName('*');
                const similarElements = new Set();
                
                for (const el of allElements) {
                    if (!baseElements.includes(el)) {
                        const score = getSimilarityScore(baseElement, el);
                        if (score >= 1.5) { // Threshold for similarity
                            similarElements.add(el);
                        }
                    }
                }
                
                // Analyze and collect results
                results.similarElements = Array.from(similarElements).map(el => ({
                    tagName: el.tagName.toLowerCase(),
                    attributes: getElementAttributes(el),
                    textContent: el.textContent.trim().substring(0, 100),
                    selector: cssPath(el),
                    similarityScore: getSimilarityScore(baseElement, el)
                }));
                
                // Sort by similarity score
                results.similarElements.sort((a, b) => b.similarityScore - a.similarityScore);
                
                // Find common patterns
                const baseAttrs = getElementAttributes(baseElement);
                results.commonPatterns = Object.entries(baseAttrs)
                    .filter(([key]) => key !== 'id' && !key.startsWith('data-'))
                    .map(([attr, value]) => ({
                        attribute: attr,
                        value: value,
                        count: document.querySelectorAll(`[${attr}="${value}"]`).length
                    }));
                
                // Analyze hierarchy relationships
                const baseParent = baseElement.parentElement;
                if (baseParent) {
                    results.hierarchyRelationships.push({
                        type: 'parent',
                        selector: cssPath(baseParent),
                        childCount: baseParent.children.length,
                        similarChildren: Array.from(baseParent.children)
                            .filter(el => el !== baseElement && getSimilarityScore(baseElement, el) >= 1.5)
                            .length
                    });
                }
                
                if (baseElement.children.length) {
                    const childTags = Array.from(baseElement.children).map(el => el.tagName.toLowerCase());
                    results.hierarchyRelationships.push({
                        type: 'children',
                        count: baseElement.children.length,
                        commonTags: Array.from(new Set(childTags)),
                        description: childTags.join(', ')
                    });
                }
                
                return results;
            } catch (error) {
                return { error: error.toString() };
            }
        }
        
        // Helper function to generate unique CSS selector for an element
        function cssPath(el) {
            if (!(el instanceof Element)) return;
            const path = [];
            while (el.nodeType === Node.ELEMENT_NODE) {
                let selector = el.nodeName.toLowerCase();
                if (el.id) {
                    selector += '#' + el.id;
                    path.unshift(selector);
                    break;
                } else {
                    let sib = el, nth = 1;
                    while (sib.previousElementSibling) {
                        sib = sib.previousElementSibling;
                        if (sib.nodeName.toLowerCase() === selector) nth++;
                    }
                    if (nth !== 1) selector += ":nth-of-type("+nth+")";
                }
                path.unshift(selector);
                el = el.parentNode;
            }
            return path.join(' > ');
        }
        """

        response = await send_to_manager("find-similar-selectors", {
            "session_id": session_id,
            "page_id": page_id,
            "selector": base_selector,
            "script": script
        })

        if "error" in response:
            return {
                "isError": True,
                "content": [
                    TextContent(
                        type="text",
                        text=response["error"]
                    )
                ]
            }

        # Format the results
        result = response.get("result", {})
        
        # Build a formatted text response
        output = ["Similar Elements Analysis:"]
        
        # Add similar elements section
        similar_elements = result.get("similarElements", [])
        output.append(f"\n1. Found {len(similar_elements)} similar elements:")
        for elem in similar_elements:
            score = elem.get('similarityScore', 0)
            output.append(f"   - {elem['tagName']} (similarity: {score:.2f})")
            output.append(f"     Selector: {elem['selector']}")
            if elem['attributes']:
                output.append("     Attributes:")
                for name, value in elem['attributes'].items():
                    if name != 'id' and not name.startswith('data-'):  # Skip noisy attributes
                        output.append(f"       {name}: {value}")
            if elem['textContent']:
                output.append(f"     Text: {elem['textContent']}")
                
        # Add common patterns section
        patterns = result.get("commonPatterns", [])
        output.append("\n2. Common Patterns:")
        for pattern in patterns:
            output.append(
                f"   - {pattern['attribute']}=\"{pattern['value']}\" "
                f"(found in {pattern['count']} elements)"
            )
            
        # Add hierarchy relationships section
        relationships = result.get("hierarchyRelationships", [])
        output.append("\n3. Hierarchy Relationships:")
        for rel in relationships:
            if rel['type'] == 'parent':
                output.append(
                    f"   - Parent: {rel['selector']}\n"
                    f"     Contains {rel['childCount']} children "
                    f"({rel.get('similarChildren', 0)} similar to target)"
                )
            elif rel['type'] == 'children':
                output.append(
                    f"   - Contains {rel['count']} children\n"
                    f"     Child elements: {rel.get('description', '')}"
                )

        return {
            "content": [
                TextContent(
                    type="text",
                    text="\n".join(output)
                )
            ]
        }

    except Exception as e:
        logger.error(f"Error in handle_find_similar_selectors: {e}")
        logger.error(traceback.format_exc())
        return {
            "isError": True,
            "content": [
                TextContent(
                    type="text",
                    text=str(e)
                )
            ]
        } 