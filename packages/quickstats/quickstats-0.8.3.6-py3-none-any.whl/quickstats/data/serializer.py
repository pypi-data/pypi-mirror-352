"""
Serializer module for data formats.

This module provides a framework for serializing and deserializing data in various formats.
It supports dynamic registration of custom serializers, automatic resolution based on file
extensions, and consideration of operation modes (load or dump).

Implementation taken from: https://github.com/riga/law
"""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from pathlib import Path
import json
import pickle
from functools import lru_cache
from typing import Any, ClassVar, Dict, List, Tuple, Type, Union

from quickstats import module_exists

AUTO = 'auto'
LOAD = 'load'
DUMP = 'dump'

class SerializerMeta(ABCMeta):
    """Metaclass for serializer registration and management."""

    _serializers: Dict[str, Type['Serializer']] = {}
    _extension_map: Dict[str, List[Type['Serializer']]] = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        if (not getattr(cls, '__abstractmethods__', False)
                and cls.name != '_base'):
            if module_exists(cls.requires):
                mcs.register(cls)
            supported_modes = []
            for mode in [LOAD, DUMP]:
                if hasattr(cls, mode) and callable(getattr(cls, mode)):
                    supported_modes.append(mode)
            cls.supported_modes = supported_modes

        return cls

    @classmethod
    def register(mcs, serializer_cls: Type['Serializer']) -> None:
        """Register a custom serializer class at runtime.

        Args:
            serializer_cls (Type[Serializer]): The serializer class to register.

        Raises:
            ValueError: If the serializer name is already registered or reserved.
        """
        if serializer_cls.name.lower() == AUTO:
            raise ValueError(
                f"Serializer name '{AUTO}' is reserved and cannot be used"
            )
        if serializer_cls.name in mcs._serializers:
            raise ValueError(
                f"Serializer name '{serializer_cls.name}' is already registered"
            )
        mcs._serializers[serializer_cls.name] = serializer_cls
        for ext in serializer_cls.extensions:
            if ext not in mcs._extension_map:
                mcs._extension_map[ext] = []
            mcs._extension_map[ext].append(serializer_cls)


def register_serializer(serializer_cls: Type[Serializer]) -> None:
    """Register a custom serializer class at runtime.

    Args:
        serializer_cls (Type[Serializer]): The serializer class to register.

    Raises:
        ValueError: If the serializer name is already registered or reserved.
    """
    SerializerMeta.register_serializer(serializer_cls)

def get_serializer(name: str, error_on_missing: bool = False) -> Optional[Type[Serializer]]:
    """Get a serializer by its registered name.

    Args:
        name (str): The name of the serializer.
        error_on_missing (bool): If True, raise ValueError if the serializer is not found.
            Defaults to False.

    Returns:
        Optional[Type[Serializer]]: The serializer class if found; otherwise, None.

    Raises:
        ValueError: If no serializer is registered with the given name and `error_on_missing` is True.
    """
    serializer = SerializerMeta._serializers.get(name)
    if serializer or not error_on_missing:
        return serializer
    raise ValueError(f"No serializer registered with name '{name}'")

def resolve_serializers(
    path: Union[str, Path], mode: str
) -> List[Type[Serializer]]:
    """Return a list of serializers that support the given path and mode.

    Args:
        path (Union[str, Path]): The file path.
        mode (str): The operation mode, 'load' or 'dump'.

    Returns:
        List[Type[Serializer]]: A list of serializer classes.

    Raises:
        ValueError: If the mode is invalid.
    """
    if mode not in ('load', 'dump'):
        raise ValueError(f"Invalid mode '{mode}'. Expected 'load' or 'dump'.")

    path = Path(path)
    suffixes = path.suffixes
    possible_extensions = (''.join(suffixes[i:]) for i in range(len(suffixes)))
    return get_serializers_by_extensions(possible_extensions, mode)


@lru_cache(maxsize=None)
def get_serializers_by_extensions(
    extensions: Union[str, Tuple[str, ...]], mode: str
) -> List[Type[Serializer]]:
    """Lookup serializers that support the given extensions and mode.

    Args:
        extensions (Union[str, Tuple[str, ...]]): A single extension or a tuple of possible file extensions.
        mode (str): The operation mode, 'load' or 'dump'.

    Returns:
        List[Type[Serializer]]: A list of serializer classes.
    """
    if isinstance(extensions, str):
        extensions = (extensions,)

    matching_serializers = []
    for ext in extensions:
        serializers = SerializerMeta._extension_map.get(ext, [])
        for serializer in serializers:
            if mode in serializer.supported_modes:
                matching_serializers.append(serializer)
    return matching_serializers


