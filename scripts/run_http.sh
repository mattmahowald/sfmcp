#!/usr/bin/env bash
set -euo pipefail
export SFMCP_HTTP_HOST="${SFMCP_HTTP_HOST:-127.0.0.1}"
export SFMCP_HTTP_PORT="${SFMCP_HTTP_PORT:-3333}"
poetry run sfmcp-http
