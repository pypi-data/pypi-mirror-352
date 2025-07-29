"""
Graceful degradation strategies for all parsing failures
Comprehensive fallback system with multiple recovery strategies
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from .error_handling import handle_scope_resolution_error, handle_tree_sitter_error, log_debug
from .regex_scope_resolver import (
    resolve_context_scope_with_regex,
    resolve_scope_with_regex_fallback,
)
from .types import IDocument, ScopeBoundary


class GracefulDegradationManager:
    """
    Manages graceful degradation across all parsing operations
    """

    def __init__(self):
        self.fallback_strategies = [
            self._strategy_regex_patterns,
            self._strategy_indentation_analysis,
            self._strategy_line_based_heuristics,
            self._strategy_simple_keyword_detection,
            self._strategy_conservative_fallback,
        ]

    def resolve_with_degradation(
        self, document: IDocument, line: int, scope: str, primary_failure_reason: str = "unknown"
    ) -> Optional[ScopeBoundary]:
        """
        Attempt resolution using multiple fallback strategies
        """
        log_debug(
            f"Starting graceful degradation for scope '{scope}' at line {line}",
            reason=primary_failure_reason,
        )

        # Try each strategy in order
        for i, strategy in enumerate(self.fallback_strategies):
            try:
                result = strategy(document, line, scope)
                if result:
                    log_debug(
                        f"Degradation strategy {i+1} succeeded",
                        strategy=strategy.__name__,
                        scope=scope,
                        line=line,
                    )
                    return result

            except Exception as e:
                log_debug(
                    f"Degradation strategy {i+1} failed", strategy=strategy.__name__, error=str(e)
                )
                continue

        # All strategies failed
        handle_scope_resolution_error(
            f"All graceful degradation strategies failed for scope '{scope}'",
            scope_type=scope,
            line_number=line,
        )
        return None

    def _strategy_regex_patterns(
        self, document: IDocument, line: int, scope: str
    ) -> Optional[ScopeBoundary]:
        """
        Strategy 1: Use comprehensive regex patterns
        """
        return resolve_scope_with_regex_fallback(document, line, scope)

    def _strategy_indentation_analysis(
        self, document: IDocument, line: int, scope: str
    ) -> Optional[ScopeBoundary]:
        """
        Strategy 2: Indentation-based analysis for block structures
        """
        if scope not in ["block", "class", "func", "function"]:
            return None

        lines = document.text.split("\n")
        if line >= len(lines):
            return None

        # Find the next significant line after the guard
        target_line = None
        for search_line in range(line, min(line + 10, len(lines))):
            line_text = lines[search_line].strip()
            if line_text and not line_text.startswith(("#", "//", "/*")):
                target_line = search_line
                break

        if target_line is None:
            return None

        base_indent = len(lines[target_line]) - len(lines[target_line].lstrip())

        # Find the end based on indentation
        end_line = target_line
        for search_line in range(target_line + 1, len(lines)):
            line_text = lines[search_line]

            if not line_text.strip():  # Skip empty lines
                continue

            current_indent = len(line_text) - len(line_text.lstrip())

            # If indentation returns to base level or less, we've found the end
            if current_indent <= base_indent:
                end_line = search_line - 1
                break
            else:
                end_line = search_line

        return ScopeBoundary(
            startLine=target_line + 1, endLine=end_line + 1, type="indentation_analysis"
        )

    def _strategy_line_based_heuristics(
        self, document: IDocument, line: int, scope: str
    ) -> Optional[ScopeBoundary]:
        """
        Strategy 3: Simple line-based heuristics
        """
        lines = document.text.split("\n")

        # Define scope-specific line counts
        scope_line_counts = {
            "class": 20,
            "func": 15,
            "function": 15,
            "block": 10,
            "signature": 3,
            "context": 5,
        }

        line_count = scope_line_counts.get(scope, 5)

        # Find next non-comment line
        start_line = line
        for search_line in range(line, min(line + 5, len(lines))):
            line_text = lines[search_line].strip()
            if line_text and not line_text.startswith(("#", "//", "/*")):
                start_line = search_line
                break

        end_line = min(start_line + line_count, len(lines))

        return ScopeBoundary(startLine=start_line + 1, endLine=end_line, type="line_heuristics")

    def _strategy_simple_keyword_detection(
        self, document: IDocument, line: int, scope: str
    ) -> Optional[ScopeBoundary]:
        """
        Strategy 4: Simple keyword-based detection
        """
        lines = document.text.split("\n")
        language_id = document.languageId.lower()

        # Language-specific keywords
        keywords = {
            "python": {
                "class": r"\bclass\s+\w+",
                "func": r"\bdef\s+\w+",
                "function": r"\bdef\s+\w+",
                "block": r"\b(if|for|while|with|try)\b",
            },
            "javascript": {
                "class": r"\bclass\s+\w+",
                "func": r"\bfunction\s+\w+",
                "function": r"\bfunction\s+\w+",
                "block": r"\b(if|for|while|switch|try)\b",
            },
            "java": {
                "class": r"\bclass\s+\w+",
                "func": r"\w+\s*\([^)]*\)\s*\{",
                "function": r"\w+\s*\([^)]*\)\s*\{",
                "block": r"\b(if|for|while|switch|try)\b",
            },
        }

        lang_keywords = keywords.get(language_id, keywords.get("python", {}))
        pattern = lang_keywords.get(scope)

        if not pattern:
            return None

        # Search for keyword pattern
        for search_line in range(line, min(line + 20, len(lines))):
            line_text = lines[search_line]
            if re.search(pattern, line_text):
                # Use simple heuristic for end
                end_line = min(search_line + 10, len(lines))
                return ScopeBoundary(
                    startLine=search_line + 1, endLine=end_line, type="keyword_detection"
                )

        return None

    def _strategy_conservative_fallback(
        self, document: IDocument, line: int, scope: str
    ) -> Optional[ScopeBoundary]:
        """
        Strategy 5: Conservative fallback - always succeeds with minimal scope
        """
        lines = document.text.split("\n")

        # Find next non-empty line
        start_line = line
        for search_line in range(line, min(line + 3, len(lines))):
            if search_line < len(lines) and lines[search_line].strip():
                start_line = search_line
                break

        # Conservative: just the next line or two
        end_line = min(start_line + 2, len(lines))

        return ScopeBoundary(
            startLine=start_line + 1, endLine=end_line, type="conservative_fallback"
        )


class RobustTreeSitterWrapper:
    """
    Wrapper around tree-sitter with comprehensive error handling and fallback
    """

    def __init__(self):
        self.degradation_manager = GracefulDegradationManager()
        self._parser_cache = {}

    def parse_with_fallback(
        self, document: IDocument, operation: str = "general"
    ) -> Tuple[Optional[Any], bool]:
        """
        Parse document with comprehensive fallback handling

        Returns:
            Tuple of (parse_result, used_fallback)
        """
        try:
            from .tree_sitter_parser import TreeSitterParser

            # Try to get cached parser or create new one
            cache_key = document.languageId
            if cache_key not in self._parser_cache:
                parser = TreeSitterParser()
                parser.initialize()
                self._parser_cache[cache_key] = parser
            else:
                parser = self._parser_cache[cache_key]

            # Attempt parsing
            parse_result = parser.parse_document(document.text, document.languageId)

            if parse_result.success and parse_result.root_node:
                return parse_result, False
            else:
                # Parsing failed but didn't throw exception
                handle_tree_sitter_error(
                    f"Tree-sitter parsing failed for {operation}", language_id=document.languageId
                )
                return None, True

        except Exception as e:
            # Parsing threw exception
            handle_tree_sitter_error(
                f"Tree-sitter parsing exception during {operation}",
                language_id=document.languageId,
                cause=e,
            )
            return None, True

    def resolve_scope_with_robust_fallback(
        self, document: IDocument, line: int, scope: str
    ) -> Optional[ScopeBoundary]:
        """
        Resolve scope with robust fallback handling
        """
        parse_result, used_fallback = self.parse_with_fallback(
            document, f"scope resolution for {scope}"
        )

        if not used_fallback and parse_result:
            # Tree-sitter succeeded, try normal resolution
            try:
                from .language_scopes import get_language_scope_mappings
                from .tree_sitter_parser import TreeSitterParser

                parser = self._parser_cache.get(document.languageId)
                if not parser:
                    return self.degradation_manager.resolve_with_degradation(
                        document, line, scope, "parser_cache_miss"
                    )

                tree = parse_result.root_node
                scope_map = get_language_scope_mappings(document.languageId)

                if not scope_map:
                    return self.degradation_manager.resolve_with_degradation(
                        document, line, scope, "no_scope_mappings"
                    )

                node_types = scope_map.get(scope) or scope_map.get(scope.lower())
                if not node_types:
                    return self.degradation_manager.resolve_with_degradation(
                        document, line, scope, "no_node_types"
                    )

                # Try to find the scope using tree-sitter
                for search_line in range(line, min(line + 30, document.lineCount)):
                    search_node = parser.find_node_at_position(tree, search_line + 1, 0)
                    if search_node:
                        for node_type in node_types:
                            found_node = parser.find_parent_of_type(search_node, node_type)
                            if found_node:
                                boundaries = parser.get_node_boundaries(found_node)
                                return ScopeBoundary(
                                    startLine=boundaries.start.line,
                                    endLine=boundaries.end.line,
                                    type=f"robust_{found_node.type}",
                                )

                # Tree-sitter didn't find anything
                return self.degradation_manager.resolve_with_degradation(
                    document, line, scope, "tree_sitter_no_match"
                )

            except Exception as e:
                return self.degradation_manager.resolve_with_degradation(
                    document, line, scope, f"tree_sitter_exception: {e}"
                )

        else:
            # Tree-sitter failed from the start
            return self.degradation_manager.resolve_with_degradation(
                document, line, scope, "tree_sitter_parse_failed"
            )


# Global instances
_degradation_manager = GracefulDegradationManager()
_robust_parser = RobustTreeSitterWrapper()


def resolve_with_graceful_degradation(
    document: IDocument, line: int, scope: str
) -> Optional[ScopeBoundary]:
    """
    Public interface for graceful degradation scope resolution
    """
    return _degradation_manager.resolve_with_degradation(document, line, scope)


def parse_with_robust_fallback(
    document: IDocument, operation: str = "general"
) -> Tuple[Optional[Any], bool]:
    """
    Public interface for robust tree-sitter parsing with fallback
    """
    return _robust_parser.parse_with_fallback(document, operation)


def resolve_scope_with_comprehensive_fallback(
    document: IDocument, line: int, scope: str
) -> Optional[ScopeBoundary]:
    """
    Public interface for comprehensive scope resolution with all fallback strategies
    """
    return _robust_parser.resolve_scope_with_robust_fallback(document, line, scope)
