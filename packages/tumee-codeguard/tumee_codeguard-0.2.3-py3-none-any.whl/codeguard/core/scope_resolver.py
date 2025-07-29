"""
Core scope resolution logic - platform agnostic
Exact port of VSCode src/core/scopeResolver.ts
No VSCode dependencies allowed in this module
"""

from typing import Any, List, Optional

from .advanced_scope_resolver import resolve_block_scope_advanced
from .language_scopes import get_language_scope_mappings
from .regex_scope_resolver import resolve_scope_with_regex_fallback
from .tree_sitter_parser import TreeSitterParser
from .types import IDocument, ScopeBoundary

# Guard tag prefix for context detection
GUARD_TAG_PREFIX = "@guard:"


def resolve_semantic_scope_sync(
    document: IDocument,
    line: int,
    scope: str,
    add_scopes: Optional[List[str]] = None,
    remove_scopes: Optional[List[str]] = None,
) -> Optional[ScopeBoundary]:
    """
    Synchronous version of resolve_semantic_scope for use in processor
    """
    return _resolve_semantic_scope_impl(document, line, scope, add_scopes, remove_scopes)


async def resolve_semantic_scope(
    document: IDocument,
    line: int,
    scope: str,
    context: Any,  # Platform-specific context for parser initialization
    add_scopes: Optional[List[str]] = None,
    remove_scopes: Optional[List[str]] = None,
) -> Optional[ScopeBoundary]:
    """
    Async version of resolve_semantic_scope for compatibility
    """
    return _resolve_semantic_scope_impl(document, line, scope, add_scopes, remove_scopes)


def _resolve_semantic_scope_impl(
    document: IDocument,
    line: int,
    scope: str,
    add_scopes: Optional[List[str]] = None,
    remove_scopes: Optional[List[str]] = None,
) -> Optional[ScopeBoundary]:
    """
    Core implementation of semantic scope resolution using tree-sitter
    """
    # Create tree-sitter parser instance
    parser = TreeSitterParser()
    parser.initialize()

    # Parse the document
    parse_result = parser.parse_document(document.text, document.languageId)
    if not parse_result.success or not parse_result.root_node:
        # Tree-sitter failed, try regex fallback
        regex_result = resolve_scope_with_regex_fallback(document, line, scope)
        if regex_result:
            return regex_result
        return None

    tree = parse_result.root_node

    language_id = document.languageId
    scope_map = get_language_scope_mappings(language_id)
    if not scope_map:
        return None

    node_types = scope_map.get(scope) or scope_map.get(scope.lower())
    if not node_types or len(node_types) == 0:
        return None

    # For scoped guards, we need to search forward from the guard line
    # to find the next occurrence of the scope type
    if scope in ["class", "func", "function", "block"]:
        # For block scope, we always want to find the next code block,
        # not apply to the comment itself

        # Start searching from the line after the guard
        for search_line in range(line + 1, document.lineCount):
            search_node = parser.find_node_at_position(tree, search_line, 0)
            if search_node:
                # For block scope, we need to handle differently
                # Dictionary/list/set nodes might be children of assignments
                target_node = None

                if scope == "block":
                    # Use advanced block scope resolution
                    advanced_result = resolve_block_scope_advanced(document, search_line)
                    if advanced_result:
                        return advanced_result

                    # Fallback to original logic
                    for node_type in node_types:
                        current = search_node
                        while current:
                            if current.type == node_type:
                                target_node = current
                                break
                            current = current.parent
                        if target_node:
                            break

                    # Special case: look for object/array/dictionary literals
                    if not target_node:
                        current = search_node
                        while current:
                            if current.type in [
                                "object",
                                "array",
                                "dictionary",
                                "object_literal",
                                "array_literal",
                            ]:
                                target_node = current
                                break
                            current = current.parent

                else:
                    # For other scopes (class, func), find exact match
                    for node_type in node_types:
                        found_node = parser.find_parent_of_type(search_node, node_type)
                        if found_node:
                            target_node = found_node
                            break

                if target_node:
                    boundaries = parser.get_node_boundaries(target_node)

                    # Special handling for Python classes: trim trailing whitespace
                    # (exact port from VSCode scopeResolver.ts lines 103-117)
                    if (
                        scope == "class"
                        and document.languageId == "python"
                        and target_node.type == "class_definition"
                    ):
                        lines = document.text.split("\n")
                        trimmed_end = boundaries.end.line

                        # Search backwards from the end of the class to find the last non-empty line
                        for trim_line in range(
                            boundaries.end.line - 1, boundaries.start.line - 1, -1
                        ):
                            if trim_line < len(lines):
                                line_text = lines[trim_line].strip()
                                if line_text:  # Found last non-empty line
                                    trimmed_end = trim_line + 1  # Convert to 1-based
                                    break

                        return ScopeBoundary(
                            startLine=boundaries.start.line,
                            endLine=trimmed_end,
                            type=target_node.type,
                        )

                    return ScopeBoundary(
                        startLine=boundaries.start.line,
                        endLine=boundaries.end.line,
                        type=target_node.type,
                    )

    # If no forward search match, try to find scope at current position
    node = parser.find_node_at_position(tree, line, 0)
    if node:
        target_node = None
        for node_type in node_types:
            found_node = parser.find_parent_of_type(node, node_type)
            if found_node:
                target_node = found_node
                break
        if target_node:
            boundaries = parser.get_node_boundaries(target_node)
            return ScopeBoundary(
                startLine=boundaries.start.line, endLine=boundaries.end.line, type=target_node.type
            )

    return None


