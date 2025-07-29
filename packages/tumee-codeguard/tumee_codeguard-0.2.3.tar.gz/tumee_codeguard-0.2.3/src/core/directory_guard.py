"""
Directory-level guard system for CodeGuard using System A.

This module provides functionality for managing directory-level guard annotations
through .ai-attributes files using the new System A architecture.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from pathspec import PathSpec

from .guard_tag_parser import parse_guard_tag
from .types import DEFAULT_PERMISSIONS


class PatternRule:
    """
    A rule defined by a pattern and associated guard annotation.

    This class represents a single rule from an .ai-attributes file,
    consisting of a file pattern and a guard annotation.
    """

    def __init__(
        self,
        pattern: str,
        target: str,  # "ai" or "human"
        permission: str,  # "r", "w", "n", "contextWrite"
        identifiers: Optional[List[str]] = None,
        description: Optional[str] = None,
        source_file: Optional[Path] = None,
        source_line: Optional[int] = None,
        context_metadata: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize a pattern rule.

        Args:
            pattern: File pattern to match
            target: Target audience ("ai" or "human")
            permission: Permission level ("r", "w", "n", "contextWrite")
            identifiers: Optional list of specific identifiers (e.g., ["claude-4", "gpt-4"])
            description: Optional description of the rule
            source_file: Path to the source .ai-attributes file
            source_line: Line number in the source file
            context_metadata: Optional metadata for context files
        """
        self.pattern = pattern
        self.target = target
        self.permission = permission
        self.identifiers = identifiers
        self.description = description
        self.source_file = source_file
        self.source_line = source_line
        self.context_metadata = context_metadata

        # Create PathSpec for this single pattern
        self._pathspec = PathSpec.from_lines("gitwildmatch", [pattern])

    def applies_to_identifier(self, identifier: str) -> bool:
        """Check if this rule applies to a specific identifier."""
        if not self.identifiers:
            return True  # No specific identifiers means applies to all
        return identifier in self.identifiers

    def matches_path(self, path: Union[str, Path]) -> bool:
        """Check if this rule applies to the given file path."""
        if isinstance(path, Path):
            path = str(path)
        return self._pathspec.match_file(path)

    def __str__(self) -> str:
        """String representation of the rule."""
        if self.identifiers:
            target_str = f"{self.target}:{','.join(self.identifiers)}"
        else:
            target_str = self.target

        return f"{self.pattern} @guard:{target_str}:{self.permission}"


