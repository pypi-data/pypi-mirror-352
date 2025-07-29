"""
Guard tag parser for CodeGuard CLI.
EXACT port of the VSCode plugin's core/guardParser.ts functionality.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Import exact patterns from VSCode port
from .patterns import GUARD_TAG_PATTERNS, normalize_permission, normalize_scope


class PermissionValue(Enum):
    """Permission values for guard tags."""

    READ = "r"
    WRITE = "w"
    NONE = "n"
    CONTEXT_WRITE = "contextWrite"


class PermissionTarget(Enum):
    """Permission targets for guard tags."""

    AI = "ai"
    HUMAN = "human"


@dataclass
class GuardTag:
    """Represents a parsed guard tag."""

    lineNumber: int
    identifier: Optional[str] = None
    scope: Optional[str] = None
    lineCount: Optional[int] = None
    addScopes: Optional[List[str]] = None
    removeScopes: Optional[List[str]] = None
    aiPermission: Optional[str] = None
    humanPermission: Optional[str] = None
    aiIsContext: bool = False
    humanIsContext: bool = False
    scopeStart: Optional[int] = None
    scopeEnd: Optional[int] = None


@dataclass
class LinePermission:
    """Represents permissions for a specific line."""

    lineNumber: int
    aiPermission: str
    humanPermission: str
    aiIsContext: bool = False
    humanIsContext: bool = False
    guardsApplied: Optional[List[GuardTag]] = None


@dataclass
class GuardStackEntry:
    """Entry in the guard processing stack."""

    guardTag: GuardTag
    endLine: Optional[int] = None
    contextType: Optional[str] = None


@dataclass
class GuardTagParseResult:
    """Guard tag parse result interface - EXACT port from VSCode."""

    identifier: Optional[str] = None
    scope: Optional[str] = None
    lineCount: Optional[int] = None
    addScopes: Optional[List[str]] = None
    removeScopes: Optional[List[str]] = None
    type: str = "guard"
    aiPermission: Optional[str] = None
    humanPermission: Optional[str] = None
    allPermission: Optional[str] = None
    aiIsContext: bool = False
    humanIsContext: bool = False
    allIsContext: bool = False
    metadata: Optional[str] = None
    conditional: Optional[str] = None


def parse_guard_tag(line: str) -> Optional[GuardTagParseResult]:
    """
    Core guard tag parser function - EXACT port from VSCode guardParser.ts
    Parses a line of text for guard tag information
    Supports ALL specification formats
    """
    # Track found permissions for each target
    ai_permission: Optional[str] = None
    human_permission: Optional[str] = None
    all_permission: Optional[str] = None
    ai_is_context = False
    human_is_context = False
    all_is_context = False
    identifier: Optional[str] = None
    scope: Optional[str] = None
    line_count: Optional[int] = None
    metadata: Optional[str] = None
    conditional: Optional[str] = None
    add_scopes: List[str] = []
    remove_scopes: List[str] = []

    # Use comprehensive pattern to find all matches in the line
    comprehensive_regex = GUARD_TAG_PATTERNS.PARSE_GUARD_TAG
    matches = list(comprehensive_regex.finditer(line))

    for match in matches:
        # Updated capture groups for comprehensive pattern:
        groups = match.groups()
        if len(groups) < 4:
            continue

        # [0] = primary target (ai|human|hu|all)
        # [1] = secondary target (if comma-separated)
        # [2] = identifier [...]
        # [3] = permission (read-only|readonly|read|write|noaccess|none|context|r|w|n)
        # [4] = context modifier (:r|:w|:read|:write)
        # [5] = metadata [...]
        # [6] = scope (.word or .number)
        # [7] = conditional (.if(condition))
        # [8] = add scopes (+scope)
        # [9] = remove scopes (-scope)

        primary_target = groups[0] if len(groups) > 0 else None
        secondary_target = groups[1] if len(groups) > 1 else None
        id_capture = groups[2] if len(groups) > 2 else None
        permission = groups[3] if len(groups) > 3 else None
        context_modifier = groups[4] if len(groups) > 4 else None
        metadata_capture = groups[5] if len(groups) > 5 else None
        scope_or_count = groups[6] if len(groups) > 6 else None
        conditional_capture = groups[7] if len(groups) > 7 else None
        add_scopes_str = groups[8] if len(groups) > 8 else None
        remove_scopes_str = groups[9] if len(groups) > 9 else None

        if not primary_target or not permission:
            continue

        # Handle targets - support multi-target syntax and normalize hu -> human
        targets = [normalize_target(primary_target)]
        if secondary_target:
            targets.append(normalize_target(secondary_target))

        # Check if scope is numeric (line count) or semantic
        is_line_count = scope_or_count and GUARD_TAG_PATTERNS.NUMERIC_SCOPE.match(scope_or_count)

        # Normalize permission using alias mapping
        normalized_permission = normalize_permission(permission)

        # Handle context modifier for context permissions
        if normalized_permission == "context" and context_modifier:
            # Remove the : prefix from context modifier
            modifier_clean = (
                context_modifier[1:] if context_modifier.startswith(":") else context_modifier
            )
            modifier_normalized = normalize_permission(modifier_clean)
            if modifier_normalized in ["w", "write"]:
                normalized_permission = "contextWrite"
            # For 'r' or 'read', keep as 'context' (read context)

        # Set identifier (use first found)
        if id_capture and not identifier:
            identifier = id_capture

        # Set metadata (use first found)
        if metadata_capture and not metadata:
            metadata = metadata_capture

        # Set scope/line count (use first found)
        if scope_or_count and not scope and not line_count:
            if is_line_count:
                line_count = int(scope_or_count)
            else:
                scope = normalize_scope(scope_or_count)

        # Set conditional (use first found)
        if conditional_capture and not conditional:
            conditional = conditional_capture

        # Parse add/remove scopes
        if add_scopes_str:
            for add_match in GUARD_TAG_PATTERNS.SCOPE_MODIFIER.finditer(add_scopes_str):
                operator, scope_name = add_match.groups()
                if operator == "+":
                    add_scopes.append(normalize_scope(scope_name))

        if remove_scopes_str:
            for remove_match in GUARD_TAG_PATTERNS.SCOPE_MODIFIER.finditer(remove_scopes_str):
                operator, scope_name = remove_match.groups()
                if operator == "-":
                    remove_scopes.append(normalize_scope(scope_name))

        # Set permissions for each target - EXACT port of VSCode logic
        for target in targets:
            if target == "ai":
                if normalized_permission == "context":
                    ai_is_context = True
                    # NO ai_permission set here - it remains None!
                elif normalized_permission == "contextWrite":
                    ai_permission = "contextWrite"
                else:
                    ai_permission = normalized_permission
            elif target == "human":
                if normalized_permission == "context":
                    human_is_context = True
                    # NO human_permission set here - it remains None!
                elif normalized_permission == "contextWrite":
                    human_permission = "contextWrite"
                else:
                    human_permission = normalized_permission
            elif target == "all":
                if normalized_permission == "context":
                    all_is_context = True
                    # NO all_permission set here - it remains None!
                elif normalized_permission == "contextWrite":
                    all_permission = "contextWrite"
                else:
                    all_permission = normalized_permission

    # Return result if any permissions or context flags were found - EXACT port of VSCode logic
    if (
        ai_permission
        or human_permission
        or all_permission
        or ai_is_context
        or human_is_context
        or all_is_context
    ):
        return GuardTagParseResult(
            identifier=identifier,
            scope=scope,
            lineCount=line_count,
            addScopes=add_scopes if add_scopes else None,
            removeScopes=remove_scopes if remove_scopes else None,
            type="guard",
            aiPermission=ai_permission,
            humanPermission=human_permission,
            allPermission=all_permission,
            aiIsContext=ai_is_context,
            humanIsContext=human_is_context,
            allIsContext=all_is_context,
            metadata=metadata,
            conditional=conditional,
        )

    return None


def normalize_target(target: str) -> str:
    """Normalize target names - handle hu -> human alias."""
    target = target.lower()
    if target == "hu":
        return "human"
    return target


def has_guard_tag(line: str) -> bool:
    """Check if a line contains a guard tag."""
    return GUARD_TAG_PATTERNS.HAS_GUARD_TAG.search(line) is not None


def extract_guard_tag_matches(line: str) -> List[Tuple[int, int]]:
    """Extract all guard tag match positions in a line."""
    matches = []

    # Check comprehensive pattern
    for match in GUARD_TAG_PATTERNS.PARSE_GUARD_TAG.finditer(line):
        matches.append((match.start(), match.end()))

    return matches


# Default permissions constant
DEFAULT_PERMISSIONS = {"ai": "r", "human": "w"}
