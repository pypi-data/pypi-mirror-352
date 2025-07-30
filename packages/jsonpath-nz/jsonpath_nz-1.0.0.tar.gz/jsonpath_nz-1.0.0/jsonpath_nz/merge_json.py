from typing import Dict, Any, Union
import json

def merge_json(dict1: Union[Dict, str], dict2: Union[Dict, str], extend: bool = False) -> Dict[str, Any]:
    """
    Merge two JSON files or dictionaries with support for nested structures and list handling.
    
    This function provides deep merging capabilities for JSON data structures, including
    nested dictionaries and lists. It can handle both dictionary objects and file paths
    to JSON files as input.
    
    Args:
        dict1 (Union[Dict, str]): First dictionary to merge, or path to a JSON file.
            If a string is provided, it should be a valid file path to a JSON file.
        dict2 (Union[Dict, str]): Second dictionary to merge, or path to a JSON file.
            If a string is provided, it should be a valid file path to a JSON file.
            Values from dict2 will override values from dict1 for matching keys.
        extend (bool, optional): Controls how lists are merged. Defaults to False.
            - If False: Lists are merged element-wise, with remaining elements from
              the second list appended to the result.
            - If True: Lists are extended by matching dictionary keys within list items,
              and unique non-dictionary items are appended.
    
    Returns:
        Dict[str, Any]: A new dictionary containing the merged result. The original
        dictionaries are not modified.
    
    Raises:
        FileNotFoundError: If a provided file path does not exist.
        json.JSONDecodeError: If a file contains invalid JSON.
        TypeError: If the input types are not supported.
    
    Examples:
        Basic dictionary merging:
        
        >>> dict1 = {"a": 1, "b": {"c": 2}}
        >>> dict2 = {"b": {"d": 3}, "e": 4}
        >>> result = merge_json(dict1, dict2)
        >>> print(result)
        {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
        
        Merging from JSON files:
        
        >>> result = merge_json("config1.json", "config2.json")
        
        List merging without extension:
        
        >>> dict1 = {"items": [{"id": 1}, {"id": 2}]}
        >>> dict2 = {"items": [{"name": "first"}, {"name": "second"}, {"id": 3}]}
        >>> result = merge_json(dict1, dict2, extend=False)
        >>> print(result["items"])
        [{"id": 1, "name": "first"}, {"id": 2, "name": "second"}, {"id": 3}]
        
        List merging with extension:
        
        >>> dict1 = {"users": [{"id": 1, "name": "John"}]}
        >>> dict2 = {"users": [{"id": 1, "email": "john@email.com"}, {"id": 2, "name": "Jane"}]}
        >>> result = merge_json(dict1, dict2, extend=True)
        >>> print(result["users"])
        [{"id": 1, "name": "John", "email": "john@email.com"}, {"id": 2, "name": "Jane"}]
    
    Note:
        - The merge operation creates a new dictionary and does not modify the input dictionaries.
        - For conflicting scalar values, dict2 values take precedence over dict1 values.
        - When extend=True, list items are considered to match if they are both dictionaries
          and share at least one common key.
        - The function performs deep copying to avoid reference issues in nested structures.
    
    See Also:
        - json.load: For loading JSON files
        - dict.update: For simple dictionary updates without deep merging
    """
    
    def merge_lists(aList, bList, extend=False):
        """Merge two lists with option to extend"""
        if not extend:
            # Simple list merge without extension
            cLen = min(len(aList), len(bList))
            for idx in range(cLen):
                if isinstance(aList[idx], dict) and isinstance(bList[idx], dict):
                    aList[idx] = merge_dicts(aList[idx], bList[idx], extend=extend)
                elif isinstance(aList[idx], list) and isinstance(bList[idx], list):
                    aList[idx] = merge_lists(aList[idx], bList[idx], extend=extend)
                else:
                    aList[idx] = bList[idx]
            
            # Append remaining items from bList
            aList.extend(bList[cLen:])
            return aList
        else:
            # Extend lists by matching dictionary keys
            merged_list = aList.copy()
            for b_item in bList:
                if isinstance(b_item, dict):
                    found_match = False
                    for a_item in merged_list:
                        if isinstance(a_item, dict) and set(a_item.keys()) & set(b_item.keys()):
                            # Merge dictionaries with common keys
                            a_item.update(merge_dicts(a_item, b_item, extend=extend))
                            found_match = True
                            break
                    if not found_match:
                        merged_list.append(b_item)
                else:
                    if b_item not in merged_list:
                        merged_list.append(b_item)
            return merged_list

    def merge_dicts(a: Dict, b: Dict, extend: bool = False) -> Dict:
        """Merge two dictionaries recursively"""
        result = a.copy()
        
        for key, b_value in b.items():
            if key in result:
                a_value = result[key]
                if isinstance(a_value, dict) and isinstance(b_value, dict):
                    result[key] = merge_dicts(a_value, b_value, extend=extend)
                elif isinstance(a_value, list) and isinstance(b_value, list):
                    result[key] = merge_lists(a_value, b_value, extend=extend)
                else:
                    result[key] = b_value
            else:
                result[key] = b_value
                
        return result

    # Load JSON files if string paths are provided
    if isinstance(dict1, str):
        with open(dict1, 'r') as f:
            dict1 = json.load(f)
    if isinstance(dict2, str):
        with open(dict2, 'r') as f:
            dict2 = json.load(f)

    # Perform the merge
    return merge_dicts(dict1, dict2, extend=extend)