"""
Advanced scope resolution with sophisticated block detection
Enhanced port of VSCode block scope logic with fallback mechanisms
"""

import re
from typing import Dict, List, Optional, Tuple

from .error_handling import handle_scope_resolution_error, log_debug
from .language_scopes import get_language_scope_mappings
from .regex_scope_resolver import resolve_scope_with_regex_fallback
from .tree_sitter_parser import TreeSitterParser
from .types import IDocument, ScopeBoundary


class AdvancedScopeResolver:
    """Advanced scope resolver with sophisticated block detection and fallback strategies"""

    def __init__(self):
        self.parser = TreeSitterParser()
        self.parser.initialize()

        # Cache for scope resolution results
        self._scope_cache: Dict[str, ScopeBoundary] = {}

        # Block detection patterns for different languages
        self._block_patterns = {
            "python": {
                "top_level_blocks": [
                    r"^(def|class|if|for|while|with|try)\s+",
                    r"^(async\s+def)\s+",
                    r"^@\w+",  # decorators
                ],
                "function_scoped_blocks": [
                    r"^\s+(if|for|while|with|try)\s+",
                    r"^\s+(elif|else|except|finally):",
                ],
                "indent_based": True,
            },
            "javascript": {
                "top_level_blocks": [
                    r"^(function|class|if|for|while|switch|try)\s+",
                    r"^(const|let|var)\s+\w+\s*=\s*(function|\(.*?\)\s*=>)",
                    r"^(export\s+)?(function|class|const|let|var)\s+",
                ],
                "function_scoped_blocks": [
                    r"^\s+(if|for|while|switch|try)\s*\(",
                    r"^\s+(else|catch|finally)\s*(\{|\()?",
                ],
                "brace_based": True,
            },
            "typescript": {
                "extends": "javascript",
                "additional_patterns": [
                    r"^(interface|type|enum|namespace)\s+",
                    r"^(abstract\s+)?(class)\s+",
                ],
            },
        }

    def resolve_block_scope_advanced(
        self, document: IDocument, start_line: int
    ) -> Optional[ScopeBoundary]:
        """
        Advanced block scope resolution with sophisticated detection
        """
        cache_key = f"{document.languageId}:{start_line}:{hash(document.text)}"
        if cache_key in self._scope_cache:
            log_debug(f"Using cached scope result for {cache_key}")
            return self._scope_cache[cache_key]

        try:
            # Primary strategy: Tree-sitter with advanced logic
            result = self._resolve_with_tree_sitter_advanced(document, start_line)

            if not result:
                log_debug(f"Tree-sitter failed for line {start_line}, trying regex fallback")
                # Fallback strategy: Regex-based detection
                result = self._resolve_with_regex_advanced(document, start_line)

            if not result:
                log_debug(f"Regex fallback failed for line {start_line}, using simple heuristics")
                # Final fallback: Simple heuristics
                result = self._resolve_with_heuristics(document, start_line)

            # Cache the result
            if result:
                self._scope_cache[cache_key] = result

            return result

        except Exception as e:
            handle_scope_resolution_error(
                f"Advanced block scope resolution failed",
                scope_type="block",
                line_number=start_line,
                cause=e,
            )
            return None

    def _resolve_with_tree_sitter_advanced(
        self, document: IDocument, start_line: int
    ) -> Optional[ScopeBoundary]:
        """
        Advanced tree-sitter based block resolution
        """
        try:
            parse_result = self.parser.parse_document(document.text, document.languageId)
            if not parse_result.success or not parse_result.root_node:
                return None

            tree = parse_result.root_node
            lines = document.text.split("\n")

            # Search forward from start_line to find next block
            for search_line in range(start_line, min(start_line + 50, len(lines))):  # Limit search
                line_text = lines[search_line].strip()

                if not line_text or line_text.startswith(("#", "//", "/*")):
                    continue

                # Find node at this line
                node = self.parser.find_node_at_position(tree, search_line + 1, 0)
                if not node:
                    continue

                # Check if this is a significant block structure
                if self._is_significant_block_node(node, document.languageId):
                    boundaries = self.parser.get_node_boundaries(node)

                    # Refine boundaries based on block type
                    refined_boundaries = self._refine_block_boundaries(
                        boundaries, document, node.type
                    )

                    return ScopeBoundary(
                        startLine=refined_boundaries.start.line,
                        endLine=refined_boundaries.end.line,
                        type=f"tree_sitter_{node.type}",
                    )

            return None

        except Exception as e:
            log_debug(f"Tree-sitter advanced resolution failed: {e}")
            return None

    def _is_significant_block_node(self, node, language_id: str) -> bool:
        """
        Determine if a node represents a significant block structure
        """
        scope_mappings = get_language_scope_mappings(language_id)
        if not scope_mappings:
            return False

        block_types = scope_mappings.get("block", [])

        # Check if node type is in block types
        if node.type in block_types:
            return True

        # Language-specific significant blocks
        if language_id == "python":
            return node.type in [
                "if_statement",
                "for_statement",
                "while_statement",
                "with_statement",
                "try_statement",
                "function_definition",
                "class_definition",
                "dictionary",
                "list",
                "set",
            ]
        elif language_id in ["javascript", "typescript"]:
            return node.type in [
                "if_statement",
                "for_statement",
                "while_statement",
                "switch_statement",
                "try_statement",
                "function_declaration",
                "class_declaration",
                "object",
                "array",
                "block",
            ]
        elif language_id == "java":
            return node.type in [
                "if_statement",
                "for_statement",
                "while_statement",
                "switch_statement",
                "try_statement",
                "method_declaration",
                "class_declaration",
                "block",
            ]

        return False

    def _refine_block_boundaries(self, boundaries, document: IDocument, node_type: str):
        """
        Refine block boundaries based on language and node type
        """
        lines = document.text.split("\n")

        # For Python, handle indentation-based refinement
        if document.languageId == "python":
            return self._refine_python_block_boundaries(boundaries, lines, node_type)

        # For brace-based languages, ensure we capture the full block
        elif document.languageId in ["javascript", "typescript", "java", "csharp"]:
            return self._refine_brace_block_boundaries(boundaries, lines, node_type)

        return boundaries

    def _refine_python_block_boundaries(self, boundaries, lines: List[str], node_type: str):
        """
        Python-specific block boundary refinement
        """
        start_line = boundaries.start.line - 1  # Convert to 0-based
        end_line = boundaries.end.line - 1

        # For dictionaries and lists, find the actual closing bracket
        if node_type in ["dictionary", "list", "set"]:
            bracket_map = {"dictionary": ("{", "}"), "list": ("[", "]"), "set": ("{", "}")}
            open_bracket, close_bracket = bracket_map.get(node_type, ("{", "}"))

            bracket_count = 0
            for i in range(start_line, min(len(lines), end_line + 10)):
                line = lines[i]
                for char in line:
                    if char == open_bracket:
                        bracket_count += 1
                    elif char == close_bracket:
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_line = i
                            break
                if bracket_count == 0:
                    break

        # Trim trailing empty lines
        while end_line > start_line and not lines[end_line].strip():
            end_line -= 1

        return type(boundaries)(
            start=type(boundaries.start)(line=start_line + 1, column=boundaries.start.column),
            end=type(boundaries.end)(line=end_line + 1, column=0),
        )

    def _refine_brace_block_boundaries(self, boundaries, lines: List[str], node_type: str):
        """
        Brace-based language block boundary refinement
        """
        start_line = boundaries.start.line - 1  # Convert to 0-based
        end_line = boundaries.end.line - 1

        # Find balanced braces
        brace_count = 0
        for i in range(start_line, min(len(lines), end_line + 10)):
            line = lines[i]
            for char in line:
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_line = i
                        break
            if brace_count == 0:
                break

        return type(boundaries)(
            start=type(boundaries.start)(line=start_line + 1, column=boundaries.start.column),
            end=type(boundaries.end)(line=end_line + 1, column=0),
        )

    def _resolve_with_regex_advanced(
        self, document: IDocument, start_line: int
    ) -> Optional[ScopeBoundary]:
        """
        Advanced regex-based block resolution with language-specific patterns
        """
        try:
            language_patterns = self._block_patterns.get(document.languageId)
            if not language_patterns:
                # Try fallback to basic regex resolver
                return resolve_scope_with_regex_fallback(document, start_line, "block")

            lines = document.text.split("\n")

            # Search for block patterns
            for search_line in range(start_line, min(start_line + 30, len(lines))):
                line_text = lines[search_line]

                # Check top-level block patterns
                for pattern in language_patterns.get("top_level_blocks", []):
                    if re.match(pattern, line_text):
                        end_line = self._find_block_end_regex(lines, search_line, language_patterns)
                        return ScopeBoundary(
                            startLine=search_line + 1, endLine=end_line + 1, type="regex_block"
                        )

                # Check function-scoped block patterns
                for pattern in language_patterns.get("function_scoped_blocks", []):
                    if re.match(pattern, line_text):
                        end_line = self._find_block_end_regex(lines, search_line, language_patterns)
                        return ScopeBoundary(
                            startLine=search_line + 1,
                            endLine=end_line + 1,
                            type="regex_function_block",
                        )

            return None

        except Exception as e:
            log_debug(f"Regex advanced resolution failed: {e}")
            return None

    def _find_block_end_regex(
        self, lines: List[str], start_line: int, language_patterns: Dict
    ) -> int:
        """
        Find the end of a block using regex patterns and language rules
        """
        if language_patterns.get("indent_based"):
            return self._find_indent_block_end(lines, start_line)
        elif language_patterns.get("brace_based"):
            return self._find_brace_block_end(lines, start_line)
        else:
            # Generic approach
            return self._find_generic_block_end(lines, start_line)

    def _find_indent_block_end(self, lines: List[str], start_line: int) -> int:
        """
        Find end of indentation-based block (Python-style)
        """
        start_indent = len(lines[start_line]) - len(lines[start_line].lstrip())

        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if not line.strip():  # Skip empty lines
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= start_indent:
                return i - 1

        return len(lines) - 1

    def _find_brace_block_end(self, lines: List[str], start_line: int) -> int:
        """
        Find end of brace-based block
        """
        brace_count = 0
        for i in range(start_line, len(lines)):
            line = lines[i]
            for char in line:
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        return i

        return len(lines) - 1

    def _find_generic_block_end(self, lines: List[str], start_line: int) -> int:
        """
        Generic block end detection
        """
        # Simple heuristic: look for next significant line at same or lower indentation
        start_indent = len(lines[start_line]) - len(lines[start_line].lstrip())

        for i in range(start_line + 1, min(start_line + 20, len(lines))):
            line = lines[i]
            if not line.strip():
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= start_indent and line.strip():
                return i - 1

        return min(start_line + 10, len(lines) - 1)

    def _resolve_with_heuristics(
        self, document: IDocument, start_line: int
    ) -> Optional[ScopeBoundary]:
        """
        Simple heuristic-based block detection as final fallback
        """
        lines = document.text.split("\n")

        # Look for next non-empty, non-comment line
        for search_line in range(start_line, min(start_line + 10, len(lines))):
            line_text = lines[search_line].strip()

            if not line_text:
                continue

            # Skip comments
            if (
                line_text.startswith("#")
                or line_text.startswith("//")
                or line_text.startswith("/*")
            ):
                continue

            # Simple end detection: next 5 lines or until indentation decreases
            end_line = min(search_line + 5, len(lines) - 1)

            return ScopeBoundary(
                startLine=search_line + 1, endLine=end_line + 1, type="heuristic_block"
            )

        # Ultimate fallback: single line
        return ScopeBoundary(
            startLine=start_line + 1, endLine=start_line + 1, type="fallback_single_line"
        )


# Global instance
_advanced_resolver = AdvancedScopeResolver()


def resolve_block_scope_advanced(document: IDocument, start_line: int) -> Optional[ScopeBoundary]:
    """
    Public interface for advanced block scope resolution
    """
    return _advanced_resolver.resolve_block_scope_advanced(document, start_line)
