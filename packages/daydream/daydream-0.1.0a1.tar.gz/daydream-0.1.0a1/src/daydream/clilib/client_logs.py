import rich
import typer

app = typer.Typer(
    help="Show logs for a client of the Daydream MCP Server, like Claude Desktop",
    no_args_is_help=True,
)


@app.command()
def claude() -> None:
    """Show logs for Claude Desktop Daydream MCP Server"""
    rich.print("Logs are available at:")
    rich.print("~/Library/Logs/Claude/mcp.log")
    rich.print("~/Library/Logs/Claude/mcp-server-daydream.log")
