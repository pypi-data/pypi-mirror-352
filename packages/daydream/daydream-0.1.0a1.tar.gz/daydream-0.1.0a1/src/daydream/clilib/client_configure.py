import json
import shlex
import shutil
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

import boto3.session
import questionary
import rich
import typer

from daydream.clilib.options import DEFAULT_PROFILE, PROFILE_OPTION
from daydream.config.utils import Config, get_config_path, save_config
from daydream.plugins.base import PluginManager

app = typer.Typer(
    help="Configure clients of the Daydream MCP Server, like Claude Desktop", no_args_is_help=True
)


def _resolve_default_claude_mcp_config_filename() -> Path:
    claude_mcp_file = (
        Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    )
    return claude_mcp_file.absolute()


_default_claude_mcp_config_filename = _resolve_default_claude_mcp_config_filename()


def _resolve_default_uv() -> Path:
    uv_path = shutil.which("uv")
    if uv_path:
        return Path(uv_path).absolute()
    return Path("uv")


_default_uv_path = _resolve_default_uv()


def _resolve_default_repo_path() -> Path:
    return Path.cwd().absolute()


_default_repo_path = _resolve_default_repo_path()


def _resolve_default_claude_app() -> Path:
    return Path("/Applications/Claude.app").resolve()


_default_claude_app = _resolve_default_claude_app()


@app.command()
def claude(
    config_filename: Annotated[
        Path,
        typer.Option(
            ...,
            "--config-filename",
            help="Path to the Claude Desktop MCP config json file",
            show_default=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            writable=True,
            resolve_path=False,
            exists=False,
        ),
    ] = _default_claude_mcp_config_filename,
    repo_path: Annotated[
        Path,
        typer.Option(
            ...,
            "--repo-path",
            help="Path to the Daydream repo",
            show_default=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            writable=False,
            resolve_path=False,
            exists=True,
        ),
    ] = _default_repo_path,
    uv_path: Annotated[
        Path,
        typer.Option(
            ...,
            "--uv-path",
            help="Path to the uv executable",
            show_default=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            writable=False,
            resolve_path=False,
            exists=True,
        ),
    ] = _default_uv_path,
    claude_app: Annotated[
        Path,
        typer.Option(
            ...,
            "--claude-app",
            help="Path to the Claude Desktop app",
            show_default=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            writable=False,
            resolve_path=False,
            exists=False,
        ),
    ] = _default_claude_app,
    profile: str = PROFILE_OPTION,
    aws_profile: Annotated[
        list[str] | None,
        typer.Option(
            ...,
            "--aws-profile",
            help="One or more AWS profiles to use for the Daydream MCP Server",
        ),
    ] = None,
    enable_plugin: Annotated[
        list[str] | None,
        typer.Option(
            ...,
            "--enable-plugin",
            help="One or more plugins to enable for the Daydream MCP Server",
        ),
    ] = None,
    command_prefix: Annotated[
        str | None,
        typer.Option(
            ...,
            "--command-prefix",
            help="Command prefix to use for the Daydream MCP Server (e.g., 'aws-vault exec your_aws_profile')",
        ),
    ] = None,
    overwrite_existing: Annotated[
        bool,
        typer.Option(
            ...,
            "--overwrite-existing",
            help="Overwrite existing Daydream MCP Server config if it exists",
        ),
    ] = False,
    skip_plugin_selection: Annotated[
        bool,
        typer.Option(
            ...,
            "--skip-plugin-selection",
            help="Skip the interactive plugin selection prompt (use --enable-plugin to enable plugins)",
        ),
    ] = False,
) -> None:
    """Configure the Claude Desktop to use the Daydream MCP Server"""
    if aws_profile is None:
        aws_profile = []
    command, *args = [
        *shlex.split(command_prefix or ""),
        str(uv_path),
        "run",
        "--directory",
        str(repo_path),
        "daydream",
        "start",
        "--disable-sse",
    ]
    env = {
        "HOME": str(Path.home()),
    }
    daydream_server_config = {
        "command": shutil.which(command),
        "args": args,
        "env": env,
    }
    if not claude_app.exists():
        raise FileNotFoundError(
            f"Claude app doesn't exist at [bright_black]{claude_app}[/bright_black]. Make sure you have it installed and use --claude-app to specify a non-default location."
        )
    if profile != DEFAULT_PROFILE:
        daydream_server_config["args"].extend(["--profile", profile])
    mcp_server_config = _ensure_config_dir_and_backup_existing(config_filename, overwrite_existing)
    cfg = PluginManager.default_config
    _enable_plugins(enable_plugin, skip_plugin_selection, cfg)
    _configure_aws_plugin(aws_profile, cfg)
    _save_daydream_config(profile, overwrite_existing, cfg)
    mcp_server_config["mcpServers"]["daydream"] = daydream_server_config
    rich.print(
        f"Writing the following MCP Server config to Claude Desktop at: [bright_black]{config_filename}[/bright_black]"
    )
    rich.print_json(data=mcp_server_config)
    config_filename.write_text(json.dumps(mcp_server_config, indent=4))
    rich.print(
        "[green]Successfully configured Claude Desktop to use the Daydream MCP Server![/green]"
    )
    rich.print_json(data=mcp_server_config)
    if typer.confirm(
        "Open Claude Desktop now?",
        default=True,
        show_default=True,
    ):
        typer.launch(str(claude_app))


