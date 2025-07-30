"""
File Purpose: AbelianOperation
    - Commutative
    - Associative
    - has identity element
    - not "truly" abelian -- doesn't assume all elements have an inverse
        (e.g. 0 has no inverse under Product)
"""
from .associative_operations import AssociativeOperation
from .commutative_operations import CommutativeOperation

class AbelianOperation(AssociativeOperation, CommutativeOperation):
    '''AbelianOperation -- abstract class for operations which are:
        - Commutative
        - Associative
        - have identity element
        - not "truly" abelian -- doesn't assume all elements have an inverse
            (e.g. 0 has no inverse under Product)
    '''
    IDENTITY = NotImplemented  # subclasses should define IDENTITY
