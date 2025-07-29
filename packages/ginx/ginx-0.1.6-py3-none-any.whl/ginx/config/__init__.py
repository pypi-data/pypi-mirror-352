"""
Ginx configuration management.

This module provides a clean API for loading and managing Ginx configuration,
including scripts, plugins, and global settings.
"""

# Core loading functions
from typing import Any, Dict

from .discovery import DEFAULT_CONFIG_FILES, find_config_file
from .loader import load_config, load_raw_config, save_config
from .plugins import (
    get_plugin_directories,
    is_plugin_enabled,
)
from .plugins import load_plugin_config
from .plugins import load_plugin_config as get_plugin_config

# Specialized loaders
from .scripts import get_script_variables, has_variables
from .scripts import load_scripts
from .scripts import load_scripts as get_scripts
from .scripts import resolve_execution_order
from .settings import (
    DEFAULT_SETTINGS,
    get_setting,
    is_dangerous_commands_enabled,
)
from .settings import load_settings
from .settings import load_settings as get_global_config


def create_sample_config(config_path: str = "ginx.yaml") -> None:
    """
    Create a sample configuration file.

    Args:
        config_path: Path where to create the config file
    """
    try:
        from ginx.init import ginx_config

        # Clean config (remove comment keys)
        clean_config = {k: v for k, v in ginx_config.items() if not k.startswith("#")}

        save_config(clean_config, config_path)

        import typer

        typer.echo("Edit this file to define your own scripts, plugins, and settings.")

    except Exception as e:
        import typer

        typer.secho(f"Error creating config: {e}", fg=typer.colors.RED)


def write_ginx_config(config: Dict[str, Any], config_path: str = "ginx.yaml") -> None:
    """Legacy alias for save_config."""
    save_config(config, config_path)


__all__ = [
    # Core functions
    "load_config",
    "load_raw_config",
    "save_config",
    "find_config_file",
    "create_sample_config",
    # Specialized loaders
    "load_scripts",
    "load_plugin_config",
    "load_settings",
    # Utility functions
    "get_setting",
    "is_plugin_enabled",
    "get_plugin_directories",
    "is_dangerous_commands_enabled",
    "has_variables",
    "get_script_variables",
    # Legacy compatibility
    "get_scripts",
    "get_plugin_config",
    "get_global_config",
    "write_ginx_config",
    # Constants
    "DEFAULT_CONFIG_FILES",
    "DEFAULT_SETTINGS",
    # Executable commands
    "resolve_execution_order",
]
