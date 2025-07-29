"""
Python-style error handling with logging
Verbose error handling using Python best practices
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class CodeGuardException(Exception):
    """Base exception for CodeGuard-specific errors"""

    pass


class TreeSitterError(CodeGuardException):
    """Tree-sitter parsing errors"""

    pass


class ScopeResolutionError(CodeGuardException):
    """Scope resolution errors"""

    pass


class GuardParsingError(CodeGuardException):
    """Guard tag parsing errors"""

    pass


class ValidationError(CodeGuardException):
    """Validation errors"""

    pass


def setup_logging(level: int = logging.WARNING, format_str: Optional[str] = None) -> logging.Logger:
    """
    Setup logging for CodeGuard with Python best practices

    Args:
        level: Logging level (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Custom format string

    Returns:
        Configured logger instance
    """
    if format_str is None:
        format_str = "[%(levelname)s] %(name)s: %(message)s"

    logger = logging.getLogger("codeguard")

    # Don't add handlers if they already exist
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(format_str)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger


def get_logger(name: str = "codeguard") -> logging.Logger:
    """Get a logger instance for CodeGuard modules"""
    return logging.getLogger(name)


# Configure default logger (only warnings and errors in normal use)
_default_logger = setup_logging(logging.WARNING)


def handle_tree_sitter_error(
    message: str,
    language_id: Optional[str] = None,
    cause: Optional[Exception] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    """Handle tree-sitter related errors with detailed logging"""
    if logger is None:
        logger = _default_logger

    context_msg = f" (language: {language_id})" if language_id else ""
    full_message = f"Tree-sitter parsing failed: {message}{context_msg}"

    if cause:
        logger.warning(f"{full_message} - Caused by: {cause}")
    else:
        logger.warning(full_message)


def handle_scope_resolution_error(
    message: str,
    scope_type: Optional[str] = None,
    line_number: Optional[int] = None,
    file_path: Optional[str] = None,
    cause: Optional[Exception] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    """Handle scope resolution errors with detailed context"""
    if logger is None:
        logger = _default_logger

    context_parts = []
    if scope_type:
        context_parts.append(f"scope: {scope_type}")
    if line_number:
        context_parts.append(f"line: {line_number}")
    if file_path:
        context_parts.append(f"file: {file_path}")

    context_msg = f" ({', '.join(context_parts)})" if context_parts else ""
    full_message = f"Scope resolution failed: {message}{context_msg}"

    if cause:
        logger.warning(f"{full_message} - Caused by: {cause}")
    else:
        logger.warning(full_message)


def handle_guard_parsing_error(
    message: str,
    guard_tag: Optional[str] = None,
    line_number: Optional[int] = None,
    file_path: Optional[str] = None,
    cause: Optional[Exception] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    """Handle guard tag parsing errors"""
    if logger is None:
        logger = _default_logger

    context_parts = []
    if guard_tag:
        context_parts.append(f"guard: {guard_tag}")
    if line_number:
        context_parts.append(f"line: {line_number}")
    if file_path:
        context_parts.append(f"file: {file_path}")

    context_msg = f" ({', '.join(context_parts)})" if context_parts else ""
    full_message = f"Guard parsing error: {message}{context_msg}"

    if cause:
        logger.error(f"{full_message} - Caused by: {cause}")
    else:
        logger.error(full_message)


def handle_validation_error(
    message: str,
    file_path: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None,
    cause: Optional[Exception] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    """Handle validation errors"""
    if logger is None:
        logger = _default_logger

    context_parts = []
    if file_path:
        context_parts.append(f"file: {file_path}")
    if additional_data:
        for key, value in additional_data.items():
            context_parts.append(f"{key}: {value}")

    context_msg = f" ({', '.join(context_parts)})" if context_parts else ""
    full_message = f"Validation error: {message}{context_msg}"

    if cause:
        logger.error(f"{full_message} - Caused by: {cause}")
    else:
        logger.error(full_message)


def log_debug(message: str, logger: Optional[logging.Logger] = None, **kwargs):
    """Log debug information (only shown when debug level is enabled)"""
    if logger is None:
        logger = _default_logger

    if kwargs:
        context = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        message = f"{message} ({context})"

    logger.debug(message)


def log_info(message: str, logger: Optional[logging.Logger] = None, **kwargs):
    """Log informational message"""
    if logger is None:
        logger = _default_logger

    if kwargs:
        context = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        message = f"{message} ({context})"

    logger.info(message)


def set_log_level(level: int):
    """Set the global logging level"""
    _default_logger.setLevel(level)
