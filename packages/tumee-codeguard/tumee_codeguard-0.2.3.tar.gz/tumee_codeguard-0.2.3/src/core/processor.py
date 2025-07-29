"""
Core guard processing logic for CodeGuard CLI.
COMPLETE REWRITE with guard stack system - exact port of VSCode processor.ts
"""

from typing import Any, Dict, List, Optional, Tuple

from .error_handling import get_logger, handle_scope_resolution_error
from .guard_stack_manager import create_guard_stack_entry, pop_guard_with_context_cleanup
from .guard_tag_parser import parse_guard_tag
from .scope_resolver import resolve_semantic_scope_sync
from .types import (
    DEFAULT_PERMISSIONS,
    GuardStackEntry,
    GuardTag,
    ICoreConfiguration,
    IDocument,
    LinePermission,
)


class Logger:
    """Simple logger interface."""

    def __init__(self, debug: bool = False):
        self.debug_enabled = debug

    def log(self, message: str):
        if self.debug_enabled:
            print(f"[LOG] {message}")

    def warn(self, message: str):
        if self.debug_enabled:
            print(f"[WARN] {message}")

    def error(self, message: str):
        if self.debug_enabled:
            print(f"[ERROR] {message}")


class Document:
    """Document implementation for CLI"""

    def __init__(self, lines: List[str], languageId: str, lineCount: int, text: str):
        self.lines = lines
        self.languageId = languageId
        self.lineCount = lineCount
        self.text = text

    def getText(self) -> str:
        return self.text

    def lineAt(self, line: int) -> Dict[str, Any]:
        """Get line information (0-based for internal use)"""
        if 0 <= line < len(self.lines):
            text = self.lines[line]
            return {
                "text": text,
                "firstNonWhitespaceCharacterIndex": len(text) - len(text.lstrip()),
                "lineNumber": line,
            }
        return {"text": "", "firstNonWhitespaceCharacterIndex": 0, "lineNumber": line}


class CoreConfiguration:
    """Core configuration for processing."""

    def __init__(self, enableDebugLogging: bool = False):
        self.enableDebugLogging = enableDebugLogging

    def get(self, key: str, defaultValue: Any) -> Any:
        return getattr(self, key, defaultValue)


def get_default_scope(tag_info) -> Optional[str]:
    """
    Determine the default scope for a guard tag based on its properties.
    Exact port of VSCode function.
    """
    # If there's a line count, don't set a default scope
    if tag_info.lineCount:
        return None

    # Check if this is a context permission
    is_context_permission = (
        tag_info.aiIsContext
        or tag_info.humanIsContext
        or tag_info.aiPermission == "contextWrite"
        or tag_info.humanPermission == "contextWrite"
    )

    if is_context_permission:
        return "context"

    # Default to block scope for other permissions
    return "block"


def get_default_permissions() -> Dict[str, str]:
    """Get default permissions."""
    return DEFAULT_PERMISSIONS.copy()


