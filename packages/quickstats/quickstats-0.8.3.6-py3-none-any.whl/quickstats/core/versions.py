from __future__ import annotations

from typing import Union, Tuple, Type, TypeVar, Any
import re
import numbers
from functools import total_ordering
from dataclasses import dataclass

T = TypeVar("T", bound="BaseVersion")

@dataclass(frozen=True)
class VersionInfo:
    """Immutable container for version information."""
    major: int
    minor: int
    micro: int = 0
    prerelease: str = ""
    build: str = ""

    def __post_init__(self) -> None:
        """Validate version components after initialization."""
        for component in (self.major, self.minor, self.micro):
            if not isinstance(component, int) or component < 0:
                raise ValueError("Version components must be non-negative integers")

    def to_tuple(self) -> Tuple[int, int, int, str, str]:
        """Convert to tuple representation."""
        return (self.major, self.minor, self.micro, self.prerelease, self.build)


@total_ordering
class BaseVersion:
    """Abstract base class for version implementations."""

    def __init__(self) -> None:
        """Initialize the base version."""
        self._version_info: VersionInfo

    @property
    def version_info(self) -> VersionInfo:
        """Get version information."""
        return self._version_info

    @property
    def major(self) -> int:
        return self._version_info.major

    @property
    def minor(self) -> int:
        return self._version_info.minor

    @property
    def micro(self) -> int:
        return self._version_info.micro

    @property
    def prerelease(self) -> str:
        return self._version_info.prerelease

    @property
    def build(self) -> str:
        return self._version_info.build

    def to_tuple(self) -> Tuple[int, int, int, str, str]:
        return self._version_info.to_tuple()

    def __eq__(self, other: object) -> bool:
        other = self.__class__.cast(other)
        return self.to_tuple()[:4] == other.to_tuple()[:4]  # Ignore build

    def __lt__(self, other: object) -> bool:
        other = self.__class__.cast(other)
        self_tuple = self.to_tuple()
        other_tuple = other.to_tuple()
        
        # Compare major.minor.micro
        for v1, v2 in zip(self_tuple[:3], other_tuple[:3]):
            if v1 != v2:
                return v1 < v2
                
        # Compare pre-release versions
        return self._compare_prerelease(self.prerelease, other.prerelease) < 0

    @staticmethod
    def _compare_prerelease(pre1: str, pre2: str) -> int:
        """Compare pre-release versions according to SemVer rules."""
        if not pre1 and not pre2:
            return 0
        if not pre1:
            return 1  # No pre-release is higher
        if not pre2:
            return -1

        pre1_parts = pre1.split('.')
        pre2_parts = pre2.split('.')
        
        for p1, p2 in zip_longest(pre1_parts, pre2_parts, fillvalue=None):
            if p1 is None:
                return -1
            if p2 is None:
                return 1
                
            n1 = int(p1) if p1.isdigit() else None
            n2 = int(p2) if p2.isdigit() else None
            
            if n1 is not None and n2 is not None:
                if n1 != n2:
                    return -1 if n1 < n2 else 1
            elif n1 is not None:
                return -1  # Numeric has lower precedence
            elif n2 is not None:
                return 1
            elif p1 != p2:
                return -1 if p1 < p2 else 1
        
        return 0

    @classmethod
    def cast(cls: Type[T], other: Any) -> T:
        """Cast a value to a Version instance."""
        if isinstance(other, cls):
            return other
        if isinstance(other, BaseVersion):
            return cls(other.to_tuple())
        try:
            return cls(other)
        except (ValueError, TypeError) as e:
            raise TypeError(f"Cannot cast {type(other).__name__} to {cls.__name__}") from e

    def __hash__(self) -> int:
        return hash(self.to_tuple()[:4])  # Ignore build


