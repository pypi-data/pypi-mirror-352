"""
Theme system for CodeGuard CLI.
Complete port of the VSCode plugin's theme loading and transformation functionality.
All themes are loaded dynamically from JSON files - no hardcoded themes.
"""

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PermissionConfig:
    """Configuration for a single permission type."""

    color: str
    transparency: float
    borderOpacity: float
    minimapColor: str
    enabled: bool
    highlightEntireLine: bool


@dataclass
class ThemeColors:
    """Color configuration for all permissions."""

    permissions: Dict[str, PermissionConfig]
    borderBarEnabled: bool
    mixPattern: str


@dataclass
class ThemeConfig:
    """Complete theme configuration structure."""

    name: str
    colors: ThemeColors


class AnsiColors:
    """ANSI color constants matching VSCode plugin."""

    reset = "\x1b[0m"
    black = "\x1b[30m"
    white = "\x1b[37m"
    dim = "\x1b[2m"

    bg = {
        "black": "\x1b[40m",
        "red": "\x1b[41m",
        "green": "\x1b[42m",
        "yellow": "\x1b[43m",
        "blue": "\x1b[44m",
        "magenta": "\x1b[45m",
        "cyan": "\x1b[46m",
        "white": "\x1b[47m",
        "blackBright": "\x1b[100m",
        "redBright": "\x1b[101m",
        "greenBright": "\x1b[102m",
        "yellowBright": "\x1b[103m",
        "blueBright": "\x1b[104m",
        "magentaBright": "\x1b[105m",
        "cyanBright": "\x1b[106m",
        "whiteBright": "\x1b[107m",
    }


# CLI Display Constants
CLI_BORDER_CHAR = "▒"  # Unicode block character U+2592
CLI_MIXED_BORDER_CHAR = "▒"  # Lighter block character for mixed permissions


def hex_to_ansi(hex_color: str, transparency: float = 0.5) -> str:
    """
    Convert hex color to ANSI with transparency support.
    Exact port of the VSCode plugin's hexToAnsi function.
    """
    hex_value = hex_color.replace("#", "")
    if len(hex_value) != 6:
        return AnsiColors.dim

    try:
        r = int(hex_value[0:2], 16)
        g = int(hex_value[2:4], 16)
        b = int(hex_value[4:6], 16)
    except ValueError:
        return AnsiColors.dim

    # Map to nearest basic ANSI colors based on RGB values
    # Normal colors for low transparency (light tint), bright colors for high transparency (solid)
    ansi_colors: List[Dict[str, Any]] = [
        {
            "name": "black",
            "bg": AnsiColors.bg["black"],
            "bgBright": AnsiColors.bg["blackBright"],
            "rgb": [0, 0, 0],
        },
        {
            "name": "red",
            "bg": AnsiColors.bg["red"],
            "bgBright": AnsiColors.bg["redBright"],
            "rgb": [205, 49, 49],
        },
        {
            "name": "green",
            "bg": AnsiColors.bg["green"],
            "bgBright": AnsiColors.bg["greenBright"],
            "rgb": [13, 188, 121],
        },
        {
            "name": "yellow",
            "bg": AnsiColors.bg["yellow"],
            "bgBright": AnsiColors.bg["yellowBright"],
            "rgb": [229, 229, 16],
        },
        {
            "name": "blue",
            "bg": AnsiColors.bg["blue"],
            "bgBright": AnsiColors.bg["blueBright"],
            "rgb": [36, 114, 200],
        },
        {
            "name": "magenta",
            "bg": AnsiColors.bg["magenta"],
            "bgBright": AnsiColors.bg["magentaBright"],
            "rgb": [188, 63, 188],
        },
        {
            "name": "cyan",
            "bg": AnsiColors.bg["cyan"],
            "bgBright": AnsiColors.bg["cyanBright"],
            "rgb": [17, 168, 205],
        },
        {
            "name": "white",
            "bg": AnsiColors.bg["white"],
            "bgBright": AnsiColors.bg["whiteBright"],
            "rgb": [229, 229, 229],
        },
    ]

    # Find closest color using Euclidean distance
    min_distance = float("inf")
    closest_color = ansi_colors[0]

    for color in ansi_colors:
        distance = math.sqrt(
            (r - int(color["rgb"][0])) ** 2
            + (g - int(color["rgb"][1])) ** 2
            + (b - int(color["rgb"][2])) ** 2
        )
        if distance < min_distance:
            min_distance = distance
            closest_color = color

    # Use bright color for high transparency (>=50% opacity), normal for low (<50%)
    return closest_color["bgBright"] if transparency >= 0.5 else closest_color["bg"]