def parse_guard_tags_core(
    document: IDocument,
    lines: List[str],
    config: ICoreConfiguration,
    extension_context: Any = None,
    logger: Logger = None,
) -> List[GuardTag]:
    """
    Basic guard tag parsing for a document.
    NOTE: This is simplified - full VSCode version uses semantic scope resolution
    """
    if logger is None:
        logger = Logger(config.get("enableDebugLogging", False))

    guard_tags = []
    total_lines = len(lines)

    # Parse each line for guard tags
    for i in range(total_lines):
        line_number = i + 1  # Convert to 1-based indexing
        line = lines[i]

        try:
            tag_info = parse_guard_tag(line)

            if tag_info:
                # Create guard tag with core processing
                guard_tag = GuardTag(
                    lineNumber=line_number,
                    identifier=tag_info.identifier,
                    scope=tag_info.scope or get_default_scope(tag_info),
                    lineCount=tag_info.lineCount,
                    addScopes=tag_info.addScopes,
                    removeScopes=tag_info.removeScopes,
                    aiPermission=tag_info.aiPermission,
                    humanPermission=tag_info.humanPermission,
                    aiIsContext=tag_info.aiIsContext,
                    humanIsContext=tag_info.humanIsContext,
                )

                # Set scope boundaries - simplified logic for now
                # TODO: Replace with semantic scope resolution
                if guard_tag.lineCount:
                    # Line count based scope
                    guard_tag.scopeStart = line_number
                    guard_tag.scopeEnd = min(line_number + guard_tag.lineCount - 1, total_lines)
                elif guard_tag.scope == "context":
                    # Context scope - find next non-comment lines
                    guard_tag.scopeStart = line_number + 1
                    end_line = line_number

                    for search_line in range(line_number, total_lines):
                        search_line_text = lines[search_line].strip()

                        # Stop at next guard tag
                        if "@guard:" in search_line_text:
                            if search_line > line_number:
                                break
                            continue

                        # Include comments in context using proper comment detection
                        from .comment_detector import is_line_a_comment

                        if is_line_a_comment(search_line_text, document.languageId):
                            end_line = search_line + 1
                        elif search_line_text == "":
                            # For blank lines, check what comes immediately after
                            next_non_empty_line_index = -1
                            for look_ahead in range(search_line + 1, total_lines):
                                next_line_text = lines[look_ahead].strip()
                                if next_line_text != "":
                                    next_non_empty_line_index = look_ahead
                                    break

                            if next_non_empty_line_index != -1:
                                next_non_empty_line = lines[next_non_empty_line_index].strip()
                                if "@guard:" in next_non_empty_line:
                                    # Next non-empty line is a guard tag, don't include this blank line
                                    break
                                else:
                                    # Include this blank line and continue processing
                                    end_line = search_line + 1
                            else:
                                # No more non-empty lines (EOF), don't include trailing blank line
                                # Don't update end_line, just continue to next iteration
                                pass
                        else:
                            # Stop at actual code (functions, classes, variable declarations, etc.)
                            break

                    guard_tag.scopeEnd = end_line
                elif guard_tag.scope == "block":
                    # Block scope - apply to next code block using tree-sitter logic like VSCode
                    start_line_number = line_number + 1  # Start from line after guard (1-based)
                    end_line_number = start_line_number

                    # Scan forward to find the end of the statement block using tree-sitter
                    for current_line in range(
                        start_line_number - 1, total_lines
                    ):  # Convert to 0-based for iteration
                        line_text = lines[current_line].strip()

                        # Stop at guard tags
                        if "@guard:" in line_text:
                            break

                        # Use tree-sitter to check if we hit a scope-breaking node type
                        try:
                            from .tree_sitter_parser import find_node_at_position, parse_document

                            parse_result = parse_document(document.text, document.languageId)
                            if parse_result.success and parse_result.root_node:
                                # Find node at this line (using VSCode's exact logic)
                                node = find_node_at_position(
                                    parse_result.root_node, current_line + 1, 0
                                )
                                if node and node.type in ["program", "module"]:
                                    # Hit program/module scope, stop here (exact VSCode logic from processor.ts:171-173)
                                    break
                        except Exception:
                            # If tree-sitter fails, continue with fallback logic
                            pass

                        # Include this line in the block
                        end_line_number = current_line + 1  # Convert to 1-based

                    guard_tag.scopeStart = start_line_number
                    guard_tag.scopeEnd = max(end_line_number, line_number)
                else:
                    # For other scopes (class, func, function, signature), use semantic scope resolution
                    if guard_tag.scope in ["class", "func", "function", "signature"]:
                        try:
                            # Use direct synchronous scope resolution to avoid async complexity
                            scope_boundary = resolve_semantic_scope_sync(
                                document,
                                line_number - 1,
                                guard_tag.scope,  # Convert to 0-based for tree-sitter
                            )

                            if scope_boundary:
                                guard_tag.scopeStart = scope_boundary.startLine
                                guard_tag.scopeEnd = scope_boundary.endLine
                            else:
                                # Fallback to single line if semantic resolution fails
                                guard_tag.scopeStart = line_number
                                guard_tag.scopeEnd = line_number

                        except Exception as e:
                            handle_scope_resolution_error(
                                f"Error in semantic scope resolution for {guard_tag.scope} at line {line_number}",
                                scope_type=guard_tag.scope,
                                line_number=line_number,
                                cause=e,
                            )
                            # Fallback to single line if semantic resolution fails
                            guard_tag.scopeStart = line_number
                            guard_tag.scopeEnd = line_number
                    else:
                        # For unrecognized scopes, fallback to single line
                        guard_tag.scopeStart = line_number
                        guard_tag.scopeEnd = line_number

                guard_tags.append(guard_tag)

        except Exception as e:
            if logger:
                logger.error(f"Error parsing guard tag at line {line_number}: {e}")

    return guard_tags


