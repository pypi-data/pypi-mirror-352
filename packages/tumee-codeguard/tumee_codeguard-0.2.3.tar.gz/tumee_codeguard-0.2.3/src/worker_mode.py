#!/usr/bin/env python3
"""
Worker Mode implementation for CodeGuard CLI.
Provides persistent, high-performance parser service via JSON over stdin/stdout.
"""

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .core.exit_codes import SUCCESS
from .core.processor import process_document
from .version import __version__


@dataclass
class TextChange:
    """Represents a text change for delta updates"""

    startLine: int
    startChar: int
    endLine: int
    endChar: int
    newText: str


@dataclass
class WorkerDocument:
    """Document state maintained by worker"""

    fileName: str
    languageId: str
    content: str
    version: int
    lines: List[str]
    guardTags: List[Dict[str, Any]]
    linePermissions: List[Dict[str, Any]]


class WorkerModeProcessor:
    """Main processor for worker mode operations"""

    def __init__(self, min_version: Optional[str] = None):
        self.min_version = min_version
        self.document: Optional[WorkerDocument] = None
        self.startup_time = time.time()

    def is_compatible_version(self, required_version: str) -> bool:
        """Check if current version is compatible with required version"""
        try:

            def version_tuple(v):
                return tuple(map(int, v.split(".")))

            return version_tuple(__version__) >= version_tuple(required_version)
        except Exception:
            return False

    def send_startup_message(self):
        """Send startup handshake message"""
        message = {
            "type": "startup",
            "version": __version__,
            "capabilities": ["delta-updates", "tree-sitter", "scope-resolution"],
            "ready": True,
        }
        self._send_response(message)

    def _send_response(self, response: Dict[str, Any]):
        """Send JSON response to stdout with double newline termination"""
        json_str = json.dumps(response, separators=(",", ":"))
        print(json_str + "\n", flush=True)

    def _send_error_response(
        self, request_id: str, error_msg: str, error_code: str = "INTERNAL_ERROR"
    ):
        """Send error response"""
        response = {"id": request_id, "status": "error", "error": error_msg, "code": error_code}
        self._send_response(response)

    def _send_success_response(
        self, request_id: str, result: Dict[str, Any], timing: Optional[float] = None
    ):
        """Send success response"""
        response = {"id": request_id, "status": "success", "result": result}
        if timing is not None:
            response["timing"] = round(timing, 2)
        self._send_response(response)

    def _lines_from_content(self, content: str) -> List[str]:
        """Split content into lines, preserving line endings"""
        if not content:
            return []
        return content.splitlines(keepends=False)

    def _apply_text_changes(self, content: str, changes: List[TextChange]) -> str:
        """Apply text changes to content"""
        lines = content.splitlines(keepends=True)

        # Sort changes by position (start from end to avoid offset issues)
        sorted_changes = sorted(changes, key=lambda c: (c.startLine, c.startChar), reverse=True)

        for change in sorted_changes:
            # Convert to 0-based indexing
            start_line = change.startLine
            end_line = change.endLine
            start_char = change.startChar
            end_char = change.endChar

            if start_line >= len(lines):
                continue

            if start_line == end_line:
                # Single line change
                line = lines[start_line].rstrip("\n\r")
                new_line = line[:start_char] + change.newText + line[end_char:]
                lines[start_line] = (
                    new_line + "\n" if lines[start_line].endswith("\n") else new_line
                )
            else:
                # Multi-line change
                start_line_content = lines[start_line][:start_char]
                end_line_content = lines[end_line][end_char:] if end_line < len(lines) else ""

                # Replace the range with new content
                new_content = start_line_content + change.newText + end_line_content
                new_lines = new_content.splitlines(keepends=True)

                # Replace the lines
                lines[start_line : end_line + 1] = new_lines

        return "".join(lines)

    def _process_document_content(
        self, content: str, language_id: str
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Process document content and return guard tags and line permissions"""
        try:
            # Process the document
            guard_tags_list, line_permissions_dict = process_document(content, language_id)

            # Convert guard tags to serializable format
            guard_tags = []
            for tag in guard_tags_list:
                guard_dict = {
                    "lineNumber": getattr(tag, "lineNumber", 0),
                    "scope": getattr(tag, "scope", "line"),
                }

                # Add optional fields if present
                for field in [
                    "identifier",
                    "lineCount",
                    "addScopes",
                    "removeScopes",
                    "scopeStart",
                    "scopeEnd",
                    "aiPermission",
                    "humanPermission",
                    "aiIsContext",
                    "humanIsContext",
                ]:
                    if hasattr(tag, field):
                        value = getattr(tag, field)
                        if value is not None:
                            guard_dict[field] = value

                guard_tags.append(guard_dict)

            # Convert line permissions to serializable format
            line_permissions = []
            for line_num, perm in line_permissions_dict.items():
                line_perm = {
                    "line": line_num,
                    "permissions": getattr(perm, "permissions", {}),
                    "isContext": getattr(perm, "isContext", {}),
                }

                # Add optional fields
                for field in ["identifier", "isTrailingWhitespace"]:
                    if hasattr(perm, field):
                        value = getattr(perm, field)
                        if value is not None:
                            line_perm[field] = value

                line_permissions.append(line_perm)

            return guard_tags, line_permissions

        except Exception as e:
            raise Exception(f"Document processing failed: {str(e)}")

    def handle_version_command(self, request: Dict[str, Any]) -> None:
        """Handle version command"""
        request_id = request.get("id", "")

        compatible = True
        min_compatible = "1.2.0"

        if self.min_version:
            compatible = self.is_compatible_version(self.min_version)
            min_compatible = self.min_version

        result = {"version": __version__, "minCompatible": min_compatible, "compatible": compatible}

        self._send_success_response(request_id, result)

    def handle_set_document_command(self, request: Dict[str, Any]) -> None:
        """Handle setDocument command"""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            start_time = time.time()

            fileName = payload.get("fileName", "")
            languageId = payload.get("languageId", "")
            content = payload.get("content", "")
            version = payload.get("version", 1)

            if not fileName or not languageId:
                self._send_error_response(
                    request_id, "fileName and languageId are required", "INVALID_REQUEST"
                )
                return

            # Process document
            guard_tags, line_permissions = self._process_document_content(content, languageId)

            # Update document state
            self.document = WorkerDocument(
                fileName=fileName,
                languageId=languageId,
                content=content,
                version=version,
                lines=self._lines_from_content(content),
                guardTags=guard_tags,
                linePermissions=line_permissions,
            )

            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            result = {
                "guardTags": guard_tags,
                "linePermissions": line_permissions,
                "documentVersion": version,
            }

            self._send_success_response(request_id, result, processing_time)

        except Exception as e:
            self._send_error_response(request_id, str(e), "PARSE_ERROR")

    def handle_apply_delta_command(self, request: Dict[str, Any]) -> None:
        """Handle applyDelta command"""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            if not self.document:
                self._send_error_response(
                    request_id, "No document loaded. Use setDocument first.", "NO_DOCUMENT"
                )
                return

            start_time = time.time()

            version = payload.get("version", 0)
            changes_data = payload.get("changes", [])

            # Convert changes to TextChange objects
            changes = []
            for change_data in changes_data:
                changes.append(
                    TextChange(
                        startLine=change_data.get("startLine", 0),
                        startChar=change_data.get("startChar", 0),
                        endLine=change_data.get("endLine", 0),
                        endChar=change_data.get("endChar", 0),
                        newText=change_data.get("newText", ""),
                    )
                )

            # Apply changes
            new_content = self._apply_text_changes(self.document.content, changes)

            # Process updated document
            guard_tags, line_permissions = self._process_document_content(
                new_content, self.document.languageId
            )

            # Update document state
            self.document.content = new_content
            self.document.version = version
            self.document.lines = self._lines_from_content(new_content)
            self.document.guardTags = guard_tags
            self.document.linePermissions = line_permissions

            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            result = {
                "guardTags": guard_tags,
                "linePermissions": line_permissions,
                "documentVersion": version,
            }

            self._send_success_response(request_id, result, processing_time)

        except Exception as e:
            self._send_error_response(request_id, str(e), "INVALID_DELTA")

    def handle_ping_command(self, request: Dict[str, Any]) -> None:
        """Handle ping command"""
        request_id = request.get("id", "")

        uptime = int((time.time() - self.startup_time) * 1000)  # Convert to milliseconds

        result = {"pong": True, "uptime": uptime}

        self._send_success_response(request_id, result)

    def handle_shutdown_command(self, request: Dict[str, Any]) -> None:
        """Handle shutdown command"""
        request_id = request.get("id", "")

        result = {"message": "Shutting down gracefully"}

        self._send_success_response(request_id, result)

        # Exit gracefully
        sys.exit(SUCCESS)

    def handle_request(self, request: Dict[str, Any]) -> None:
        """Handle incoming request"""
        request_id = request.get("id", "")
        command = request.get("command", "")

        if command == "version":
            self.handle_version_command(request)
        elif command == "setDocument":
            self.handle_set_document_command(request)
        elif command == "applyDelta":
            self.handle_apply_delta_command(request)
        elif command == "ping":
            self.handle_ping_command(request)
        elif command == "shutdown":
            self.handle_shutdown_command(request)
        else:
            self._send_error_response(request_id, f"Unknown command: {command}", "UNKNOWN_COMMAND")

    def run(self):
        """Main worker mode loop"""
        # Send startup message
        self.send_startup_message()

        # Process stdin line by line
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                self.handle_request(request)
            except json.JSONDecodeError as e:
                # Send error for malformed JSON
                error_response = {
                    "id": "unknown",
                    "status": "error",
                    "error": f"Invalid JSON: {str(e)}",
                    "code": "INVALID_JSON",
                }
                self._send_response(error_response)
            except Exception as e:
                # Send error for other exceptions
                error_response = {
                    "id": "unknown",
                    "status": "error",
                    "error": f"Internal error: {str(e)}",
                    "code": "INTERNAL_ERROR",
                }
                self._send_response(error_response)


def start_worker_mode(min_version: Optional[str] = None):
    """Start worker mode with optional minimum version requirement"""
    processor = WorkerModeProcessor(min_version)
    processor.run()
