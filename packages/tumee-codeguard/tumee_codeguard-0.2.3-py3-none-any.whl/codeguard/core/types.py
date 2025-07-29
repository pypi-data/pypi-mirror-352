"""
Core types for the parsing module - platform agnostic
Exact port of VSCode src/core/types.ts
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Protocol, Union


class IDocument(Protocol):
    """Generic document interface that can be implemented by any platform"""

    text: str
    languageId: str
    lineCount: int

    def getText(self) -> str:
        ...

    def lineAt(self, line: int) -> "ITextLine":
        ...


class ITextLine(Protocol):
    """Generic text line interface"""

    lineNumber: int
    text: str


@dataclass
class ScopeBoundary:
    """Represents a scope boundary in the document"""

    startLine: int
    endLine: int
    type: str


class IExtensionContext(Protocol):
    """Generic extension context interface for resource loading"""

    extensionPath: str

    def asAbsolutePath(self, relativePath: str) -> str:
        ...


@dataclass
class IParsingConfig:
    """Configuration interface for parsing behavior"""

    enablePerformanceMonitoring: Optional[bool] = None
    maxFileSize: Optional[int] = None
    chunkSize: Optional[int] = None


@dataclass
class ParseResult:
    """Result of parsing a document with tree-sitter"""

    tree: Any  # Tree type from tree-sitter
    languageId: str
    success: bool
    error: Optional[str] = None


@dataclass
class NodePosition:
    """Node position information"""

    row: int
    column: int


@dataclass
class NodeBoundaries:
    """Node boundaries information"""

    startLine: int
    endLine: int
    startColumn: int
    endColumn: int


# Default permissions for AI and human targets
# These are used when no guard tags are present
DEFAULT_PERMISSIONS = {
    "ai": "r",  # AI has read-only access by default
    "human": "w",  # Human has write access by default
}

# Type for permission values
PermissionValue = Literal["r", "w", "n"]

# Type for permission targets
PermissionTarget = Literal["ai", "human"]


@dataclass
class GuardTag:
    """Guard tag information"""

    lineNumber: int
    identifier: Optional[str] = None
    scope: Optional[str] = None
    lineCount: Optional[int] = None
    addScopes: Optional[List[str]] = None
    removeScopes: Optional[List[str]] = None
    scopeStart: Optional[int] = None
    scopeEnd: Optional[int] = None
    # Store the actual permissions for each target
    aiPermission: Optional[Literal["r", "w", "n", "contextWrite"]] = None
    humanPermission: Optional[Literal["r", "w", "n", "contextWrite"]] = None
    # Track if permissions are context-based
    aiIsContext: Optional[bool] = None
    humanIsContext: Optional[bool] = None


@dataclass
class LinePermission:
    """Line permission information"""

    line: int
    permissions: Dict[str, str]  # e.g., { 'ai': 'w', 'human': 'r' }
    isContext: Dict[str, bool]  # e.g., { 'ai': True, 'human': False }
    identifier: Optional[str] = None
    isTrailingWhitespace: Optional[
        bool
    ] = None  # True if this is trailing whitespace at end of a guard scope


@dataclass
class GuardStackEntry:
    """Stack entry for guard processing - contains complete permission state"""

    permissions: Dict[str, str]  # e.g., { 'ai': 'w', 'human': 'r' }
    isContext: Dict[str, bool]  # e.g., { 'ai': True, 'human': False }
    startLine: int
    endLine: int
    isLineLimited: bool
    sourceGuard: Optional[GuardTag] = None  # The guard that triggered this state change


class ICoreConfiguration(Protocol):
    """Core configuration interface"""

    def get(self, key: str, defaultValue: Any) -> Any:
        ...
