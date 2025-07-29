"""
Centralized exit codes for CodeGuard CLI
Each error type has a unique exit code for debugging and automation
"""

# Success
SUCCESS = 0

# Tree-sitter related errors (10-19)
TREE_SITTER_NOT_INSTALLED = 10
TREE_SITTER_LANGUAGE_NOT_SUPPORTED = 11
TREE_SITTER_LANGUAGE_LOAD_FAILED = 12
TREE_SITTER_NOT_INITIALIZED = 13

# Parser errors (20-29)
PARSER_INITIALIZATION_FAILED = 20
PARSER_DOCUMENT_FAILED = 21
PARSER_NODE_LOOKUP_FAILED = 22

# Scope resolution errors (30-39)
SCOPE_RESOLUTION_FAILED = 30
SCOPE_TYPE_INVALID = 31
REGEX_FALLBACK_FAILED = 32

# Guard processing errors (40-49)
GUARD_TAG_PARSE_FAILED = 40
GUARD_SYNTAX_INVALID = 41
GUARD_PERMISSION_CONFLICT = 42

# Document processing errors (50-59)
DOCUMENT_READ_FAILED = 50
DOCUMENT_FORMAT_INVALID = 51
DOCUMENT_ACCESS_DENIED = 52

# Validation errors (60-69)
VALIDATION_FAILED = 60
INPUT_VALIDATION_FAILED = 61
CONFIG_VALIDATION_FAILED = 62

# General application errors (70-79)
UNEXPECTED_ERROR = 70
DEPENDENCY_MISSING = 71
CONFIGURATION_ERROR = 72
PERMISSION_DENIED = 73

# Resource errors (80-89)
FILE_NOT_FOUND = 80
DIRECTORY_NOT_FOUND = 81
INSUFFICIENT_MEMORY = 82
DISK_FULL = 83
THEME_LOAD_FAILED = 84

# Network/external errors (90-99)
NETWORK_ERROR = 90
EXTERNAL_TOOL_FAILED = 91
API_ERROR = 92


def get_exit_code_description(code: int) -> str:
    """Get human-readable description for an exit code"""
    descriptions = {
        SUCCESS: "Success",
        # Tree-sitter errors
        TREE_SITTER_NOT_INSTALLED: "Tree-sitter library not installed",
        TREE_SITTER_LANGUAGE_NOT_SUPPORTED: "Programming language not supported by tree-sitter",
        TREE_SITTER_LANGUAGE_LOAD_FAILED: "Failed to load tree-sitter language parser",
        TREE_SITTER_NOT_INITIALIZED: "Tree-sitter parser not initialized",
        # Parser errors
        PARSER_INITIALIZATION_FAILED: "Parser initialization failed",
        PARSER_DOCUMENT_FAILED: "Failed to parse document",
        PARSER_NODE_LOOKUP_FAILED: "Failed to lookup AST node",
        # Scope resolution errors
        SCOPE_RESOLUTION_FAILED: "Scope resolution failed",
        SCOPE_TYPE_INVALID: "Invalid scope type specified",
        REGEX_FALLBACK_FAILED: "Regex fallback parsing failed",
        # Guard processing errors
        GUARD_TAG_PARSE_FAILED: "Guard tag parsing failed",
        GUARD_SYNTAX_INVALID: "Invalid guard tag syntax",
        GUARD_PERMISSION_CONFLICT: "Guard permission conflict detected",
        # Document processing errors
        DOCUMENT_READ_FAILED: "Failed to read document",
        DOCUMENT_FORMAT_INVALID: "Invalid document format",
        DOCUMENT_ACCESS_DENIED: "Document access denied",
        # Validation errors
        VALIDATION_FAILED: "Validation failed",
        INPUT_VALIDATION_FAILED: "Input validation failed",
        CONFIG_VALIDATION_FAILED: "Configuration validation failed",
        # General errors
        UNEXPECTED_ERROR: "Unexpected error occurred",
        DEPENDENCY_MISSING: "Required dependency missing",
        CONFIGURATION_ERROR: "Configuration error",
        PERMISSION_DENIED: "Permission denied",
        # Resource errors
        FILE_NOT_FOUND: "File not found",
        DIRECTORY_NOT_FOUND: "Directory not found",
        INSUFFICIENT_MEMORY: "Insufficient memory",
        DISK_FULL: "Disk full",
        THEME_LOAD_FAILED: "Theme loading failed",
        # Network/external errors
        NETWORK_ERROR: "Network error",
        EXTERNAL_TOOL_FAILED: "External tool failed",
        API_ERROR: "API error",
    }

    return descriptions.get(code, f"Unknown exit code: {code}")