def resolve_serializer(
    path: Union[str, Path], mode: str, name: str = AUTO
) -> Type[Serializer]:
    """Get the appropriate serializer based on the file extension and optional serializer name.

    Args:
        path (Union[str, Path]): The file path.
        mode (str): The operation mode, 'load' or 'dump'.
        name (str): The serializer name to use. If 'auto', automatically select
            the first registered serializer that supports the file extension.

    Returns:
        Type[Serializer]: The serializer class.

    Raises:
        ValueError: If the serializer does not support the requested mode.
        ValueError: If no suitable serializer is found when name is 'auto'.
    """
    if name.lower() != AUTO:
        serializer = get_serializer(name, error_on_missing=True)
        if mode in serializer.supported_modes:
            return serializer
        else:
            raise ValueError(
                f"Serializer '{name}' does not support mode '{mode}'"
            )
    else:
        candidates = resolve_serializers(path, mode=mode)
        if not candidates:
            raise ValueError(
                f"No suitable serializer found for path '{path}' that supports mode '{mode}'"
            )
        return candidates[0]

def available_serializers() -> List[str]:
    return list(SerializerMeta._serializers)

class Serializer(metaclass=SerializerMeta):
    """Base class for all serializers."""

    name: ClassVar[str] = '_base'
    extensions: ClassVar[Tuple[str, ...]] = ()
    requires: ClassVar[str] = 'python'

    @classmethod
    def load(
        cls, path: Union[str, Path], *args, **kwargs
    ) -> Any:
        """Load data from the specified path."""
        raise NotImplementedError

    @classmethod
    def dump(
        cls, path: Union[str, Path], data: Any, *args, **kwargs
    ) -> None:
        """Save data to the specified path."""
        raise NotImplementedError

    @classmethod
    def validate(cls, path: Union[str, Path]) -> bool:
        """Check if the path has a supported extension."""
        return str(path).endswith(cls.extensions)


class TextSerializer(Serializer):
    """Serializer for text files."""

    name = 'text'
    extensions = ('.txt', '.log')

    @classmethod
    def load(cls, path: Union[str, Path], *args, **kwargs) -> str:
        """Load text content from a file."""
        with open(str(path), "r", **kwargs) as f:
            return f.read(*args)

    @classmethod
    def dump(
        cls, path: Union[str, Path], content: str, *args, **kwargs
    ) -> None:
        """Write text content to a file."""
        with open(str(path), "w", **kwargs) as f:
            f.write(str(content))


class JSONSerializer(Serializer):
    """Serializer for JSON files."""

    name = 'json'
    extensions = ('.json', '.js')

    @classmethod
    def load(cls, path: Union[str, Path], *args, **kwargs) -> Any:
        """Load JSON data from a file."""
        with open(str(path), "r", **kwargs) as f:
            return json.load(f, *args)

    @classmethod
    def dump(
        cls, path: Union[str, Path], data: Any, *args, **kwargs
    ) -> None:
        """Write JSON data to a file."""
        with open(str(path), "w", **kwargs) as f:
            json.dump(data, f, *args, **kwargs)


class YAMLSerializer(Serializer):
    """Serializer for YAML files."""

    name = 'yaml'
    extensions = ('.yaml', '.yml')
    requires = 'yaml'

    @classmethod
    def load(cls, path: Union[str, Path], *args, **kwargs) -> Any:
        """Load YAML data from a file."""
        import yaml
        with open(str(path), "r", **kwargs) as f:
            return yaml.safe_load(f, *args)

    @classmethod
    def dump(
        cls, path: Union[str, Path], data: Any, *args, **kwargs
    ) -> None:
        """Write YAML data to a file."""
        import yaml
        with open(str(path), "w", **kwargs) as f:
            yaml.dump(data, f, *args, **kwargs)


class PickleSerializer(Serializer):
    """Serializer for pickle files."""

    name = 'pickle'
    extensions = ('.pkl', '.pickle')

    @classmethod
    def load(cls, path: Union[str, Path], *args, **kwargs) -> Any:
        """Load pickled data from a file."""
        with open(str(path), 'rb') as f:
            return pickle.load(f, *args)

    @classmethod
    def dump(
        cls, path: Union[str, Path], data: Any, *args, **kwargs
    ) -> None:
        """Write pickled data to a file."""
        with open(str(path), 'wb') as f:
            pickle.dump(data, f, *args, **kwargs)