def map_theme_to_ansi(theme_colors: Dict[str, PermissionConfig]) -> Dict[str, str]:
    """
    Map theme colors to ANSI codes.
    Exact port of the VSCode plugin's mapThemeToAnsi function.
    """
    mapping = {}

    for key, config in theme_colors.items():
        if config.enabled and config.transparency > 0:
            # Pass transparency to get appropriate ANSI variant
            mapping[key] = hex_to_ansi(config.color, config.transparency)
        else:
            mapping[key] = AnsiColors.dim  # Dim for disabled

    return mapping


class ThemeLoader:
    """Loads and manages theme configurations dynamically from files."""

    def __init__(self):
        self._cached_themes: Optional[Dict[str, ThemeConfig]] = None

    def load_all_themes(self) -> Dict[str, ThemeConfig]:
        """Load all themes from system and user locations."""
        if self._cached_themes:
            return self._cached_themes

        themes = {}

        # Load system themes from resources directory
        system_themes = self._load_system_themes()
        themes.update(system_themes)

        # Load user themes from user config locations
        user_themes = self._load_user_themes()
        themes.update(user_themes)  # User themes override system themes

        self._cached_themes = themes
        return themes

    def _load_system_themes(self) -> Dict[str, ThemeConfig]:
        """Load system themes from CLI's own resources directory."""
        themes = {}

        # Load from CLI's own themes.json file
        cli_themes_file = self._find_cli_themes_file()
        if cli_themes_file:
            try:
                with open(cli_themes_file, "r") as f:
                    data = json.load(f)

                # Parse themes format
                for theme_id, theme_data in data.get("themes", {}).items():
                    theme_config = self._parse_theme_data(theme_id, theme_data)
                    if theme_config:
                        themes[theme_id] = theme_config

            except Exception as e:
                print(f"Warning: Failed to load CLI themes file {cli_themes_file}: {e}")

        # Also load from individual theme files in resources
        system_themes_dirs = self._find_system_themes_directories()
        for themes_dir in system_themes_dirs:
            if not themes_dir.exists():
                continue

            # Load individual theme files (*.json, excluding the main themes.json)
            for theme_file in themes_dir.glob("*.json"):
                if theme_file.name == "themes.json":
                    continue  # Skip main themes file (already loaded above)
                try:
                    theme_config = self._load_theme_file(theme_file)
                    if theme_config:
                        theme_id = theme_file.stem  # filename without extension
                        themes[theme_id] = theme_config
                except Exception as e:
                    print(f"Warning: Failed to load system theme {theme_file}: {e}")

        return themes

    def _load_user_themes(self) -> Dict[str, ThemeConfig]:
        """Load user themes from user configuration locations."""
        themes = {}

        # Load from user config directories
        user_themes_dirs = self._find_user_themes_directories()

        for themes_dir in user_themes_dirs:
            if not themes_dir.exists():
                continue

            # Load individual theme files (*.json)
            for theme_file in themes_dir.glob("*.json"):
                try:
                    theme_config = self._load_theme_file(theme_file)
                    if theme_config:
                        theme_id = theme_file.stem  # filename without extension
                        themes[theme_id] = theme_config
                except Exception as e:
                    print(f"Warning: Failed to load user theme {theme_file}: {e}")

        return themes

    def _find_cli_themes_file(self) -> Optional[Path]:
        """Find the CLI's own themes.json file."""
        possible_paths = [
            # CLI's own resources directory
            Path(__file__).parent.parent / "resources" / "themes" / "themes.json",
            # Environment variable override
            (
                Path(os.environ.get("CODEGUARD_CLI_THEMES_FILE", ""))
                if os.environ.get("CODEGUARD_CLI_THEMES_FILE")
                else None
            ),
        ]

        for path in possible_paths:
            if path and path.exists():
                return path

        return None

    def _find_system_themes_directories(self) -> List[Path]:
        """Find system themes directories."""
        possible_paths = [
            # Relative to this module
            Path(__file__).parent.parent / "resources" / "themes",
            # Environment variable
            (
                Path(os.environ.get("CODEGUARD_SYSTEM_THEMES_DIR", ""))
                if os.environ.get("CODEGUARD_SYSTEM_THEMES_DIR")
                else None
            ),
        ]

        return [p for p in possible_paths if p and p.exists()]

    def _find_user_themes_directories(self) -> List[Path]:
        """Find user themes directories in standard config locations."""
        home = Path.home()
        possible_paths = []

        if os.name == "nt":  # Windows
            # Windows AppData
            appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
            possible_paths.extend(
                [
                    appdata / "CodeGuard" / "themes",
                    appdata / "TuMee" / "CodeGuard" / "themes",
                ]
            )
        elif os.name == "posix":
            if "darwin" in os.uname().sysname.lower():  # macOS
                possible_paths.extend(
                    [
                        home / "Library" / "Application Support" / "CodeGuard" / "themes",
                        home / "Library" / "Application Support" / "TuMee" / "CodeGuard" / "themes",
                    ]
                )
            else:  # Linux/Unix
                # XDG config directory
                xdg_config = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
                possible_paths.extend(
                    [
                        xdg_config / "codeguard" / "themes",
                        xdg_config / "tumee" / "codeguard" / "themes",
                        home / ".codeguard" / "themes",
                    ]
                )

        # Environment variable override
        if os.environ.get("CODEGUARD_USER_THEMES_DIR"):
            possible_paths.insert(0, Path(os.environ["CODEGUARD_USER_THEMES_DIR"]))

        return possible_paths

    def save_user_theme(self, theme_id: str, theme_config: ThemeConfig) -> bool:
        """Save a user theme to the user config directory."""
        try:
            # Get the first user themes directory (create if needed)
            user_themes_dirs = self._find_user_themes_directories()
            if not user_themes_dirs:
                return False

            themes_dir = user_themes_dirs[0]  # Use first (highest priority) directory
            themes_dir.mkdir(parents=True, exist_ok=True)

            # Convert theme config to JSON format
            theme_data = self._theme_config_to_dict(theme_config)

            # Save to file
            theme_file = themes_dir / f"{theme_id}.json"
            with open(theme_file, "w") as f:
                json.dump(theme_data, f, indent=2)

            # Clear cache to force reload
            self._cached_themes = None

            return True

        except Exception as e:
            print(f"Error saving user theme {theme_id}: {e}")
            return False

    def delete_user_theme(self, theme_id: str) -> bool:
        """Delete a user theme."""
        try:
            # Look for the theme in user directories
            user_themes_dirs = self._find_user_themes_directories()

            for themes_dir in user_themes_dirs:
                theme_file = themes_dir / f"{theme_id}.json"
                if theme_file.exists():
                    theme_file.unlink()
                    # Clear cache to force reload
                    self._cached_themes = None
                    return True

            return False  # Theme not found

        except Exception as e:
            print(f"Error deleting user theme {theme_id}: {e}")
            return False

    def _theme_config_to_dict(self, theme_config: ThemeConfig) -> Dict[str, Any]:
        """Convert ThemeConfig to dictionary format for saving."""
        permissions_dict = {}
        for key, perm in theme_config.colors.permissions.items():
            permissions_dict[key] = {
                "color": perm.color,
                "transparency": perm.transparency,
                "borderOpacity": perm.borderOpacity,
                "minimapColor": perm.minimapColor,
                "enabled": perm.enabled,
                "highlightEntireLine": perm.highlightEntireLine,
            }

        return {
            "name": theme_config.name,
            "colors": {
                "permissions": permissions_dict,
                "borderBarEnabled": theme_config.colors.borderBarEnabled,
                "mixPattern": theme_config.colors.mixPattern,
            },
        }

    def _parse_theme_data(self, theme_id: str, theme_data: Dict[str, Any]) -> Optional[ThemeConfig]:
        """Parse theme data format."""
        try:
            name = theme_data.get("name", theme_id)
            colors_data = theme_data.get("colors", {})

            # Parse permissions
            permissions_data = colors_data.get("permissions", {})
            permissions = {}

            for perm_key, perm_data in permissions_data.items():
                permissions[perm_key] = PermissionConfig(
                    color=perm_data.get("color", "#000000"),
                    transparency=perm_data.get("transparency", 0.5),
                    borderOpacity=perm_data.get("borderOpacity", 1.0),
                    minimapColor=perm_data.get("minimapColor", perm_data.get("color", "#000000")),
                    enabled=perm_data.get("enabled", True),
                    highlightEntireLine=perm_data.get("highlightEntireLine", False),
                )

            theme_colors = ThemeColors(
                permissions=permissions,
                borderBarEnabled=colors_data.get("borderBarEnabled", True),
                mixPattern=colors_data.get("mixPattern", "humanBorder"),
            )

            return ThemeConfig(name=name, colors=theme_colors)

        except Exception as e:
            print(f"Error parsing theme {theme_id}: {e}")
            return None

    def _load_theme_file(self, theme_file: Path) -> Optional[ThemeConfig]:
        """Load a single theme file."""
        try:
            with open(theme_file, "r") as f:
                data = json.load(f)

            # Check if it's the expected theme format
            if "colors" in data and "permissions" in data.get("colors", {}):
                # Standard theme format
                return self._parse_theme_data(theme_file.stem, data)
            else:
                # Simplified format - convert to standard format
                # This allows for simpler theme files while maintaining compatibility
                print(f"Warning: Theme {theme_file} uses unsupported simplified format")
                return None

        except Exception as e:
            print(f"Error loading theme file {theme_file}: {e}")
            return None

    def get_theme(self, theme_name: str) -> Optional[ThemeConfig]:
        """Get a specific theme by name."""
        themes = self.load_all_themes()
        return themes.get(theme_name)

    def list_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        themes = self.load_all_themes()
        return list(themes.keys())

    def load_theme_for_cli(
        self, theme_name: str = None, fail_on_missing: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Load theme in the format expected by the CLI display engine.
        Exact port of the VSCode plugin's loadTheme function.

        Args:
            theme_name: Name of theme to load (defaults to "default")
            fail_on_missing: If True, raise exception when theme cannot be loaded
        """
        selected_theme = theme_name or "default"

        themes = self.load_all_themes()

        if selected_theme in themes:
            theme_data = themes[selected_theme]

            return {
                "colors": map_theme_to_ansi(theme_data.colors.permissions),
                "mixPattern": theme_data.colors.mixPattern,
                "permissions": theme_data.colors.permissions,
            }

        # Theme not found - handle based on fail_on_missing flag
        if fail_on_missing:
            available_themes = list(themes.keys())
            if not available_themes:
                raise RuntimeError(
                    f"No themes could be loaded from the theme system. "
                    f"This may indicate a packaging issue where resource files are missing. "
                    f"Expected theme file location: {self._find_cli_themes_file()}"
                )
            else:
                raise ValueError(
                    f"Theme '{selected_theme}' not found. Available themes: {', '.join(available_themes)}"
                )

        return None

    def clear_cache(self):
        """Clear cached themes."""
        self._cached_themes = None


# Global theme loader instance
_theme_loader: Optional[ThemeLoader] = None


def get_theme_loader() -> ThemeLoader:
    """Get the global theme loader instance."""
    global _theme_loader
    if _theme_loader is None:
        _theme_loader = ThemeLoader()
    return _theme_loader


def load_all_themes() -> Dict[str, ThemeConfig]:
    """Load all available themes."""
    return get_theme_loader().load_all_themes()


def get_theme(theme_name: str) -> Optional[ThemeConfig]:
    """Get a specific theme by name."""
    return get_theme_loader().get_theme(theme_name)


def list_available_themes() -> List[str]:
    """Get list of available theme names."""
    return get_theme_loader().list_available_themes()


def load_theme_for_cli(
    theme_name: str = None, fail_on_missing: bool = False
) -> Optional[Dict[str, Any]]:
    """Load theme in the format expected by the CLI display engine."""
    return get_theme_loader().load_theme_for_cli(theme_name, fail_on_missing)


def clear_theme_cache():
    """Clear cached themes."""
    get_theme_loader().clear_cache()


def save_user_theme(theme_id: str, theme_config: ThemeConfig) -> bool:
    """Save a user theme."""
    return get_theme_loader().save_user_theme(theme_id, theme_config)


def delete_user_theme(theme_id: str) -> bool:
    """Delete a user theme."""
    return get_theme_loader().delete_user_theme(theme_id)