class Version(BaseVersion):
    """A class to represent and compare package versions with pre-release and build metadata."""

    _VERSION_PATTERN = re.compile(
        r'^(\d+)\.(\d+)(?:\.(\d+))?'        # Core version (major.minor.micro)
        r'(?:-([a-zA-Z0-9.-]+))?'           # Optional pre-release
        r'(?:\+([a-zA-Z0-9.-]+))?$'         # Optional build metadata
    )

    def __init__(
        self,
        version: Union[str, Tuple[Union[int, str], ...], Version, VersionInfo]
    ) -> None:
        """Initialize a Version instance."""
        super().__init__()

        if isinstance(version, str):
            parsed_tuple = self._parse_version_string(version)
        elif isinstance(version, tuple):
            parsed_tuple = self._parse_version_tuple(version)
        elif isinstance(version, Version):
            parsed_tuple = version.to_tuple()
        elif isinstance(version, VersionInfo):
            parsed_tuple = version.to_tuple()
        else:
            raise TypeError("Version must be a string, tuple, Version, or VersionInfo instance")

        self._version_info = VersionInfo(*parsed_tuple)

    @classmethod
    def _parse_version_string(cls, version: str) -> Tuple[int, int, int, str, str]:
        """Parse a version string into a tuple."""
        if not version:
            raise ValueError("Version string cannot be empty")
            
        match = cls._VERSION_PATTERN.match(version)
        if not match:
            raise ValueError("Invalid version string format")
            
        major, minor, micro, prerelease, build = match.groups()
        try:
            major_val = int(major)
            minor_val = int(minor)
            micro_val = int(micro) if micro else 0
        except (ValueError, TypeError) as e:
            raise ValueError("Version components must be valid integers") from e
            
        return major_val, minor_val, micro_val, prerelease or "", build or ""

    @classmethod
    def _parse_version_tuple(cls, version: Tuple[Union[int, str], ...]) -> Tuple[int, int, int, str, str]:
        """Validate a version tuple."""
        if not (2 <= len(version) <= 5):
            raise ValueError("Version tuple must have 2 to 5 elements")

        major, minor, *optional = version
        if not (isinstance(major, int) and isinstance(minor, int)):
            raise ValueError("Major and minor versions must be integers")

        micro = 0
        prerelease = ""
        build = ""

        if optional:
            first = optional[0]
            if isinstance(first, int):
                micro = first
            elif isinstance(first, str):
                prerelease = first
            else:
                raise ValueError("Optional third element must be micro (int) or prerelease (str)")

            if len(optional) >= 2:
                if not isinstance(optional[1], str):
                    raise ValueError("Pre-release identifier must be a string")
                prerelease = optional[1]
            
            if len(optional) == 3:
                if not isinstance(optional[2], str):
                    raise ValueError("Build metadata must be a string")
                build = optional[2]

        return major, minor, micro, prerelease, build

    def __repr__(self) -> str:
        components = [self.major, self.minor]
        if self.micro or self.prerelease or self.build:
            components.append(self.micro)
        if self.prerelease:
            components.append(repr(self.prerelease))
        if self.build:
            components.append(repr(self.build))
        return f"{self.__class__.__name__}({', '.join(str(c) for c in components)})"

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}"
        if self.micro or self.prerelease or self.build:
            version += f".{self.micro}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version


class ROOTVersion(Version):
    """Class representing a ROOT version number."""

    _ROOT_VERSION_PATTERN = re.compile(
        r"(?P<major>\d+)\.(?P<minor>\d+)[./](?P<micro>\d+)"
    )

    def __init__(
        self,
        version: Union[int, str, Tuple[int, ...], Version, VersionInfo]
    ) -> None:
        """Initialize a ROOTVersion instance."""
        if isinstance(version, numbers.Integral):
            version = self._parse_version_int(version)
        super().__init__(version)

    @classmethod
    def _parse_version_int(cls, version: int) -> Tuple[int, int, int, str, str]:
        """Parse an integer version number."""
        if version < 10000:
            raise ValueError(f"{version} is not a valid ROOT version integer")

        major = version // 10000
        minor = (version // 100) % 100
        micro = version % 100

        return major, minor, micro, "", ""

    @classmethod
    def _parse_version_string(cls, version: str) -> Tuple[int, int, int, str, str]:
        """Parse a ROOT version string."""
        if not version:
            raise ValueError("Version string cannot be empty")
            
        match = cls._ROOT_VERSION_PATTERN.match(version)
        if not match:
            raise ValueError(f"'{version}' is not a valid ROOT version string")

        try:
            parts = [int(match.group(name)) for name in ('major', 'minor', 'micro')]
            return *parts, "", ""
        except ValueError as e:
            raise ValueError("Version components must be valid integers") from e

    def __str__(self) -> str:
        """Return the ROOT-style string representation."""
        return f"{self.major}.{self.minor:02d}/{self.micro:02d}"

    def to_int(self) -> int:
        """Convert to ROOT integer version format."""
        if any(x >= 100 for x in (self.minor, self.micro)):
            raise ValueError("Minor and micro versions must be less than 100")
        return self.major * 10000 + self.minor * 100 + self.micro