class NumpySerializer(Serializer):
    """Serializer for NumPy array files."""

    name = 'numpy'
    extensions = ('.npy', '.npz', '.txt')
    requires = 'numpy'

    @classmethod
    def load(
        cls, path: Union[str, Path], *args, **kwargs
    ) -> 'numpy.ndarray':
        """Load NumPy array data from a file."""
        import numpy as np
        path_str = str(path)
        if path_str.endswith('.txt'):
            return np.loadtxt(path_str, *args, **kwargs)
        else:
            return np.load(path_str, *args, **kwargs)

    @classmethod
    def dump(
        cls, path: Union[str, Path], data: 'numpy.ndarray', *args, **kwargs
    ) -> None:
        """Write NumPy array data to a file."""
        import numpy as np
        path_str = str(path)
        if path_str.endswith('.txt'):
            np.savetxt(path_str, data, *args, **kwargs)
        elif path_str.endswith('.npz'):
            np.savez(path_str, data, *args, **kwargs)
        else:
            np.save(path_str, data, *args, **kwargs)


class PandasSerializer(Serializer):
    """Serializer for pandas DataFrames supporting multiple file formats."""

    name = 'pandas'
    extensions = (
        '.csv', '.h5', '.hdf', '.hdf5', '.parquet', '.feather',
        '.xls', '.xlsx'
    )
    requires = 'pandas'

    @classmethod
    def load(
        cls, path: Union[str, Path], *args, **kwargs
    ) -> 'pandas.DataFrame':
        """Load data into a pandas DataFrame from a file."""
        import pandas as pd
        path_str = str(path)

        if path_str.endswith(('.h5', '.hdf', '.hdf5')):
            return pd.read_hdf(path_str, *args, **kwargs)
        elif path_str.endswith('.parquet'):
            return pd.read_parquet(path_str, *args, **kwargs)
        elif path_str.endswith('.feather'):
            return pd.read_feather(path_str, *args, **kwargs)
        elif path_str.endswith('.csv'):
            return pd.read_csv(path_str, *args, **kwargs)
        elif path_str.endswith(('.xls', '.xlsx')):
            return pd.read_excel(path_str, *args, **kwargs)
        else:
            raise ValueError(
                f"Unsupported file extension for pandas serializer: "
                f"'{Path(path_str).suffix}'"
            )

    @classmethod
    def dump(
        cls, path: Union[str, Path], data: 'pandas.DataFrame', *args, **kwargs
    ) -> None:
        """Write a pandas DataFrame to a file."""
        path_str = str(path)

        if path_str.endswith(('.h5', '.hdf', '.hdf5')):
            key = kwargs.pop('key', 'data')
            data.to_hdf(path_str, key=key, *args, **kwargs)
        elif path_str.endswith('.parquet'):
            data.to_parquet(path_str, *args, **kwargs)
        elif path_str.endswith('.feather'):
            data.to_feather(path_str, *args, **kwargs)
        elif path_str.endswith('.csv'):
            data.to_csv(path_str, *args, **kwargs)
        elif path_str.endswith(('.xls', '.xlsx')):
            data.to_excel(path_str, *args, **kwargs)
        else:
            raise ValueError(
                f"Unsupported file extension for pandas serializer: "
                f"'{Path(path_str).suffix}'"
            )

class XMLSerializer(Serializer):
    """Serializer for XML files."""

    name = 'xml'
    extensions = ('.xml',)
    requires = 'xml'

    @classmethod
    def load(
        cls, path: Union[str, Path], *args, **kwargs
    ) -> Any:
        """Load XML data from a file."""
        import xml.etree.ElementTree as ET
        return ET.parse(str(path), *args)

    @classmethod
    def dump(
        cls, path: Union[str, Path], data: Any, *args, **kwargs
    ) -> None:
        """Write XML data to a file."""
        import xml.etree.ElementTree as ET

        if not isinstance(data, (ET.ElementTree, ET.Element)):
            raise ValueError(
                "Data must be an xml.etree.ElementTree.ElementTree or Element"
            )

        tree = data if isinstance(data, ET.ElementTree) else ET.ElementTree(data)
        with open(str(path), 'wb') as f:
            tree.write(f, *args, **kwargs)