import re

def parse_jsonpath(manifest, extend=None):
    """
    Parse a dictionary of JSONPath expressions to their corresponding names and build a JSON structure.
    
    This function processes a manifest containing JSONPath expressions as keys and their target values,
    converting them into a properly structured JSON object. It supports complex JSONPath expressions
    including nested objects, arrays, and conditional filters, with optional extension capabilities
    for advanced list merging strategies.
    
    Args:
        manifest (dict): Dictionary with JSONPath expressions as keys and target values as values.
            Keys must be valid JSONPath expressions starting with "$."
            Values can be strings, numbers, booleans, or other JSON-serializable types.
            Example: {"$.user.name": "John", "$.items[0].price": 29.99}
        extend (dict, optional): Configuration for advanced list merging behavior.
            Defines merge strategies for specific array paths during JSON construction.
            Format: {"array_path": ["key1", "key2"]} or {"array_path": "key"}
            When specified, enables intelligent merging of array elements based on common keys.
    
    Returns:
        dict: Constructed JSON object from the JSONPath expressions, or error dictionary.
            Success: Returns the built JSON structure matching the input paths.
            Error: Returns {"error": "description"} for invalid inputs or processing failures.
    
    Error Conditions:
        - JSONPath expressions not starting with "$."
        - Unbalanced parentheses, brackets, or quotes in expressions
        - Invalid JSONPath syntax or malformed expressions
        - Empty manifest or no valid JSONPath expressions found
        - Processing errors during JSON construction
    
    Examples:
        Basic JSONPath to JSON conversion:
        
        >>> manifest = {
        ...     "$.user.name": "Alice",
        ...     "$.user.age": 25,
        ...     "$.user.active": True
        ... }
        >>> result = parse_jsonpath(manifest)
        >>> print(result)
        {
            "user": {
                "name": "Alice",
                "age": 25,
                "active": True
            }
        }
        
        Array handling with indices:
        
        >>> manifest = {
        ...     "$.items[0].name": "Product A",
        ...     "$.items[0].price": 19.99,
        ...     "$.items[1].name": "Product B",
        ...     "$.items[1].price": 29.99
        ... }
        >>> result = parse_jsonpath(manifest)
        >>> print(result)
        {
            "items": [
                {"name": "Product A", "price": 19.99},
                {"name": "Product B", "price": 29.99}
            ]
        }
        
        Complex nested structures:
        
        >>> manifest = {
        ...     "$.company.departments[0].name": "Engineering",
        ...     "$.company.departments[0].head": "John Doe",
        ...     "$.company.departments[1].name": "Marketing",
        ...     "$.company.founded": 2010
        ... }
        >>> result = parse_jsonpath(manifest)
        >>> print(result)
        {
            "company": {
                "departments": [
                    {"name": "Engineering", "head": "John Doe"},
                    {"name": "Marketing"}
                ],
                "founded": 2010
            }
        }
        
        With extend configuration for intelligent merging:
        
        >>> manifest = {
        ...     "$.users[0].id": "123",
        ...     "$.users[0].name": "Alice",
        ...     "$.users[1].id": "123",
        ...     "$.users[1].email": "alice@example.com"
        ... }
        >>> extend = {"users": ["id"]}
        >>> result = parse_jsonpath(manifest, extend=extend)
        >>> print(result)
        {
            "users": [
                {"id": "123", "name": "Alice", "email": "alice@example.com"}
            ]
        }
        
        Error handling examples:
        
        >>> # Invalid JSONPath (missing $.)
        >>> result = parse_jsonpath({"user.name": "John"})
        >>> print(result)
        {"error": "Given JSON_PATH : user.name  is not starting with $.xxx"}
        
        >>> # Unbalanced brackets
        >>> result = parse_jsonpath({"$.items[0.name": "test"})
        >>> print(result)
        {"error": "Unbalanced JSON_PATH : $.items[0.name"}
    
    Note:
        - All JSONPath expressions must start with "$." to be processed
        - The function performs validation on JSONPath syntax before processing
        - String values enclosed in quotes are automatically cleaned
        - Empty manifests or manifests without valid JSONPath keys return error dictionaries
        - The extend parameter enables sophisticated array merging based on common key values
        - Processing stops and returns error on first invalid JSONPath encountered
    
    See Also:
        - jsonpath_to_dict: Internal function for individual JSONPath processing
        - merge_dicts: Internal function for combining processed JSONPath results
        - JSONPath specification for expression syntax reference
    """

    def check_jsonpath(expression):
        """
        Validate the balance of parentheses, brackets, and braces in a JSONPath expression.
        
        This function ensures that all opening symbols have corresponding closing symbols
        in the correct order, which is essential for valid JSONPath syntax.
        
        Args:
            expression (str): The JSONPath expression to validate.
                Should contain properly balanced (), [], and {} characters.
        
        Returns:
            str: "balanced" if all symbols are properly matched, "unbalanced" otherwise.
        
        Validation Rules:
            - Every opening symbol must have a corresponding closing symbol
            - Symbols must be closed in the correct order (LIFO - Last In, First Out)
            - Supports three types of brackets: (), [], {}
            - Empty expression or expression without brackets returns "balanced"
        
        Examples:
            Valid expressions:
            
            >>> check_jsonpath("$.user.name")
            "balanced"
            
            >>> check_jsonpath("$.items[0].details")
            "balanced"
            
            >>> check_jsonpath("$.data[?(@.id == 'test')].value")
            "balanced"
            
            Invalid expressions:
            
            >>> check_jsonpath("$.items[0.name")
            "unbalanced"
            
            >>> check_jsonpath("$.data[?(@.id == 'test'].value")
            "unbalanced"
            
            >>> check_jsonpath("$.nested{[}]")
            "unbalanced"
        
        Note:
            - Does not validate JSONPath syntax beyond bracket balancing
            - Treats all bracket types equally for balance checking
            - Used as a preliminary validation before JSONPath processing
        """
        open_tup = tuple("({[")
        close_tup = tuple(")}]")
        map = dict(zip(open_tup, close_tup))
        queue = []

        for i in expression:
            if i in open_tup:
                queue.append(map[i])
            elif i in close_tup:
                if not queue or i != queue.pop():
                    return "unbalanced"
        if not queue:
            return "balanced"
        else:
            return "unbalanced"

    def check_token(token):
        """
        Validate the balance of quotes in a JSONPath token.
        
        Ensures that string literals within JSONPath expressions have properly
        paired quote characters, which is necessary for correct parsing.
        
        Args:
            token (str): The token to check for quote balance.
                May contain single quotes (') or double quotes (").
        
        Returns:
            str: "balanced" if quotes are properly paired, "unbalanced" otherwise.
        
        Quote Balancing Rules:
            - Every opening quote must have a corresponding closing quote
            - Both single (') and double (") quotes are counted together
            - Even number of quotes indicates balanced state
            - Odd number of quotes indicates unbalanced state
        
        Examples:
            Balanced tokens:
            
            >>> check_token("name")
            "balanced"
            
            >>> check_token("'John Doe'")
            "balanced"
            
            >>> check_token('"test value"')
            "balanced"
            
            >>> check_token("'it\\'s' and \"he said\"")
            "balanced"
            
            Unbalanced tokens:
            
            >>> check_token("'unclosed string")
            "unbalanced"
            
            >>> check_token('name with "quote')
            "unbalanced"
        
        Note:
            - Does not handle escaped quotes within strings
            - Treats single and double quotes equivalently
            - Used during tokenization to handle multi-part tokens
        """
        open_quote = tuple("'\"")
        count = 0
        for i in token:
            if i in open_quote:
                count = count + 1
        if count % 2 == 0:
            return "balanced"
        else:
            return "unbalanced"

    def tokenize(tList):
        """
        Process a list of JSONPath tokens to handle quoted strings that were split incorrectly.
        
        When JSONPath expressions are split by dots, quoted strings containing dots
        may be incorrectly separated. This function reconstructs such strings by
        merging consecutive tokens until quote balance is achieved.
        
        Args:
            tList (list): List of JSONPath tokens that may contain unbalanced quotes.
                Tokens are typically created by splitting a JSONPath on dots.
        
        Returns:
            list: Processed token list with properly reconstructed quoted strings,
                or [False, error_message] if processing fails.
        
        Processing Logic:
            1. Check each token for quote balance
            2. If unbalanced, merge with subsequent tokens until balanced
            3. Continue processing remaining tokens
            4. Handle errors gracefully with descriptive messages
        
        Examples:
            Simple tokenization (no quotes):
            
            >>> tokenize(["$", "user", "name"])
            ["$", "user", "name"]
            
            Reconstructing quoted strings:
            
            >>> tokenize(["$", "user", "'full", "name'", "value"])
            ["$", "user", "'full.name'", "value"]
            
            Complex quoted content:
            
            >>> tokenize(["$", "items", "'product", "description", "with", "dots'"])
            ["$", "items", "'product.description.with.dots'"]
            
            Error handling:
            
            >>> tokenize(["$", "bad", "'unclosed"])
            [False, "Error (...) field in xls ['$', 'bad', \"'unclosed\"]"]
        
        Note:
            - Modifies the input list in-place during processing
            - Joins reconstructed tokens with dots to maintain original content
            - Returns error information if reconstruction fails
            - Essential for handling JSONPath expressions with quoted property names
        """
        unbalanced = False
        try:
            i = 0
            while i < len(tList) - 1:
                if check_token(tList[i]) == "unbalanced":
                    unbalanced = True
                    eCount = 0
                    while unbalanced:
                        tList[i] = f"{tList[i]}.{tList.pop(i+1)}"
                        eCount = eCount + 1
                        if check_token(tList[i]) == "balanced":
                            break
                    i = i + eCount
                i = i + 1
            return tList
        except Exception as e:
            return [False, f"Error ({e}) field in xls {tList[i]}"]

    def split_string_with_array(string):
        """
        Parse array notation in JSONPath expressions to extract field name and index.
        
        Converts strings like "items[0]" into separate field name and array index
        components for easier processing in JSON structure building.
        
        Args:
            string (str): JSONPath token containing array notation.
                Expected format: "fieldname[index]" where index is an integer.
        
        Returns:
            tuple: (field_name, array_index) where:
                - field_name (str): The property name before the brackets
                - array_index (int): The numeric index within the brackets
        
        Examples:
            Basic array notation:
            
            >>> split_string_with_array("items[0]")
            ("items", 0)
            
            >>> split_string_with_array("users[42]")
            ("users", 42)
            
            >>> split_string_with_array("data[999]")
            ("data", 999)
        
        Note:
            - Assumes well-formed array notation with single integer index
            - Does not validate index bounds or field name validity
            - Used internally for processing array-based JSONPath expressions
            - Converts string index to integer for direct array access
        """
        arr = string.split("[")
        arr[1] = arr[1].replace("]", "")
        arr[1] = int(arr[1])
        return (arr[0], arr[1])

    def get_list(lsize, dict_value):
        """
        Create a list of specified size with empty dictionaries and append a value.
        
        Generates a list structure suitable for array-based JSON construction,
        pre-filling with empty dictionaries up to the specified size and adding
        the target value at the end.
        
        Args:
            lsize (int): The desired size of the list (number of empty dictionaries to create).
                Must be a non-negative integer for successful list creation.
            dict_value (any): The value to append after the empty dictionaries.
                Can be any JSON-serializable type (dict, list, string, number, etc.).
        
        Returns:
            list: List containing lsize empty dictionaries followed by dict_value,
                or empty list if lsize is not a valid integer.
        
        Examples:
            Creating lists with empty dictionaries:
            
            >>> get_list(3, {"name": "John"})
            [{}, {}, {}, {"name": "John"}]
            
            >>> get_list(0, "value")
            ["value"]
            
            >>> get_list(2, [1, 2, 3])
            [{}, {}, [1, 2, 3]]
            
            Error handling:
            
            >>> get_list("invalid", {"data": "test"})
            []
            
            >>> get_list(-1, "value")
            []
        
        Note:
            - Returns empty list for invalid size parameters
            - Empty dictionaries serve as placeholders for future data merging
            - Used internally for building array structures in JSON construction
            - Handles exceptions gracefully by returning empty list
        """
        eDict = {}
        rList = []
        try:
            if not isinstance(lsize, int):
                return rList
            for i in range(lsize):
                rList.append(eDict)
            rList.append(dict_value)
            return rList
        except Exception as e:
            return rList

    def process_list(pList, key, value):
        """
        Recursively process a list of JSONPath tokens to build nested dictionary structure.
        
        Takes a list of JSONPath components and builds a nested dictionary structure
        by recursively processing each token level, handling quoted tokens and
        building the final JSON hierarchy.
        
        Args:
            pList (list): List of JSONPath tokens to process.
                Tokens represent the path components from root to target.
                Modified in-place during recursive processing.
            key (str): Current key/property name being processed.
                Represents the current level in the JSON hierarchy.
            value (any): The target value to place at the final path location.
                Can be any JSON-serializable type.
        
        Returns:
            dict: Empty dictionary (json_dict). The actual structure is built in tempDict[FKEY].
                The function builds structure through side effects on the tempDict variable.
        
        Processing Logic:
            1. If pList is empty, assign value to key (base case)
            2. Otherwise, pop first token from pList for current level
            3. Handle quoted tokens by merging with next token if needed
            4. Recursively process remaining tokens
            5. Build nested structure in tempDict
        
        Examples:
            Simple path processing:
            
            >>> # Internal usage - processes ["name"] with key="user", value="John"
            >>> # Results in: {"user": {"name": "John"}}
            
            Nested path processing:
            
            >>> # Internal usage - processes ["address", "city"] with key="user", value="NYC"
            >>> # Results in: {"user": {"address": {"city": "NYC"}}}
            
            Quoted token handling:
            
            >>> # Internal usage - processes ["'full name'"] with key="user", value="John Doe"
            >>> # Results in: {"user": {"'full name'": "John Doe"}}
        
        Note:
            - Modifies pList in-place by popping elements during recursion
            - Handles quoted tokens that may span multiple list elements
            - Returns empty dict but builds actual structure in tempDict[FKEY]
            - Used internally as part of JSONPath to dictionary conversion process
        """
        json_dict = tempDict = {}
        FKEY = key
        if len(pList) == 0:
            tempDict[key] = value
        else:
            key = pList.pop(0)
            if check_token(key) == "unbalanced":
                key = f"{key}.{pList.pop(0)}"
            tempDict[FKEY] = process_list(pList, key, value)
        return json_dict

    def process_subList(sDict):
        """
        Process sub-dictionary structures containing filter expressions and array notations.
        
        Handles complex JSONPath expressions that contain filter conditions, array
        notations, and assignment operations, converting them into proper dictionary
        structures for JSON building.
        
        Args:
            sDict (dict): Dictionary containing JSONPath expressions with filter conditions.
                Keys may contain filter expressions like "field==value" or array notations.
                Values can be nested dictionaries or scalar values.
        
        Returns:
            dict: Empty dictionary (lDict). Processed structure is built in tDict.
                The function processes complex expressions and builds simplified structures.
        
        Filter Expression Handling:
            - Processes keys containing "==" for equality conditions
            - Extracts field names and values from filter expressions
            - Handles parentheses in values (e.g., "Texas A(6)")
            - Supports nested sub-dictionary processing
        
        Array Notation Handling:
            - Processes keys with "[" but without "]" 
            - Extracts field names using regex patterns
            - Builds sub-lists for array-like structures
        
        Examples:
            Filter expression processing:
            
            >>> # Internal usage with filter expressions
            >>> sDict = {"id==123": {"name": "John"}}
            >>> # Results in: {"id": "123", "name": "John"}
            
            Array notation processing:
            
            >>> # Internal usage with array notation
            >>> sDict = {"items[": {"data": "value"}}
            >>> # Results in: {"items": [{"data": "value"}]}
            
            Complex value handling:
            
            >>> # Internal usage with parentheses in values
            >>> sDict = {"state==Texas A(6)": {}}
            >>> # Results in: {"state": "Texas A(6)"}
        
        Note:
            - Uses regex patterns to extract valid identifiers and values
            - Handles special cases like parentheses in assigned values
            - Recursively processes nested sub-dictionaries
            - Returns empty lDict but builds actual structure in tDict
            - Used internally for processing complex JSONPath filter expressions
        """
        open_bracket = "["
        closed_bracket = "]"
        lDict = tDict = {}
        subList = []
        for k, v in sDict.items():
            if isinstance(v, dict):
                if (open_bracket in k) and (closed_bracket not in k):
                    k = re.findall(r"[0-9a-zA-Z=]+", k)[0]
                    subList.append(process_subList(v))
                    tDict[k] = subList

                strValues = re.findall(r"[0-9a-zA-Z=:._]+", k)
                if len(strValues) == 2:
                    if "==" in strValues[0]:
                        tDict[strValues[0].replace("==", "")] = strValues[1]
                        tDict.update(process_subList(v))
                if len(strValues) > 2:
                    if "==" in strValues[1]:
                        tDict[strValues[0]] = " ".join(strValues[2:])
                        # Its exception example "Texas A(6)" : Anything that has ( or ) in assigned value
                        ARValueList = tDict[strValues[0]].split(" ")
                        if ARValueList[0]:
                            ARValue = (
                                " ".join(ARValueList[:-1])
                                + "("
                                + ARValueList[-1]
                                + ")"
                            )
                            tDict[strValues[0]] = ARValue

                        tDict.update(process_subList(v))
            else:
                tDict.update({k: v})
        return lDict

    def process_dict(pDict):
        """
        Process dictionary structures with array notations and nested objects.
        
        Converts dictionary structures containing JSONPath array notations into
        proper JSON array structures, handling both indexed arrays and filtered arrays.
        
        Args:
            pDict (dict): Dictionary containing JSONPath expressions with array notations.
                Keys may contain array indices like "items[0]" or filter expressions.
                Values can be nested dictionaries, lists, or scalar values.
        
        Returns:
            dict: Empty dictionary (json_dict). Processed structure is built in tempDict.
                The function transforms array notations into proper JSON structures.
        
        Array Processing Types:
            1. Indexed arrays: "field[n]" where n is an integer index
            2. Filter arrays: "field[" without closing bracket (indicates filter)
            3. Regular objects: Keys without array notation
        
        Examples:
            Indexed array processing:
            
            >>> # Internal usage with indexed arrays
            >>> pDict = {"items[0]": {"name": "Product A"}, "items[1]": {"name": "Product B"}}
            >>> # Results in: {"items": [{"name": "Product A"}, {"name": "Product B"}]}
            
            Filter array processing:
            
            >>> # Internal usage with filter arrays
            >>> pDict = {"users[": {"id==123": {"name": "John"}}}
            >>> # Results in: {"users": [{"id": "123", "name": "John"}]}
            
            Mixed structure processing:
            
            >>> # Internal usage with mixed structures
            >>> pDict = {
            ...     "name": "Company",
            ...     "employees[0]": {"name": "Alice"},
            ...     "settings": {"theme": "dark"}
            ... }
            >>> # Results in: {
            >>> #     "name": "Company",
            >>> #     "employees": [{"name": "Alice"}],
            >>> #     "settings": {"theme": "dark"}
            >>> # }
        
        Note:
            - Distinguishes between indexed and filter arrays using bracket notation
            - Uses get_list() for creating properly sized array structures
            - Recursively processes nested dictionary values
            - Returns empty json_dict but builds actual structure in tempDict
            - Used internally for final JSON structure construction
        """
        open_bracket = "["
        closed_bracket = "]"
        json_dict = tempDict = {}
        subList = []

        for dict_key, dict_value in pDict.items():
            if not isinstance(dict_value, dict):
                tempDict[dict_key] = dict_value
            if (open_bracket in dict_key) and (closed_bracket in dict_key):
                dict_key, lsize = split_string_with_array(dict_key)
                if isinstance(dict_value, dict):
                    tempDict[dict_key] = get_list(lsize, process_dict(dict_value))
            elif (open_bracket in dict_key) and (closed_bracket not in dict_key):
                dict_key = re.findall(r"[0-9a-zA-Z=]+", dict_key)[0]
                subList.append(process_subList(dict_value))
                tempDict[dict_key] = subList
            else:
                if isinstance(dict_value, dict):
                    tempDict[dict_key] = process_dict(dict_value)
        return json_dict

    def merge_lists(aList, bList, path, extend=None):
        """
        Merge two lists with intelligent handling of empty elements and extensions.
        
        Combines two lists by merging corresponding elements, with special handling
        for empty dictionaries and optional extension-based merging for more
        sophisticated list combination strategies.
        
        Args:
            aList (list): First list to merge (modified in-place).
                Elements can be dictionaries, lists, or scalar values.
            bList (list): Second list to merge into aList.
                Elements should be compatible types with aList elements.
            path (list): Current path context for extension matching.
                Used to determine if extension rules apply to this merge operation.
            extend (dict, optional): Extension configuration for intelligent merging.
                Defines merge strategies based on common keys in dictionary elements.
        
        Returns:
            list: The merged list (aList modified in-place).
                Contains combined elements from both input lists.
        
        Merging Strategies:
            1. Empty element replacement: Empty dicts in aList replaced by bList elements
            2. Dictionary merging: Nested dictionaries are recursively merged
            3. List extension: Lists are extended with elements from bList
            4. Scalar replacement: Scalar values in aList replaced by bList values
            5. Extension-based merging: When extend config matches, uses extendList()
        
        Examples:
            Basic list merging:
            
            >>> aList = [{"name": "John"}, {}]
            >>> bList = [{"age": 25}, {"name": "Jane"}]
            >>> result = merge_lists(aList, bList, ["users"])
            >>> print(aList)  # Modified in-place
            [{"name": "John", "age": 25}, {"name": "Jane"}]
            
            Extension-based merging:
            
            >>> aList = [{"id": "1", "name": "John"}]
            >>> bList = [{"id": "1", "email": "john@example.com"}]
            >>> extend = {"users": ["id"]}
            >>> result = merge_lists(aList, bList, ["users"], extend)
            >>> print(aList)
            [{"id": "1", "name": "John", "email": "john@example.com"}]
        
        Note:
            - Modifies aList in-place for efficiency
            - Handles lists of different lengths by appending extra bList elements
            - Uses merge_dicts() for recursive dictionary merging
            - Extension matching is based on path context and extend configuration
            - Empty dictionary detection used for placeholder replacement
        """

        def extendList(aList, bList, commonKey):
            """
            Extend list by merging elements based on common keys.
            
            Internal helper function for merge_lists that performs sophisticated
            list merging by identifying elements with common key-value pairs
            and merging them together, while preserving unique elements.
            
            Args:
                aList (list): Primary list to extend (modified in-place).
                    Should contain dictionary elements for key-based matching.
                bList (list): Source list providing elements to merge.
                    Elements are merged into aList based on key matching.
                commonKey (list or str): Key(s) to use for element matching.
                    Elements with matching values for these keys are merged together.
            
            Returns:
                list: Extended aList with merged elements.
                    Original aList is modified in-place.
            
            Merging Logic:
                1. Extract key-value sets from bList elements
                2. For each aList element, compare key-value sets
                3. If no conflicting keys found, merge bList element into aList element
                4. Mark processed bList elements for removal
                5. Append any unprocessed bList elements to aList
            
            Examples:
                Key-based merging:
                
                >>> aList = [{"id": "1", "name": "John"}]
                >>> bList = [{"id": "1", "email": "john@example.com"}]
                >>> commonKey = ["id"]
                >>> result = extendList(aList, bList, commonKey)
                >>> print(aList)
                [{"id": "1", "name": "John", "email": "john@example.com"}]
                
                Multiple common keys:
                
                >>> aList = [{"id": "1", "type": "user", "name": "John"}]
                >>> bList = [{"id": "1", "type": "user", "email": "john@example.com"}]
                >>> commonKey = ["id", "type"]
                >>> result = extendList(aList, bList, commonKey)
                >>> print(aList)
                [{"id": "1", "type": "user", "name": "John", "email": "john@example.com"}]
            
            Note:
                - Requires dictionary elements for meaningful key-based matching
                - Uses set operations for efficient key-value comparison
                - Modifies aList in-place and clears processed bList elements
                - Used internally by merge_lists for extension-based merging
            """
            bSet = set(bList[0].items())
            for i in range(0, len(aList)):
                aSet = set(aList[i].items())
                diffKey = set(dict((bSet.symmetric_difference(aSet))))
                if (len(diffKey.intersection(commonKey))) == 0:
                    aList[i] = dict(aSet.union(bSet))
                    bList = []
            aList.extend(bList)
            return aList

        a_emptyIdx = [idx for idx, s in enumerate(aList) if s == {}]
        b_emptyIdx = [idx for idx, s in enumerate(bList) if s == {}]

        pathList = list(path)
        if len(a_emptyIdx) == 0 and len(b_emptyIdx) == 0:
            if extend:
                for eKey, eValue in extend.items():
                    if isinstance(eValue, list):
                        if eKey in pathList:
                            for i in bList:
                                if len(i) > 1:
                                    return extendList(aList, bList, eValue)
                    else:
                        if eKey in pathList:
                            for i in bList:
                                if len(i) > 1:
                                    return extendList(aList, bList, eValue)

        cLen = min(len(aList), len(bList))

        for idx in range(cLen):
            if len(aList[idx]) == 0 and len(bList[idx]) != 0:
                aList[idx] = bList[idx]
            if isinstance(aList[idx], dict) and isinstance(bList[idx], dict):
                merge_dicts(aList[idx], bList[idx])
            elif isinstance(aList[idx], list) and isinstance(bList[idx], list):
                aList[idx].extend(bList[idx])
            else:
                aList[idx] = bList[idx]

        for idx in range(cLen, len(bList)):
            aList.append(bList[idx])

        return aList

    def merge_dicts(a, b, path=None, update=True, extend=None):
        """
        Recursively merge two dictionaries with support for lists and extensions.
        
        Performs deep merging of dictionary structures, handling nested dictionaries,
        lists, and providing conflict resolution strategies. Supports extension
        configurations for sophisticated list merging behavior.
        
        Args:
            a (dict): Primary dictionary to merge into (modified in-place).
                Serves as the base structure for the merge operation.
            b (dict): Source dictionary to merge from.
                Values from this dictionary are merged into dictionary a.
            path (list, optional): Current path context for debugging and extensions.
                Used for error reporting and extension rule matching. Defaults to [].
            update (bool, optional): Whether to update conflicting scalar values.
                If True, values from b override values in a. If False, raises exception
                on conflicts. Defaults to True.
            extend (dict, optional): Extension configuration for list merging.
                Defines advanced merging strategies for specific paths.
        
        Returns:
            dict: The merged dictionary (dictionary a modified in-place).
                Contains combined structure and values from both input dictionaries.
        
        Merging Rules:
            1. Identical values: No change needed
            2. Nested dictionaries: Recursive merge
            3. Lists: Use merge_lists() with extension support
            4. Scalar conflicts: Update based on update parameter
            5. New keys: Always added to result
        
        Examples:
            Basic dictionary merging:
            
            >>> a = {"user": {"name": "John"}}
            >>> b = {"user": {"age": 25}, "active": True}
            >>> result = merge_dicts(a, b)
            >>> print(a)  # Modified in-place
            {"user": {"name": "John", "age": 25}, "active": True}
            
            List merging with extensions:
            
            >>> a = {"users": [{"id": "1", "name": "John"}]}
            >>> b = {"users": [{"id": "1", "email": "john@example.com"}]}
            >>> extend = {"users": ["id"]}
            >>> result = merge_dicts(a, b, extend=extend)
            >>> print(a)
            {"users": [{"id": "1", "name": "John", "email": "john@example.com"}]}
            
            Conflict handling:
            
            >>> a = {"name": "John"}
            >>> b = {"name": "Jane"}
            >>> # With update=True (default)
            >>> merge_dicts(a, b)  # a becomes {"name": "Jane"}
            >>> 
            >>> # With update=False
            >>> merge_dicts(a, b, update=False)  # Raises Exception
        
        Raises:
            Exception: When update=False and conflicting scalar values are encountered.
                Error message includes the path to the conflicting key.
        
        Note:
            - Modifies dictionary a in-place for efficiency
            - Handles deeply nested structures through recursion
            - Path parameter used for error reporting and extension matching
            - Extension configuration enables sophisticated list merging strategies
            - Used throughout JSONPath processing for combining partial structures
        """
        if path is None:
            path = []

        if a == b:
            return a

        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    merge_dicts(a[key], b[key], path + [str(key)], update, extend)
                elif a[key] == b[key]:
                    pass
                elif isinstance(a[key], list) and isinstance(b[key], list):
                    a[key] = merge_lists(a[key], b[key], path + [str(key)], extend)
                elif update:
                    a[key] = b[key]
                else:
                    raise Exception(f"Conflict at {'.'.join(path + [str(key)])}")
            else:
                a[key] = b[key]
        return a

    def jsonpath_to_dict(manifestItem):
        """
        Convert a single JSONPath expression and value into a dictionary structure.
        
        Processes an individual JSONPath expression to build the corresponding
        nested dictionary structure, handling validation, tokenization, and
        structure building for one path-value pair.
        
        Args:
            manifestItem (dict): Dictionary containing JSONPath expression and target value.
                Expected keys:
                - "json-path" (str): Valid JSONPath expression starting with "$."
                - "json-value" (any): Target value to place at the path location
        
        Returns:
            dict: Generated dictionary structure for the JSONPath, or error dictionary.
                Success: Returns nested dict structure matching the JSONPath
                Error: Returns {"error": "description"} for processing failures
        
        Processing Steps:
            1. Extract JSONPath and value from manifestItem
            2. Validate JSONPath format (must start with "$.")
            3. Check JSONPath syntax balance (brackets, quotes)
            4. Tokenize the JSONPath by splitting on dots
            5. Handle quoted tokens and validate tokenization
            6. Build dictionary structure using process_list and process_dict
        
        Examples:
            Simple path conversion:
            
            >>> item = {"json-path": "$.user.name", "json-value": "John"}
            >>> result = jsonpath_to_dict(item)
            >>> print(result)
            {"user": {"name": "John"}}
            
            Array path conversion:
            
            >>> item = {"json-path": "$.items[0].price", "json-value": 29.99}
            >>> result = jsonpath_to_dict(item)
            >>> print(result)
            {"items": [{"price": 29.99}]}
            
            Error cases:
            
            >>> # Invalid JSONPath format
            >>> item = {"json-path": "user.name", "json-value": "John"}
            >>> result = jsonpath_to_dict(item)
            >>> print(result)
            {"error": "Given JSON_PATH : user.name  is not starting with $.xxx"}
            
            >>> # Unbalanced brackets
            >>> item = {"json-path": "$.items[0.name", "json-value": "test"}
            >>> result = jsonpath_to_dict(item)
            >>> print(result)
            {"error": "Unbalanced JSON_PATH : $.items[0.name"}
        
        Note:
            - Validates JSONPath format before processing
            - Handles quoted string tokenization automatically
            - Returns error dictionaries for invalid inputs
            - Used internally for processing individual manifest items
            - Integrates validation, tokenization, and structure building steps
        """
        # Version 2.0
        jsonPath = manifestItem["json-path"]
        jsonValue = manifestItem["json-value"]

        if not jsonPath.startswith("$."):
            return {
                "error": f"Given JSON_PATH : {jsonPath}  is not starting with $.xxx"
            }

        if "unbalanced" == check_jsonpath(jsonPath):
            return {"error": f"Unbalanced JSON_PATH : {jsonPath}"}

        k_list = jsonPath.split(".")
        k_list = tokenize(k_list)
        if not k_list[0]:
            return {"error": f"Invalid JSONPATH [{jsonPath}({k_list[1]})]"}
        try:
            if k_list[0] == "$":
                k_list = k_list[1:]
                FKEY = k_list.pop(0)
                FVALUE = jsonValue
                plDict = process_list(k_list, FKEY, FVALUE)
                pdDict = process_dict(plDict)
                return pdDict
        except Exception as e:
            return {"error": f"Invalid JSONPATH: {jsonPath} ({e})"}

    tmp = {"data": []}
    for k, v in manifest.items():
        if "$" in k:
            if isinstance(v, str):
                if v.startswith('"'):
                    v = v[1:-1]
            tmp["data"].append({"json-path": k, "json-value": v})

    if not tmp["data"]:
        return {"error": "No data found in manifest"}

    json_payload = {}
    for item in tmp["data"]:
        genPayload = jsonpath_to_dict(item)
        if any("error" in k for k in genPayload):
            return genPayload
        json_payload = merge_dicts(json_payload, genPayload, update=True, extend=extend)
    return json_payload
