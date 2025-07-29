"""
Tree-sitter based parser for CodeGuard CLI.
Port of the VSCode plugin's core/parser.ts functionality.
"""

import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .error_handling import get_logger
from .exit_codes import (
    TREE_SITTER_LANGUAGE_LOAD_FAILED,
    TREE_SITTER_LANGUAGE_NOT_SUPPORTED,
    TREE_SITTER_NOT_INITIALIZED,
    TREE_SITTER_NOT_INSTALLED,
)

try:
    import tree_sitter as ts
    from tree_sitter import Language, Node, Tree

    TREE_SITTER_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.critical(f"tree-sitter is required but not available: {e}")
    logger.critical("Install tree-sitter with: pip install tree-sitter")
    sys.exit(TREE_SITTER_NOT_INSTALLED)


@dataclass
class NodePosition:
    """Position information for a tree-sitter node."""

    line: int
    column: int


@dataclass
class NodeBoundaries:
    """Boundary information for a tree-sitter node."""

    start: NodePosition
    end: NodePosition


@dataclass
class ParseResult:
    """Result of parsing a document with tree-sitter."""

    tree: Optional["Tree"]
    root_node: Optional["Node"]
    language: str
    success: bool
    error_message: Optional[str] = None


class TreeSitterParser:
    """Tree-sitter parser for various programming languages."""

    def __init__(self):
        self._languages: Dict[str, Language] = {}
        self._supported_languages = {
            "python": "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "typescriptreact": "tsx",
            "javascriptreact": "javascript",
            "java": "java",
            "c": "c",
            "cpp": "cpp",
            "csharp": "c_sharp",
            "go": "go",
            "rust": "rust",
            "php": "php",
            "ruby": "ruby",
            "html": "html",
            "css": "css",
            "bash": "bash",
            "sql": "sql",
            "json": "json",
            "yaml": "yaml",
            "toml": "toml",
            "lua": "lua",
            "scala": "scala",
            "haskell": "haskell",
            "ocaml": "ocaml",
        }
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize tree-sitter - parsers are loaded lazily per language."""
        if self._initialized:
            return True

        # Just mark as initialized - parsers are loaded on-demand
        self._initialized = True
        return self._initialized

    def _load_language_parser(self, language_id: str) -> bool:
        """Load a specific language parser on-demand. Exit if it fails to load."""
        if language_id in self._languages:
            return True  # Already loaded

        # Map of language IDs to their tree-sitter package imports
        language_imports = {
            "python": "tree_sitter_python",
            "javascript": "tree_sitter_javascript",
            "typescript": "tree_sitter_typescript",
            "typescriptreact": "tree_sitter_typescript",
            "javascriptreact": "tree_sitter_javascript",
            "java": "tree_sitter_java",
            "c": "tree_sitter_cpp",  # Use cpp parser for C
            "cpp": "tree_sitter_cpp",
            "csharp": "tree_sitter_c_sharp",
            "go": "tree_sitter_go",
            "rust": "tree_sitter_rust",
            "php": "tree_sitter_php",
            "ruby": "tree_sitter_ruby",
            "html": "tree_sitter_html",
            "css": "tree_sitter_css",
            "bash": "tree_sitter_bash",
            "sql": "tree_sitter_sql",
            "json": "tree_sitter_json",
            "yaml": "tree_sitter_yaml",
            "toml": "tree_sitter_toml",
            "lua": "tree_sitter_lua",
            "scala": "tree_sitter_scala",
            "haskell": "tree_sitter_haskell",
            "ocaml": "tree_sitter_ocaml",
        }

        if language_id not in language_imports:
            logger = get_logger(__name__)
            logger.critical(f"Language {language_id} not supported")
            logger.critical(f"Supported languages: {list(language_imports.keys())}")
            sys.exit(TREE_SITTER_LANGUAGE_NOT_SUPPORTED)

        module_name = language_imports[language_id]
        try:
            # Import the language package and get language object
            import importlib

            module = importlib.import_module(module_name)

            # Handle special cases for typescript (has multiple functions)
            if language_id == "typescript":
                language_obj = module.language_typescript()
            elif language_id == "typescriptreact":
                language_obj = module.language_tsx()
            else:
                # Standard case
                language_obj = module.language()

            # Create Language wrapper - this is the working pattern from the existing code
            language = Language(language_obj)
            self._languages[language_id] = language
            return True

        except ImportError as e:
            logger = get_logger(__name__)
            logger.critical(f"Required tree-sitter package not installed: {module_name}")
            logger.critical(f"Install with: pip install {module_name.replace('_', '-')}")
            sys.exit(TREE_SITTER_LANGUAGE_LOAD_FAILED)
        except Exception as e:
            logger = get_logger(__name__)
            logger.critical(f"Failed to load tree-sitter parser for {language_id}: {e}")
            sys.exit(TREE_SITTER_LANGUAGE_LOAD_FAILED)

    def _find_wasm_directory(self) -> Optional[Path]:
        """Find the tree-sitter WASM parsers directory."""
        # Check multiple possible locations
        possible_paths = [
            # Relative to this module
            Path(__file__).parent.parent.parent / "resources" / "tree-sitter-wasm",
            # From VSCode plugin (if available)
            Path(__file__).parent.parent.parent.parent
            / "CodeGuard-vscode-plugin"
            / "resources"
            / "tree-sitter-wasm",
            # Current working directory
            Path.cwd() / "resources" / "tree-sitter-wasm",
            # Check environment variable
            (
                Path(os.environ.get("TREE_SITTER_WASM_DIR", ""))
                if os.environ.get("TREE_SITTER_WASM_DIR")
                else None
            ),
        ]

        for path in possible_paths:
            if path and path.exists() and path.is_dir():
                return path

        return None

    def is_language_supported(self, language_id: str) -> bool:
        """Check if a language is supported."""
        return language_id in self._languages

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language IDs."""
        return list(self._languages.keys())

    def parse_document(self, content: str, language_id: str) -> ParseResult:
        """Parse a document using tree-sitter."""
        if not self._initialized:
            logger = get_logger(__name__)
            logger.critical("Tree-sitter not initialized")
            sys.exit(TREE_SITTER_NOT_INITIALIZED)

        # Load the language parser on-demand (exits if it fails to load)
        self._load_language_parser(language_id)

        try:
            language = self._languages[language_id]
            parser = ts.Parser(language)

            tree = parser.parse(content.encode("utf8"))
            return ParseResult(tree, tree.root_node, language_id, True)

        except Exception as e:
            # Don't exit on parsing errors - return failed result for recovery
            return ParseResult(None, None, language_id, False, str(e))

    def find_node_at_position(self, root_node: Node, line: int, column: int) -> Optional[Node]:
        """Find the smallest node containing the given position."""
        if not root_node:
            return None

        point = (line - 1, column)  # Convert to 0-based indexing
        return root_node.descendant_for_point_range(point, point)

    def find_parent_of_type(self, node: Node, node_type: str) -> Optional[Node]:
        """Find the first parent node of the specified type."""
        current = node.parent
        while current:
            if current.type == node_type:
                return current
            current = current.parent
        return None

    def get_node_boundaries(self, node: Node) -> NodeBoundaries:
        """Get the boundaries of a node."""
        start = NodePosition(node.start_point[0] + 1, node.start_point[1])  # Convert to 1-based
        end = NodePosition(node.end_point[0] + 1, node.end_point[1])
        return NodeBoundaries(start, end)

    def get_node_type_for_line(self, content: str, language_id: str, line_number: int) -> str:
        """Get the semantic node type for a specific line."""
        parse_result = self.parse_document(content, language_id)
        if not parse_result.success or not parse_result.root_node:
            return "comment"  # Fallback to "comment" when parsing fails

        # Find the most specific node for this line
        lines = content.split("\n")
        if line_number <= 0 or line_number > len(lines):
            return "unknown"

        line_content = lines[line_number - 1]

        # For empty lines, find node at position 0 to get containing scope
        if not line_content.strip():
            node = self.find_node_at_position(parse_result.root_node, line_number, 0)
        else:
            # Find node at the start of the line's content
            first_char_col = len(line_content) - len(line_content.lstrip())
            node = self.find_node_at_position(parse_result.root_node, line_number, first_char_col)

        if not node:
            return "unknown"

        # Return the most specific node type that covers this line
        node_type = node.type

        # Map some common node types to more readable names - matching VSCode output
        type_mappings = {
            "module": "program",
            "source_file": "program",
            "program": "program",
            "function_declaration": "function",
            "function_definition": "function",
            "method_definition": "method",
            "method_declaration": "method",
            "class_definition": "class",
            "class_declaration": "class",
            "interface_declaration": "interface",
            "type_declaration": "interface",
            "block": "body",
            "compound_statement": "body",
            "statement_block": "body",
            "expression_statement": "statement",
            "assignment_statement": "statement",
            "if_statement": "statement",
            "for_statement": "statement",
            "for_in_statement": "statement",
            "while_statement": "statement",
            "return_statement": "statement",
            "try_statement": "statement",
            "for": "statement",
            "try": "statement",
            "return": "statement",
            "if": "statement",
            "await": "statement",
            "await_expression": "statement",
            "comment": "comment",
            "string_literal": "string_fragment",
            "template_string": "template_str",
            "formal_parameters": "formal_param",
            "parameter_list": "formal_param",
            "import_statement": "import",
            "import_declaration": "import",
            "export_statement": "export",
            "export_declaration": "export",
            "variable_declaration": "lexical",
            "lexical_declaration": "lexical",
            "variable_declarator": "lexical",
            "const": "lexical",
            "let": "lexical",
            "var": "lexical",
            "object_expression": "object",
            "object_literal": "object",
            "object": "object",
            "pair": "pair",
            "property_identifier": "object",
            "shorthand_property_identifier": "shorthand_property_identifier",
            "dictionary": "object",
            "}": "object",
            "interface_body": "interface_body",
            "call_expression": "identifier",
            "member_expression": "identifier",
            "assignment_expression": "identifier",
            "binary_expression": "identifier",
            "identifier": "identifier",
            "this": "identifier",
            "static": "static",
            "async": "async",
        }

        return type_mappings.get(node_type, node_type)


