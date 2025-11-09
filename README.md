# Salesforce MCP Server

This server provides MCP (Model Context Protocol) tools for interacting with Salesforce using the `sf` CLI. It exposes Salesforce data and metadata through standardized MCP tools that can be used with Claude Desktop and other MCP clients.

<a href="https://glama.ai/mcp/servers/@mattmahowald/sfmcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@mattmahowald/sfmcp/badge" alt="Salesforce Server MCP server" />
</a>

## Features

- **Query Tool** (`salesforce_query`) - Run SOQL queries and return structured results
- **List Objects** (`salesforce_list_objects`) - Get all Salesforce object names in your org
- **Describe Objects** (`salesforce_describe`) - Get detailed field information for any Salesforce object
- **List Flows** (`salesforce_list_flows`) - Get all Salesforce flows with status and version information
- **Describe Flow** (`salesforce_describe_flow`) - Get the complete XML metadata for a specific flow
- **List Reports** (`salesforce_list_reports`) - Get all Salesforce reports with folder and usage information
- **List Dashboards** (`salesforce_list_dashboards`) - Get all Salesforce dashboards with folder and usage information

## Prerequisites

Before running the configuration script, you must install these prerequisites:

- **macOS** (this setup is optimized for macOS, but should work on Linux/Windows)
- **Python 3.11+** - Required for running the MCP server
- **Poetry** - Python dependency management
- **Node.js** - Required for Salesforce CLI
- **Salesforce CLI** - Command line interface for Salesforce

### Prerequisites Installation Guide

**1. Python 3.11+**
```bash
# macOS (via Homebrew)
brew install python@3.11

# Or download directly from Python.org
# https://www.python.org/downloads/
```

**2. Poetry**
```bash
# Install Poetry (official installer)
curl -sSL https://install.python-poetry.org | python3 -

# Verify installation
poetry --version
```

**3. Node.js**
```bash
# macOS (via Homebrew)
brew install node

# Or download from Node.js website
# https://nodejs.org/
```

**4. Salesforce CLI**
```bash
# Install via npm (requires Node.js)
npm install -g @salesforce/cli

# Verify installation
sf --version
```

### Quick Prerequisites Check
Run these commands to verify all prerequisites are installed:
```bash
python3 --version    # Should be 3.11+
poetry --version     # Should show Poetry version
node --version       # Should show Node version
sf --version         # Should show Salesforce CLI version
```

## Installation

**Quick Start** (after installing prerequisites):

```bash
git clone https://github.com/mattmahowald/sfmcp.git
cd sfmcp
./install.py  # Configures SFMCP for your Salesforce org
```

The configuration script will:

- ✅ Check all prerequisites are installed
- 📦 Install Python dependencies via Poetry
- 🔐 Authenticate with your Salesforce org (or select existing auth)
- ⚙️ Create `.env` configuration file
- 🖥️ Update Claude Desktop configuration

**Prerequisites must be installed first** - see the Prerequisites section above.

### Manual Setup (Alternative)

If you prefer to set up manually:

1. **Install prerequisites** (see Prerequisites section above)

2. **Install Python dependencies:**
   ```bash
   poetry install
   ```

3. **Authenticate with Salesforce:**
   ```bash
   sf org login web
   ```

4. **Create `.env` file** with your Salesforce org details:
   ```bash
   SF_INSTANCE_URL=https://your-org.my.salesforce.com
   SF_ACCESS_TOKEN=your-access-token
   SF_ORG_ALIAS=your-org-alias
   SF_USERNAME=your-username
   ```

5. **Configure Claude Desktop** by adding this to your `claude_desktop_config.json`:
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

6. **Restart Claude Desktop** to load the new MCP server.

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

**"Prerequisites check failed"**

- Install missing prerequisites using the commands in the Prerequisites section
- Verify installations with: `python3 --version`, `poetry --version`, `node --version`, `sf --version`

**"Salesforce CLI not found"**

- Install Salesforce CLI: `npm install -g @salesforce/cli`
- Verify Node.js is installed: `node --version`

**"Authentication failed"**

- Run `sf org list` to check authenticated orgs
- Re-authenticate: `sf org login web`
- Re-run the configuration script: `python install.py`

**"Permission denied"**

- Make sure you have proper Salesforce org permissions
- Check that your access token hasn't expired
- Try re-authenticating with `sf org login web`

**"Poetry not found"**

- Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
- Add to PATH if needed: `export PATH="$HOME/.local/bin:$PATH"`
- Restart your terminal and try again