"""
Core regex patterns and normalization functions - platform agnostic
Single source of truth for all guard tag patterns
Port of the VSCode plugin's core/patterns.ts functionality
"""

import re
from typing import Dict, Optional

from .error_handling import handle_validation_error

# Guard tag prefix constant
GUARD_TAG_PREFIX = "@guard:"

# Permission aliases mapping - EXACT port from VSCode
PERMISSION_ALIASES = {
    "read": "r",
    "readonly": "r",
    "read-only": "r",
    "write": "w",
    "noaccess": "n",
    "none": "n",
    "no-access": "n",
}

# Scope aliases mapping - EXACT port from VSCode
SCOPE_ALIASES = {
    "sig": "signature",
    "func": "function",
    "stmt": "statement",
    "doc": "docstring",
    "dec": "decorator",
    "val": "value",
    "expr": "expression",
}


# Guard tag patterns - EXACT port from VSCode patterns.ts
class GUARD_TAG_PATTERNS:
    # Comprehensive guard tag pattern supporting ALL specification formats
    # Pattern: @guard:target[identifier]:permission[.scope][+scope][-scope][.if(condition)][metadata]
    GUARD_TAG = re.compile(
        r"(?://|#|--|/\*|\*|<!--)*\s*@guard:(ai|human|hu|all)(?:,(ai|human|hu|all))*(?:\[([^\]]+)\])?:(read-only|readonly|read|write|noaccess|none|context|r|w|n)(?::(r|w|read|write))?(?:\[([^\]]+)\])?(?:\.([a-zA-Z]+|\d+))?(?:\.if\(([^)]+)\))?(?:(\+[a-zA-Z]+)*)?(?:(-[a-zA-Z]+)*)?",
        re.IGNORECASE,
    )

    # Markdown-specific guard tag pattern
    MARKDOWN_GUARD_TAG = re.compile(
        r"<!--\s*@guard:(ai|human|hu|all)(?:,(ai|human|hu|all))*(?:\[([^\]]+)\])?:(read-only|readonly|read|write|noaccess|none|context|r|w|n)(?::(r|w|read|write))?(?:\[([^\]]+)\])?(?:\.([a-zA-Z]+|\d+))?(?:\.if\(([^)]+)\))?(?:(\+[a-zA-Z]+)*)?(?:(-[a-zA-Z]+)*)?(?:\s*-->)?",
        re.IGNORECASE,
    )

    # Pattern for extracting scope modifiers
    SCOPE_MODIFIER = re.compile(r"([+-])([a-zA-Z]+)", re.IGNORECASE)

    # Pattern for numeric line counts
    NUMERIC_SCOPE = re.compile(r"^\d+$")

    # Inline guard tag pattern for parseGuardTag function (non-global)
    PARSE_GUARD_TAG = re.compile(
        r"(?://|#|--|/\*|\*|<!--)*\s*@guard:(ai|human|hu|all)(?:,(ai|human|hu|all))*(?:\[([^\]]+)\])?:(read-only|readonly|read|write|noaccess|none|context|r|w|n)(?::(r|w|read|write))?(?:\[([^\]]+)\])?(?:\.([a-zA-Z]+|\d+))?(?:\.if\(([^)]+)\))?(?:(\+[a-zA-Z]+)*)?(?:(-[a-zA-Z]+)*)?",
        re.IGNORECASE,
    )

    # Simple pattern to detect any guard tag (case-insensitive)
    HAS_GUARD_TAG = re.compile(r"@guard:", re.IGNORECASE)


# Helper functions for normalizing permissions and scopes
def normalize_permission(permission: str) -> str:
    """Normalize permission using alias mapping."""
    normalized = permission.lower()
    return PERMISSION_ALIASES.get(normalized, normalized)


def normalize_scope(scope: str) -> str:
    """Normalize scope using alias mapping."""
    normalized = scope.lower()
    return SCOPE_ALIASES.get(normalized, normalized)


# Utility patterns
class UTILITY_PATTERNS:
    # Path normalization
    BACKSLASH = re.compile(r"\\")
    TRAILING_SLASH = re.compile(r"/+$")

    # Line splitting
    LINE_SPLIT = re.compile(r"\r?\n")

    # Numeric validation
    NUMERIC_ONLY = re.compile(r"^\d+$")


