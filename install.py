#!/usr/bin/env python3
"""
Installation script for SFMCP - Salesforce MCP Server
Converts the original setup.sh to Python for better cross-platform support.
"""
import os
import subprocess
import sys
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional


def run_command(
    command: List[str], capture_output: bool = True, check: bool = True
) -> subprocess.CompletedProcess:
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, capture_output=capture_output, text=True, check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(command)}")
        print(f"Error: {e}")
        sys.exit(1)


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None


def install_poetry() -> None:
    """Install Poetry if it's not already installed"""
    print("Checking for Poetry...")

    if check_command_exists("poetry"):
        print("Poetry is already installed")
        return

    print("Poetry not found. Installing Poetry...")

    try:
        # Download and run the Poetry installer
        import urllib.request
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
            print("Downloading Poetry installer...")
            with urllib.request.urlopen(
                "https://install.python-poetry.org"
            ) as response:
                installer_script = response.read().decode("utf-8")
            f.write(installer_script)
            installer_path = f.name

        # Run the installer
        result = subprocess.run(
            [sys.executable, installer_path], capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"❌ Poetry installation failed: {result.stderr}")
            print("Please install Poetry manually: https://python-poetry.org/docs/")
            sys.exit(1)

        # Clean up
        os.unlink(installer_path)

        print("✅ Poetry installed successfully")
        print("🔄 Please restart your terminal or run 'source ~/.bashrc' (or ~/.zshrc)")
        print("   Then re-run this script.")

        # Check if poetry is now available
        if not check_command_exists("poetry"):
            print("\n⚠️  Poetry was installed but is not in PATH.")
            print("   You may need to add it manually or restart your terminal.")
            print('   Try running: export PATH="$HOME/.local/bin:$PATH"')
            sys.exit(1)

    except Exception as e:
        print(f"❌ Failed to install Poetry: {e}")
        print("Please install Poetry manually from: https://python-poetry.org/docs/")
        sys.exit(1)


def install_sf_cli() -> None:
    """Install the Salesforce CLI"""
    print("Installing Salesforce CLI...")

    # Check if node is installed
    if not check_command_exists("node"):
        print("Error: You must have Node.js installed to run this project")
        print("Please install Node.js from: https://nodejs.org/")
        sys.exit(1)

    # Check if sf CLI is already installed
    if check_command_exists("sf"):
        print("sf CLI is already installed")
        return

    print("sf CLI not found. Installing...")
    try:
        run_command(["npm", "install", "-g", "@salesforce/cli"], capture_output=False)
        print("✅ Salesforce CLI installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Salesforce CLI")
        print("Please try installing manually: npm install -g @salesforce/cli")
        sys.exit(1)


def get_authenticated_orgs() -> Dict[str, Dict[str, Any]]:
    """Get dict of currently authenticated Salesforce orgs keyed by alias"""
    try:
        result = run_command(["sf", "org", "list", "--json"])
        data = json.loads(result.stdout)

        # Get orgs that are connected from all possible locations
        orgs = {}
        if "result" not in data:
            return orgs
        for org_type in ["other", "devHubs", "sandboxes", "nonScratchOrgs"]:
            for org in data["result"].get(org_type, []):
                if org.get("connectedStatus") != "Connected":
                    continue
                alias = org.get("alias", org.get("username", "Unknown"))
                orgs[alias] = {
                    "alias": alias,
                    "username": org.get("username", ""),
                    "instanceUrl": org.get("instanceUrl", ""),
                    "isDefault": org.get("isDefaultUsername", False),
                    "lastUsed": org.get("lastUsed", ""),
                }

        return orgs
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        return {}


