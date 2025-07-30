# JSONPath-NZ (NextZen)

A comprehensive Python library for bidirectional conversion between JSON objects and JSONPath expressions, with advanced features for complex data manipulation, XML processing, JSON merging, and enhanced logging capabilities.

- `Author` : Yakub Mohammad (yakub@arusatech.com , arusatechnology@gmail.com) , Rishaad (rishaad@arusatech.com) | AR USA LLC

## Features

### Core JSONPath Operations
- **Bidirectional conversion** between JSON objects and JSONPath expressions
- **Advanced filter conditions** using `extend` parameter for intelligent array handling
- **Complex nested structures** support with proper data integrity
- **Array indexing and filtering** with conditional expressions
- **Error handling and validation** for robust JSONPath processing

### JSON Utilities
- **Pretty printing** with flexible formatting options (`jprint`)
- **JSON merging** with deep merge capabilities and list handling strategies
- **XML to JSON conversion** with namespace preservation options

### Enhanced Logging System
- **Multi-level logging** with console and file output
- **Automatic caller information** (file name and line number)
- **Selective file capture** for important messages
- **Detailed traceback logging** for exception handling
- **Dynamic configuration** for runtime log file management

## Installation

```bash
pip install jsonpath-nz
```

## API Reference

### Core Functions

#### `parse_jsonpath(manifest, extend=None)`

Convert JSONPath expressions to a dictionary structure with advanced filtering support.

**Parameters:**
- `manifest` (dict): Dictionary with JSONPath expressions as keys and target values
- `extend` (dict, optional): Configuration for advanced list merging behavior

**Returns:**
- dict: Processed dictionary structure or error dictionary

**Features:**
- Validates JSONPath syntax and bracket balancing
- Supports complex nested structures and arrays
- Handles filter conditions with extend parameter
- Provides detailed error reporting for invalid expressions

**Example:**
```python
from jsonpath_nz import parse_jsonpath, jprint

# JSONPath expressions with filter conditions
jsonpath_data = {
    "$.store.book[1].author": "Yakub Mohammad",
    "$.store.local": "False",
    "$.channel": "online",
    "$.loanApplication.borrower[?(@.firstName == 'John' && @.lastName == 'Doe')].contact": "9876543210",
    "$.loanApplication.borrower[?(@.firstName == 'John' && @.lastName == 'wright')].contact": "9876543211"
}

extend = {
    "borrower": ["firstName", "lastName"]
}

result = parse_jsonpath(jsonpath_data, extend=extend)
jprint(result)
```

**Output:**
```json
{
  "store": {
    "book": [
      {},
      {
        "author": "Yakub Mohammad"
      }
    ],
    "local": "False"
  },
  "channel": "online",
  "loanApplication": {
    "borrower": [
      {
        "firstName": "(John)",
        "lastName": "(Doe)",
        "contact": "9876543210"
      },
      {
        "firstName": "(John)",
        "lastName": "(wright)",
        "contact": "9876543211"
      }
    ]
  }
}
```

#### `parse_dict(data, parent_path="$", paths=None, extend=None)`

Convert a dictionary to JSONPath expressions with support for both array indices and filter conditions.

**Parameters:**
- `data` (dict): Input dictionary to convert to JSONPath expressions
- `parent_path` (str, optional): Base JSONPath prefix (defaults to "$")
- `paths` (dict, optional): Dictionary to accumulate results (created if None)
- `extend` (dict, optional): Configuration for filter-based array handling

**Returns:**
- dict: Dictionary mapping JSONPath expressions to their values

**JSONPath Expression Types:**
- Simple paths: `$.user.name` for nested values
- Array index paths: `$.items[0].price` for array elements
- Filter paths: `$.users[?(@.id == '123' && @.active == 'true')].email`

**Example:**
```python
from jsonpath_nz import parse_dict, jprint

# Complex nested dictionary
dict_data = {
    "store": {"book": [{"author": "Yakub Mohammad"}, {"category": "Fiction"}]},
    "channel": "online",
    "loanApplication": {
        'borrower': [
            {'firstName': 'John', 'lastName': 'Doe', 'contact': '9876543210'},
            {'firstName': 'John', 'lastName': 'wright', 'contact': '9876543211'}
        ]
    }
}

extend = {
    "borrower": ["firstName", "lastName"]
}

result = parse_dict(dict_data, extend=extend)
jprint(result)
```

