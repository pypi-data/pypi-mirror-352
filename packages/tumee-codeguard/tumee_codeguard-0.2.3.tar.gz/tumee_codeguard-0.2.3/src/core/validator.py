"""
Core validation logic for CodeGuard using System A.

This module contains the main validation engine that orchestrates the process
of detecting guard annotations, calculating hashes, and identifying violations
using the new System A architecture.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

from .comparison_engine import ComparisonEngine, GuardViolation, ViolationSeverity
from .directory_guard import DirectoryGuard
from .processor import detect_language, process_document
from .types import GuardTag, LinePermission


class ValidationResult:
    """
    Contains the results of a validation operation using System A.
    """

    def __init__(
        self,
        files_checked: int = 0,
        violations: Optional[List[GuardViolation]] = None,
        directory_guards_used: bool = False,
        directory_rules_applied: int = 0,
        guard_tags_found: int = 0,
        line_permissions_calculated: int = 0,
    ):
        """
        Initialize validation result.

        Args:
            files_checked: Number of files checked
            violations: List of violations found
            directory_guards_used: Whether directory guards were used
            directory_rules_applied: Number of directory rules applied
            guard_tags_found: Number of guard tags found
            line_permissions_calculated: Number of lines with permissions calculated
        """
        self.files_checked = files_checked
        self.violations = violations or []
        self.directory_guards_used = directory_guards_used
        self.directory_rules_applied = directory_rules_applied
        self.guard_tags_found = guard_tags_found
        self.line_permissions_calculated = line_permissions_calculated

    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0

    @property
    def violation_count(self) -> int:
        """Get total number of violations."""
        return len(self.violations)


class CodeGuardValidator:
    """
    Main validator class using System A architecture.

    This class orchestrates the validation process by:
    1. Processing documents to extract guard tags and line permissions
    2. Applying directory-level rules
    3. Comparing original and modified versions
    4. Detecting violations
    """

    def __init__(
        self,
        normalize_whitespace: bool = True,
        normalize_line_endings: bool = True,
        ignore_blank_lines: bool = True,
        ignore_indentation: bool = False,
        context_lines: int = 3,
        enable_directory_guards: bool = True,
        root_directory: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize the validator.

        Args:
            normalize_whitespace: Normalize whitespace in comparisons
            normalize_line_endings: Normalize line endings in comparisons
            ignore_blank_lines: Ignore blank lines in comparisons
            ignore_indentation: Ignore indentation in comparisons
            context_lines: Number of context lines around violations
            enable_directory_guards: Enable directory-level guard processing
            root_directory: Root directory for directory guards
        """
        self.comparison_engine = ComparisonEngine(
            normalize_whitespace=normalize_whitespace,
            normalize_line_endings=normalize_line_endings,
            ignore_blank_lines=ignore_blank_lines,
            ignore_indentation=ignore_indentation,
            context_lines=context_lines,
        )

        self.directory_guard = None
        if enable_directory_guards:
            self.directory_guard = DirectoryGuard(root_directory)

    def validate_file(
        self,
        file_path: Union[str, Path],
        original_content: Optional[str] = None,
        modified_content: Optional[str] = None,
        target: str = "ai",
        identifier: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate a single file for guard violations.

        Args:
            file_path: Path to the file to validate
            original_content: Original file content (if None, reads from file)
            modified_content: Modified file content (if None, same as original)
            target: Target audience ("ai" or "human")
            identifier: Optional specific identifier

        Returns:
            ValidationResult containing violations and statistics
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Read file content if not provided
        if original_content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    original_content = f.read()
            except Exception as e:
                return ValidationResult(
                    files_checked=1,
                    violations=[
                        GuardViolation(
                            file=str(file_path),
                            line_start=1,
                            line_end=1,
                            severity=ViolationSeverity.ERROR,
                            violation_type="file_read_error",
                            message=f"Failed to read file: {e}",
                            target=target,
                        )
                    ],
                )

        if modified_content is None:
            modified_content = original_content

        # Detect language
        language_id = detect_language(str(file_path))

        # Process original content
        original_tags, original_permissions = process_document(original_content, language_id)

        # Process modified content
        modified_tags, modified_permissions = process_document(modified_content, language_id)

        # Apply directory-level permissions if enabled
        directory_rules_applied = 0
        if self.directory_guard:
            directory_rules_applied = self._apply_directory_permissions(
                file_path, original_permissions, modified_permissions, target, identifier
            )

        # Compare for violations
        violations = []

        # Compare permissions
        permission_violations = self.comparison_engine.compare_permissions(
            original_permissions,
            modified_permissions,
            str(file_path),
            original_content,
            modified_content,
            target,
            identifier,
        )
        violations.extend(permission_violations)

        # Compare guard tags
        tag_violations = self.comparison_engine.compare_guard_tags(
            original_tags, modified_tags, str(file_path)
        )
        violations.extend(tag_violations)

        return ValidationResult(
            files_checked=1,
            violations=violations,
            directory_guards_used=self.directory_guard is not None,
            directory_rules_applied=directory_rules_applied,
            guard_tags_found=len(original_tags),
            line_permissions_calculated=len(original_permissions),
        )

    def _apply_directory_permissions(
        self,
        file_path: Path,
        original_permissions: Dict[int, LinePermission],
        modified_permissions: Dict[int, LinePermission],
        target: str,
        identifier: Optional[str] = None,
    ) -> int:
        """
        Apply directory-level permissions to line permissions.

        Args:
            file_path: Path to the file
            original_permissions: Original line permissions to update
            modified_permissions: Modified line permissions to update
            target: Target audience
            identifier: Optional specific identifier

        Returns:
            Number of directory rules applied
        """
        if not self.directory_guard:
            return 0

        # Load directory rules
        rules_loaded = self.directory_guard.load_rules_from_directory(file_path.parent)

        # Get effective permission for this file
        effective_permission = self.directory_guard.get_effective_permissions(
            file_path, target, identifier
        )

        # Apply to all lines that don't have explicit permissions
        rules_applied = 0

        for line_permissions in [original_permissions, modified_permissions]:
            for line_num, line_perm in line_permissions.items():
                current_perm = line_perm.permissions.get(target)

                # Only apply directory permission if no explicit permission exists
                # or if directory permission is more restrictive
                should_apply = False

                if current_perm is None:
                    should_apply = True
                elif effective_permission == "n":
                    should_apply = True  # "n" is always most restrictive
                elif effective_permission == "r" and current_perm == "w":
                    should_apply = True  # Directory says read-only, file says write

                if should_apply:
                    line_perm.permissions[target] = effective_permission
                    rules_applied += 1

        return rules_applied

    def validate_directory(
        self,
        directory_path: Union[str, Path],
        file_patterns: Optional[List[str]] = None,
        target: str = "ai",
        identifier: Optional[str] = None,
        recursive: bool = True,
    ) -> ValidationResult:
        """
        Validate all files in a directory.

        Args:
            directory_path: Path to directory to validate
            file_patterns: Optional list of file patterns to match
            target: Target audience
            identifier: Optional specific identifier
            recursive: Whether to search recursively

        Returns:
            Aggregated ValidationResult for all files
        """
        if isinstance(directory_path, str):
            directory_path = Path(directory_path)

        if not directory_path.is_dir():
            return ValidationResult(
                violations=[
                    GuardViolation(
                        file=str(directory_path),
                        line_start=1,
                        line_end=1,
                        severity=ViolationSeverity.ERROR,
                        violation_type="directory_not_found",
                        message=f"Directory not found: {directory_path}",
                        target=target,
                    )
                ]
            )

        # Default file patterns if none provided
        if file_patterns is None:
            file_patterns = ["*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c", "*.cs"]

        # Find files to validate
        files_to_validate = []
        for pattern in file_patterns:
            if recursive:
                files_to_validate.extend(directory_path.rglob(pattern))
            else:
                files_to_validate.extend(directory_path.glob(pattern))

        # Validate each file
        all_violations = []
        total_files = 0
        total_guard_tags = 0
        total_line_permissions = 0
        total_directory_rules = 0

        for file_path in files_to_validate:
            if file_path.is_file():
                result = self.validate_file(file_path, target=target, identifier=identifier)
                all_violations.extend(result.violations)
                total_files += result.files_checked
                total_guard_tags += result.guard_tags_found
                total_line_permissions += result.line_permissions_calculated
                total_directory_rules += result.directory_rules_applied

        return ValidationResult(
            files_checked=total_files,
            violations=all_violations,
            directory_guards_used=self.directory_guard is not None,
            directory_rules_applied=total_directory_rules,
            guard_tags_found=total_guard_tags,
            line_permissions_calculated=total_line_permissions,
        )

    def get_file_permissions(
        self,
        file_path: Union[str, Path],
        content: Optional[str] = None,
        target: str = "ai",
        identifier: Optional[str] = None,
    ) -> Dict[int, LinePermission]:
        """
        Get line permissions for a file.

        Args:
            file_path: Path to the file
            content: File content (if None, reads from file)
            target: Target audience
            identifier: Optional specific identifier

        Returns:
            Dictionary mapping line numbers to permissions
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Read content if not provided
        if content is None:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        # Detect language and process
        language_id = detect_language(str(file_path))
        guard_tags, line_permissions = process_document(content, language_id)

        # Apply directory permissions
        if self.directory_guard:
            self._apply_directory_permissions(
                file_path, line_permissions, line_permissions, target, identifier
            )

        return line_permissions
