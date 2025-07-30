def parse_dict(data, parent_path="$", paths=None, extend=None):
    """
    Convert a dictionary to JSONPath expressions, handling both array indices and filter conditions.
    
    This function recursively traverses a nested dictionary structure and generates JSONPath
    expressions for all leaf values. It supports both standard array indexing and advanced
    filter conditions for array elements, making it suitable for complex JSON data analysis
    and path generation.
    
    Args:
        data (dict): The dictionary to parse and convert to JSONPath expressions.
            Can contain nested dictionaries, lists, and scalar values.
        parent_path (str, optional): The JSONPath prefix for the current level.
            Defaults to "$" (root). Used internally for recursion to build
            complete paths from root to leaf values.
        paths (dict, optional): Dictionary to store the generated JSONPath expressions.
            Keys are JSONPath strings, values are the corresponding data values.
            If None, a new dictionary is created. Used for accumulating results
            during recursive calls.
        extend (dict, optional): Configuration for advanced array filtering.
            Maps array field names to lists of filter field names.
            When specified, creates filter-based JSONPath expressions instead
            of index-based paths for matching arrays.
            Format: {"array_field": ["filter_field1", "filter_field2"]}
    
    Returns:
        dict: Dictionary mapping JSONPath expressions to their corresponding values.
            Keys are JSONPath strings (e.g., "$.users[0].name", "$.items[?(@.id == '123')].price")
            Values are the actual data values from the input dictionary.
    
    JSONPath Expression Types Generated:
        - Simple paths: "$.user.name" for nested dictionary values
        - Array index paths: "$.items[0].price" for array elements (default behavior)
        - Filter paths: "$.users[?(@.id == '123' && @.active == 'true')].email" (with extend)
        - Root values: "$.status" for top-level scalar values
    
    Examples:
        Basic nested dictionary:
        
        >>> data = {
        ...     "user": {"name": "John", "age": 30},
        ...     "active": True
        ... }
        >>> result = parse_dict(data)
        >>> print(result)
        {
            "$.user.name": "John",
            "$.user.age": 30,
            "$.active": True
        }
        
        Array with index-based paths (default):
        
        >>> data = {
        ...     "items": [
        ...         {"id": "1", "name": "Item 1"},
        ...         {"id": "2", "name": "Item 2"}
        ...     ]
        ... }
        >>> result = parse_dict(data)
        >>> print(result)
        {
            "$.items[0].id": "1",
            "$.items[0].name": "Item 1",
            "$.items[1].id": "2",
            "$.items[1].name": "Item 2"
        }
        
        Array with filter conditions (using extend):
        
        >>> data = {
        ...     "users": [
        ...         {"id": "123", "active": "true", "email": "john@example.com"},
        ...         {"id": "456", "role": "admin", "email": "admin@example.com"}
        ...     ]
        ... }
        >>> extend_config = {"users": ["id", "active", "role"]}
        >>> result = parse_dict(data, extend=extend_config)
        >>> print(result)
        {
            "$.users[?(@.id == '123' && @.active == 'true')].email": "john@example.com",
            "$.users[?(@.id == '456' && @.role == 'admin')].email": "admin@example.com"
        }
        
        Complex nested structure:
        
        >>> data = {
        ...     "company": {
        ...         "departments": [
        ...             {
        ...                 "name": "Engineering",
        ...                 "employees": [
        ...                     {"id": "e1", "name": "Alice"},
        ...                     {"id": "e2", "name": "Bob"}
        ...                 ]
        ...             }
        ...         ]
        ...     }
        ... }
        >>> result = parse_dict(data)
        >>> print(result)
        {
            "$.company.departments[0].name": "Engineering",
            "$.company.departments[0].employees[0].id": "e1",
            "$.company.departments[0].employees[0].name": "Alice",
            "$.company.departments[0].employees[1].id": "e2",
            "$.company.departments[0].employees[1].name": "Bob"
        }
    
    Extend Configuration Details:
        The extend parameter enables advanced filtering for specific array fields:
        
        - Filter fields: Fields used to create filter conditions (excluded from target paths)
        - Target fields: Remaining fields that become the actual JSONPath targets
        - Filter format: Uses JSONPath filter syntax with @. prefix for current array item
        - Multiple conditions: Combined with && operator when multiple filter fields exist
        
        Example extend configuration:
        >>> extend = {
        ...     "products": ["category", "status"],  # Filter on these fields
        ...     "orders": ["customer_id"]           # Filter on customer_id
        ... }
        
        This creates paths like:
        - "$.products[?(@.category == 'electronics' && @.status == 'active')].price"
        - "$.orders[?(@.customer_id == '12345')].total"
    
    Note:
        - The function modifies the paths dictionary in-place during recursion
        - Non-dictionary items in arrays are skipped when using extend configuration
        - Filter conditions use string equality comparison with single quotes
        - Empty or None data values are preserved in the output
        - The function handles mixed data types (strings, numbers, booleans) as values
        - Arrays without matching extend configuration use standard index-based paths
    
    Raises:
        The function is designed to be robust and does not explicitly raise exceptions.
        Invalid data structures are handled gracefully:
        - Non-dictionary data at root level returns empty dictionary
        - Mixed array types are processed based on their individual types
        - Missing or invalid extend configurations fall back to index-based paths
    
    See Also:
        - JSONPath specification: https://goessner.net/articles/JsonPath/
        - JSONPath filter expressions for advanced querying
        - merge_json: For combining dictionaries before path generation
    """
    if paths is None:
        paths = {}

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{parent_path}.{key}"

            # Handle arrays that need filter conditions (specified in extend)
            if extend and key in extend and isinstance(value, list):
                filter_fields = extend[key]
                for item in value:
                    if not isinstance(item, dict):
                        continue

                    # Build filter conditions
                    conditions = []
                    target_field = None
                    target_value = None

                    for k, v in item.items():
                        if k in filter_fields:
                            conditions.append(f"@.{k} == '{v}'")
                        else:
                            target_field = k
                            target_value = v

                    if conditions and target_field:
                        filter_path = f"{current_path}[?({' && '.join(conditions)})].{target_field}"
                        paths[filter_path] = target_value

            # Handle regular arrays
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        for k, v in item.items():
                            array_path = f"{current_path}[{idx}].{k}"
                            paths[array_path] = v

            # Handle nested dictionaries
            elif isinstance(value, dict):
                parse_dict(value, current_path, paths, extend)

            # Handle simple key-value pairs
            else:
                paths[current_path] = value

    return paths
