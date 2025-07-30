from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from ..exceptions import SpecFileError
from ..logging.debug import debug_logger
from .file_metadata import FileMetadataExtractor
from .file_type_detector import FileTypeDetector
from .ignore_patterns import IgnorePatternMatcher


class DirectoryTraversal:
    """Handles intelligent directory traversal with filtering and analysis."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.ignore_matcher = IgnorePatternMatcher()
        self.type_detector = FileTypeDetector()
        self.metadata_extractor = FileMetadataExtractor()

    def find_processable_files(
        self, directory: Optional[Path] = None, max_files: Optional[int] = None
    ) -> List[Path]:
        """Find all processable files in a directory tree.

        Args:
            directory: Directory to search (defaults to root_path)
            max_files: Maximum number of files to return

        Returns:
            List of processable file paths
        """
        if directory is None:
            directory = self.root_path

        if not directory.exists() or not directory.is_dir():
            raise SpecFileError(f"Directory does not exist: {directory}")

        debug_logger.log(
            "INFO",
            "Finding processable files",
            directory=str(directory),
            max_files=max_files,
        )

        processable_files = []
        total_checked = 0

        try:
            for file_path in self._walk_directory(directory):
                total_checked += 1

                # Convert to relative path for ignore checking
                try:
                    relative_path = file_path.relative_to(self.root_path)
                except ValueError:
                    # File is outside root path, skip
                    continue

                # Check ignore patterns
                if self.ignore_matcher.should_ignore(relative_path):
                    continue

                # Check if processable
                if self.type_detector.is_processable_file(file_path):
                    processable_files.append(relative_path)

                    # Check max files limit
                    if max_files and len(processable_files) >= max_files:
                        debug_logger.log(
                            "INFO", "Reached max files limit", max_files=max_files
                        )
                        break

            debug_logger.log(
                "INFO",
                "Processable file search complete",
                directory=str(directory),
                total_checked=total_checked,
                processable_found=len(processable_files),
            )

            return processable_files

        except OSError as e:
            raise SpecFileError(
                f"Error traversing directory {directory}: {e}",
                {"directory": str(directory), "os_error": str(e)},
            ) from e

    def _walk_directory(self, directory: Path) -> Generator[Path, None, None]:
        """Walk directory tree, yielding file paths."""
        try:
            for item in directory.rglob("*"):
                if item.is_file():
                    yield item
        except OSError as e:
            debug_logger.log(
                "WARNING",
                "Error accessing path during walk",
                path=str(item),
                error=str(e),
            )

    def analyze_directory_structure(
        self, directory: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Analyze directory structure and provide detailed report.

        Args:
            directory: Directory to analyze (defaults to root_path)

        Returns:
            Dictionary with analysis results
        """
        if directory is None:
            directory = self.root_path

        debug_logger.log(
            "INFO", "Analyzing directory structure", directory=str(directory)
        )

        analysis: Dict[str, Any] = {
            "directory": str(directory),
            "total_files": 0,
            "processable_files": 0,
            "ignored_files": 0,
            "file_types": {},
            "file_categories": {},
            "largest_files": [],
            "deepest_path": "",
            "max_depth": 0,
        }

        try:
            max_depth = 0
            deepest_path = ""
            files_by_size = []

            for file_path in self._walk_directory(directory):
                analysis["total_files"] += 1

                # Calculate depth
                try:
                    relative_path = file_path.relative_to(directory)
                    depth = len(relative_path.parts)
                    if depth > max_depth:
                        max_depth = depth
                        deepest_path = str(relative_path)
                except ValueError:
                    continue

                # Check if ignored
                try:
                    relative_to_root = file_path.relative_to(self.root_path)
                    if self.ignore_matcher.should_ignore(relative_to_root):
                        analysis["ignored_files"] += 1
                        continue
                except ValueError:
                    continue

                # Analyze file type
                file_type = self.type_detector.get_file_type(file_path)
                analysis["file_types"][file_type] = (
                    analysis["file_types"].get(file_type, 0) + 1
                )

                # Analyze file category
                category = self.type_detector.get_file_category(file_path)
                if category:
                    analysis["file_categories"][category] = (
                        analysis["file_categories"].get(category, 0) + 1
                    )

                # Check if processable
                if self.type_detector.is_processable_file(file_path):
                    analysis["processable_files"] += 1

                # Track file sizes for largest files
                try:
                    size = file_path.stat().st_size
                    files_by_size.append((file_path, size))
                except OSError:
                    continue

            analysis["max_depth"] = max_depth
            analysis["deepest_path"] = deepest_path

            # Get top 5 largest files
            files_by_size.sort(key=lambda x: x[1], reverse=True)
            for file_path, size in files_by_size[:5]:
                try:
                    relative_path = file_path.relative_to(directory)
                    analysis["largest_files"].append(
                        {
                            "path": str(relative_path),
                            "size": size,
                            "size_formatted": self._format_size(size),
                        }
                    )
                except ValueError:
                    continue

            debug_logger.log(
                "INFO",
                "Directory analysis complete",
                directory=str(directory),
                total_files=analysis["total_files"],
                processable_files=analysis["processable_files"],
            )

            return analysis

        except OSError as e:
            raise SpecFileError(
                f"Error analyzing directory {directory}: {e}",
                {"directory": str(directory), "os_error": str(e)},
            ) from e

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        size_float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size_float < 1024.0:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024.0
        return f"{size_float:.1f} TB"

    def find_files_by_pattern(
        self, pattern: str, directory: Optional[Path] = None
    ) -> List[Path]:
        """Find files matching a pattern.

        Args:
            pattern: Glob pattern to match
            directory: Directory to search (defaults to root_path)

        Returns:
            List of matching file paths
        """
        if directory is None:
            directory = self.root_path

        debug_logger.log(
            "INFO",
            "Finding files by pattern",
            pattern=pattern,
            directory=str(directory),
        )

        try:
            matching_files = []

            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    try:
                        relative_path = file_path.relative_to(self.root_path)
                        if not self.ignore_matcher.should_ignore(relative_path):
                            matching_files.append(relative_path)
                    except ValueError:
                        continue

            debug_logger.log(
                "INFO",
                "Pattern search complete",
                pattern=pattern,
                matches=len(matching_files),
            )

            return matching_files

        except OSError as e:
            raise SpecFileError(
                f"Error searching for pattern {pattern} in {directory}: {e}",
                {"pattern": pattern, "directory": str(directory), "os_error": str(e)},
            ) from e

    def get_directory_summary(self, directory: Optional[Path] = None) -> Dict[str, Any]:
        """Get a summary of directory contents.

        Args:
            directory: Directory to summarize (defaults to root_path)

        Returns:
            Dictionary with directory summary
        """
        if directory is None:
            directory = self.root_path

        try:
            processable_files = self.find_processable_files(directory, max_files=100)
            analysis = self.analyze_directory_structure(directory)

            summary = {
                "directory": str(directory),
                "processable_file_count": len(processable_files),
                "total_file_count": analysis["total_files"],
                "ignored_file_count": analysis["ignored_files"],
                "primary_file_types": self._get_top_items(analysis["file_types"], 5),
                "primary_categories": self._get_top_items(
                    analysis["file_categories"], 3
                ),
                "directory_depth": analysis["max_depth"],
                "ready_for_spec_generation": len(processable_files) > 0,
            }

            return summary

        except Exception as e:
            debug_logger.log(
                "ERROR",
                "Error creating directory summary",
                directory=str(directory),
                error=str(e),
            )
            return {
                "directory": str(directory),
                "error": str(e),
                "ready_for_spec_generation": False,
            }

    def _get_top_items(
        self, items_dict: Dict[str, int], limit: int
    ) -> List[Dict[str, Any]]:
        """Get top items from a count dictionary."""
        sorted_items = sorted(items_dict.items(), key=lambda x: x[1], reverse=True)
        return [{"type": item, "count": count} for item, count in sorted_items[:limit]]
