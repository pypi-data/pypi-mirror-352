"""
Core guard stack operations and permission inheritance - platform agnostic
Exact port of VSCode src/core/guardStackManager.ts
Handles stack manipulation, context guard cleanup, and permission state management
No dependencies allowed in this module
"""

from typing import Dict, List, Optional

from .types import GuardStackEntry, GuardTag


def pop_guard_with_context_cleanup(guard_stack: List[GuardStackEntry]) -> None:
    """
    Pop expired guards from stack and clean up any context guards below
    Context guards cannot resume after being interrupted
    """
    guard_stack.pop()

    # After popping, also pop any context guards below
    # Context guards cannot resume after being interrupted
    while guard_stack:
        next_entry = guard_stack[-1]
        # Check if any permission in this entry is 'context'
        has_context_permission = "context" in next_entry.permissions.values()
        if has_context_permission:
            guard_stack.pop()
        else:
            break


def remove_interrupted_context_guards(guard_stack: List[GuardStackEntry]) -> None:
    """
    Remove any context guards from the top of the stack
    Context guards cannot be interrupted and resumed later
    """
    while guard_stack:
        top = guard_stack[-1]
        # Check if any permission in this entry is 'context'
        has_context_permission = "context" in top.permissions.values()
        if has_context_permission:
            guard_stack.pop()
        else:
            break


def create_guard_stack_entry(
    permissions: Dict[str, str],
    is_context: Dict[str, bool],
    start_line: int,
    end_line: int,
    is_line_limited: bool,
    source_guard: Optional[GuardTag] = None,
) -> GuardStackEntry:
    """
    Create a new guard stack entry
    """
    return GuardStackEntry(
        permissions=permissions,
        isContext=is_context,
        startLine=start_line,
        endLine=end_line,
        isLineLimited=is_line_limited,
        sourceGuard=source_guard,
    )
