"""
Main CLI runner for Ginx - Run project scripts defined in a YAML file.
"""

import shlex
import subprocess
import time
from typing import Any, Dict, List
import typing

import typer

from ginx.cmd import COMMANDS
from ginx.constants import COMMON_SHELL_COMMANDS
from ginx.loader import create_sample_config, get_global_config, get_scripts
from ginx.plugins import get_plugin_manager
from ginx.utils import (
    check_dependencies,
    expand_variables,
    extract_commands_from_shell_string,
    find_requirements_files,
    format_duration,
    parse_command_and_extra,
    parse_requirements_file,
    run_command_with_streaming,
    run_command_with_streaming_shell,
    validate_command,
)

app = typer.Typer(
    help="Ginx - Run project scripts defined in a YAML file.",
    invoke_without_command=True,
    add_completion=True,
    rich_help_panel="Commands",
)

# Initialize plugin manager
plugin_manager = get_plugin_manager()

# Global settings from the config
global_config = get_global_config()

# Auto Register built-in plugins
try:
    from ginx.plugins import auto_register_builtin_plugins

    auto_register_builtin_plugins()
except Exception:
    pass

# Discover and load external plugins
try:
    plugin_manager.discover_plugins()
except Exception:
    pass

# Add plugin commands to the app
try:
    plugin_manager.add_plugin_commands(app)
except Exception:
    pass


