from typing import Optional, Union, List, Dict, Tuple
import os
import copy

from quickstats.utils.string_utils import partial_formatter, get_field_names

__all__ = ['DynamicFilePath', 'PathManager']

PathType = Union[str, 'DynamicFilePath', Tuple[Optional[str], str]]

class DynamicFilePath:
    """
    Represents a dynamic file path that can be formatted with parameters.

    Parameters
    ----------------------------------------------------
    basename : str
        The base name of the file.
    dirname : str, optional
        The directory name of the file.
    """

    def __init__(self, basename: str, dirname: Optional[str] = None) -> None:
        self.dirname = dirname
        self.basename = basename

    def __repr__(self) -> str:
        return f"DynamicFilePath(dirname={self.dirname}, basename={self.basename})"

    @staticmethod
    def _format_path(path: str, partial_format: bool = False, **parameters) -> str:
        """
        Format a path string using `partial_formatter`.

        Parameters
        ----------------------------------------------------
        path : str
            The path string to format.
        partial_format : bool
            Whether to allow partially filled format fields.
        **parameters :
            Parameters to fill in the path format.

        Returns
        ----------------------------------------------------
        str
            The formatted path string.

        Raises
        ----------------------------------------------------
        RuntimeError
            If required fields are missing and partial_format is False.
        """
        formatted_path = partial_formatter.format(path, **parameters)

        if partial_format or partial_formatter.is_fully_formatted(formatted_path):
            return formatted_path

        required_fields = get_field_names(formatted_path)
        missing_fields = [field for field in required_fields if field not in parameters]

        raise RuntimeError(
            f"Missing the following required field names for path formatting: {missing_fields}"
        )

    def resolve_basename(self, partial_format: bool = False, **parameters) -> str:
        """
        Resolve the base name with the given parameters.

        Parameters
        ----------------------------------------------------
        partial_format : bool, optional
            Whether to allow partially filled format fields.
        **parameters :
            Parameters to format the base name.

        Returns
        ----------------------------------------------------
        str
            The formatted base name.
        """
        return self._format_path(self.basename, partial_format=partial_format, **parameters)

    def resolve_dirname(self, partial_format: bool = False, **parameters) -> str:
        """
        Resolve the directory name with the given parameters.

        Parameters
        ----------------------------------------------------
        partial_format : bool, optional
            Whether to allow partially filled format fields.
        **parameters :
            Parameters to format the directory name.

        Returns
        ----------------------------------------------------
        str
            The formatted directory name, or an empty string if dirname is None.
        """
        return (
            self._format_path(self.dirname, partial_format=partial_format, **parameters)
            if self.dirname
            else ""
        )