# Global parser instance
_parser_instance: Optional[TreeSitterParser] = None


def get_parser() -> TreeSitterParser:
    """Get the global parser instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = TreeSitterParser()
        _parser_instance.initialize()
    return _parser_instance


def is_tree_sitter_available() -> bool:
    """Check if tree-sitter is available and initialized."""
    # Tree-sitter is always required, so this should always return True
    # If tree-sitter is not available, the module would have exited during import
    return get_parser()._initialized


def parse_document(content: str, language_id: str) -> ParseResult:
    """Parse a document using tree-sitter."""
    return get_parser().parse_document(content, language_id)


def get_node_type_for_line(content: str, language_id: str, line_number: int) -> str:
    """Get the semantic node type for a specific line."""
    return get_parser().get_node_type_for_line(content, language_id, line_number)


def find_node_at_position(root_node: Node, line: int, column: int) -> Optional[Node]:
    """Find the smallest node containing the given position."""
    return get_parser().find_node_at_position(root_node, line, column)


def find_parent_of_type(node: Node, node_type: str) -> Optional[Node]:
    """Find the first parent node of the specified type."""
    return get_parser().find_parent_of_type(node, node_type)


def get_node_boundaries(node: Node) -> NodeBoundaries:
    """Get the boundaries of a node."""
    return get_parser().get_node_boundaries(node)


def get_supported_languages() -> List[str]:
    """Get list of supported language IDs."""
    return get_parser().get_supported_languages()


def is_language_supported(language_id: str) -> bool:
    """Check if a language is supported."""
    return get_parser().is_language_supported(language_id)