def select_existing_org(orgs: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """Allow user to select from existing authenticated orgs"""

    # Sort orgs by default first, then by last used
    org_list = list(orgs.values())
    org_list.sort(key=lambda x: (not x["isDefault"], x["lastUsed"]), reverse=True)

    print("\nFound authenticated orgs:")
    for i, org in enumerate(org_list, 1):
        default_marker = " (DEFAULT)" if org["isDefault"] else ""
        instance = (
            org["instanceUrl"].replace("https://", "").split(".")[0]
            if org["instanceUrl"]
            else "Unknown"
        )
        print(f"{i}. {org['alias']} ({org['username']}) - {instance}{default_marker}")

    print("\nWould you like to:")
    print("1. Use an existing authenticated org")
    print("2. Authenticate a new org")

    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice in ["1", "2"]:
            break
        print("Invalid choice. Please enter 1 or 2.")

    if choice == "1":
        while True:
            try:
                org_num = int(
                    input(
                        f"Enter the number of the org you want to use (1-{len(org_list)}): "
                    )
                )
                if 1 <= org_num <= len(org_list):
                    selected_org = org_list[org_num - 1]
                    alias = selected_org["alias"]
                    print(f"Using existing org: {alias}\n")

                    # Get detailed org info and write to .env
                    org_details = get_org_details(alias)
                    write_env_file(org_details)

                    return alias
                else:
                    print(f"Please enter a number between 1 and {len(org_list)}")
            except ValueError:
                print("Please enter a valid number")

    return None


def authenticate_new_org() -> None:
    """Authenticate to a new Salesforce org"""
    print("\n=== Authenticating New Org ===")

    instance_url = input(
        "Enter your Salesforce instance URL (e.g., https://mycompany.my.salesforce.com): "
    ).strip()
    org_alias = input("Enter an alias for this org (e.g., mycompany-prod): ").strip()

    if not instance_url or not org_alias:
        print("❌ Error: Both instance URL and alias are required")
        sys.exit(1)

    print(f"Authenticating to {instance_url} with alias '{org_alias}'...")

    try:
        # Authenticate with the specified instance URL and alias
        run_command(
            ["sf", "org", "login", "web", "-d", "-a", org_alias, "-r", instance_url],
            capture_output=False,
        )
        print(f"✅ Successfully authenticated to {org_alias}")

    except subprocess.CalledProcessError:
        print("❌ Authentication failed")
        print("Please check your instance URL and try again")
        sys.exit(1)


def write_env_file(org_data: Dict[str, Any]) -> None:
    """Write org configuration to .env file"""
    env_path = Path(".env")

    # Create .env content
    env_content = f"""# Salesforce MCP Server Configuration
# Generated by install.py

SF_INSTANCE_URL={org_data['instanceUrl']}
SF_ACCESS_TOKEN={org_data['accessToken']}
SF_ORG_ALIAS={org_data['alias']}
SF_USERNAME={org_data['username']}

# Server Configuration (optional)
SFMCP_HTTP_HOST=127.0.0.1
SFMCP_HTTP_PORT=3333
"""

    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        print(f"✅ Configuration written to {env_path.absolute()}")
    except Exception as e:
        print(f"❌ Failed to write .env file: {e}")
        sys.exit(1)


def get_org_details(alias: str) -> Dict[str, Any]:
    """Get detailed org information including access token"""
    try:
        result = run_command(["sf", "org", "display", "--target-org", alias, "--json"])
        data = json.loads(result.stdout)

        if "result" in data:
            return data["result"]
        else:
            raise Exception("Unexpected response format from SF CLI")
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        print(f"❌ Could not get details for org: {alias}")
        sys.exit(1)


def update_claude_desktop_config() -> None:
    """Update Claude Desktop MCP configuration with this server"""
    current_dir = Path.cwd().absolute()
    wrapper_script = current_dir / "run-mcp.sh"

    # Determine config file path based on OS
    if sys.platform == "darwin":  # macOS
        config_path = (
            Path.home()
            / "Library/Application Support/Claude/claude_desktop_config.json"
        )
    elif sys.platform == "win32":  # Windows
        config_path = (
            Path(os.getenv("APPDATA", "")) / "Claude/claude_desktop_config.json"
        )
    else:  # Linux/other
        config_path = Path.home() / ".config/claude/claude_desktop_config.json"

    print(f"\n📝 Updating Claude Desktop configuration...")
    print(f"Config file: {config_path}")
    print(f"Server path: {current_dir}")
    print(f"Wrapper script: {wrapper_script}")

    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing config or create new one
    config = {"mcpServers": {}}
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print("⚠️ Could not read existing config, creating new one")
            config = {"mcpServers": {}}

    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add or update sfmcp server configuration using wrapper script
    config["mcpServers"]["sfmcp"] = {
        "command": str(wrapper_script),
        "args": [],
    }

    try:
        # Write updated config
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print("✅ Claude Desktop configuration updated successfully")
        print("\n🔄 Please restart Claude Desktop to load the new MCP server")
    except Exception as e:
        print(f"❌ Failed to update Claude Desktop config: {e}")
        print(f"\n📋 Manual configuration needed:")
        print(f"Add this to {config_path}:")
        print(
            json.dumps(
                {
                    "mcpServers": {
                        "sfmcp": {
                            "command": "poetry",
                            "args": ["run", "sfmcp-stdio"],
                            "cwd": str(current_dir),
                        }
                    }
                },
                indent=2,
            )
        )


def verify_authentication() -> None:
    """Verify that authentication was successful"""
    try:
        result = run_command(["sf", "org", "display", "--json"])
        data = json.loads(result.stdout)

        if "result" in data:
            org_info = data["result"]
            print(f"\n✅ Successfully connected to:")
            print(
                f"   Org: {org_info.get('alias', 'N/A')} ({org_info.get('username', 'N/A')})"
            )
            print(f"   Instance: {org_info.get('instanceUrl', 'N/A')}")
        else:
            print("❌ Could not verify authentication")

    except (subprocess.CalledProcessError, json.JSONDecodeError):
        print("❌ Could not verify authentication")


def print_manual_config() -> None:
    """Print manual Claude Desktop configuration instructions"""
    print("\n📋 Manual Claude Desktop Configuration:")
    print("Add this to your claude_desktop_config.json file:")
    current_dir = Path.cwd().absolute()
    wrapper_script = current_dir / "run-mcp.sh"
    print(
        json.dumps(
            {
                "mcpServers": {
                    "sfmcp": {
                        "command": str(wrapper_script),
                        "args": [],
                    }
                }
            },
            indent=2,
        )
    )


def handle_claude_desktop_config() -> None:
    """Handle Claude Desktop configuration (automatic or manual)"""
    print("\n" + "=" * 50)
    update_config = (
        input(
            "Would you like to update your Claude Desktop configuration automatically? (y/n): "
        )
        .strip()
        .lower()
    )

    if update_config in ["y", "yes", ""]:
        update_claude_desktop_config()
    else:
        print_manual_config()


def print_completion_message() -> None:
    """Print setup completion message"""
    print("\n🎉 Setup complete! You can now use the SFMCP server.")
    print("\nNext steps:")
    print("1. Restart Claude Desktop (if config was updated)")
    print("2. Test the server: poetry run sfmcp-stdio")
    print("3. Or start HTTP server: poetry run sfmcp-http")


def main() -> None:
    """Main installation flow"""
    print("🚀 SFMCP Installation Script")
    print("=" * 40)

    # Step 1: Install dependencies
    install_poetry()

    print("\nInstalling Python dependencies...")
    try:
        run_command(["poetry", "install"], capture_output=False)
        print("✅ Python dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        print("Please check your Poetry installation and try again")
        sys.exit(1)

    install_sf_cli()

    # Step 2: Handle Salesforce authentication
    print("\nChecking for authenticated Salesforce orgs...")
    authenticated_orgs = get_authenticated_orgs()

    if authenticated_orgs:
        selected_alias = select_existing_org(authenticated_orgs)
        if not selected_alias:
            # User chose to authenticate new org
            authenticate_new_org()
    else:
        print("No authenticated orgs found. Proceeding with authentication...")
        authenticate_new_org()

    # Step 3: Verify authentication and complete setup
    verify_authentication()
    handle_claude_desktop_config()
    print_completion_message()


if __name__ == "__main__":
    main()
