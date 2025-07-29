#!/usr/bin/env python3
"""
Section validation module for comparing external tool parsing with internal parsing.

This module implements the validation mode that allows external tools (like VS Code plugins)
to verify their guard section parsing matches exactly with CodeGuard's internal parsing.

Important: Guards create overlapping protection layers, not sequential non-overlapping sections.
A single line of code can be covered by multiple guard annotations with different targets,
permissions, and scopes.
"""

import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..version import __version__

# Exit codes
EXIT_SUCCESS = 0  # Perfect match
EXIT_VALIDATION_MISMATCH = 1  # Validation differences found
EXIT_PARSING_ERROR = 2  # Error parsing source file
EXIT_JSON_ERROR = 3  # Invalid JSON format or structure
EXIT_FILE_NOT_FOUND = 4  # Source file not found
EXIT_FILE_CHANGED = 5  # File content changed since plugin parse
EXIT_VERSION_INCOMPATIBLE = 6  # Plugin/tool version mismatch
EXIT_INTERNAL_ERROR = 7  # Unexpected internal error

# Status values in JSON response
STATUS_MATCH = "MATCH"  # Perfect match
STATUS_MISMATCH = "MISMATCH"  # Validation differences
STATUS_ERROR_PARSING = "ERROR_PARSING"  # Could not parse file
STATUS_ERROR_JSON = "ERROR_JSON"  # Invalid request format
STATUS_ERROR_FILE_NOT_FOUND = "ERROR_FILE_NOT_FOUND"
STATUS_ERROR_FILE_CHANGED = "ERROR_FILE_CHANGED"
STATUS_ERROR_VERSION = "ERROR_VERSION"
STATUS_ERROR_INTERNAL = "ERROR_INTERNAL"

# Discrepancy types
DISCREPANCY_TYPES = {
    "boundary_mismatch": "Guard region start/end lines don't match",
    "guard_missing": "Plugin found guard, tool did not",
    "guard_extra": "Tool found guard, plugin did not",
    "guard_interpretation": "Same guard parsed differently",
    "permission_mismatch": "Different permission interpretation",
    "scope_mismatch": "Different scope interpretation",
    "target_mismatch": "Different target (ai/human) interpretation",
    "identifier_mismatch": "Different identifier parsing",
    "layer_mismatch": "Different overlapping guard layers at line",
    "effective_permission_mismatch": "Different effective permissions after layer resolution",
    "scope_boundary_mismatch": "Guard scope ends at different line",
    "inheritance_mismatch": "Different guard inheritance interpretation",
    "override_mismatch": "Different interpretation of guard overrides",
    "content_hash_mismatch": "Guard region content changed",
    "line_count_mismatch": "File has different number of lines",
}


# Use the new system types directly
from .types import GuardTag, LinePermission


@dataclass
class LineCoverage:
    """Represents which guards apply to a specific line."""

    line: int
    guards: List[int]  # Indices of guards that apply to this line


@dataclass
class Discrepancy:
    """Represents a validation discrepancy."""

    type: str
    severity: str  # "ERROR" or "WARNING"
    message: str
    line: Optional[int] = None
    guard_index: Optional[int] = None
    plugin_region: Optional[Dict[str, Any]] = None
    tool_region: Optional[Dict[str, Any]] = None
    plugin_guards: Optional[List[Dict[str, Any]]] = None
    tool_guards: Optional[List[Dict[str, Any]]] = None
    plugin_effective: Optional[str] = None
    tool_effective: Optional[str] = None
    target: Optional[str] = None


def compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of file contents."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_content_hash(lines: List[str]) -> str:
    """Compute SHA-256 hash of content lines."""
    content = "\n".join(lines)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def create_error_response(
    exit_code: int, status: str, error: str, details: Optional[Dict[str, Any]] = None
) -> int:
    """Create and output an error response."""
    response = {"validation_result": {"status": status, "exit_code": exit_code, "error": error}}

    if details:
        response["validation_result"]["details"] = details

    sys.stdout.write(json.dumps(response, indent=2))
    sys.stdout.flush()
    return exit_code


