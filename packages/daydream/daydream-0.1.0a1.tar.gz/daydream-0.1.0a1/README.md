# Daydream

> [!WARNING]
> **ALPHA SOFTWARE**
> Daydream is experimental, under heavy development, and may be unstable. Use at your own risk!


Daydream is an MCP server to enable your LLM-powered application to understand and query your infrastructure.

## Quickstart

```
# Install uv and uvx
brew install uv # macOS

# Configure your AWS credentials
$ aws-vault exec production-engineerreadonly bash  # Or use your favorite credential management solution

# Configure your Aptible credentials
$ aptible login

# Build the graph
$ uvx daydream build-graph

# Start the MCP server (or configure your LLM assistant's MCP integration)
$ uvx daydream start
```

## Walkthrough

### 0. Install Daydream

It is recommended to run `daydream` with `uvx`:

```
uvx daydream --help
```

You may also install the package with `pip`:

```
pip install daydream
```

### 1. Check your configuration

Daydream works by importing resources from your platforms and tools using your local credentials. For this to work, you'll need to have those credentials configured wherever you're using Daydream.

At the moment, Daydream plugins resolve credentials in a similar way as official tools, whenever possible. For example:

* The `aws` plugin will attempt to resolve credentials in the [same way as the AWS CLI](https://docs.aws.amazon.com/cli/latest/topic/config-vars.html#precedence). For example, using aws profiles and the AWS_PROFILE environment variable will work.
* The `aptible` plugin uses your `~/.aptible/tokens.json`, which is created when running `aptible login`.

Make sure your credentials are configured for those tools before building the graph.

### 2. Build your graph

Before you can use Daydream with your LLM, you'll need to build your knowledge graph. This is an automatic process that may take a few minutes depending on the size of your infrastructure.

```
$ uvx daydream build-graph
```

> **Note:** if you're planning on working with multiple graphs, you can specify `--profile your-graph-name` or set the environment variable `DAYDREAM_PROFILE=your-graph-name`, which will store the generated graph under a specific profile.

### 3. Start Daydreaming with the MCP server

With your graph built run:

```
uvx daydream start
```

> **Note:** By default, Daydream listens on all supported transports (SSE and stdio). You can disable them individually with `--disable-sse` or `--disable-stdio`.

#### MCP Config File

This is the template for the MCP configuration file that your AI assistant (like Claude Desktop or Amazon Q) will use to run the Daydream:

```json
{
    "mcpServers": {
        "daydream": {
            "command": "/path/to/your/bin/uvx",
            "args": ["daydream", "start"],
            "env": {
                "AWS_PROFILE": "YOUR_AWS_PROFILE",
            }
        }
    }
}
```

Here is an example file that works on macOS. It supports AWS access via an AWS profile named `dev-daydream`:

```json
{
    "mcpServers": {
        "daydream": {
            "command": "/opt/homebrew/bin/uxv",
            "args": ["daydream", "start"],
            "env": {
                "AWS_PROFILE": "dev-daydream",
            }
        }
    }
}
```

Here is an example using aws-vault on macOS:

```json
{
    "mcpServers": {
        "daydream": {
            "command": "aws-vault",
            "args": ["exec", "YOUR_AWS_PROFILE", "--", "/opt/homebrew/bin/uv", "run", "--directory", "/Users/YOUR_USERNAME/src/aptible/daydream", "daydream", "start", "--disable-sse"]
        }
    }
}
```

#### Claude Desktop on macOS Setup

Add the MCP config to `~/Library/Application Support/Claude/claude_desktop_config.json`

More details at: https://modelcontextprotocol.io/quickstart/user

#### Amazon Q on macOS Setup

Add the MCP config to `~/.aws/amazonq/mcp.json`

More details at: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-mcp-configuration.html

## How Daydream Works

Daydream builds a knowledge graph of your infrastructure using a fairly simple inference strategy:

1. Daydream queries the APIs of your integrated tools and retrieves all supported resources, and adds each one as a node in the knowledge graph.
2. Daydream extracts unique identifiers and aliases for each retrieved resource, and adds them to a mapping.
3. Daydream extracts potential references from each retrieved resource, and attempts to match them to identifiers and aliases in the mapping to create edges between nodes.

Once the graph is built, the MCP server provides a set of tools for traversing the graph and interacting with nodes.
