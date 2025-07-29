"""
Comparison Engine for CodeGuard.

This module is responsible for comparing guard permissions between original
and modified versions of code, and identifying violations using System A.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..utils.hash_calculator import HashCalculator
from .types import GuardTag, LinePermission


class ViolationSeverity(Enum):
    """Severity levels for guard violations."""

    CRITICAL = "critical"  # None (N) permissions
    ERROR = "error"  # Read-only (R) regions
    WARNING = "warning"  # Context violations
    INFO = "info"  # Permission mismatches


class GuardViolation:
    """
    Represents a detected violation of a guard rule.

    This class encapsulates information about a code modification that
    violates a guard annotation, including the location, type of violation,
    content changes, and severity level.
    """

    def __init__(
        self,
        file: str,
        line_start: int,
        line_end: int,
        severity: ViolationSeverity,
        violation_type: str,
        message: str,
        original_content: str = "",
        modified_content: str = "",
        guard_identifier: Optional[str] = None,
        target: str = "ai",
        expected_permission: str = "",
        actual_permission: str = "",
    ):
        self.file = file
        self.line_start = line_start
        self.line_end = line_end
        self.severity = severity
        self.violation_type = violation_type
        self.message = message
        self.original_content = original_content
        self.modified_content = modified_content
        self.guard_identifier = guard_identifier
        self.target = target
        self.expected_permission = expected_permission
        self.actual_permission = actual_permission


class ComparisonEngine:
    """
    Engine for comparing guard permissions and detecting violations using System A.

    This class compares line permissions between original and modified versions
    of a file to detect violations of guard rules.
    """

    def __init__(
        self,
        normalize_whitespace: bool = True,
        normalize_line_endings: bool = True,
        ignore_blank_lines: bool = True,
        ignore_indentation: bool = False,
        context_lines: int = 3,
    ) -> None:
        """Initialize the comparison engine with normalization options."""
        self.hash_calculator = HashCalculator(
            normalize_whitespace=normalize_whitespace,
            normalize_line_endings=normalize_line_endings,
            ignore_blank_lines=ignore_blank_lines,
            ignore_indentation=ignore_indentation,
        )
        self.context_lines = context_lines

    def compare_permissions(
        self,
        original_permissions: Dict[int, LinePermission],
        modified_permissions: Dict[int, LinePermission],
        file_path: str,
        original_content: str,
        modified_content: str,
        target: str = "ai",
        identifier: Optional[str] = None,
    ) -> List[GuardViolation]:
        """
        Compare line permissions between original and modified code to detect violations.

        Args:
            original_permissions: Line permissions from original code
            modified_permissions: Line permissions from modified code
            file_path: Path to the file being validated
            original_content: Complete content of the original file
            modified_content: Complete content of the modified file
            target: Target audience to check permissions for (default: "ai")
            identifier: Optional specific identifier within the target group

        Returns:
            List of GuardViolation objects representing detected violations
        """
        violations = []
        original_lines = original_content.split("\n")
        modified_lines = modified_content.split("\n")

        # Check each line for permission violations
        max_lines = max(len(original_lines), len(modified_lines))

        for line_num in range(1, max_lines + 1):
            original_line = original_lines[line_num - 1] if line_num <= len(original_lines) else ""
            modified_line = modified_lines[line_num - 1] if line_num <= len(modified_lines) else ""

            # Get permissions for this line
            orig_perm = original_permissions.get(line_num)
            mod_perm = modified_permissions.get(line_num)

            # Check for content changes
            if original_line != modified_line:
                # Line was modified, check permissions
                permission = orig_perm.permissions.get(target, "r") if orig_perm else "r"

                if permission == "n":
                    # No permission - critical violation
                    violations.append(
                        GuardViolation(
                            file=file_path,
                            line_start=line_num,
                            line_end=line_num,
                            severity=ViolationSeverity.CRITICAL,
                            violation_type="no_permission",
                            message=f"Modification not allowed for {target} on line {line_num}",
                            original_content=original_line,
                            modified_content=modified_line,
                            target=target,
                            expected_permission="n",
                            actual_permission="modified",
                        )
                    )
                elif permission == "r":
                    # Read-only - error violation
                    violations.append(
                        GuardViolation(
                            file=file_path,
                            line_start=line_num,
                            line_end=line_num,
                            severity=ViolationSeverity.ERROR,
                            violation_type="read_only_violation",
                            message=f"Read-only violation for {target} on line {line_num}",
                            original_content=original_line,
                            modified_content=modified_line,
                            target=target,
                            expected_permission="r",
                            actual_permission="modified",
                        )
                    )
                elif permission == "contextWrite":
                    # Context write permission - check if it's context
                    is_context = orig_perm.isContext.get(target, False) if orig_perm else False
                    if not is_context:
                        violations.append(
                            GuardViolation(
                                file=file_path,
                                line_start=line_num,
                                line_end=line_num,
                                severity=ViolationSeverity.WARNING,
                                violation_type="context_violation",
                                message=f"Context write permission required for {target} on line {line_num}",
                                original_content=original_line,
                                modified_content=modified_line,
                                target=target,
                                expected_permission="contextWrite",
                                actual_permission="modified",
                            )
                        )

        return violations

    def compare_guard_tags(
        self,
        original_tags: List[GuardTag],
        modified_tags: List[GuardTag],
        file_path: str,
    ) -> List[GuardViolation]:
        """
        Compare guard tags to detect structural changes.

        Args:
            original_tags: Guard tags from original code
            modified_tags: Guard tags from modified code
            file_path: Path to the file being validated

        Returns:
            List of violations for guard tag changes
        """
        violations = []

        # Map tags by line number
        orig_map = {tag.lineNumber: tag for tag in original_tags}
        mod_map = {tag.lineNumber: tag for tag in modified_tags}

        # Check for removed guards
        for line_num, orig_tag in orig_map.items():
            if line_num not in mod_map:
                violations.append(
                    GuardViolation(
                        file=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        severity=ViolationSeverity.ERROR,
                        violation_type="guard_removed",
                        message=f"Guard tag removed from line {line_num}",
                        guard_identifier=orig_tag.identifier,
                    )
                )

        # Check for added guards
        for line_num, mod_tag in mod_map.items():
            if line_num not in orig_map:
                violations.append(
                    GuardViolation(
                        file=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        severity=ViolationSeverity.INFO,
                        violation_type="guard_added",
                        message=f"Guard tag added at line {line_num}",
                        guard_identifier=mod_tag.identifier,
                    )
                )

        # Check for modified guards
        for line_num in orig_map.keys() & mod_map.keys():
            orig_tag = orig_map[line_num]
            mod_tag = mod_map[line_num]

            # Compare key properties
            if (
                orig_tag.aiPermission != mod_tag.aiPermission
                or orig_tag.humanPermission != mod_tag.humanPermission
                or orig_tag.scope != mod_tag.scope
            ):
                violations.append(
                    GuardViolation(
                        file=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        severity=ViolationSeverity.WARNING,
                        violation_type="guard_modified",
                        message=f"Guard tag modified at line {line_num}",
                        guard_identifier=orig_tag.identifier,
                    )
                )

        return violations
