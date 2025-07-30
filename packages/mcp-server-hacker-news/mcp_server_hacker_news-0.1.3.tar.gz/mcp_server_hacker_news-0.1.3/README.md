# MCP Hacker News Server

This project is a Hacker News information retrieval server implementation for the Model Context Protocol (MCP). It uses the FastMCP framework to provide HN API functionality.

## Available Tools

### get_top_stories

A function that retrieves the current top stories from Hacker News.

- `limit` (int, optional): Number of articles to retrieve. Defaults to 10.
  - **Returns**: A list of story object

### get_story

A function that retrieves details of a specific story.

- `id` (string, required): The story ID to retrieve
  - **Returns**: A story object containing title, url, score, etc.

## Installation

### Using `uv` (Recommended)

No special installation is required when using `uv`. You can run `mcp-server-hacker-news` directly using `uvx`.

### Using PIP

Alternatively, you can install `mcp-server-hacker-news` using pip:

```bash
pip install mcp-server-hacker-news
```

After installation, you can run the server as follows:

```bash
mcp-server-hacker-news
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx</summary>

```json
{
  "mcpServers": {
    "testing": {
      "command": "uvx",
      "args": ["mcp-server-hacker-news"]
    }
  }
}
```

</details>

### Configure for VS Code

For quick installation, use one of the one-click install buttons below...

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=hacker-news&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-server-hacker-news%22%5D%7D)

### Command Line Options

You can specify the following options when running the server:

- `--sse`: Enable SSE transport

  - **Choices**: `on`, `off`
  - **Default**: `off`
  - **Description**: Enables SSE transport when set to "on"

- `--host`: Host to bind the server

  - **Default**: `localhost`
  - **Description**: Specifies the host address the server should bind to

- `--port`: Port to bind the server

  - **Type**: Integer
  - **Default**: `8000`
  - **Description**: Specifies the port number the server should listen on
