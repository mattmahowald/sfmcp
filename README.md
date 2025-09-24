# Salesforce local MCP server

This server uses the `sf` command line tool to extract information from salesforce,
exposed in tools for MCP access.

## Setup

### Temporary Authorization Setup

> You can complete all of these steps by running `bash setup.sh`

`sfmcp` bypasses the oauth process for the app by using local credentials and the `sf`
command line tool. Start by installing the `sf` cli by following these
(instructions)[https://developer.salesforce.com/docs/atlas.en-us.sfdx_setup.meta/sfdx_setup/sfdx_setup_install_cli.htm].

Run through the authorization workflow to connect to your target project. You can do
