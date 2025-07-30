#!/usr/bin/env python3
"""
Utility functions for embedding operations.
"""

import numpy as np
from typing import List, Dict, Any, Union, Optional


def generate_random_vectors(num_vectors: int, dimension: int) -> List[np.ndarray]:
    """
    Generate random embedding vectors for testing.
    
    Args:
        num_vectors: Number of vectors to generate
        dimension: Dimension of each vector
        
    Returns:
        List of random vectors as numpy arrays
    """
    # Generate random vectors and normalize them
    vectors = []
    for _ in range(num_vectors):
        # Create random vector
        vector = np.random.randn(dimension).astype(np.float32)
        
        # Normalize to unit length
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        vectors.append(vector)
    
    return vectors


# TODO: [KNW-23] Refactor to use core PydanticConfigWrapper directly
# This will reduce duplication and centralize config schema
# Planned for after Week 5 integration
def convert_config_dict(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a configuration dictionary to ensure it's compatible with both
    ConfigModel and PydanticConfig classes.
    
    This is a utility function to help with the transition between the two
    config systems.
    
    Args:
        config_dict: Input configuration dictionary
        
    Returns:
        Cleaned dictionary with appropriate structure
    """
    # Make a copy to avoid modifying the original
    result = {}
    
    # Copy all the keys and values
    for key, value in config_dict.items():
        # If value is a dictionary, recursively convert it
        if isinstance(value, dict):
            result[key] = convert_config_dict(value)
        # If value has a to_dict method (like ConfigModel), use it
        elif hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
            result[key] = convert_config_dict(value.to_dict())
        # For Pydantic v2 models, use the model_dump() method
        elif hasattr(value, 'model_dump') and callable(getattr(value, 'model_dump')):
            result[key] = convert_config_dict(value.model_dump())
        # For Pydantic v1 models, use the dict() method (for backward compatibility)
        elif hasattr(value, 'dict') and callable(getattr(value, 'dict')):
            result[key] = convert_config_dict(value.dict())
        else:
            result[key] = value
            
    return result 