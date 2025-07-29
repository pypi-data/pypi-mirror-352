"""
CLI Display Engine for CodeGuard CLI.
Complete port of the VSCode plugin's cli/displayEngine.ts functionality.
Produces exactly the same output as the VSCode plugin.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .core.processor import (
    CoreConfiguration,
    Document,
    Logger,
    detect_language,
    get_node_type_for_line_display,
    process_document,
)
from .themes import (
    CLI_BORDER_CHAR,
    CLI_MIXED_BORDER_CHAR,
    AnsiColors,
    PermissionConfig,
    hex_to_ansi,
    load_theme_for_cli,
)


def detect_mixed_permissions(guard_tags: List[Any]) -> Set[int]:
    """
    Check for overlapping guards (mixed permissions).
    Port of the VSCode plugin's mixed permission detection logic.
    """
    mixed_lines = set()

    for i in range(len(guard_tags)):
        for j in range(i + 1, len(guard_tags)):
            g1 = guard_tags[i]
            g2 = guard_tags[j]

            # Check if guards overlap (basic check)
            if (
                g1.scopeStart is not None
                and g1.scopeEnd is not None
                and g2.scopeStart is not None
                and g2.scopeEnd is not None
                and g1.scopeStart <= g2.scopeEnd
                and g2.scopeStart <= g1.scopeEnd
            ):
                # Mark all overlapping lines as mixed
                overlap_start = max(g1.scopeStart, g2.scopeStart)
                overlap_end = min(g1.scopeEnd, g2.scopeEnd)
                for line in range(overlap_start, overlap_end + 1):
                    mixed_lines.add(line)  # Already 1-based

    return mixed_lines


def determine_line_colors(
    ai_perm: str,
    human_perm: str,
    is_context: bool,
    is_mixed: bool,
    theme: Dict[str, Any],
    perm: Any,
) -> Dict[str, Any]:
    """
    Determine colors for a line based on permissions and theme.
    Port of the VSCode plugin's color determination logic.
    """
    result: Dict[str, Any] = {
        "bgColor": "",
        "borderColor": "",
        "textColor": AnsiColors.black,
        "borderChar": CLI_MIXED_BORDER_CHAR if is_mixed else CLI_BORDER_CHAR,
        "highlightEntireLine": False,
    }

    ai_color = ""
    human_color = ""
    ai_config = None
    human_config = None

    if is_context:
        # Determine if this is read or write context based on the permission that has context
        is_write_context = (perm and perm.isContext.get("ai", False) and ai_perm == "w") or (
            perm and perm.isContext.get("human", False) and human_perm == "w"
        )
        context_color = theme["colors"].get("contextWrite" if is_write_context else "contextRead")
        if context_color and context_color != AnsiColors.dim:
            ai_color = human_color = context_color
            context_config = theme["permissions"].get(
                "contextWrite" if is_write_context else "contextRead"
            )
            result["highlightEntireLine"] = (
                context_config.highlightEntireLine if context_config else False
            )
    else:
        # AI color
        ai_key = "aiWrite" if ai_perm == "w" else "aiRead" if ai_perm == "r" else "aiNoAccess"
        ai_config = theme["permissions"].get(ai_key)
        if ai_config and ai_config.enabled and ai_config.transparency > 0:
            ai_color = theme["colors"].get(ai_key)

        # Human color
        human_key = (
            "humanWrite"
            if human_perm == "w"
            else "humanRead"
            if human_perm == "r"
            else "humanNoAccess"
        )
        human_config = theme["permissions"].get(human_key)
        if human_config and human_config.enabled and human_config.transparency > 0:
            human_color = theme["colors"].get(human_key)

    # Apply mix pattern if both colors present
    if ai_color and human_color and ai_color != AnsiColors.dim and human_color != AnsiColors.dim:
        # Both colors enabled - use mix pattern
        mix_pattern = theme.get("mixPattern", "humanBorder")

        if mix_pattern == "aiBorder":
            result["bgColor"] = human_color
            result["borderColor"] = ai_color
            # For border bar, use border opacity if available
            if ai_config and ai_config.borderOpacity != ai_config.transparency:
                result["borderColor"] = hex_to_ansi(ai_config.color, ai_config.borderOpacity)
        elif mix_pattern == "humanBorder":
            result["bgColor"] = ai_color
            result["borderColor"] = human_color
            # For border bar, use border opacity if available
            if human_config and human_config.borderOpacity != human_config.transparency:
                result["borderColor"] = hex_to_ansi(human_config.color, human_config.borderOpacity)
        elif mix_pattern == "aiPriority":
            result["bgColor"] = result["borderColor"] = ai_color
        elif mix_pattern == "humanPriority":
            result["bgColor"] = result["borderColor"] = human_color
        elif mix_pattern == "average":
            # For average, both get the same blended color (we can't blend ANSI easily)
            # So we'll just use AI color for simplicity
            result["bgColor"] = result["borderColor"] = ai_color
        else:
            result["bgColor"] = ai_color
            result["borderColor"] = human_color

        # Determine highlightEntireLine for mixed permissions
        if not is_context:
            result["highlightEntireLine"] = (ai_config and ai_config.highlightEntireLine) or (
                human_config and human_config.highlightEntireLine
            )
    else:
        result["bgColor"] = ai_color or human_color
        result["borderColor"] = result["bgColor"]
        # For single color, use its highlightEntireLine setting
        if not is_context:
            if ai_color and ai_config:
                result["highlightEntireLine"] = ai_config.highlightEntireLine
            elif human_color and human_config:
                result["highlightEntireLine"] = human_config.highlightEntireLine

    # Set text color based on background
    if result["bgColor"] and (
        "41" in str(result["bgColor"])
        or "44" in str(result["bgColor"])
        or "45" in str(result["bgColor"])
    ):
        result["textColor"] = AnsiColors.white

    return result


def display_file(
    file_path: str,
    color: bool = False,
    theme: str = None,
    debug: bool = False,
    tree_sitter_debug: bool = False,
) -> None:
    """
    Main display function - exact port of the VSCode plugin's displayFile function.
    """
    # Read file content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    language_id = detect_language(file_path)
    lines = content.split("\n")

    # Configure logging
    logger = Logger(debug)
    config = CoreConfiguration(enableDebugLogging=debug)

    # Process document
    guard_tags, line_permissions = process_document(content, language_id, config, None, logger)

    # Load theme if using colors
    theme_data = None
    if color:
        if debug:
            logger.log(f"Loading theme: {theme or 'default'}")

        try:
            theme_data = load_theme_for_cli(theme, fail_on_missing=True)
            if debug:
                logger.log(f"Theme loaded: {'SUCCESS' if theme_data else 'FAILED'}")
                if theme_data:
                    logger.log(f"Theme colors: {list(theme_data.get('colors', {}).keys())}")
                    logger.log(f"Mix pattern: {theme_data.get('mixPattern')}")
        except (RuntimeError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            from .core.exit_codes import THEME_LOAD_FAILED

            sys.exit(THEME_LOAD_FAILED)

    # Detect mixed permissions
    mixed_lines = detect_mixed_permissions(guard_tags)

    # Calculate max line length for padding
    max_line_length = max(80, max(len(line) for line in lines) if lines else 0)

    # Display each line
    for i, line in enumerate(lines):
        line_num = i + 1
        perm = line_permissions.get(line_num)

        ai_perm = "r"
        human_perm = "w"
        is_context = False

        if perm:
            # Normalize contextWrite back to 'w' for display
            ai_perm = (
                "w"
                if perm.permissions.get("ai") == "contextWrite"
                else perm.permissions.get("ai") or "r"
            )
            human_perm = (
                "w"
                if perm.permissions.get("human") == "contextWrite"
                else perm.permissions.get("human") or "w"
            )
            is_context = perm.isContext.get("ai", False) or perm.isContext.get("human", False)

        # Format permission block
        context_marker = "*" if is_context else " "
        perm_block = f"[AI:{ai_perm} HU:{human_perm} {context_marker}]"

        # Add tree-sitter debug info if requested
        if tree_sitter_debug:
            node_type = get_node_type_for_line_display(content, language_id, line_num)
            # Clean format: {nodeType}[AI:x HU:y  ] with 12 char width for nodeType
            truncated_node_type = node_type[:12].ljust(12)
            perm_block = f"{{{truncated_node_type}}}[AI:{ai_perm} HU:{human_perm} {context_marker}]"

        line_num_str = f"{line_num:5d}"

        # Determine if this line should be padded based on its permissions
        # This must be calculated outside the color block to work for all lines
        highlight_entire_line = False
        if perm and theme_data:
            # Check permission configs to determine highlightEntireLine setting
            ai_key = "aiWrite" if ai_perm == "w" else "aiRead" if ai_perm == "r" else "aiNoAccess"
            human_key = (
                "humanWrite"
                if human_perm == "w"
                else "humanRead"
                if human_perm == "r"
                else "humanNoAccess"
            )

            ai_config = theme_data.get("permissions", {}).get(ai_key)
            human_config = theme_data.get("permissions", {}).get(human_key)

            if is_context:
                # For context lines, check context permission configs
                is_write_context = (perm.isContext.get("ai", False) and ai_perm == "w") or (
                    perm.isContext.get("human", False) and human_perm == "w"
                )
                context_key = "contextWrite" if is_write_context else "contextRead"
                context_config = theme_data.get("permissions", {}).get(context_key)
                highlight_entire_line = (
                    context_config.highlightEntireLine if context_config else False
                )
            else:
                # For non-context lines, use individual permission configs
                highlight_entire_line = (ai_config and ai_config.highlightEntireLine) or (
                    human_config and human_config.highlightEntireLine
                )

        # Apply line padding based on highlightEntireLine setting
        line_content = line.ljust(max_line_length) if highlight_entire_line else line

        if color and theme_data:
            # Check if this line has mixed permissions
            is_mixed = line_num in mixed_lines

            # Determine colors based on permissions
            color_info = determine_line_colors(
                ai_perm, human_perm, is_context, is_mixed, theme_data, perm
            )

            bg_color = color_info["bgColor"]
            border_color = color_info["borderColor"]
            text_color = color_info["textColor"]
            border_char = color_info["borderChar"]

            # Apply colors
            if bg_color and bg_color != AnsiColors.dim:
                # Format: line# [perms]|content (where | is the colored border char)
                if border_color and bg_color and border_color != bg_color:
                    # Different colors for border and background
                    print(
                        f"{line_num_str} {perm_block}{border_color}{border_char}{AnsiColors.reset}{bg_color}{text_color}{line_content}{AnsiColors.reset}"
                    )
                elif bg_color:
                    # Same color for both or no border color
                    print(
                        f"{line_num_str} {perm_block}{bg_color}{text_color}{border_char}{line_content}{AnsiColors.reset}"
                    )
                elif border_color:
                    # Only border color
                    print(
                        f"{line_num_str} {perm_block}{border_color}{border_char}{AnsiColors.reset} {line_content}"
                    )
                else:
                    # Fallback - no colors
                    print(f"{line_num_str} {perm_block} {line_content}")
            else:
                # Default state - no colors (including aiRead_humanWrite default state)
                print(f"{line_num_str} {perm_block} {line_content}")
        else:
            # No color mode
            print(f"{line_num_str} {perm_block} {line_content}")


def main():
    """
    Main entry point for CLI usage.
    """
    import argparse

    parser = argparse.ArgumentParser(description="CodeGuard CLI Display Engine")
    parser.add_argument("file", help="File to display")
    parser.add_argument("-c", "--color", action="store_true", help="Enable colored output")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("-t", "--theme", help="Theme name")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument(
        "--tree-sitter-debug", action="store_true", help="Show tree-sitter node types"
    )
    parser.add_argument("--list-themes", action="store_true", help="List available themes")

    args = parser.parse_args()

    if args.list_themes:
        from .themes import list_available_themes

        themes = list_available_themes()
        print("Available Themes:")
        print("=================")
        if themes:
            for theme_name in sorted(themes):
                print(f"  {theme_name}")
        else:
            print("  No themes found")
        return

    if not args.file:
        parser.print_help()
        return

    color_enabled = args.color and not args.no_color

    try:
        display_file(
            args.file,
            color=color_enabled,
            theme=args.theme,
            debug=args.debug,
            tree_sitter_debug=args.tree_sitter_debug,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
