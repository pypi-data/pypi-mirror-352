"""
Core language scope mappings - embedded in CLI for consistency
Exact port of VSCode src/core/languageScopes.ts
No filesystem dependencies allowed in this module
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class LanguageScopes:
    scopes: Dict[str, List[str]]
    extends: Optional[str] = None


@dataclass
class LanguageScopeConfig:
    version: str
    commonPatterns: Optional[Dict[str, List[str]]] = None
    languages: Optional[Dict[str, LanguageScopes]] = None


# Embedded language scope configuration - identical to VSCode
EMBEDDED_LANGUAGE_SCOPES = LanguageScopeConfig(
    version="1.0.0",
    commonPatterns={
        "block": [
            "block",
            "statement_block",
            "compound_statement",
            "code_block",
            "object",
            "array",
            "dictionary",
        ],
        "func": [
            "function_declaration",
            "method_declaration",
            "function_definition",
            "method_definition",
        ],
        "class": ["class_declaration", "class_definition"],
        "statement": ["expression_statement", "assignment_statement", "declaration_statement"],
        "signature": [
            "function_declaration",
            "method_declaration",
            "function_definition",
            "method_definition",
        ],
    },
    languages={
        "javascript": LanguageScopes(
            scopes={
                "func": [
                    "function_declaration",
                    "method_definition",
                    "arrow_function",
                    "function_expression",
                ],
                "class": ["class_declaration"],
                "block": ["statement_block", "object", "array"],
                "statement": [
                    "expression_statement",
                    "variable_declaration",
                    "assignment_expression",
                ],
                "signature": ["function_declaration", "method_definition"],
            }
        ),
        "typescript": LanguageScopes(
            extends="javascript",
            scopes={
                "func": [
                    "function_declaration",
                    "method_definition",
                    "arrow_function",
                    "function_expression",
                    "method_signature",
                ],
                "class": ["class_declaration", "interface_declaration"],
                "block": ["statement_block", "object_type", "object", "array"],
                "statement": [
                    "expression_statement",
                    "variable_declaration",
                    "assignment_expression",
                    "type_alias_declaration",
                ],
                "signature": ["function_declaration", "method_definition", "method_signature"],
            },
        ),
        "tsx": LanguageScopes(extends="typescript", scopes={}),
        "javascriptreact": LanguageScopes(extends="javascript", scopes={}),
        "python": LanguageScopes(
            scopes={
                "func": ["function_definition", "async_function_definition"],
                "class": ["class_definition"],
                "block": ["block", "suite"],
                "statement": ["expression_statement", "assignment", "simple_statement"],
                "signature": ["function_definition", "async_function_definition"],
            }
        ),
        "java": LanguageScopes(
            scopes={
                "func": ["method_declaration", "constructor_declaration"],
                "class": ["class_declaration", "interface_declaration"],
                "block": ["block", "class_body", "interface_body"],
                "statement": ["expression_statement", "local_variable_declaration", "statement"],
                "signature": ["method_declaration", "constructor_declaration"],
            }
        ),
        "csharp": LanguageScopes(
            scopes={
                "func": ["method_declaration", "constructor_declaration"],
                "class": ["class_declaration", "interface_declaration", "struct_declaration"],
                "block": ["block", "class_body", "interface_body", "struct_body"],
                "statement": ["expression_statement", "local_declaration_statement", "statement"],
                "signature": ["method_declaration", "constructor_declaration"],
            }
        ),
        "c": LanguageScopes(
            scopes={
                "func": ["function_definition", "function_declarator"],
                "class": ["struct_specifier", "union_specifier"],
                "block": ["compound_statement", "struct_specifier", "union_specifier"],
                "statement": ["expression_statement", "declaration", "statement"],
                "signature": ["function_definition", "function_declarator"],
            }
        ),
        "cpp": LanguageScopes(
            extends="c",
            scopes={
                "func": ["function_definition", "function_declarator", "method_definition"],
                "class": ["class_specifier", "struct_specifier", "union_specifier"],
                "block": ["compound_statement", "class_specifier", "struct_specifier"],
                "statement": ["expression_statement", "declaration", "statement"],
                "signature": ["function_definition", "function_declarator", "method_definition"],
            },
        ),
        "go": LanguageScopes(
            scopes={
                "func": ["function_declaration", "method_declaration"],
                "class": ["type_declaration", "struct_type"],
                "block": ["block", "struct_type", "interface_type"],
                "statement": [
                    "expression_statement",
                    "assignment_statement",
                    "short_var_declaration",
                ],
                "signature": ["function_declaration", "method_declaration"],
            }
        ),
        "rust": LanguageScopes(
            scopes={
                "func": ["function_item"],
                "class": ["struct_item", "enum_item", "trait_item"],
                "block": ["block", "struct_item", "enum_item"],
                "statement": ["expression_statement", "let_declaration", "statement"],
                "signature": ["function_item"],
            }
        ),
        "ruby": LanguageScopes(
            scopes={
                "func": ["method", "singleton_method"],
                "class": ["class", "module"],
                "block": ["begin", "class", "module"],
                "statement": ["expression_statement", "assignment", "statement"],
                "signature": ["method", "singleton_method"],
            }
        ),
        "php": LanguageScopes(
            scopes={
                "func": ["function_definition", "method_declaration"],
                "class": ["class_declaration", "interface_declaration", "trait_declaration"],
                "block": ["compound_statement", "class_declaration", "interface_declaration"],
                "statement": ["expression_statement", "simple_statement", "statement"],
                "signature": ["function_definition", "method_declaration"],
            }
        ),
        "swift": LanguageScopes(
            scopes={
                "func": ["function_declaration", "method_declaration"],
                "class": ["class_declaration", "struct_declaration", "protocol_declaration"],
                "block": ["statements", "class_body", "struct_body"],
                "statement": ["expression_statement", "property_declaration", "statement"],
                "signature": ["function_declaration", "method_declaration"],
            }
        ),
        "kotlin": LanguageScopes(
            scopes={
                "func": ["function_declaration"],
                "class": ["class_declaration", "interface_declaration", "object_declaration"],
                "block": ["statements", "class_body", "interface_body"],
                "statement": ["expression_statement", "property_declaration", "statement"],
                "signature": ["function_declaration"],
            }
        ),
    },
)


def get_language_scope_mappings(language_id: str) -> Optional[Dict[str, List[str]]]:
    """
    Get scope mappings for a specific language
    Handles language extension via 'extends' property
    """
    if not EMBEDDED_LANGUAGE_SCOPES.languages:
        return None

    language_config = EMBEDDED_LANGUAGE_SCOPES.languages.get(language_id)
    if not language_config:
        return None

    # Start with base scopes
    scope_mappings = {}

    # If this language extends another, start with the parent's scopes
    if language_config.extends:
        parent_config = EMBEDDED_LANGUAGE_SCOPES.languages.get(language_config.extends)
        if parent_config:
            scope_mappings.update(parent_config.scopes)

    # Add/override with this language's specific scopes
    scope_mappings.update(language_config.scopes)

    return scope_mappings


def get_common_patterns() -> Optional[Dict[str, List[str]]]:
    """Get common patterns that apply across languages"""
    return EMBEDDED_LANGUAGE_SCOPES.commonPatterns


def get_supported_languages() -> List[str]:
    """Get list of all supported language IDs"""
    if not EMBEDDED_LANGUAGE_SCOPES.languages:
        return []
    return list(EMBEDDED_LANGUAGE_SCOPES.languages.keys())