def create_success_response(
    request: Dict[str, Any], guard_tags: List[GuardTag], line_permissions: List[LinePermission]
) -> int:
    """Create and output a success response."""
    # Calculate statistics
    total_lines = request["validation_request"]["total_lines"]
    line_coverage = build_line_coverage(line_permissions)

    # Count lines with multiple permissions
    lines_with_multiple = sum(1 for perms in line_coverage.values() if len(perms) > 1)
    max_overlapping = max(len(perms) for perms in line_coverage.values()) if line_coverage else 0

    response = {
        "validation_result": {
            "status": STATUS_MATCH,
            "exit_code": EXIT_SUCCESS,
            "file_path": request["validation_request"]["file_path"],
            "timestamp": datetime.now().isoformat() + "Z",
            "tool_version": __version__,
            "plugin_version": request["validation_request"]["plugin_version"],
            "discrepancies": [],
            "statistics": {
                "total_lines": total_lines,
                "plugin_guard_regions": len(request["validation_request"]["guard_regions"]),
                "tool_guard_tags": len(guard_tags),
                "matching_regions": len(request["validation_request"]["guard_regions"]),
                "max_overlapping_guards": max_overlapping,
                "lines_with_multiple_guards": lines_with_multiple,
            },
        }
    }

    sys.stdout.write(json.dumps(response, indent=2))
    sys.stdout.flush()
    return EXIT_SUCCESS


def create_mismatch_response(
    request: Dict[str, Any],
    guard_tags: List[GuardTag],
    line_permissions: List[LinePermission],
    discrepancies: List[Discrepancy],
) -> int:
    """Create and output a mismatch response."""
    # Calculate statistics
    total_lines = request["validation_request"]["total_lines"]
    matching_regions = len(request["validation_request"]["guard_regions"]) - len(
        [d for d in discrepancies if d.type in ["guard_missing", "guard_extra"]]
    )

    # Count affected lines
    affected_lines = set()
    for d in discrepancies:
        if d.line:
            affected_lines.add(d.line)

    response = {
        "validation_result": {
            "status": STATUS_MISMATCH,
            "exit_code": EXIT_VALIDATION_MISMATCH,
            "file_path": request["validation_request"]["file_path"],
            "timestamp": datetime.now().isoformat() + "Z",
            "tool_version": __version__,
            "plugin_version": request["validation_request"]["plugin_version"],
            "discrepancies": [asdict(d) for d in discrepancies],
            "statistics": {
                "total_lines": total_lines,
                "plugin_guard_regions": len(request["validation_request"]["guard_regions"]),
                "tool_guard_tags": len(guard_tags),
                "matching_regions": matching_regions,
                "discrepancy_count": len(discrepancies),
                "affected_lines": len(affected_lines),
            },
        }
    }

    sys.stdout.write(json.dumps(response, indent=2))
    sys.stdout.flush()
    return EXIT_VALIDATION_MISMATCH


def validate_request_structure(request: Dict[str, Any]) -> Optional[str]:
    """Validate the structure of the validation request."""
    # Check for required top-level fields
    if "validation_request" not in request:
        return "Missing required field: validation_request"

    vr = request["validation_request"]

    # Check required fields in validation_request
    required_fields = [
        "file_path",
        "file_hash",
        "total_lines",
        "timestamp",
        "plugin_version",
        "plugin_name",
        "guard_regions",
    ]

    for field in required_fields:
        if field not in vr:
            return f"Missing required field: validation_request.{field}"

    # Validate guard_regions
    if not isinstance(vr["guard_regions"], list):
        return "validation_request.guard_regions must be a list"

    for i, region in enumerate(vr["guard_regions"]):
        # Check required region fields
        required_region_fields = [
            "index",
            "guard",
            "parsed_guard",
            "declaration_line",
            "start_line",
            "end_line",
        ]
        for field in required_region_fields:
            if field not in region:
                return f"Missing required field in guard_region {i}: {field}"

        # Validate parsed_guard structure
        pg = region["parsed_guard"]
        required_guard_fields = ["raw", "target", "identifiers", "permission", "scope"]
        for field in required_guard_fields:
            if field not in pg:
                return f"Missing required field in guard_region {i} parsed_guard: {field}"

    # Validate optional line_coverage if present
    if "line_coverage" in vr:
        if not isinstance(vr["line_coverage"], list):
            return "validation_request.line_coverage must be a list"

        for i, coverage in enumerate(vr["line_coverage"]):
            if "line" not in coverage or "guards" not in coverage:
                return f"Invalid line_coverage entry {i}: must have 'line' and 'guards'"

    return None


def parse_file_guards(file_path: str) -> Tuple[List[GuardTag], List[LinePermission]]:
    """Parse a file and extract guard tags and line permissions using CodeGuard's new processor."""
    from .processor import detect_language, process_document

    # Read file content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse the file using new processor
    try:
        language_id = detect_language(file_path)
        guard_tags, line_permissions = process_document(content, language_id)
        return guard_tags, line_permissions
    except Exception as e:
        raise Exception(f"Failed to parse file: {str(e)}")


