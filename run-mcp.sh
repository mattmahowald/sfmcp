#!/bin/bash
# Simple wrapper to run SFMCP server

# Go to script directory
cd "$(dirname "$0")"

# Add common macOS poetry/python paths
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

# Run the server
exec poetry run sfmcp-stdio