def _save_daydream_config(profile: str, overwrite_existing: bool, cfg: Config) -> None:
    cfg_path = get_config_path(profile, create=True)
    if cfg_path.exists():
        rich.print(f"Found existing config file at: [bright_black]{cfg_path}[/bright_black]")
        if not overwrite_existing:
            typer.confirm(
                "Would you like to overwrite the existing config?",
                default=False,
                show_default=True,
                abort=True,
            )
        backup_config_filename = cfg_path.with_suffix(
            f".yaml.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        rich.print(
            f"Backing up existing Daydream '{profile}' profile config file to: [bright_black]{backup_config_filename}[/bright_black]"
        )
        shutil.copy(cfg_path, backup_config_filename)
    rich.print(
        f"Writing Daydream '{profile}' profile config to: [bright_black]{cfg_path}[/bright_black]"
    )
    save_config(cfg, profile, create=True)


def _configure_aws_plugin(aws_profile: list[str] | None, cfg: Config) -> None:
    if "aws" in cfg.plugins:
        aws_plugin_cfg = cfg.plugins["aws"]
        if aws_plugin_cfg.enabled:
            selected_aws_profiles = []
            if aws_profile:
                selected_aws_profiles = list(aws_profile)
            else:
                avail_aws_profile = boto3.session.Session().available_profiles
                enable_search = len(avail_aws_profile) > 10
                selected_aws_profiles = questionary.checkbox(
                    "Which AWS profiles would you like to use with the Daydream MCP Server? (leave empty to use all available profiles)",
                    choices=avail_aws_profile,
                    use_search_filter=enable_search,
                    use_jk_keys=not enable_search,
                ).ask()

            aws_plugin_cfg.settings["accounts"] = {
                profile_name: {
                    "profile": profile_name,
                }
                for profile_name in selected_aws_profiles
            }


def _enable_plugins(
    enable_plugin: list[str] | None, skip_plugin_selection: bool, cfg: Config
) -> None:
    if enable_plugin:
        for plugin_name, plugin_cfg in cfg.plugins.items():
            plugin_cfg.enabled = plugin_name in enable_plugin
    elif not skip_plugin_selection:
        possible_plugins = list(cfg.plugins.keys())
        enabled_search = len(possible_plugins) > 10
        selected_plugins = questionary.checkbox(
            "Which plugins would you like to enable for the Daydream MCP Server? (leave empty to enable all available plugins)",
            choices=[
                questionary.Choice(p, checked=plugin_cfg.enabled)
                for p, plugin_cfg in cfg.plugins.items()
            ],
            use_search_filter=enabled_search,
            use_jk_keys=not enabled_search,
        ).ask()
        for plugin_name, plugin_cfg in cfg.plugins.items():
            plugin_cfg.enabled = plugin_name in selected_plugins


def _ensure_config_dir_and_backup_existing(
    config_filename: Path, overwrite_existing: bool
) -> dict[str, Any]:
    mcp_server_config: dict[str, Any] = {"mcpServers": {}}
    if config_filename.exists():
        existing_content = config_filename.read_text()
        mcp_server_config = json.loads(existing_content)
        existing_daydream_config = mcp_server_config.get("mcpServers", {}).get("daydream", None)
        if existing_daydream_config:
            print(f'Found existing "daydream" config for Claude Desktop ({config_filename}):')
            rich.print_json(data={"daydream": existing_daydream_config})
            if not overwrite_existing:
                typer.confirm(
                    "Would you like to overwrite the existing config?",
                    default=False,
                    show_default=True,
                    abort=True,
                )
            backup_config_filename = config_filename.with_suffix(
                f".json.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            rich.print(
                f"Backing up existing config file to: [bright_black]{backup_config_filename}[/bright_black]"
            )
            shutil.copy(config_filename, backup_config_filename)
    else:
        rich.print(f"Creating Claude Desktop MCP config file directory at: {config_filename}")
        config_filename.parent.mkdir(parents=True, exist_ok=True)
    return mcp_server_config