class PathManager:
    """
    Tool for managing file and directory paths.

    Parameters
    ----------------------------------------------------
    base_path : str, optional
        The base directory path for all paths defined (except absolute paths).
    directories : dict of {str : PathType}, optional
        Managed directories, mapping a key to a path definition.
    files : dict of {str : PathType}, optional
        Managed files, mapping a key to a path definition.
    """

    DEFAULT_DIRECTORIES: Dict[str, DynamicFilePath] = {}
    DEFAULT_FILES: Dict[str, DynamicFilePath] = {}

    def __init__(
        self,
        base_path: Optional[str] = None,
        directories: Optional[Dict[str, PathType]] = None,
        files: Optional[Dict[str, PathType]] = None
    ) -> None:
        self.base_path = base_path

        # Initialize directory storage
        self.directories = copy.deepcopy(self.DEFAULT_DIRECTORIES)
        if directories:
            self.update_directories(directories)

        # Initialize file storage
        self.files = copy.deepcopy(self.DEFAULT_FILES)
        if files:
            self.update_files(files)

    @property
    def directories(self) -> Dict[str, DynamicFilePath]:
        """
        Accessor for the dictionary of managed directories.
        """
        return self._directories

    @directories.setter
    def directories(self, values: Optional[Dict[str, PathType]]) -> None:
        """
        Setter for the dictionary of managed directories.
        """
        self._directories = self._parse_paths(values)

    @property
    def files(self) -> Dict[str, DynamicFilePath]:
        """
        Accessor for the dictionary of managed files.
        """
        return self._files

    @files.setter
    def files(self, values: Optional[Dict[str, PathType]]) -> None:
        """
        Setter for the dictionary of managed files.
        """
        self._files = self._parse_paths(values)

    @staticmethod
    def _parse_paths(paths: Optional[Dict[str, PathType]]) -> Dict[str, DynamicFilePath]:
        """
        Parse a dictionary of paths into DynamicFilePath objects.

        Parameters
        ----------------------------------------------------
        paths : dict of {str : PathType}, optional
            The paths to parse.

        Returns
        ----------------------------------------------------
        dict of {str : DynamicFilePath}
            The parsed paths.

        Raises
        ----------------------------------------------------
        TypeError
            If `paths` is not a dictionary or contains invalid keys or values.
        """
        if paths is None:
            return {}
        if not isinstance(paths, dict):
            raise TypeError("Paths must be specified in dict format")

        parsed_paths: Dict[str, DynamicFilePath] = {}
        for key, value in paths.items():
            if not isinstance(key, str):
                raise TypeError("Path name must be a string")
            parsed_paths[key] = PathManager._parse_path(value)
        return parsed_paths

    @staticmethod
    def _parse_path(path: PathType) -> DynamicFilePath:
        """
        Parse a path into a DynamicFilePath object.

        Parameters
        ----------------------------------------------------
        path : PathType
            The path to parse.

        Returns
        ----------------------------------------------------
        DynamicFilePath
            The parsed path.

        Raises
        ----------------------------------------------------
        ValueError
            If `path` is a tuple but has a length other than 2.
        TypeError
            If `path` is not a tuple, string, or DynamicFilePath.
        """
        if isinstance(path, tuple):
            if len(path) != 2:
                raise ValueError("A tuple path must have two elements (dirname, basename)")
            return DynamicFilePath(path[1], path[0])
        if isinstance(path, str):
            return DynamicFilePath(path)
        if isinstance(path, DynamicFilePath):
            return path
        raise TypeError("Path must be a tuple, string, or DynamicFilePath")

    def update_directories(self, directories: Optional[Dict[str, PathType]] = None) -> None:
        """
        Update the managed directories.

        Parameters
        ----------------------------------------------------
        directories : dict of {str : PathType}, optional
            Directories to update.
        """
        new_directories = self._parse_paths(directories)
        self._directories.update(new_directories)

    def update_files(self, files: Optional[Dict[str, PathType]] = None) -> None:
        """
        Update the managed files.

        Parameters
        ----------------------------------------------------
        files : dict of {str : PathType}, optional
            Files to update.
        """
        new_files = self._parse_paths(files)
        self._files.update(new_files)

    def set_directory(self, directory_name: str, path: PathType, absolute: bool = False) -> None:
        """
        Set a directory path.

        Parameters
        ----------------------------------------------------
        directory_name : str
            The name (key) for the directory.
        path : PathType
            The path to associate with `directory_name`.
        absolute : bool
            Whether to convert the path's basename to an absolute path.
        """
        parsed_path = self._parse_path(path)
        if absolute:
            parsed_path.basename = os.path.abspath(parsed_path.basename)
        self.update_directories({directory_name: parsed_path})

    def set_file(self, file_name: str, file: PathType) -> None:
        """
        Set a file path.

        Parameters
        ----------------------------------------------------
        file_name : str
            The name (key) for the file.
        file : PathType
            The path to associate with `file_name`.
        """
        self.update_files({file_name: self._parse_path(file)})

    def set_base_path(self, path: str) -> None:
        """
        Set the base path for the manager.

        Parameters
        ----------------------------------------------------
        path : str
            The base path to set.
        """
        self.base_path = path

    def get_base_path(self) -> Optional[str]:
        """
        Get the base path for the manager.

        Returns
        ----------------------------------------------------
        str or None
            The base path, or None if not set.
        """
        return self.base_path

    def get_basename(self, filename: str, partial_format: bool = False, **parameters) -> str:
        """
        Convenience method to retrieve only the resolved basename of a file.

        Parameters
        ----------------------------------------------------
        filename : str
            The file name (key) in the `files` dictionary.
        partial_format : bool
            Whether to allow partially filled format fields.
        **parameters :
            Additional parameters for formatting the path.

        Returns
        ----------------------------------------------------
        str
            The resolved file basename.
        """
        return self.get_file(
            filename,
            basename_only=True,
            partial_format=partial_format,
            **parameters
        )

    def get_resolved_path(
        self,
        path: PathType,
        subdirectory: Optional[str] = None,
        basename_only: bool = False,
        partial_format: bool = False,
        **parameters
    ) -> str:
        """
        Resolve a path with optional parameters.

        Parameters
        ----------------------------------------------------
        path : PathType
            The path to resolve.
        subdirectory : str, optional
            An optional subdirectory to join before the basename.
        basename_only : bool
            Whether to return the base name only, by default False.
        partial_format : bool
            Whether to allow partially filled format fields.
        **parameters :
            Additional parameters for formatting the path.

        Returns
        ----------------------------------------------------
        str
            The resolved path.
        """
        # Ensure we have a DynamicFilePath object
        if not isinstance(path, DynamicFilePath):
            path = self._parse_path(path)

        basename = path.resolve_basename(partial_format=partial_format, **parameters)

        if basename_only:
            return basename

        if subdirectory:
            basename = os.path.join(subdirectory, basename)

        if path.dirname:
            dirname_key = path.resolve_dirname(partial_format=partial_format, **parameters)
            dirname = self.get_directory(dirname_key, partial_format=partial_format, **parameters)
        elif self.base_path:
            dirname = self.base_path
        else:
            dirname = ""

        return os.path.join(dirname, basename)

    def get_directory(
        self,
        dirname: str,
        check_exist: bool = False,
        basename_only: bool = False,
        partial_format: bool = False,
        **parameters
    ) -> str:
        """
        Get a resolved directory path.

        Parameters
        ----------------------------------------------------
        dirname : str
            The key in `directories`.
        check_exist : bool
            Whether to check if the resolved directory actually exists.
        basename_only : bool
            Whether to return only the directory basename, by default False.            
        partial_format : bool
            Whether to allow partially filled format fields.
        **parameters :
            Additional parameters for formatting the path.

        Returns
        ----------------------------------------------------
        str
            The resolved directory path.

        Raises
        ----------------------------------------------------
        KeyError
            If dirname is not found in `directories`.
        ValueError
            If partial_format is True but check_exist is also True.
        FileNotFoundError
            If check_exist is True but the directory does not exist.
        """
        if dirname not in self.directories:
            raise KeyError(f'Unrecognized directory name "{dirname}"')

        if partial_format and check_exist:
            raise ValueError("Partial format is not allowed when `check_exist` is True")

        directory_obj = self.directories[dirname]
        resolved_directory = self.get_resolved_path(
            directory_obj,
            basename_only=basename_only,
            partial_format=partial_format,
            **parameters
        )

        if check_exist and not os.path.exists(resolved_directory):
            raise FileNotFoundError(f'Directory "{resolved_directory}" does not exist')

        return resolved_directory

    def get_file(
        self,
        filename: str,
        check_exist: bool = False,
        subdirectory: Optional[str] = None,
        basename_only: bool = False,
        partial_format: bool = False,
        **parameters
    ) -> str:
        """
        Get a resolved file path.

        Parameters
        ----------------------------------------------------
        filename : str
            The key in `files`.
        check_exist : bool
            Whether to check if the resolved file actually exists.
        subdirectory : str, optional
            An optional subdirectory to join before the basename.
        basename_only : bool
            Whether to return only the file basename, by default False.
        partial_format : bool
            Whether to allow partially filled format fields.
        **parameters :
            Additional parameters for formatting the path.

        Returns
        ----------------------------------------------------
        str
            The resolved file path.

        Raises
        ----------------------------------------------------
        KeyError
            If filename is not found in `files`.
        ValueError
            If partial_format is True but check_exist is also True.
        FileNotFoundError
            If check_exist is True but the file does not exist.
        """
        if filename not in self.files:
            raise KeyError(f'Unrecognized file name "{filename}"')

        if partial_format and check_exist:
            raise ValueError("Partial format is not allowed when `check_exist` is True")

        file_obj = self.files[filename]
        resolved_file = self.get_resolved_path(
            file_obj,
            subdirectory=subdirectory,
            basename_only=basename_only,
            partial_format=partial_format,
            **parameters
        )

        if check_exist and not os.path.exists(resolved_file):
            raise FileNotFoundError(f'File "{resolved_file}" does not exist')

        return resolved_file

    @staticmethod
    def check_files(files: List[str], file_only: bool = True, check_exist: bool = True) -> None:
        """
        Check if files exist and optionally that they are files (not directories).

        Parameters
        ----------------------------------------------------
        files : list of str
            List of file paths to check.
        file_only : bool
            Whether to check if the paths are not directories.
        check_exist : bool
            Whether to check if the files exist.

        Raises
        ----------------------------------------------------
        FileNotFoundError
            If a file does not exist and check_exist is True.
        IsADirectoryError
            If a path is a directory and file_only is True.
        """
        if check_exist:
            for file_path in files:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f'File "{file_path}" does not exist')

        if file_only:
            for file_path in files:
                if os.path.isdir(file_path):
                    raise IsADirectoryError(f'"{file_path}" is a directory')

    def get_directories(
        self,
        dirnames: Optional[List[str]] = None,
        partial_format: bool = False,
        check_exist: bool = False,
        **parameters
    ) -> Dict[str, str]:
        """
        Get resolved paths for multiple directories.

        Parameters
        ----------------------------------------------------
        dirnames : list of str, optional
            List of directory names to resolve. If None, resolve all known directories.
        partial_format : bool
            Whether to allow partially filled format fields.
        check_exist : bool
            Whether to check if the directories exist.
        **parameters :
            Additional parameters for formatting the directory paths.

        Returns
        ----------------------------------------------------
        dict of {str : str}
            A dictionary mapping directory names to their resolved paths.
        """
        directories = {}
        if dirnames is None:
            dirnames = list(self.directories.keys())

        for dirname in dirnames:
            directories[dirname] = self.get_directory(
                dirname,
                check_exist=check_exist,
                partial_format=partial_format,
                **parameters
            )
        return directories

    def get_files(
        self,
        filenames: Optional[List[str]] = None,
        partial_format: bool = False,
        check_exist: bool = False,
        **parameters
    ) -> Dict[str, str]:
        """
        Get resolved paths for multiple files.

        Parameters
        ----------------------------------------------------
        filenames : list of str, optional
            List of file names to resolve. If None, resolve all known files.
        partial_format : bool
            Whether to allow partially filled format fields.
        check_exist : bool
            Whether to check if the files exist.
        **parameters :
            Additional parameters for formatting the file paths.

        Returns
        ----------------------------------------------------
        dict of {str : str}
            A dictionary mapping file names to their resolved paths.
        """
        file_paths = {}
        if filenames is None:
            filenames = list(self.files.keys())

        for filename in filenames:
            file_paths[filename] = self.get_file(
                filename,
                check_exist=check_exist,
                partial_format=partial_format,
                **parameters
            )
        return file_paths

    def get_relpath(self, path: str) -> str:
        """
        Get a path relative to the base path if one is set.

        Parameters
        ----------------------------------------------------
        path : str
            The path to make relative.

        Returns
        ----------------------------------------------------
        str
            The relative path (or the original path if base_path is None).
        """
        if self.base_path is None:
            return path
        return os.path.join(self.base_path, path)

    def directory_exists(self, dirname: str, **parameters) -> bool:
        """
        Check if a directory exists.

        Parameters
        ----------------------------------------------------
        dirname : str
            The key in `directories`.
        **parameters :
            Additional parameters for formatting the directory path.

        Returns
        ----------------------------------------------------
        bool
            True if the directory exists, False otherwise.
        """
        directory_path = self.get_directory(dirname, **parameters)
        return os.path.exists(directory_path)

    def file_exists(self, filename: str, **parameters) -> bool:
        """
        Check if a file exists.

        Parameters
        ----------------------------------------------------
        filename : str
            The key in `files`.
        **parameters :
            Additional parameters for formatting the file path.

        Returns
        ----------------------------------------------------
        bool
            True if the file exists, False otherwise.
        """
        file_path = self.get_file(filename, **parameters)
        return os.path.exists(file_path)

    def check_directory(self, dirname: str, **parameters) -> None:
        """
        Check if a directory exists and raise an exception if not.

        Parameters
        ----------------------------------------------------
        dirname : str
            The key in `directories`.
        **parameters :
            Additional parameters for formatting the directory path.

        Raises
        ----------------------------------------------------
        FileNotFoundError
            If the directory does not exist.
        """
        self.get_directory(dirname, check_exist=True, **parameters)

    def check_file(self, filename: str, **parameters) -> None:
        """
        Check if a file exists and raise an exception if not.

        Parameters
        ----------------------------------------------------
        filename : str
            The key in `files`.
        **parameters :
            Additional parameters for formatting the file path.

        Raises
        ----------------------------------------------------
        FileNotFoundError
            If the file does not exist.
        """
        self.get_file(filename, check_exist=True, **parameters)

    def makedirs(
        self,
        include_names: Optional[List[str]] = None,
        exclude_names: Optional[List[str]] = None,
        **parameters
    ) -> None:
        """
        Create directories for the specified directory names.

        Parameters
        ----------------------------------------------------
        include_names : list of str, optional
            Names of directories to include. If None, all known directories are included.
        exclude_names : list of str, optional
            Names of directories to exclude. If None, none are excluded.
        **parameters :
            Additional parameters for formatting the directory paths.
        """
        if include_names is None:
            include_names = list(self.directories.keys())
        if exclude_names is None:
            exclude_names = []

        dirnames_to_make = list(set(include_names) - set(exclude_names))
        resolved_dirnames = self.get_directories(dirnames_to_make, **parameters)

        from quickstats.utils.common_utils import batch_makedirs
        batch_makedirs(resolved_dirnames)

    def makedir_for_files(self, filenames: Union[str, List[str]], **parameters) -> None:
        """
        Create directories for the specified file names.

        Parameters
        ----------------------------------------------------
        filenames : str or list of str
            A file name or list of file names defined in `files`.
        **parameters :
            Additional parameters for formatting the file paths.
        """
        if isinstance(filenames, str):
            filenames = [filenames]

        resolved_files = self.get_files(filenames, **parameters)
        resolved_dirnames = [os.path.dirname(file_path) for file_path in resolved_files.values()]

        from quickstats.utils.common_utils import batch_makedirs
        batch_makedirs(resolved_dirnames)