def build_line_coverage(line_permissions: List[LinePermission]) -> Dict[int, List[str]]:
    """Build a mapping of line numbers to permission information."""
    line_coverage = {}

    for perm in line_permissions:
        line_coverage[perm.line] = list(perm.permissions.keys())

    return line_coverage


def compare_parsing_results(
    plugin_regions: List[Dict[str, Any]],
    guard_tags: List[GuardTag],
    line_permissions: List[LinePermission],
    total_lines: int,
    plugin_line_coverage: List[Dict[str, Any]] = None,
) -> List[Discrepancy]:
    """Compare plugin parsing with tool parsing and identify discrepancies."""
    discrepancies = []

    # For now, just check if we have different counts
    plugin_count = len(plugin_regions)
    tool_count = len(guard_tags)

    if plugin_count != tool_count:
        discrepancies.append(
            Discrepancy(
                type="guard_missing" if plugin_count > tool_count else "guard_extra",
                severity="ERROR",
                message=f"Different number of guards: plugin found {plugin_count}, tool found {tool_count}",
            )
        )

    # Simple line permission comparison
    tool_line_coverage = build_line_coverage(line_permissions)

    if plugin_line_coverage:
        plugin_coverage_map = {
            entry["line"]: set(entry.get("guards", [])) for entry in plugin_line_coverage
        }

        for line_entry in plugin_line_coverage:
            line = line_entry["line"]
            plugin_perms = set(line_entry.get("guards", []))
            tool_perms = set(tool_line_coverage.get(line, []))

            if plugin_perms != tool_perms:
                discrepancies.append(
                    Discrepancy(
                        type="layer_mismatch",
                        severity="WARNING",
                        line=line,
                        message=f"Different permissions at line {line}: plugin {plugin_perms} vs tool {tool_perms}",
                    )
                )

    return discrepancies


def validate_sections(
    json_file_path: str, source_file_path: Optional[str] = None, verbose: bool = False
) -> int:
    """
    Validate that external tool's guard section parsing matches our internal parsing.

    Args:
        json_file_path: Path to JSON validation request
        source_file_path: Optional override for source file path (defaults to path in JSON)
        verbose: Include detailed parsing information

    Returns:
        Exit code
    """
    try:
        # Load validation request
        with open(json_file_path, "r") as f:
            request = json.load(f)
    except FileNotFoundError:
        return create_error_response(
            EXIT_FILE_NOT_FOUND,
            STATUS_ERROR_FILE_NOT_FOUND,
            f"JSON file not found: {json_file_path}",
        )
    except json.JSONDecodeError as e:
        return create_error_response(
            EXIT_JSON_ERROR,
            STATUS_ERROR_JSON,
            f"Invalid JSON format",
            {"error": str(e), "line": e.lineno, "column": e.colno},
        )

    # Validate request structure
    validation_error = validate_request_structure(request)
    if validation_error:
        return create_error_response(EXIT_JSON_ERROR, STATUS_ERROR_JSON, validation_error)

    # Get file path
    file_path = source_file_path or request["validation_request"]["file_path"]

    # Check file exists
    if not os.path.exists(file_path):
        return create_error_response(
            EXIT_FILE_NOT_FOUND,
            STATUS_ERROR_FILE_NOT_FOUND,
            f"Source file not found: {file_path}",
            {"file_path": file_path},
        )

    # Verify file hasn't changed
    current_hash = compute_file_hash(file_path)
    if current_hash != request["validation_request"]["file_hash"]:
        # Get line count for additional context
        with open(file_path, "r") as f:
            current_lines = len(f.readlines())

        return create_error_response(
            EXIT_FILE_CHANGED,
            STATUS_ERROR_FILE_CHANGED,
            "File content has changed since plugin parsing",
            {
                "plugin_file_hash": request["validation_request"]["file_hash"],
                "current_file_hash": current_hash,
                "plugin_line_count": request["validation_request"]["total_lines"],
                "current_line_count": current_lines,
            },
        )

    # Parse file independently using new processor
    try:
        guard_tags, line_permissions = parse_file_guards(file_path)
    except Exception as e:
        return create_error_response(
            EXIT_PARSING_ERROR,
            STATUS_ERROR_PARSING,
            "Failed to parse source file",
            {"parser_error": str(e), "file_path": file_path},
        )

    # Compare parsing results
    discrepancies = compare_parsing_results(
        request["validation_request"]["guard_regions"],
        guard_tags,
        line_permissions,
        request["validation_request"]["total_lines"],
        request["validation_request"].get("line_coverage", []),
    )

    if not discrepancies:
        return create_success_response(request, guard_tags, line_permissions)
    else:
        return create_mismatch_response(request, guard_tags, line_permissions, discrepancies)