def get_line_permissions_core(
    document: IDocument,
    guard_tags: List[GuardTag],
    config: ICoreConfiguration,
    logger: Logger = None,
) -> Dict[int, LinePermission]:
    """
    Get line permissions for a document - EXACT PORT of VSCode guard stack logic
    """
    if logger is None:
        logger = Logger(config.get("enableDebugLogging", False))

    line_permissions: Dict[int, LinePermission] = {}
    guard_stack: List[GuardStackEntry] = []
    total_lines = document.lineCount

    # Initialize with default permissions
    default_perms = get_default_permissions()

    # Process each line
    for line_number in range(1, total_lines + 1):
        # Check if any guards end at this line
        while guard_stack and guard_stack[-1].endLine < line_number:
            pop_guard_with_context_cleanup(guard_stack)

        # Check if any guards start at this line
        guards_at_line = [tag for tag in guard_tags if tag.lineNumber == line_number]

        for guard in guards_at_line:
            if guard.scopeStart is not None and guard.scopeEnd is not None:
                # Create permissions object
                permissions: Dict[str, str] = {}
                is_context: Dict[str, bool] = {}

                # Set AI permissions
                if guard.aiPermission:
                    permissions["ai"] = guard.aiPermission
                    is_context["ai"] = guard.aiPermission == "contextWrite" or bool(
                        guard.aiIsContext
                    )
                elif guard.aiIsContext:
                    # Handle context-only guards like @guard:ai:context (no explicit permission)
                    # Default to read permission with context flag
                    permissions["ai"] = "r"
                    is_context["ai"] = True

                # Set human permissions
                if guard.humanPermission:
                    permissions["human"] = guard.humanPermission
                    is_context["human"] = guard.humanPermission == "contextWrite" or bool(
                        guard.humanIsContext
                    )
                elif guard.humanIsContext:
                    # Handle context-only guards like @guard:human:context (no explicit permission)
                    # Default to read permission with context flag
                    permissions["human"] = "r"
                    is_context["human"] = True

                # Push to stack
                stack_entry = create_guard_stack_entry(
                    permissions,
                    is_context,
                    guard.scopeStart,
                    guard.scopeEnd,
                    bool(guard.lineCount),
                    guard,
                )

                guard_stack.append(stack_entry)

        # Determine current permissions (top of stack or default)
        current_permissions = default_perms.copy()
        current_is_context: Dict[str, bool] = {}

        if guard_stack:
            top_stack = guard_stack[-1]
            current_permissions.update(top_stack.permissions)
            current_is_context = top_stack.isContext.copy()

        # Set line permissions
        line_permissions[line_number] = LinePermission(
            line=line_number, permissions=current_permissions, isContext=current_is_context
        )

    return line_permissions


def process_document(
    content: str,
    language_id: str,
    config: CoreConfiguration = None,
    extension_context: Any = None,
    logger: Logger = None,
) -> Tuple[List[GuardTag], Dict[int, LinePermission]]:
    """
    Process a complete document and return guard tags and line permissions.
    """
    if config is None:
        config = CoreConfiguration()

    if logger is None:
        logger = Logger(config.get("enableDebugLogging", False))

    lines = content.split("\n")
    document = Document(lines=lines, languageId=language_id, lineCount=len(lines), text=content)

    # Parse guard tags
    guard_tags = parse_guard_tags_core(document, lines, config, extension_context, logger)

    # Get line permissions using guard stack system
    line_permissions = get_line_permissions_core(document, guard_tags, config, logger)

    return guard_tags, line_permissions


def detect_language(file_path: str) -> str:
    """
    Detect programming language from file extension.
    """
    import os

    ext = os.path.splitext(file_path)[1].lower()

    lang_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescriptreact",
        ".jsx": "javascriptreact",
        ".cs": "csharp",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".go": "go",
        ".rb": "ruby",
        ".php": "php",
        ".rs": "rust",
        ".swift": "swift",
        ".kt": "kotlin",
        ".md": "markdown",
    }

    return lang_map.get(ext, "plaintext")


def clean_node_type_for_display(node_type: str) -> str:
    """
    Clean up node type names for display.
    Port of the VSCode plugin's node type cleaning logic.
    """
    # Clean up node type names for display
    if node_type.endswith("_declaration"):
        node_type = node_type.replace("_declaration", "")
    if node_type.endswith("_definition"):
        node_type = node_type.replace("_definition", "")
    if node_type.endswith("_expression"):
        node_type = node_type.replace("_expression", "")
    if node_type.endswith("_operator"):
        node_type = node_type.replace("_operator", "")
    if node_type.endswith("_statement"):
        node_type = node_type.replace("_statement", "")
    if node_type == "statement_block":
        node_type = "statement"
    if node_type == "class_body":
        node_type = "body"
    if node_type.startswith("import_"):
        node_type = "import"

    return node_type


def get_node_type_for_line_display(content: str, language_id: str, line_number: int) -> str:
    """
    Get the semantic node type for a specific line for display purposes only.
    """
    from .tree_sitter_parser import get_node_type_for_line, is_tree_sitter_available

    if not is_tree_sitter_available():
        return "unknown"

    try:
        node_type = get_node_type_for_line(content, language_id, line_number)
        return clean_node_type_for_display(node_type)
    except Exception:
        return "error"