# Language-specific patterns for semantic scope detection
LANGUAGE_PATTERNS = {
    # JavaScript/TypeScript patterns
    "javascript": {
        "FUNCTION": re.compile(
            r"^(?:\s*(?:export\s+)?(?:async\s+)?function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>|\w+\s*=>))"
        ),
        "CLASS": re.compile(r"^(?:\s*(?:export\s+)?(?:abstract\s+)?class\s+\w+)"),
        "METHOD": re.compile(
            r"^(?:\s*(?:async\s+)?(?:static\s+)?(?:get\s+|set\s+)?\w+\s*\([^)]*\)\s*(?:\{|=>))"
        ),
        "BLOCK": re.compile(r"^(?:\s*(?:if|for|while|do|try|catch|finally)\s*(?:\([^)]*\))?\s*\{)"),
    },
    # Python patterns
    "python": {
        "FUNCTION": re.compile(r"^(?:\s*(?:async\s+)?def\s+\w+\s*\()"),
        "CLASS": re.compile(r"^(?:\s*class\s+\w+(?:\s*\([^)]*\))?:)"),
        "METHOD": re.compile(r"^(?:\s{4,}(?:async\s+)?def\s+\w+\s*\()"),
        "BLOCK": re.compile(r"^(?:\s*(?:if|for|while|try|except|finally|with)\s+.+:)"),
        "DECORATOR": re.compile(r"^(?:\s*@\w+)"),
    },
    # Java patterns
    "java": {
        "FUNCTION": re.compile(
            r"^(?:\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:\w+(?:<[^>]+>)?)\s+\w+\s*\([^)]*\)\s*(?:throws\s+\w+(?:\s*,\s*\w+)*)?\s*\{)"
        ),
        "CLASS": re.compile(
            r"^(?:\s*(?:public|private|protected)?\s*(?:abstract\s+|final\s+)?class\s+\w+(?:<[^>]+>)?(?:\s+extends\s+\w+)?(?:\s+implements\s+\w+(?:\s*,\s*\w+)*)?\s*\{)"
        ),
        "METHOD": re.compile(
            r"^(?:\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:\w+(?:<[^>]+>)?)\s+\w+\s*\([^)]*\)\s*(?:throws\s+\w+(?:\s*,\s*\w+)*)?\s*\{)"
        ),
        "BLOCK": re.compile(r"^(?:\s*(?:if|for|while|do|try|catch|finally)\s*(?:\([^)]*\))?\s*\{)"),
    },
    # C# patterns
    "csharp": {
        "FUNCTION": re.compile(
            r"^(?:\s*(?:public|private|protected|internal)?\s*(?:static\s+)?(?:async\s+)?(?:\w+(?:<[^>]+>)?)\s+\w+\s*\([^)]*\)\s*(?:where\s+\w+\s*:\s*\w+)?\s*\{)"
        ),
        "CLASS": re.compile(
            r"^(?:\s*(?:public|private|protected|internal)?\s*(?:abstract\s+|sealed\s+)?(?:partial\s+)?class\s+\w+(?:<[^>]+>)?(?:\s*:\s*\w+(?:\s*,\s*\w+)*)?(?:\s*where\s+\w+\s*:\s*\w+)?\s*\{)"
        ),
        "METHOD": re.compile(
            r"^(?:\s*(?:public|private|protected|internal)?\s*(?:static\s+)?(?:async\s+)?(?:\w+(?:<[^>]+>)?)\s+\w+\s*\([^)]*\)\s*(?:where\s+\w+\s*:\s*\w+)?\s*\{)"
        ),
        "BLOCK": re.compile(
            r"^(?:\s*(?:if|for|foreach|while|do|try|catch|finally)\s*(?:\([^)]*\))?\s*\{)"
        ),
    },
}

# Cache for dynamically created patterns
_pattern_cache: Dict[str, re.Pattern] = {}


def get_cached_pattern(pattern: str, flags: int = 0) -> re.Pattern:
    """Get or create a cached regex pattern."""
    key = f"{pattern}::{flags}"

    if key not in _pattern_cache:
        try:
            _pattern_cache[key] = re.compile(pattern, flags)
        except re.error as error:
            handle_validation_error(
                f"Failed to compile regex pattern: {pattern}",
                additional_data={"pattern": pattern, "flags": flags},
                cause=error,
            )
            # Return a pattern that never matches
            return re.compile(r"(?!)")

    return _pattern_cache[key]


def clear_pattern_cache() -> None:
    """Clear the pattern cache (useful for testing)."""
    _pattern_cache.clear()


def get_language_patterns(language_id: str) -> Optional[Dict[str, re.Pattern]]:
    """Get language-specific patterns."""
    language_map = {
        "javascript": "javascript",
        "javascriptreact": "javascript",
        "typescript": "javascript",
        "typescriptreact": "javascript",
        "python": "python",
        "java": "java",
        "c": "csharp",  # Use C# patterns for C (similar structure)
        "cpp": "csharp",  # Use C# patterns for C++ (similar structure)
        "csharp": "csharp",
        "cs": "csharp",
        "go": "csharp",  # Use C# patterns for Go (similar structure)
        "rust": "csharp",  # Use C# patterns for Rust (similar structure)
        "php": "csharp",  # Use C# patterns for PHP (similar structure)
        "ruby": "python",  # Use Python patterns for Ruby (similar structure)
        "html": "javascript",  # Use JavaScript patterns for HTML
        "css": "javascript",  # Use JavaScript patterns for CSS
        "bash": "python",  # Use Python patterns for Bash
        "sql": "javascript",  # Use JavaScript patterns for SQL
        "json": "javascript",  # Use JavaScript patterns for JSON
        "yaml": "python",  # Use Python patterns for YAML
        "toml": "python",  # Use Python patterns for TOML
        "lua": "python",  # Use Python patterns for Lua
        "scala": "java",  # Use Java patterns for Scala (similar structure)
        "haskell": "python",  # Use Python patterns for Haskell
        "ocaml": "python",  # Use Python patterns for OCaml
        "swift": "csharp",  # Use C# patterns for Swift
        "kotlin": "java",  # Use Java patterns for Kotlin
    }

    mapped_language = language_map.get(language_id)
    return LANGUAGE_PATTERNS.get(mapped_language) if mapped_language else None