**Output:**
```json
{
  "$.store.book[0].author": "Yakub Mohammad",
  "$.store.book[1].category": "Fiction",
  "$.channel": "online",
  "$.loanApplication.borrower[?(@.firstName == 'John' && @.lastName == 'Doe')].contact": "9876543210",
  "$.loanApplication.borrower[?(@.firstName == 'John' && @.lastName == 'wright')].contact": "9876543211"
}
```

#### `merge_json(dict1, dict2, extend=False)`

Merge two JSON files or dictionaries with support for nested structures and intelligent list handling.

**Parameters:**
- `dict1` (Union[Dict, str]): First dictionary or path to JSON file
- `dict2` (Union[Dict, str]): Second dictionary or path to JSON file (takes precedence)
- `extend` (bool, optional): Controls list merging behavior (defaults to False)

**Returns:**
- dict: New merged dictionary without modifying originals

**List Merging Modes:**
- `extend=False`: Element-wise merging with remaining elements appended
- `extend=True`: Key-based matching for dictionary items in lists

**Example:**
```python
from jsonpath_nz import merge_json, jprint

# Basic merging
dict1 = {
    "user": {"name": "John", "age": 25},
    "settings": {"theme": "dark"}
}

dict2 = {
    "user": {"email": "john@example.com", "age": 26},
    "settings": {"language": "en"}
}

result = merge_json(dict1, dict2)
jprint(result)
```

**Output:**
```json
{
  "user": {
    "name": "John",
    "age": 26,
    "email": "john@example.com"
  },
  "settings": {
    "theme": "dark",
    "language": "en"
  }
}
```

#### `xml_to_json(xml_data, namespace=True)`

Convert XML data to JSON format with comprehensive namespace handling and flexible input support.

**Parameters:**
- `xml_data` (str or file-like): XML content, file path, or file-like object
- `namespace` (bool, optional): Preserve namespaces with prefixes (defaults to True)

**Returns:**
- str: Pretty-printed JSON string with UTF-8 support

**Input Types Supported:**
- XML strings (content starting with '<?xml' or '<')
- File paths to XML files
- File-like objects with read() method

**Namespace Handling:**
- `namespace=True`: Preserves namespaces as prefixes (e.g., "ns0:elementName")
- `namespace=False`: Strips namespaces, keeping only local names

**Example:**
```python
from jsonpath_nz import xml_to_json

xml_string = '''<?xml version="1.0"?>
<catalog xmlns:lib="http://library.org">
    <lib:book id="1">
        <title>XML Guide</title>
        <author>John Doe</author>
        <price>29.99</price>
    </lib:book>
</catalog>'''

# With namespace preservation
result_with_ns = xml_to_json(xml_string, namespace=True)
print("With namespaces:")
print(result_with_ns)

# Without namespaces
result_without_ns = xml_to_json(xml_string, namespace=False)
print("\nWithout namespaces:")
print(result_without_ns)
```

### Utility Functions

#### `jprint(data, load=False, marshall=True, indent=2)`

Pretty-print data in JSON format with flexible input handling and formatting options.

**Parameters:**
- `data` (Any): Data to print (dict, list, string, or any object)
- `load` (bool, optional): Parse string input as JSON (defaults to False)
- `marshall` (bool, optional): Convert non-serializable objects to strings (defaults to True)
- `indent` (int, optional): JSON indentation spaces (defaults to 2)

**Features:**
- Handles various input types automatically
- Graceful fallback for serialization errors
- Custom object conversion with marshalling
- Consistent JSON formatting

**Example:**
```python
from jsonpath_nz import jprint
from datetime import datetime

# Pretty print with custom objects
data = {
    "timestamp": datetime.now(),
    "items": [1, 2, 3],
    "user": {"name": "John", "active": True}
}

jprint(data, indent=4)  # Custom indentation
```

### Enhanced Logging System

The library includes a sophisticated logging system with automatic caller information and selective file capture.

#### `LoggerConfig` Class

Enhanced logging configuration with file capture and caller information.

**Features:**
- Automatic file name and line number inclusion
- Conditional file capture with capture parameter
- Enhanced traceback logging
- Runtime configuration updates

