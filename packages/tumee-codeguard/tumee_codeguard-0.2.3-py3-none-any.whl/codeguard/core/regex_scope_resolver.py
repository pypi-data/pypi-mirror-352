"""
Regex-based scope resolution fallback system
Exact port of VSCode src/core/regexScopeResolver.ts
Used when tree-sitter parsing fails or is unavailable
"""

import re
from typing import Dict, List, Optional, Tuple

from .language_scopes import get_language_scope_mappings
from .types import IDocument, ScopeBoundary


class RegexScopeResolver:
    """Regex-based scope resolution for when tree-sitter fails"""

    def __init__(self):
        self._language_patterns = self._initialize_language_patterns()

    def _initialize_language_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize regex patterns for each language and scope type"""
        return {
            "python": {
                "class": [
                    r"^(\s*)class\s+\w+.*?:",
                    r"^(\s*)@\w+.*?\n\s*class\s+\w+.*?:",  # decorated classes
                ],
                "func": [
                    r"^(\s*)def\s+\w+.*?:",
                    r"^(\s*)async\s+def\s+\w+.*?:",
                    r"^(\s*)@\w+.*?\n\s*def\s+\w+.*?:",  # decorated functions
                    r"^(\s*)@\w+.*?\n\s*async\s+def\s+\w+.*?:",  # decorated async functions
                ],
                "function": [
                    r"^(\s*)def\s+\w+.*?:",
                    r"^(\s*)async\s+def\s+\w+.*?:",
                    r"^(\s*)@\w+.*?\n\s*def\s+\w+.*?:",
                    r"^(\s*)@\w+.*?\n\s*async\s+def\s+\w+.*?:",
                ],
                "signature": [r"^(\s*)def\s+\w+.*?:", r"^(\s*)async\s+def\s+\w+.*?:"],
            },
            "javascript": {
                "class": [
                    r"^(\s*)class\s+\w+.*?\{",
                    r"^(\s*)export\s+class\s+\w+.*?\{",
                    r"^(\s*)export\s+default\s+class\s+\w+.*?\{",
                ],
                "func": [
                    r"^(\s*)function\s+\w+.*?\{",
                    r"^(\s*)async\s+function\s+\w+.*?\{",
                    r"^(\s*)\w+\s*:\s*function.*?\{",
                    r"^(\s*)\w+\s*:\s*async\s+function.*?\{",
                    r"^(\s*)\w+.*?=>\s*\{",
                    r"^(\s*)const\s+\w+\s*=\s*.*?=>\s*\{",
                    r"^(\s*)let\s+\w+\s*=\s*.*?=>\s*\{",
                    r"^(\s*)var\s+\w+\s*=\s*.*?=>\s*\{",
                ],
                "function": [
                    r"^(\s*)function\s+\w+.*?\{",
                    r"^(\s*)async\s+function\s+\w+.*?\{",
                    r"^(\s*)\w+\s*:\s*function.*?\{",
                    r"^(\s*)\w+\s*:\s*async\s+function.*?\{",
                    r"^(\s*)\w+.*?=>\s*\{",
                    r"^(\s*)const\s+\w+\s*=\s*.*?=>\s*\{",
                    r"^(\s*)let\s+\w+\s*=\s*.*?=>\s*\{",
                    r"^(\s*)var\s+\w+\s*=\s*.*?=>\s*\{",
                ],
            },
            "typescript": {
                "class": [
                    r"^(\s*)class\s+\w+.*?\{",
                    r"^(\s*)export\s+class\s+\w+.*?\{",
                    r"^(\s*)export\s+default\s+class\s+\w+.*?\{",
                    r"^(\s*)abstract\s+class\s+\w+.*?\{",
                ],
                "func": [
                    r"^(\s*)function\s+\w+.*?\{",
                    r"^(\s*)async\s+function\s+\w+.*?\{",
                    r"^(\s*)\w+\s*:\s*function.*?\{",
                    r"^(\s*)\w+\s*:\s*async\s+function.*?\{",
                    r"^(\s*)\w+.*?=>\s*\{",
                    r"^(\s*)const\s+\w+\s*=\s*.*?=>\s*\{",
                    r"^(\s*)let\s+\w+\s*=\s*.*?=>\s*\{",
                    r"^(\s*)\w+\(.*?\)\s*:\s*.*?\s*\{",  # typed functions
                    r"^(\s*)public\s+\w+\(.*?\)\s*:\s*.*?\s*\{",
                    r"^(\s*)private\s+\w+\(.*?\)\s*:\s*.*?\s*\{",
                    r"^(\s*)protected\s+\w+\(.*?\)\s*:\s*.*?\s*\{",
                ],
            },
            "java": {
                "class": [
                    r"^(\s*)public\s+class\s+\w+.*?\{",
                    r"^(\s*)private\s+class\s+\w+.*?\{",
                    r"^(\s*)protected\s+class\s+\w+.*?\{",
                    r"^(\s*)class\s+\w+.*?\{",
                    r"^(\s*)abstract\s+class\s+\w+.*?\{",
                    r"^(\s*)final\s+class\s+\w+.*?\{",
                ],
                "func": [
                    r"^(\s*)public\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                    r"^(\s*)private\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                    r"^(\s*)protected\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                    r"^(\s*)static\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                    r"^(\s*)final\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                ],
            },
            "csharp": {
                "class": [
                    r"^(\s*)public\s+class\s+\w+.*?\{",
                    r"^(\s*)private\s+class\s+\w+.*?\{",
                    r"^(\s*)protected\s+class\s+\w+.*?\{",
                    r"^(\s*)internal\s+class\s+\w+.*?\{",
                    r"^(\s*)abstract\s+class\s+\w+.*?\{",
                    r"^(\s*)sealed\s+class\s+\w+.*?\{",
                    r"^(\s*)static\s+class\s+\w+.*?\{",
                ],
                "func": [
                    r"^(\s*)public\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                    r"^(\s*)private\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                    r"^(\s*)protected\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                    r"^(\s*)internal\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                    r"^(\s*)static\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                    r"^(\s*)async\s+.*?\s+\w+\s*\(.*?\)\s*\{",
                ],
            },
        }

    def resolve_scope_with_regex(
        self, document: IDocument, start_line: int, scope: str
    ) -> Optional[ScopeBoundary]:
        """
        Resolve scope using regex patterns as fallback
        """
        language_id = document.languageId.lower()

        # Get patterns for this language
        language_patterns = self._language_patterns.get(language_id)
        if not language_patterns:
            return None

        scope_patterns = language_patterns.get(scope)
        if not scope_patterns:
            return None

        lines = document.text.split("\n")
        total_lines = len(lines)

        # Search forward from start_line to find matching pattern
        for search_line in range(start_line, total_lines):
            line_text = lines[search_line]

            for pattern in scope_patterns:
                match = re.match(pattern, line_text, re.MULTILINE | re.DOTALL)
                if match:
                    # Found the start of the scope
                    scope_start = search_line + 1  # Convert to 1-based
                    scope_end = self._find_scope_end(
                        lines, search_line, match.group(1), language_id, scope
                    )

                    return ScopeBoundary(
                        startLine=scope_start, endLine=scope_end, type=f"regex_{scope}"
                    )

        return None

    def _find_scope_end(
        self, lines: List[str], start_line: int, base_indent: str, language_id: str, scope: str
    ) -> int:
        """
        Find the end of a scope based on indentation and language-specific rules
        """
        if language_id == "python":
            return self._find_python_scope_end(lines, start_line, base_indent)
        elif language_id in ["javascript", "typescript", "java", "csharp"]:
            return self._find_brace_scope_end(lines, start_line)
        else:
            # Fallback: use indentation
            return self._find_indent_scope_end(lines, start_line, base_indent)

    def _find_python_scope_end(self, lines: List[str], start_line: int, base_indent: str) -> int:
        """
        Find end of Python scope using indentation rules
        """
        base_indent_level = len(base_indent)

        for i in range(start_line + 1, len(lines)):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                continue

            # Calculate indentation level
            current_indent = len(line) - len(line.lstrip())

            # If we find a line with equal or less indentation than base, scope ends
            if current_indent <= base_indent_level:
                return i  # 1-based line number

        # If we reach end of file, scope extends to end
        return len(lines)

    def _find_brace_scope_end(self, lines: List[str], start_line: int) -> int:
        """
        Find end of brace-based scope (JavaScript, TypeScript, Java, C#)
        """
        brace_count = 0
        found_opening = False

        for i in range(start_line, len(lines)):
            line = lines[i]

            # Count braces in this line
            for char in line:
                if char == "{":
                    brace_count += 1
                    found_opening = True
                elif char == "}":
                    brace_count -= 1

                    # If we've found the opening brace and count returns to 0
                    if found_opening and brace_count == 0:
                        return i + 1  # Convert to 1-based

        # If we reach end without closing, scope extends to end
        return len(lines)

    def _find_indent_scope_end(self, lines: List[str], start_line: int, base_indent: str) -> int:
        """
        Generic indentation-based scope detection
        """
        base_indent_level = len(base_indent)

        for i in range(start_line + 1, len(lines)):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                continue

            # Calculate indentation level
            current_indent = len(line) - len(line.lstrip())

            # If indentation decreases to base level or less, scope ends
            if current_indent <= base_indent_level:
                return i  # 1-based line number

        return len(lines)

    def resolve_context_scope_regex(self, document: IDocument, start_line: int) -> ScopeBoundary:
        """
        Resolve context scope using regex patterns for comment detection
        """
        lines = document.text.split("\n")
        language_id = document.languageId.lower()

        # Language-specific comment patterns
        comment_patterns = {
            "python": [r"^\s*#", r"^\s*\"\"\"", r"^\s*'''"],
            "javascript": [r"^\s*//", r"^\s*/\*", r"^\s*\*"],
            "typescript": [r"^\s*//", r"^\s*/\*", r"^\s*\*"],
            "java": [r"^\s*//", r"^\s*/\*", r"^\s*\*"],
            "csharp": [r"^\s*//", r"^\s*/\*", r"^\s*\*"],
            "c": [r"^\s*//", r"^\s*/\*", r"^\s*\*"],
            "cpp": [r"^\s*//", r"^\s*/\*", r"^\s*\*"],
        }

        patterns = comment_patterns.get(language_id, [r"^\s*#", r"^\s*//"])
        end_line = start_line

        # Find next non-comment lines
        for i in range(start_line, len(lines)):
            line = lines[i].strip()

            if not line:
                continue

            # Check if line matches any comment pattern
            is_comment = any(re.match(pattern, lines[i]) for pattern in patterns)

            if not is_comment:
                end_line = i + 1  # Convert to 1-based
                break

        return ScopeBoundary(startLine=start_line + 1, endLine=end_line, type="regex_context")


# Global instance for reuse
_regex_resolver = RegexScopeResolver()


def resolve_scope_with_regex_fallback(
    document: IDocument, start_line: int, scope: str
) -> Optional[ScopeBoundary]:
    """
    Public interface for regex scope resolution
    """
    return _regex_resolver.resolve_scope_with_regex(document, start_line, scope)


def resolve_context_scope_with_regex(document: IDocument, start_line: int) -> ScopeBoundary:
    """
    Public interface for regex context scope resolution
    """
    return _regex_resolver.resolve_context_scope_regex(document, start_line)
