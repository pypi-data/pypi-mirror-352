"""
JSON utility functions for the Cogent Memory library.
"""

import json
from typing import Any, Dict, Optional


def merge_json_objects(obj1: Dict[str, Any], obj2: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
    """
    Merge two JSON objects, with optional deep merging.
    
    Args:
        obj1: First JSON object
        obj2: Second JSON object
        deep: If True, perform deep merging of nested objects
        
    Returns:
        Merged JSON object
        
    Example:
        >>> obj1 = {"a": 1, "b": {"x": 1}}
        >>> obj2 = {"b": {"y": 2}, "c": 3}
        >>> merge_json_objects(obj1, obj2)
        {'a': 1, 'b': {'x': 1, 'y': 2}, 'c': 3}
    """
    if not deep:
        return {**obj1, **obj2}
    
    result = obj1.copy()
    
    for key, value in obj2.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = merge_json_objects(result[key], value, deep=True)
        else:
            result[key] = value
            
    return result 