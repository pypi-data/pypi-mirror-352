import json
def jprint(data, load=False, marshall=True, indent=2):
    """
    Pretty-print data in JSON format with flexible input handling and formatting options.
    
    This function provides a convenient way to print data structures in a readable JSON format.
    It can handle various input types including dictionaries, lists, strings, and custom objects,
    with options for JSON parsing, data marshalling, and output formatting.
    
    Args:
        data (Any): The data to print. Can be:
            - Dictionary or list: Will be directly formatted as JSON
            - String: If load=True, treated as JSON string to parse; otherwise printed as-is
            - Any other object: Will be converted to string if marshall=True
        load (bool, optional): Whether to treat string input as JSON data to parse.
            Defaults to False.
            - If True: String data is parsed as JSON before formatting
            - If False: String data is treated as a regular value
        marshall (bool, optional): Whether to convert non-JSON-serializable objects to strings.
            Defaults to True.
            - If True: Custom objects are recursively converted to strings
            - If False: Data is used as-is (may cause JSON serialization errors)
        indent (int, optional): Number of spaces for JSON indentation. Defaults to 2.
            Controls the pretty-printing format of the JSON output.
    
    Returns:
        None: This function prints to stdout and does not return a value.
    
    Examples:
        Basic dictionary printing:
        
        >>> data = {"name": "John", "age": 30, "city": "New York"}
        >>> jprint(data)
        {
          "name": "John",
          "age": 30,
          "city": "New York"
        }
        
        Printing with custom indentation:
        
        >>> jprint(data, indent=4)
        {
            "name": "John",
            "age": 30,
            "city": "New York"
        }
        
        Loading and formatting JSON string:
        
        >>> json_string = '{"status": "success", "data": [1, 2, 3]}'
        >>> jprint(json_string, load=True)
        {
          "status": "success",
          "data": [
            1,
            2,
            3
          ]
        }
        
        Handling custom objects with marshalling:
        
        >>> from datetime import datetime
        >>> data = {"timestamp": datetime.now(), "items": [1, 2, 3]}
        >>> jprint(data, marshall=True)
        {
          "timestamp": "2023-12-07 10:30:45.123456",
          "items": [
            1,
            2,
            3
          ]
        }
        
        Disabling marshalling (may cause errors with non-serializable objects):
        
        >>> jprint(data, marshall=False)  # May raise TypeError for datetime object
        
    Note:
        - If JSON serialization fails (e.g., due to non-serializable objects when marshall=False),
          the function will fall back to printing the raw data without formatting.
        - The marshalling process recursively converts custom objects to strings while preserving
          the structure of dictionaries and lists.
        - When load=True, invalid JSON strings will cause the function to fall back to printing
          the original string without parsing.
        - The function uses json.dumps() for formatting, which provides consistent JSON output.
    
    Raises:
        No exceptions are explicitly raised. The function includes error handling that falls
        back to printing raw data if JSON operations fail.
    
    See Also:
        - json.dumps: For direct JSON serialization
        - pprint.pprint: For general pretty-printing of Python objects
        - json.loads: For parsing JSON strings
    """
    def _stringify_val(data):
        if isinstance(data, dict):
            return {k: _stringify_val(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [_stringify_val(v) for v in data]
        elif isinstance(data, (str, int, float)):
            return data
        return str(data)

    _data = _stringify_val(data) if marshall else data
    try:
        _d = (
            json.dumps(json.loads(_data), indent=indent) if load else
            json.dumps(_data, indent=indent)
        )
    except:
        _d = _data

    print(_d)