class DirectoryGuard:
    """
    Manages directory-level guard rules through .ai-attributes files.

    This class provides functionality for:
    - Loading and parsing .ai-attributes files
    - Matching files against directory-level rules
    - Determining effective permissions for files based on patterns
    - Managing hierarchical rule inheritance
    """

    AI_ATTRIBUTES_FILE = ".ai-attributes"

    def __init__(self, root_directory: Optional[Union[str, Path]] = None):
        """
        Initialize DirectoryGuard for a specific directory tree.

        Args:
            root_directory: Root directory to start searching from.
                           If None, uses current working directory.
        """
        if root_directory is None:
            root_directory = Path.cwd()
        elif isinstance(root_directory, str):
            root_directory = Path(root_directory)

        self.root_directory = root_directory.resolve()
        self.rules: List[PatternRule] = []
        self._loaded_files: Set[Path] = set()

    def load_rules_from_directory(self, directory: Optional[Union[str, Path]] = None) -> int:
        """
        Load rules from .ai-attributes files in the directory tree.

        Searches from the specified directory up to the root directory,
        loading rules from all .ai-attributes files found.

        Args:
            directory: Directory to start searching from.
                      If None, uses the configured root directory.

        Returns:
            Number of rules loaded
        """
        if directory is None:
            directory = self.root_directory
        elif isinstance(directory, str):
            directory = Path(directory)

        directory = directory.resolve()
        rules_loaded = 0

        # Search up the directory tree
        current_dir = directory
        while True:
            attrs_file = current_dir / self.AI_ATTRIBUTES_FILE
            if attrs_file.exists() and attrs_file not in self._loaded_files:
                rules_loaded += self._load_rules_from_file(attrs_file)
                self._loaded_files.add(attrs_file)

            # Stop if we've reached the root or gone outside our scope
            parent = current_dir.parent
            if parent == current_dir or not str(parent).startswith(str(self.root_directory)):
                break
            current_dir = parent

        return rules_loaded

    def _load_rules_from_file(self, file_path: Path) -> int:
        """
        Load rules from a single .ai-attributes file.

        Args:
            file_path: Path to the .ai-attributes file

        Returns:
            Number of rules loaded from this file
        """
        rules_loaded = 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse the line - format: "pattern @guard:target:permission"
                if "@guard:" not in line:
                    continue

                try:
                    pattern_part, guard_part = line.split("@guard:", 1)
                    pattern = pattern_part.strip()

                    # Parse the guard annotation
                    guard_line = f"# @guard:{guard_part.strip()}"
                    tag_info = parse_guard_tag(guard_line)

                    if tag_info:
                        # Create rule for AI permission
                        if tag_info.aiPermission:
                            rule = PatternRule(
                                pattern=pattern,
                                target="ai",
                                permission=tag_info.aiPermission,
                                identifiers=None,  # Could be extended to parse identifiers
                                source_file=file_path,
                                source_line=line_num,
                            )
                            self.rules.append(rule)
                            rules_loaded += 1

                        # Create rule for human permission
                        if tag_info.humanPermission:
                            rule = PatternRule(
                                pattern=pattern,
                                target="human",
                                permission=tag_info.humanPermission,
                                identifiers=None,
                                source_file=file_path,
                                source_line=line_num,
                            )
                            self.rules.append(rule)
                            rules_loaded += 1

                except Exception as e:
                    # Log parsing error but continue
                    print(f"Warning: Failed to parse rule at {file_path}:{line_num}: {e}")
                    continue

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return rules_loaded

    def get_effective_permissions(
        self, file_path: Union[str, Path], target: str = "ai", identifier: Optional[str] = None
    ) -> str:
        """
        Get the effective permission for a file based on directory rules.

        Args:
            file_path: Path to the file to check
            target: Target audience ("ai" or "human")
            identifier: Optional specific identifier

        Returns:
            Effective permission string ("r", "w", "n", "contextWrite")
            Returns default permission if no rules match.
        """
        if isinstance(file_path, Path):
            file_path = str(file_path)

        # Make path relative to root directory for matching
        try:
            abs_path = Path(file_path).resolve()
            rel_path = abs_path.relative_to(self.root_directory)
            match_path = str(rel_path)
        except ValueError:
            # File is outside root directory
            match_path = file_path

        # Find matching rules (most specific first)
        matching_rules = []
        for rule in self.rules:
            if (
                rule.target == target
                and rule.matches_path(match_path)
                and (identifier is None or rule.applies_to_identifier(identifier))
            ):
                matching_rules.append(rule)

        # If we have matching rules, return the most restrictive permission
        if matching_rules:
            # Order: "n" > "r" > "contextWrite" > "w"
            permissions = [rule.permission for rule in matching_rules]
            if "n" in permissions:
                return "n"
            elif "r" in permissions:
                return "r"
            elif "contextWrite" in permissions:
                return "contextWrite"
            else:
                return "w"

        # Return default permission from System A
        return DEFAULT_PERMISSIONS.get(target, "r")

    def list_rules(self, target: Optional[str] = None) -> List[PatternRule]:
        """
        List all loaded rules, optionally filtered by target.

        Args:
            target: Optional target to filter by ("ai" or "human")

        Returns:
            List of matching rules
        """
        if target is None:
            return self.rules.copy()
        return [rule for rule in self.rules if rule.target == target]

    def validate_rules(self) -> List[str]:
        """
        Validate all loaded rules and return any errors found.

        Returns:
            List of validation error messages
        """
        errors = []

        for rule in self.rules:
            # Check for valid permissions
            valid_permissions = {"r", "w", "n", "contextWrite"}
            if rule.permission not in valid_permissions:
                errors.append(
                    f"Invalid permission '{rule.permission}' in {rule.source_file}:{rule.source_line}"
                )

            # Check for valid targets
            valid_targets = {"ai", "human"}
            if rule.target not in valid_targets:
                errors.append(
                    f"Invalid target '{rule.target}' in {rule.source_file}:{rule.source_line}"
                )

        return errors

    def find_conflicts(self) -> List[Tuple[PatternRule, PatternRule]]:
        """
        Find conflicting rules (same pattern, target, but different permissions).

        Returns:
            List of tuples containing conflicting rule pairs
        """
        conflicts = []

        for i, rule1 in enumerate(self.rules):
            for rule2 in self.rules[i + 1 :]:
                if (
                    rule1.pattern == rule2.pattern
                    and rule1.target == rule2.target
                    and rule1.permission != rule2.permission
                ):
                    conflicts.append((rule1, rule2))

        return conflicts
