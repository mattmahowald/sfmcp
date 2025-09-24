# Salesforce MCP Server

This server provides MCP (Model Context Protocol) tools for interacting with Salesforce using the `sf` CLI. It exposes Salesforce data and metadata through standardized MCP tools that can be used with Claude Desktop and other MCP clients.

## Features

- **Query Tool** (`salesforce_query`) - Run SOQL queries and return structured results
- **List Objects** (`salesforce_list_objects`) - Get all Salesforce object names in your org
- **Describe Objects** (`salesforce_describe`) - Get detailed field information for any Salesforce object
- **List Flows** (`salesforce_list_flows`) - Get all Salesforce flows with status and version information
- **Describe Flow** (`salesforce_describe_flow`) - Get the complete XML metadata for a specific flow
- **List Reports** (`salesforce_list_reports`) - Get all Salesforce reports with folder and usage information
- **List Dashboards** (`salesforce_list_dashboards`) - Get all Salesforce dashboards with folder and usage information

## Prerequisites

- **macOS** (this setup is optimized for macOS)
- **Python 3.11+**

## Installation

**One-command setup:**

```bash
git clone https://github.com/yourusername/sfmcp.git
cd sfmcp
./install.py  # Installs everything and configures Claude Desktop
```

The installer will automatically:
- Install Poetry and Python dependencies
- Install Node.js Salesforce CLI (if needed)
- Authenticate with your Salesforce org (or select existing auth)
- Create `.env` configuration
- Update Claude Desktop configuration

That's it! The script handles everything needed to get you up and running.

### Manual Setup (Alternative)

If you prefer to set up manually or the automatic installer doesn't work:

1. **Install dependencies:**
   ```bash
   # Install Poetry (if needed)
   curl -sSL https://install.python-poetry.org | python3 -

   # Install Python dependencies
   poetry install

   # Install Salesforce CLI (if needed)
   npm install -g @salesforce/cli
   ```

2. **Authenticate with Salesforce:**
   ```bash
   sf org login web
   ```

3. **Configure Claude Desktop** by adding this to your `claude_desktop_config.json`:
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

4. **Restart Claude Desktop** to load the new MCP server.

## Usage

Once configured, you can use these tools in Claude Desktop conversations:

- **"List all Salesforce objects"** - Uses `salesforce_list_objects`
- **"Describe the Account object"** - Uses `salesforce_describe`
- **"Query all active accounts"** - Uses `salesforce_query`
- **"List all flows"** - Uses `salesforce_list_flows`
- **"Describe the Contact_Last_Reply_Date flow"** - Uses `salesforce_describe_flow`
- **"List all reports"** - Uses `salesforce_list_reports`
- **"List all dashboards"** - Uses `salesforce_list_dashboards`

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
- Re-run the installer: `python install.py`
- Or install manually: `npm install -g @salesforce/cli`

**"Authentication failed"**
- Run `sf org list` to check authenticated orgs
- Re-run `python install.py` to set up authentication

**"Permission denied"**
- Make sure you have proper Salesforce org permissions
- Check that your access token hasn't expired