def create_script_command(script_name: str, script_config: Dict[str, Any]):
    def script_command(
        extra: str = typer.Argument("", help="Extra CLI arguments"),
        streaming: bool = typer.Option(
            True, "--stream/--no-stream", help="Stream output"
        ),
        dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Dry run"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    ) -> None:
        return execute_script_logic(
            script_name, script_config, extra, streaming, dry_run, verbose
        )

    script_command.__name__ = f"script_{script_name}"
    script_command.__doc__ = script_config.get(
        "description", f"Run {script_name} script"
    )
    return script_command


def register_script_commands() -> None:
    try:
        scripts = get_scripts()
        existing_commands = COMMANDS
        for script_name, script_config in scripts.items():
            if script_name not in existing_commands:
                script_command = create_script_command(script_name, script_config)
                app.command(script_name, help=script_config.get("description"))(
                    script_command
                )
    except Exception as e:
        typer.echo(f"Warning: Could not load scripts: {e}")


@app.callback()
def main(ctx: typer.Context) -> None:
    """
    Ginx is a command-line script runner powered by YAML configuration.

    Define your scripts in a YAML file and run them directly by name.

    Examples:
        ginx format              # Run the format script
        ginx build --verbose     # Run build script with verbose output
        ginx commit "fix: bug"   # Run commit script with extra args
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())

        raise typer.Exit()


@app.command("version", help="Show Ginx version.")
def show_version() -> None:
    """Show the current version of Ginx."""
    try:
        from ginx import __version__

        typer.echo(f"Ginx version {__version__}")
    except ImportError:
        typer.echo("Version information not available")


@app.command("list", help="List all available scripts.")
def list_scripts() -> None:
    """Displays all scripts from the YAML configuration."""
    scripts = get_scripts()
    if not scripts:
        typer.echo("No scripts found.")
        raise typer.Exit()

    typer.secho("Available scripts:", fg=typer.colors.BLUE, bold=True)
    typer.echo()

    for name, data in scripts.items():
        description = data.get("description", "No description")
        command = data.get("command", "")

        typer.secho(f"  {name}", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"    Description: {description}")
        typer.echo(f"    Command: {command}")
        typer.echo()


def execute_script_logic(
    script_name: str,
    script_config: Dict[str, Any],
    extra: str,
    streaming: bool,
    dry_run: bool,
    verbose: bool,
) -> None:
    """
    Runs a script defined in the YAML file.

    \b
    Example:
        ginx build
        ginx deploy "--force --region us-west"
        ginx test --stream --verbose
    """
    scripts = get_scripts()
    if script_name not in scripts:
        typer.secho(f"Script '{script_name}' not found.", fg=typer.colors.RED)
        typer.echo("\nAvailable scripts:")
        for name in scripts.keys():
            typer.echo(f"  - {name}")
        raise typer.Exit(code=1)

    script = scripts[script_name]
    command_str = script["command"]

    # Expand environment variables
    script_env = script.get("env", {})
    command_str = expand_variables(command_str, script_env)

    # Validate command
    if not validate_command(command_str):
        typer.secho("Command validation failed. Aborting.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Check if command contains shell operators or builtins
    shell_operators = ["&&", "||", ";", "|", ">", "<", "&", "$(", "`"]
    shell_builtins = [
        "cd",
        "export",
        "set",
        "unset",
        "alias",
        "source",
        ".",
        "eval",
        "exec",
    ]

    needs_shell = any(op in command_str for op in shell_operators)

    if not needs_shell:
        # Check for shell builtins in the command
        command = extract_commands_from_shell_string(command_str)
        for cmd in command:
            # Check if command is a shell builtin
            if cmd in shell_builtins:
                needs_shell = True

    # Parse command and add extra arguments
    full_command, command_display = parse_command_and_extra(
        command_str, extra, needs_shell=True
    )

    if verbose:
        typer.secho(f"Script: {script_name}", fg=typer.colors.BLUE)
        typer.secho(
            f"Description: {script.get('description', 'N/A')}", fg=typer.colors.BLUE
        )
        typer.secho(
            f"Working directory: {script.get('cwd', 'current')}", fg=typer.colors.BLUE
        )
        typer.secho(
            f"Shell mode: {'Yes' if needs_shell else 'No'}", fg=typer.colors.BLUE
        )

    typer.secho(f"Running: {command_display}", fg=typer.colors.CYAN)

    if dry_run:
        typer.secho("Dry run - command not executed", fg=typer.colors.YELLOW)
        return

    start_time = time.time()

    try:
        if streaming:
            # Use streaming output
            if needs_shell:
                exit_code = run_command_with_streaming_shell(
                    (
                        str(full_command)
                        if isinstance(full_command, list)
                        else full_command
                    ),
                    cwd=script.get("cwd"),
                    env=script.get("env"),
                )
            else:
                exit_code = run_command_with_streaming(
                    (
                        full_command
                        if isinstance(full_command, list)
                        else shlex.split(full_command)
                    ),
                    cwd=script.get("cwd"),
                    env=script.get("env"),
                )

            if exit_code == 0:
                duration = time.time() - start_time
                typer.secho(
                    f"\n✓ Script completed successfully in {format_duration(duration)}",
                    fg=typer.colors.GREEN,
                )
            else:
                typer.secho(
                    f"\n✗ Script failed with exit code {exit_code}", fg=typer.colors.RED
                )
                raise typer.Exit(code=exit_code)
        else:
            # Capture output
            if needs_shell:
                result = subprocess.run(
                    full_command,
                    shell=True,
                    check=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=not streaming,
                    cwd=script.get("cwd"),
                    env=script.get("env"),
                )
            else:
                result = subprocess.run(
                    full_command,
                    check=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=not streaming,
                    cwd=script.get("cwd"),
                    env=script.get("env"),
                )

            duration = time.time() - start_time

            if result.stdout and not streaming:
                typer.echo(result.stdout)

            typer.secho(
                f"✓ Script completed successfully in {format_duration(duration)}",
                fg=typer.colors.GREEN,
            )

    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        typer.secho(
            f"\n✗ Script execution failed after {format_duration(duration)}",
            fg=typer.colors.RED,
        )

        if e.stderr:
            typer.echo("Error output:")
            typer.echo(e.stderr)
        elif hasattr(e, "output") and e.output:
            typer.echo("Output:")
            typer.echo(e.output)

        raise typer.Exit(code=e.returncode)
    except KeyboardInterrupt:
        duration = time.time() - start_time
        typer.secho(
            f"\n⚠ Script interrupted after {format_duration(duration)}",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=130)


@app.command("run", help="Run a script by name.")
def run_script(
    script_name: str,
    extra: str = typer.Argument("", help="Extra CLI arguments"),
    streaming: bool = typer.Option(
        True,
        "--stream/--no-stream",
        help="Stream output in real-time (default: enabled)",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what would be executed without running"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show verbose output"),
) -> None:
    """
    Runs a script defined in the YAML file.

    \b
    Example:
        ginx run build
        ginx run deploy "--force --region us-west"
        ginx run test --stream --verbose
    """
    scripts = get_scripts()
    if script_name not in scripts:
        typer.secho(f"Script '{script_name}' not found.", fg=typer.colors.RED)
        typer.echo("\nAvailable scripts:")
        for name in scripts.keys():
            typer.echo(f"  - {name}")
        raise typer.Exit(code=1)

    script = scripts[script_name]
    command_str = script["command"]

    # Expand environment variables
    script_env = script.get("env", {})
    command_str = expand_variables(command_str, script_env)

    # Validate command
    if not validate_command(command_str):
        typer.secho("Command validation failed. Aborting.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Check if command contains shell operators or builtins
    shell_operators = ["&&", "||", ";", "|", ">", "<", "&", "$(", "`"]
    shell_builtins = [
        "cd",
        "export",
        "set",
        "unset",
        "alias",
        "source",
        ".",
        "eval",
        "exec",
    ]

    needs_shell = any(op in command_str for op in shell_operators)

    if not needs_shell:
        # Check for shell builtins in the command
        command = extract_commands_from_shell_string(command_str)
        for cmd in command:
            # Check if command is a shell builtin
            if cmd in shell_builtins:
                needs_shell = True

    # Parse command and add extra arguments
    full_command, command_display = parse_command_and_extra(
        command_str, extra, needs_shell=True
    )

    if verbose:
        typer.secho(f"Script: {script_name}", fg=typer.colors.BLUE)
        typer.secho(
            f"Description: {script.get('description', 'N/A')}", fg=typer.colors.BLUE
        )
        typer.secho(
            f"Working directory: {script.get('cwd', 'current')}", fg=typer.colors.BLUE
        )
        typer.secho(
            f"Shell mode: {'Yes' if needs_shell else 'No'}", fg=typer.colors.BLUE
        )

    typer.secho(f"Running: {command_display}", fg=typer.colors.CYAN)

    if dry_run:
        typer.secho("Dry run - command not executed", fg=typer.colors.YELLOW)
        return

    start_time = time.time()

    try:
        if streaming:
            # Use streaming output
            if needs_shell:
                exit_code = run_command_with_streaming_shell(
                    (
                        str(full_command)
                        if isinstance(full_command, list)
                        else full_command
                    ),
                    cwd=script.get("cwd"),
                    env=script.get("env"),
                )
            else:
                exit_code = run_command_with_streaming(
                    (
                        full_command
                        if isinstance(full_command, list)
                        else shlex.split(full_command)
                    ),
                    cwd=script.get("cwd"),
                    env=script.get("env"),
                )

            if exit_code == 0:
                duration = time.time() - start_time
                typer.secho(
                    f"\n✓ Script completed successfully in {format_duration(duration)}",
                    fg=typer.colors.GREEN,
                )
            else:
                typer.secho(
                    f"\n✗ Script failed with exit code {exit_code}", fg=typer.colors.RED
                )
                raise typer.Exit(code=exit_code)
        else:
            # Capture output
            if needs_shell:
                result = subprocess.run(
                    full_command,
                    shell=True,
                    check=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=streaming,
                    cwd=script.get("cwd"),
                    env=script.get("env"),
                )
            else:
                result = subprocess.run(
                    full_command,
                    check=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=streaming,
                    cwd=script.get("cwd"),
                    env=script.get("env"),
                )

            duration = time.time() - start_time

            if result.stdout and streaming:
                typer.echo(result.stdout)

            typer.secho(
                f"✓ Script completed successfully in {format_duration(duration)}",
                fg=typer.colors.GREEN,
            )

    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        typer.secho(
            f"\n✗ Script execution failed after {format_duration(duration)}",
            fg=typer.colors.RED,
        )

        if e.stderr:
            typer.echo("Error output:")
            typer.echo(e.stderr)
        elif hasattr(e, "output") and e.output:
            typer.echo("Output:")
            typer.echo(e.output)

        raise typer.Exit(code=e.returncode)
    except KeyboardInterrupt:
        duration = time.time() - start_time
        typer.secho(
            f"\n⚠ Script interrupted after {format_duration(duration)}",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=130)


@app.command("init", help="Create a sample ginx.yaml configuration file.")
def init_config(
    filename: str = typer.Option(
        "ginx.yaml", "--file", "-f", help="Configuration filename"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite existing configuration file"
    ),
) -> None:
    """Create a sample configuration file with common script examples."""
    import os

    if os.path.exists(filename) and not force:
        typer.secho(
            f"Configuration file '{filename}' already exists. Use --force to overwrite.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=1)

    create_sample_config(filename)


@app.command("validate", help="Validate the configuration file.")
def validate_config() -> None:
    """Validate the YAML configuration file and check for issues."""
    scripts = get_scripts()

    if not scripts:
        typer.secho("No valid configuration found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho("Configuration validation:", fg=typer.colors.BLUE, bold=True)
    typer.echo()

    issues_found = False

    for name, script in scripts.items():
        typer.secho(f"Script: {name}", fg=typer.colors.GREEN)

        # Check required fields
        if "command" not in script:
            typer.secho(f"  ✗ Missing required 'command' field", fg=typer.colors.RED)
            issues_found = True
        else:
            typer.secho(f"  ✓ Command: {script['command']}", fg=typer.colors.GREEN)

        # Check command validity
        if "command" in script and not validate_command(script["command"]):
            typer.secho(f"  ⚠ Command validation warning", fg=typer.colors.YELLOW)

        # Check working directory
        if "cwd" in script:
            import os

            if not os.path.exists(script["cwd"]):
                typer.secho(
                    f"  ⚠ Working directory does not exist: {script['cwd']}",
                    fg=typer.colors.YELLOW,
                )

        typer.echo()

    if issues_found:
        typer.secho(
            "Configuration has issues that need to be fixed.", fg=typer.colors.RED
        )
        raise typer.Exit(code=1)
    else:
        typer.secho("✓ Configuration is valid!", fg=typer.colors.GREEN, bold=True)


@app.command("deps", help="Check dependencies and requirements files.")
def check_script_dependencies() -> None:
    """Check if required commands/tools are available and show requirements file status."""
    scripts = get_scripts()

    # Check requirements files
    req_files = find_requirements_files()
    if req_files:
        typer.secho("Found requirements files:", fg=typer.colors.BLUE, bold=True)
        for req_file in req_files:
            packages = parse_requirements_file(req_file)
            typer.echo(f"  {req_file}: {len(packages)} packages")
        typer.echo()

    if not scripts:
        typer.secho("No scripts found.", fg=typer.colors.RED)
        if not req_files:
            raise typer.Exit(code=1)
        return

    # Extract commands from scripts
    commands_to_check: typing.Set[str] = set()
    for script in scripts.values():
        command = script.get("command", "")
        if command:
            found_commands = extract_commands_from_shell_string(command)
            all_commands: List[str] = []
            for command in found_commands:
                if command not in COMMON_SHELL_COMMANDS:
                    all_commands.append(command)
                pass
            commands_to_check.update(all_commands)

    if not commands_to_check:
        typer.echo("No external commands found in scripts.")
        return

    typer.secho("Script dependencies:", fg=typer.colors.BLUE, bold=True)

    results = check_dependencies(list(commands_to_check))
    missing_commands: List[str] = []

    for cmd, available in results.items():
        if available:
            typer.secho(f"  ✓ {cmd}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"  ✗ {cmd}", fg=typer.colors.RED)
            missing_commands.append(cmd)

    if missing_commands:
        typer.echo()
        typer.secho("Missing commands:", fg=typer.colors.RED, bold=True)
        for cmd in missing_commands:
            typer.echo(f"  - {cmd}")

        typer.echo()
        typer.secho("Install missing dependencies")
        typer.secho(f"Use command: pip install {" ".join(missing_commands)}")
        typer.echo()


@app.command("debug-plugins", help="Debug plugin loading status.")
def debug_plugins() -> None:
    """Debug plugin loading and registration."""
    typer.secho("Plugin Debug Information:", fg=typer.colors.BLUE, bold=True)

    plugins = plugin_manager.list_plugins()
    typer.echo(f"Registered plugins: {len(plugins)}")

    for name, plugin in plugins.items():
        typer.secho(f"  ✓ {name}", fg=typer.colors.GREEN)
        typer.echo(f"    Version: {plugin.version}")
        typer.echo(f"    Description: {plugin.description}")

    if not plugins:
        typer.secho("  No plugins registered", fg=typer.colors.YELLOW)


register_script_commands()


if __name__ == "__main__":
    app()