#### Logging Methods

- `log.debug(msg, *args, **kwargs)` - Detailed debugging information
- `log.info(msg, *args, **kwargs)` - General program information
- `log.warning(msg, *args, **kwargs)` - Warning messages
- `log.error(msg, *args, **kwargs)` - Error messages
- `log.critical(msg, *args, **kwargs)` - Critical system errors
- `log.traceback(exc_info=None)` - Detailed exception logging
- `log.config(log_file_path=None)` - Runtime configuration

**Capture Options:**
- Keyword argument: `log.info("Message", capture=True)`
- Positional flag: `log.error("Error occurred", 1)`

**Example:**
```python
from jsonpath_nz import log

# Configure log file (optional)
log.config("application.log")

# Basic logging (console only)
log.info("Application started")
log.debug("Processing data")

# Logging with file capture
log.warning("Configuration issue detected", capture=True)
log.error("Database connection failed", 1)  # Using positional flag

# Exception handling with traceback
try:
    result = 1 / 0
except Exception as e:
    log.traceback(e)  # Automatically captures to file
    log.error("Division by zero error occurred", capture=True)
```

**Output Format:**
```
2025-01-05 10:30:45,123 - INFO     [main.py:15] Application started
2025-01-05 10:30:45,124 - DEBUG    [main.py:16] Processing data
2025-01-05 10:30:45,125 - WARNING  [main.py:19] Configuration issue detected
2025-01-05 10:30:45,126 - ERROR    [main.py:20] Database connection failed
2025-01-05 10:30:45,127 - ERROR    [main.py:26] ======= TRACEBACK =======
Traceback (most recent call last):
  File "main.py", line 23, in <module>
    result = 1 / 0
ZeroDivisionError: division by zero
```

## Advanced Features

### JSONPath Extend Filter Configuration

The extend parameter enables sophisticated filtering and merging strategies for array elements:

```python
extend_config = {
    "array_field_name": ["filter_field1", "filter_field2"],
    "users": ["id", "email"],
    "products": ["sku", "category"]
}
```

**Filter Behavior:**
- Fields listed in extend become filter conditions
- Remaining fields become target paths
- Multiple filter fields combined with AND logic
- Creates JSONPath expressions like: `$.users[?(@.id == 'value' && @.email == 'user@example.com')].name`

### Error Handling

All functions include comprehensive error handling:

- **parse_jsonpath**: Returns `{"error": "description"}` for invalid JSONPath expressions
- **parse_dict**: Graceful handling of mixed data types and invalid structures
- **merge_json**: File access and JSON parsing error handling
- **xml_to_json**: XML parsing and conversion error handling with detailed messages
- **Logging**: Built-in exception handling with fallback behavior

### Performance Considerations

- **Memory Usage**: Functions process data entirely in memory
- **Large Files**: Consider memory constraints for very large JSON/XML files
- **Namespace Processing**: XML namespace extraction may parse files twice
- **Deep Nesting**: Recursive processing handles deeply nested structures efficiently

## Best Practices

1. **JSONPath Validation**: Always check return values for error dictionaries
2. **Extend Configuration**: Use extend parameter for intelligent array handling
3. **Namespace Handling**: Choose appropriate namespace mode for XML conversion
4. **Logging Capture**: Use selective file capture for important messages only
5. **Error Handling**: Implement proper error checking in production code

## Testing

The library includes comprehensive test suites:

- `tests/test_parse_jsonpath.py` - JSONPath to dictionary conversion tests
- `tests/test_parse_dict.py` - Dictionary to JSONPath conversion tests
- `tests/test_merge_json.py` - JSON merging functionality tests
- `tests/test_xml_to_json.py` - XML to JSON conversion tests
- `tests/test_log.py` - Enhanced logging system tests
- `tests/test_jprint.py` - Pretty printing utility tests

## Contributing

Contributions are welcome! Please ensure:

1. All new features include comprehensive docstrings
2. Test coverage for new functionality
3. Examples in documentation
4. Error handling for edge cases

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact:
- Email: yakub@arusatech.com, arusatechnology@gmail.com
- Company: AR USA LLC

---

*JSONPath-NZ (NextZen) - Powerful JSON manipulation with intelligent path handling*










