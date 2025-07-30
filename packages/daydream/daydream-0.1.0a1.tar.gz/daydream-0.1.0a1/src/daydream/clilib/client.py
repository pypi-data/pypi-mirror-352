import typer

import daydream.clilib.client_configure as client_configure
import daydream.clilib.client_logs as client_logs

app = typer.Typer(help="Work with clients of the Daydream MCP Server", no_args_is_help=True)
app.add_typer(client_configure.app, name="configure")
app.add_typer(client_logs.app, name="logs")
