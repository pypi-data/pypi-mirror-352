from pathlib import Path
from typing import Optional, Union

from ..config.settings import SpecSettings, get_settings
from ..exceptions import SpecFileError, SpecValidationError
from ..logging.debug import debug_logger
from .path_utils import remove_specs_prefix


class PathResolver:
    """Handles path resolution and validation for spec operations.

    Provides consistent path handling with project boundary enforcement,
    validation, and conversion between different path contexts.
    """

    def __init__(self, settings: Optional[SpecSettings] = None):
        self.settings = settings or get_settings()

    def resolve_input_path(self, path_str: str) -> Path:
        """Resolve and validate an input path for spec operations.

        Args:
            path_str: Path string from user input (relative, absolute, or ".")

        Returns:
            Resolved path relative to project root

        Raises:
            SpecValidationError: If path is outside project boundaries
            SpecFileError: If path resolution fails
        """
        with debug_logger.timer(f"resolve_input_path_{Path(path_str).name}"):
            debug_logger.log("INFO", "Resolving input path", input_path=path_str)

            try:
                # Handle current directory shorthand
                if path_str == ".":
                    current_dir = Path.cwd()
                    debug_logger.log(
                        "INFO", "Resolving current directory", cwd=str(current_dir)
                    )
                    return self._ensure_within_project(current_dir)

                input_path = Path(path_str)

                # Handle absolute paths
                if input_path.is_absolute():
                    debug_logger.log(
                        "INFO", "Processing absolute path", path=str(input_path)
                    )
                    return self._ensure_within_project(input_path)

                # Handle relative paths - resolve relative to current working directory
                resolved_path = (Path.cwd() / input_path).resolve()
                debug_logger.log(
                    "INFO",
                    "Processing relative path",
                    original=path_str,
                    resolved=str(resolved_path),
                )
                return self._ensure_within_project(resolved_path)

            except OSError as e:
                raise SpecFileError(f"Failed to resolve path '{path_str}': {e}") from e

    def _ensure_within_project(self, absolute_path: Path) -> Path:
        """Ensure path is within project boundaries and return relative path.

        Args:
            absolute_path: Absolute path to validate

        Returns:
            Path relative to project root

        Raises:
            SpecValidationError: If path is outside project boundaries
        """
        try:
            # Resolve both paths to handle symlinks consistently
            resolved_absolute = absolute_path.resolve()
            resolved_root = self.settings.root_path.resolve()

            relative_path = resolved_absolute.relative_to(resolved_root)
            debug_logger.log(
                "INFO",
                "Path within project boundaries",
                absolute=str(resolved_absolute),
                relative=str(relative_path),
            )
            return relative_path

        except ValueError as e:
            raise SpecValidationError(
                f"Path '{absolute_path}' is outside project root '{self.settings.root_path}'"
            ) from e

    def convert_to_spec_directory_path(self, file_path: Path) -> Path:
        """Convert file path to corresponding spec directory path.

        Args:
            file_path: Path to source file (relative to project root)

        Returns:
            Path to spec directory (e.g., src/models.py -> .specs/src/models/)
        """
        debug_logger.log(
            "INFO", "Converting to spec directory path", source_file=str(file_path)
        )

        # Remove file extension and create directory path
        spec_dir = self.settings.specs_dir / file_path.parent / file_path.stem

        debug_logger.log(
            "INFO",
            "Spec directory path created",
            source_file=str(file_path),
            spec_dir=str(spec_dir),
        )

        return spec_dir

    def convert_from_specs_path(self, specs_path: Union[str, Path]) -> Path:
        """Convert path from .specs/ context to relative project path.

        Args:
            specs_path: Path that may be in .specs/ context

        Returns:
            Path relative to project root (for Git operations)
        """
        path_obj = Path(specs_path)

        # If absolute path, try to make relative to .specs/
        if path_obj.is_absolute():
            try:
                relative_path = path_obj.relative_to(self.settings.specs_dir)
                debug_logger.log(
                    "INFO",
                    "Converted absolute specs path",
                    absolute=str(path_obj),
                    relative=str(relative_path),
                )
                return relative_path
            except ValueError:
                # Path is not under .specs/, return as-is
                debug_logger.log(
                    "INFO",
                    "Path not under .specs/, returning as-is",
                    path=str(path_obj),
                )
                return path_obj

        # If path starts with .specs/ or .specs\, remove the prefix using cross-platform utility
        path_str = str(path_obj)
        if path_str.startswith((".specs/", ".specs\\")):
            relative_path_str = remove_specs_prefix(path_str)
            relative_path = Path(relative_path_str)
            debug_logger.log(
                "INFO",
                "Removed .specs prefix (cross-platform)",
                original=path_str,
                relative=str(relative_path),
                normalized=relative_path_str,
            )
            return relative_path

        # Return path as-is
        debug_logger.log(
            "INFO", "Path already relative, returning as-is", path=str(path_obj)
        )
        return path_obj

    def is_within_project(self, path: Path) -> bool:
        """Check if path is within the project root.

        Args:
            path: Path to check (can be relative or absolute)

        Returns:
            True if path is within project boundaries
        """
        try:
            if path.is_absolute():
                # Resolve both paths to handle symlinks consistently
                resolved_path = path.resolve()
                resolved_root = self.settings.root_path.resolve()
                resolved_path.relative_to(resolved_root)
            return True
        except ValueError:
            return False

    def get_absolute_path(self, relative_path: Path) -> Path:
        """Convert relative path to absolute path within project.

        Args:
            relative_path: Path relative to project root

        Returns:
            Absolute path
        """
        absolute_path = self.settings.root_path / relative_path
        debug_logger.log(
            "INFO",
            "Converted to absolute path",
            relative=str(relative_path),
            absolute=str(absolute_path),
        )
        return absolute_path

    def validate_path_exists(self, path: Path) -> None:
        """Validate that a path exists.

        Args:
            path: Path to validate (relative to project root)

        Raises:
            SpecFileError: If path does not exist
        """
        absolute_path = self.get_absolute_path(path) if not path.is_absolute() else path

        if not absolute_path.exists():
            raise SpecFileError(f"Path does not exist: {absolute_path}")

        debug_logger.log(
            "INFO", "Path exists validation passed", path=str(absolute_path)
        )
