# Salesforce MCP Server

This server provides MCP (Model Context Protocol) tools for interacting with Salesforce using the `sf` CLI. It exposes Salesforce data and metadata through standardized MCP tools that can be used with Claude Desktop and other MCP clients.

## Features

- **Query Tool** (`salesforce.query`) - Run SOQL queries and return structured results
- **List Objects** (`salesforce.list_objects`) - Get all Salesforce object names in your org
- **Describe Objects** (`salesforce.describe`) - Get detailed field information for any Salesforce object

## Prerequisites

- **macOS** (this setup is optimized for macOS)
- **Node.js** (for Salesforce CLI)
- **Python 3.11+**
- **Poetry** (for dependency management)

## Installation

**One-command setup:**

```bash
git clone https://github.com/yourusername/sfmcp.git
cd sfmcp
./install.py  # Installs everything and configures Claude Desktop
```

The installer will automatically:
- Install Poetry (if needed)
- Install Python dependencies
- Install/authenticate Salesforce CLI
- Create `.env` configuration
- Update Claude Desktop configuration

This will:
- Install Salesforce CLI if needed
- Authenticate with your Salesforce org (or select existing auth)
- Create a `.env` file with your org configuration
- Set up the default org for the MCP server

Alternatively, you can install Salesforce CLI manually:
```bash
npm install -g @salesforce/cli
sf org login web
```

### 3. Configure Claude Desktop

Add this server to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sfmcp": {
      "command": "/path/to/your/sfmcp/run-mcp.sh",
      "args": []
    }
  }
}
```

**Important:** Replace `/path/to/your/sfmcp/run-mcp.sh` with the actual path to the `run-mcp.sh` script in this project directory.

**Note:** The `install.py` script automatically detects the correct path and updates your Claude Desktop configuration.

### 4. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the new MCP server.

## Usage

Once configured, you can use these tools in Claude Desktop conversations:

- **"List all Salesforce objects"** - Uses `salesforce.list_objects`
- **"Describe the Account object"** - Uses `salesforce.describe`
- **"Query all active accounts"** - Uses `salesforce.query`

Example queries:
- `SELECT Id, Name FROM Account LIMIT 10`
- `SELECT Id, Email FROM Contact WHERE Email != null`

## Development

### Running the Server

**STDIO Mode (for MCP clients):**
```bash
poetry run sfmcp-stdio
# or
./scripts/run_stdio.sh
```

**HTTP Mode (for testing):**
```bash
poetry run sfmcp-http
# or
./scripts/run_http.sh
```

### Code Quality

```bash
# Type checking
poetry run mypy sfmcp/

# Linting
poetry run ruff check sfmcp/

# Formatting
poetry run ruff format sfmcp/
```

## Configuration

The server uses environment variables from `.env` file:

- `SF_INSTANCE_URL` - Your Salesforce instance URL
- `SF_ACCESS_TOKEN` - Salesforce access token (automatically managed)
- `SF_ORG_ALIAS` - Alias for your Salesforce org
- `SF_USERNAME` - Your Salesforce username
- `SFMCP_HTTP_HOST` - HTTP server host (default: 127.0.0.1)
- `SFMCP_HTTP_PORT` - HTTP server port (default: 3333)

## Troubleshooting

**"Salesforce CLI not found"**
- Make sure Node.js is installed
- Install SF CLI: `npm install -g @salesforce/cli`

**"Authentication failed"**
- Run `sf org list` to check authenticated orgs
- Re-run `python install.py` to set up authentication

**"Permission denied"**
- Make sure you have proper Salesforce org permissions
- Check that your access token hasn't expired
