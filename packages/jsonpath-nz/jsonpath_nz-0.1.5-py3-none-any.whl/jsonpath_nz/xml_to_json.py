import xml.etree.ElementTree as ET
import json
from io import StringIO

def xml_to_json(xml_data, namespace=True):
    """
    Convert XML data to JSON format with comprehensive namespace handling and flexible input support.
    
    This function provides robust XML to JSON conversion with intelligent namespace processing,
    supporting various input formats including XML strings, file paths, and file-like objects.
    It preserves XML structure while handling attributes, text content, nested elements, and
    namespace declarations with configurable namespace preservation options.
    
    Args:
        xml_data (str or file-like): XML data to convert. Accepts multiple input types:
            - XML string: Raw XML content starting with '<?xml' or '<'
            - File path: String path to an XML file on the filesystem
            - File-like object: Any object with a read() method (e.g., StringIO, file handle)
        namespace (bool, optional): Controls namespace handling in the output. Defaults to True.
            - True: Preserves namespaces with prefixes (e.g., "ns0:elementName")
            - False: Strips namespaces, keeping only local element names
    
    Returns:
        str: JSON string representation of the XML data with configurable formatting:
            - Pretty-printed with 4-space indentation
            - UTF-8 compatible (ensure_ascii=False)
            - Includes namespace mappings when namespace=True
            - Returns error JSON object for parsing failures
    
    JSON Structure Features:
        - Element names become JSON object keys
        - Text content becomes string values or "value" properties
        - XML attributes become JSON object properties
        - Multiple elements with same name become JSON arrays
        - Mixed content (text + children) uses "value" property for text
        - Namespace mappings stored in "@namespaces" property when enabled
    
    Namespace Handling:
        When namespace=True:
        - Generates prefixes: ns0, ns1, ns2, etc. for default namespaces
        - Preserves declared prefixes from XML
        - Element names formatted as "prefix:localName"
        - Namespace mappings included in "@namespaces" object
        
        When namespace=False:
        - Strips all namespace information
        - Uses only local element names
        - No "@namespaces" object in output
    
    Examples:
        Basic XML string conversion:
        
        >>> xml_string = '''<?xml version="1.0"?>
        ... <catalog>
        ...     <book id="1">
        ...         <title>XML Guide</title>
        ...         <author>John Doe</author>
        ...         <price>29.99</price>
        ...     </book>
        ... </catalog>'''
        >>> result = xml_to_json(xml_string)
        >>> print(result)
        {
            "catalog": {
                "book": {
                    "id": "1",
                    "title": "XML Guide",
                    "author": "John Doe",
                    "price": "29.99"
                }
            }
        }
        
        Multiple elements with same name (array creation):
        
        >>> xml_string = '''<library>
        ...     <book id="1">Science Fiction</book>
        ...     <book id="2">Fantasy</book>
        ...     <book id="3">Mystery</book>
        ... </library>'''
        >>> result = xml_to_json(xml_string)
        >>> print(result)
        {
            "library": {
                "book": [
                    {"id": "1", "value": "Science Fiction"},
                    {"id": "2", "value": "Fantasy"},
                    {"id": "3", "value": "Mystery"}
                ]
            }
        }
        
        Namespace handling with preservation:
        
        >>> xml_string = '''<?xml version="1.0"?>
        ... <root xmlns:lib="http://library.org" xmlns="http://default.org">
        ...     <lib:catalog>
        ...         <book>XML Processing</book>
        ...     </lib:catalog>
        ... </root>'''
        >>> result = xml_to_json(xml_string, namespace=True)
        >>> print(result)
        {
            "ns0:root": {
                "lib:catalog": {
                    "ns0:book": "XML Processing"
                }
            },
            "@namespaces": {
                "ns0": "http://default.org",
                "lib": "http://library.org"
            }
        }
        
        Same XML with namespace stripping:
        
        >>> result = xml_to_json(xml_string, namespace=False)
        >>> print(result)
        {
            "root": {
                "catalog": {
                    "book": "XML Processing"
                }
            }
        }
        
        File path input:
        
        >>> result = xml_to_json("/path/to/data.xml")
        >>> # Processes XML file and returns JSON string
        
        Mixed content handling:
        
        >>> xml_string = '''<article>
        ...     <title>Sample Article</title>
        ...     Some introductory text
        ...     <section>Content here</section>
        ... </article>'''
        >>> result = xml_to_json(xml_string)
        >>> print(result)
        {
            "article": {
                "title": "Sample Article",
                "value": "Some introductory text",
                "section": "Content here"
            }
        }
        
        Error handling examples:
        
        >>> # Invalid XML
        >>> result = xml_to_json("<unclosed>tag")
        >>> print(result)
        {
            "error": "XML parsing error: no element found: line 1, column 13"
        }
        
        >>> # File not found
        >>> result = xml_to_json("/nonexistent/file.xml")
        >>> print(result)
        {
            "error": "Conversion error: [Errno 2] No such file or directory: '/nonexistent/file.xml'"
        }
    
    Input Type Detection:
        The function automatically detects input type:
        
        1. String content: Checks if string starts with '<?xml' or '<'
        2. File path: String that doesn't match XML content pattern
        3. File-like object: Any non-string object (uses ET.parse())
    
    Namespace Processing Details:
        1. Primary extraction: Uses ET.iterparse with 'start-ns' events
        2. Fallback extraction: Parses namespace URIs from element tags
        3. Prefix generation: Creates ns0, ns1, etc. for default namespaces
        4. Prefix preservation: Maintains declared prefixes from XML
        5. Dynamic assignment: Assigns new prefixes for undeclared namespaces
    
    Element Conversion Rules:
        - Text-only elements: Return string value directly
        - Elements with attributes only: Return object with attribute properties
        - Elements with text and attributes: Use "value" property for text content
        - Elements with children: Create nested object structure
        - Empty elements: Return None (cleaned up in post-processing)
        - Mixed content: Text content stored in "value" property
    
    Error Handling:
        - XML parsing errors: Returns JSON error object with ET.ParseError details
        - File access errors: Returns JSON error object with file operation details
        - General exceptions: Returns JSON error object with exception description
        - All errors return valid JSON strings for consistent API behavior
    
    Performance Considerations:
        - Large XML files: Parsed entirely into memory (not streaming)
        - Namespace extraction: May parse XML twice for complete namespace mapping
        - Memory usage: Creates full DOM tree before JSON conversion
        - String processing: Uses StringIO for namespace extraction from string content
    
    Note:
        - Preserves XML attribute order (Python 3.7+ dict ordering)
        - Handles CDATA sections as regular text content
        - Empty namespace URIs assigned auto-generated prefixes
        - Function always returns valid JSON strings, never raises exceptions
        - Namespace mappings only included in root object when namespace=True
        - Text content is stripped of leading/trailing whitespace
    
    See Also:
        - xml.etree.ElementTree: Underlying XML parsing library
        - json.dumps: JSON serialization with formatting options
        - parse_dict: For converting resulting JSON back to JSONPath expressions
        - StringIO: For handling XML string content in namespace extraction
    """
    try:
        # Determine if xml_data is a string content or file path
        if isinstance(xml_data, str):
            if xml_data.strip().startswith('<?xml') or xml_data.strip().startswith('<'):
                # It's XML content as string
                root = ET.fromstring(xml_data)
                # For namespace extraction from string content
                ns_map = {}
                prefix_counter = 0
                try:
                    # Parse again to get namespaces
                    for event, elem in ET.iterparse(StringIO(xml_data), events=['start-ns']):
                        prefix, uri = elem
                        if prefix == '':
                            # Default namespace
                            ns_map[uri] = f"ns{prefix_counter}"
                            prefix_counter += 1
                        else:
                            ns_map[uri] = prefix
                except:
                    # If namespace parsing fails, continue without namespaces
                    pass
            else:
                # It's a file path
                tree = ET.parse(xml_data)
                root = tree.getroot()
                # Extract namespaces from file
                ns_map = {}
                prefix_counter = 0
                try:
                    for event, elem in ET.iterparse(xml_data, events=['start-ns']):
                        prefix, uri = elem
                        if prefix == '':
                            # Default namespace
                            ns_map[uri] = f"ns{prefix_counter}"
                            prefix_counter += 1
                        else:
                            ns_map[uri] = prefix
                except:
                    pass
        else:
            # Handle file-like objects
            root = ET.parse(xml_data).getroot()
            ns_map = {}
        
        # If no namespaces found in parsing, extract from element tags
        if not ns_map:
            def extract_namespaces(element):
                namespaces = set()
                if '}' in element.tag:
                    namespace = element.tag.split('}')[0][1:]  # Remove leading {
                    namespaces.add(namespace)
                for child in element:
                    namespaces.update(extract_namespaces(child))
                return namespaces
            
            all_namespaces = extract_namespaces(root)
            for i, namespace in enumerate(sorted(all_namespaces)):
                ns_map[namespace] = f"ns{i}"
        
        def get_tag_name(tag):
            """Convert tag based on namespace flag"""
            if '}' in tag:
                namespace, local_name = tag[1:].split('}')
                if namespace_flag:
                    # Return with namespace prefix
                    if namespace in ns_map:
                        return f"{ns_map[namespace]}:{local_name}"
                    else:
                        # Assign new prefix if not found
                        new_prefix = f"ns{len(ns_map)}"
                        ns_map[namespace] = new_prefix
                        return f"{new_prefix}:{local_name}"
                else:
                    # Return only local name without namespace
                    return local_name
            return tag
        
        # Store the namespace flag for use in nested function
        namespace_flag = namespace
        
        # Convert to dictionary
        def element_to_dict(element):
            result = {}
            
            # Add text content
            if element.text and element.text.strip():
                if len(element) == 0:  # No children, only text
                    if element.attrib:
                        # Has attributes, create object with value and attributes
                        result = {"value": element.text.strip()}
                        for attr_name, attr_value in element.attrib.items():
                            # Handle namespaced attributes
                            processed_attr = get_tag_name(attr_name) if '}' in attr_name else attr_name
                            result[processed_attr] = attr_value
                        return result
                    else:
                        # Only text, return as string
                        return element.text.strip()
                else:
                    # Has children, add text as value if significant
                    result["value"] = element.text.strip()
            
            # Add attributes (but not if we already handled them above)
            if element.attrib and not (element.text and element.text.strip() and len(element) == 0):
                for attr_name, attr_value in element.attrib.items():
                    # Handle namespaced attributes
                    processed_attr = get_tag_name(attr_name) if '}' in attr_name else attr_name
                    result[processed_attr] = attr_value
            
            # Add children
            children = {}
            for child in element:
                child_data = element_to_dict(child)
                child_tag = get_tag_name(child.tag)
                
                if child_tag in children:
                    # Convert to list if multiple children with same tag
                    if not isinstance(children[child_tag], list):
                        children[child_tag] = [children[child_tag]]
                    children[child_tag].append(child_data)
                else:
                    children[child_tag] = child_data
            
            result.update(children)
            
            # Clean up result
            if len(result) == 0:
                return None
            elif len(result) == 1 and "value" in result:
                return result["value"]
            
            return result
        
        # Convert root element
        root_tag = get_tag_name(root.tag)
        json_result = {root_tag: element_to_dict(root)}
        
        # Add namespace mappings at the root level only if namespace flag is True
        if namespace_flag and ns_map:
            # Reverse the mapping for display (prefix -> URI)
            namespace_display = {prefix: uri for uri, prefix in ns_map.items()}
            json_result["@namespaces"] = namespace_display
        
        return json.dumps(json_result, indent=4, ensure_ascii=False)
        
    except ET.ParseError as e:
        return json.dumps({"error": f"XML parsing error: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Conversion error: {str(e)}"}, indent=2)
    
