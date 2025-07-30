
import numpy as np
from typing import Type

def types_match(typeA:Type, typeB:Type) -> bool:
    """Returns true is typeA is the same as typeB regardless of NumPy version Python typing"""

    # typeA is a numpy type (typeB is any)
    if isinstance(typeA, np.dtype):
        if np.issubdtype(typeA, np.integer):
            return typeB in (int, np.integer)
        elif np.issubdtype(typeA, np.floating):
            return typeB in (float, np.floating)
        elif np.issubdtype(typeA, np.bool_):
            return typeB in (bool, np.bool_)
        elif np.issubdtype(typeA, np.object_):
            return typeB is str
        
    # typeB is a numpy type and typeA is not
    if isinstance(typeB, np.dtype):
        if np.issubdtype(typeB, np.integer):
            return typeA in (int, np.integer)
        elif np.issubdtype(typeB, np.floating):
            return typeA in (float, np.floating)
        elif np.issubdtype(typeB, np.bool_):
            return typeA in (bool, np.bool_)
        elif np.issubdtype(typeB, np.object_):
            return typeA is str
        
    # if both are Python types
    else:
        return typeA is typeB
    