def resolve_line_count_scope(
    document: IDocument, start_line: int, line_count: int
) -> ScopeBoundary:
    """
    Resolve a line-count based scope
    """
    end_line = min(start_line + line_count - 1, document.lineCount)
    return ScopeBoundary(startLine=start_line, endLine=end_line, type="line_count")


def resolve_context_scope(document: IDocument, guard_line: int) -> ScopeBoundary:
    """
    Resolve context scope - applies to next non-comment lines
    """
    lines = document.text.split("\n")

    # Start from the line after the guard
    start_line = guard_line + 1
    end_line = guard_line

    # Find next non-comment lines
    for search_line in range(guard_line, len(lines)):
        search_line_text = lines[search_line].strip()
        if search_line_text and not search_line_text.startswith(("//:", "#")):
            end_line = search_line + 1  # Convert to 1-based
            break

    return ScopeBoundary(startLine=start_line, endLine=end_line, type="context")


def resolve_file_scope(document: IDocument, guard_line: int) -> ScopeBoundary:
    """
    Resolve file scope - applies to entire remaining file
    """
    return ScopeBoundary(startLine=guard_line + 1, endLine=document.lineCount, type="file")


async def resolve_guard_scope(
    document: IDocument,
    guard_line: int,
    scope: Optional[str],
    line_count: Optional[int],
    context: Any,
) -> ScopeBoundary:
    """
    Main scope resolution function - determines the boundary for a guard
    """
    # Line count takes precedence
    if line_count is not None:
        return resolve_line_count_scope(document, guard_line, line_count)

    # Handle specific scope types
    if scope == "context":
        return resolve_context_scope(document, guard_line)
    elif scope == "file":
        return resolve_file_scope(document, guard_line)
    elif scope in ["block", "class", "func", "function", "signature"]:
        # Use semantic scope resolution
        semantic_boundary = await resolve_semantic_scope(
            document, guard_line - 1, scope, context  # Convert to 0-based for tree-sitter
        )
        if semantic_boundary:
            return semantic_boundary
        else:
            # Fallback to single line if semantic resolution fails
            return ScopeBoundary(startLine=guard_line, endLine=guard_line, type="fallback")
    else:
        # Default fallback to single line
        return ScopeBoundary(startLine=guard_line, endLine=guard_line, type="default")
