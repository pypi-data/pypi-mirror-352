# Weibo MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server for fetching Weibo user information, posts, and search functionality. This server helps retrieve detailed user information, posts, and perform user searches on Weibo.

<a href="https://glama.ai/mcp/servers/@qinyuanpei/mcp-server-weibo">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@qinyuanpei/mcp-server-weibo/badge" alt="Weibo Server MCP server" />
</a>

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/qinyuanpei-mcp-server-weibo-badge.png)](https://mseep.ai/app/qinyuanpei-mcp-server-weibo)

## Installation

From source code:

```json
{
    "mcpServers": {
        "weibo": {
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/qinyuanpei/mcp-server-weibo.git",
                "mcp-server-weibo"
            ]
        }
    }
}
```

From package manager:

```json
{
    "mcpServers": {
        "weibo": {
            "command": "uvx",
            "args": ["mcp-server-weibo"],
        }
    }
}
```

## Components

### Tools

- `search_users(keyword, limit)`: Search for Weibo users
- `get_profile(uid)`: Get detailed user information
- `get_feeds(uid, limit)`: Get user posts
- `get_hot_search(limit)`: Get Weibo hot search
- `search_content(keyword, limit, page)`: Search Weibo posts

### Resources   

None

### Prompts

None

## Requirements

- Python >= 3.10
- httpx >= 0.24.0

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Disclaimer

For more information, see the Chinese README (`README.md`).

This project is not affiliated with Weibo and is intended for learning and research purposes only.