from typing import Dict, Type, Any, Tuple

class MergeAnnotationsMeta(type):
    """
    A metaclass that merges type annotations from all base classes into the 
    derived class. If a base class has annotations, they are collected and 
    combined with annotations from the current class.
    """
    
    def __new__(cls: Type['MergeAnnotationsMeta'], 
                name: str, 
                bases: Tuple[Type, ...], 
                dct: Dict[str, Any]) -> 'MergeAnnotationsMeta':
        """
        Create a new class with merged type annotations from its base classes.

        Args:
            cls: The metaclass (MergeAnnotationsMeta).
            name: The name of the class being created.
            bases: A tuple of the base classes from which the class inherits.
            dct: A dictionary representing the class attributes.

        Returns:
            The newly created class with merged annotations.
        """
        # Collect annotations from all base classes
        annotations: Dict[str, Any] = {}
        for base in bases:
            if hasattr(base, '__annotations__'):
                annotations.update(base.__annotations__)

        # Merge annotations from the current class
        annotations.update(dct.get('__annotations__', {}))
        dct['__annotations__'] = annotations

        # Create the new class with the merged annotations
        return super().__new__(cls, name, bases, dct)